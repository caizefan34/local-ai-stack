import json
from pathlib import Path
import tempfile
import unittest

from agent_workflows.engine import AgentEngine, AgentError
from agent_workflows.schemas import ActionValidationError, FinalAction, ToolAction, parse_action
from agent_workflows.tools import ToolError, ToolRegistry, WorkspaceTools
from agent_workflows.workflows import get_workflow


class ScriptedModel:
    def __init__(self, responses):
        self.responses = iter(responses)
        self.prompts = []

    def complete(self, prompt):
        self.prompts.append(prompt)
        return next(self.responses)


class AgentWorkflowTests(unittest.TestCase):
    def test_schema_accepts_only_strict_actions(self):
        self.assertEqual(parse_action('{"type":"final","answer":"done"}'), FinalAction("done"))
        self.assertEqual(parse_action('```json\n{"type":"tool","tool":"list_files","arguments":{},"summary":"Inspect files"}\n```'), ToolAction("list_files", {}, "Inspect files"))
        with self.assertRaises(ActionValidationError):
            parse_action('{"type":"final","answer":"done","extra":true}')

    def test_multi_step_run_records_summaries_without_raw_reasoning(self):
        with tempfile.TemporaryDirectory() as directory:
            Path(directory, "app.py").write_text("def main():\n    return 1\n", encoding="utf-8")
            model = ScriptedModel([
                '{"type":"tool","tool":"search_text","arguments":{"query":"main","pattern":"*.py"},"summary":"Locate the entry point"}',
                '{"type":"tool","tool":"read_file","arguments":{"path":"app.py"},"summary":"Inspect the implementation"}',
                '{"type":"final","answer":"app.py defines main on line 1."}',
            ])
            result = AgentEngine(model, Path(directory), get_workflow("workspace-investigate")).run("Find the entry point")
        self.assertEqual(result.steps, 3)
        self.assertEqual([event.summary for event in result.trace[:2]], ["Locate the entry point", "Inspect the implementation"])
        self.assertIn("UNTRUSTED TOOL OUTPUT", model.prompts[-1])

    def test_invalid_json_gets_one_repair_attempt(self):
        with tempfile.TemporaryDirectory() as directory:
            model = ScriptedModel(["not json", '{"type":"final","answer":"repaired"}'])
            result = AgentEngine(model, Path(directory), get_workflow("workspace-investigate")).run("Task")
        self.assertEqual(result.answer, "repaired")
        self.assertEqual(len(model.prompts), 2)

    def test_repeated_actions_and_step_budget_stop_loops(self):
        action = '{"type":"tool","tool":"list_files","arguments":{},"summary":"List again"}'
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(AgentError, "Repeated action"):
                AgentEngine(ScriptedModel([action, action, action]), Path(directory), get_workflow("workspace-investigate"), max_steps=4).run("Loop")
            with self.assertRaisesRegex(AgentError, "Step budget"):
                AgentEngine(ScriptedModel([action]), Path(directory), get_workflow("workspace-investigate"), max_steps=1).run("Budget")

    def test_unknown_tool_is_returned_as_observation_for_recovery(self):
        with tempfile.TemporaryDirectory() as directory:
            model = ScriptedModel([
                '{"type":"tool","tool":"shell","arguments":{},"summary":"Try an unavailable tool"}',
                '{"type":"final","answer":"Shell access is unavailable."}',
            ])
            result = AgentEngine(model, Path(directory), get_workflow("workspace-investigate")).run("Use shell")
        self.assertEqual(result.answer, "Shell access is unavailable.")
        self.assertIn("Unknown tool", model.prompts[-1])

    def test_workspace_tools_enforce_boundaries_and_sensitive_file_denial(self):
        with tempfile.TemporaryDirectory() as directory, tempfile.TemporaryDirectory() as outside:
            root = Path(directory)
            (root / "src").mkdir()
            (root / "src" / "app.py").write_text("token = 'not-a-secret'\n", encoding="utf-8")
            (root / ".env").write_text("SECRET=value\n", encoding="utf-8")
            Path(outside, "outside.txt").write_text("outside", encoding="utf-8")
            tools = WorkspaceTools(root)
            self.assertEqual(tools.search_text("token", pattern="*.py")["results"][0]["path"], "src/app.py")
            self.assertNotIn(".env", tools.list_files()["files"])
            with self.assertRaises(ToolError):
                tools.read_file(".env")
            with self.assertRaises(ToolError):
                tools.read_file(str(Path(outside, "outside.txt")))

    def test_registry_rejects_invalid_arguments(self):
        with tempfile.TemporaryDirectory() as directory:
            registry = ToolRegistry(Path(directory))
            with self.assertRaisesRegex(ToolError, "Invalid arguments"):
                registry.execute("list_files", {"unknown": True})


if __name__ == "__main__":
    unittest.main()
