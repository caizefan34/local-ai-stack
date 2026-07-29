import importlib.util
from pathlib import Path
import tempfile
import unittest
from code_intelligence import lsp_server


ROOT = Path(__file__).resolve().parents[1]


def load_module(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "code_intelligence" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


router = load_module("router")
indexer = load_module("index_codebase")
sandbox = load_module("sandbox")
feedback = load_module("feedback")
project_actions = load_module("project_actions")
feedback_prep = load_module("../lora-finetune/scripts/prepare_feedback")


class CodeIntelligenceTests(unittest.TestCase):
    def test_router_selects_code_and_completion_models(self):
        self.assertEqual(router.choose_model("修复这个 Python bug")['model'], "qwen2.5-coder:7b")
        self.assertEqual(router.choose_model("```python\nprint('hi')", completion=True)['model'], "qwen2.5-coder:1.5b")
        self.assertEqual(router.choose_model("Explain local RAG")['model'], "qwen3:8b")

    def test_python_index_contains_symbols_and_import_graph(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "sample.py").write_text('import os\nfrom pkg.mod import helper\n\nclass Service:\n    """Example service."""\n    def run(self):\n        return helper()\n\ndef main():\n    return Service().run()\n', encoding="utf-8")
            result = indexer.index_directory(root)
        names = {(chunk['kind'], chunk['name']) for chunk in result['chunks']}
        self.assertIn(('class', 'Service'), names)
        self.assertIn(('method', 'run'), names)
        self.assertIn(('function', 'main'), names)
        self.assertIn({'source': 'sample.py', 'target': 'pkg.mod'}, result['dependencies'])

    def test_sandbox_has_network_and_write_protections(self):
        command = sandbox.docker_command(Path('.'), 'python:3.12-alpine', 'python -m pytest', 30)
        self.assertIn('none', command)
        self.assertIn('--read-only', command)
        self.assertIn('--cap-drop', command)
        self.assertIn('no-new-privileges', command)

    def test_feedback_requires_explicit_approval_flag(self):
        source = (ROOT / "code_intelligence" / "feedback.py").read_text(encoding="utf-8")
        self.assertIn('if not args.approved', source)
        self.assertIn('feedback.jsonl', source)

    def test_project_actions_require_confirmation(self):
        source = (ROOT / "code_intelligence" / "project_actions.py").read_text(encoding="utf-8")
        self.assertIn('if args.confirm', source)
        self.assertIn('--confirm', source)

    def test_vscode_extension_uses_local_completion_model(self):
        manifest = (ROOT / "ide" / "vscode" / "package.json").read_text(encoding="utf-8")
        extension = (ROOT / "ide" / "vscode" / "extension.js").read_text(encoding="utf-8")
        self.assertIn('localAiStack.completionModel', manifest)
        self.assertIn('registerInlineCompletionItemProvider', extension)
        self.assertIn('localAiStack.fixSelection', extension)
        self.assertIn('localAiStack.generateTests', extension)
        self.assertIn('registerWebviewViewProvider', extension)
        self.assertIn('"viewsContainers"', manifest)
        self.assertIn('feedback', extension)
        self.assertIn('rating', extension)
        self.assertIn('thumb-up', extension)
        self.assertIn('thumb-down', extension)

    def test_fastgpt_exposes_code_models(self):
        config = (ROOT / "config" / "fastgpt-config.json").read_text(encoding="utf-8")
        self.assertIn('"model": "qwen2.5-coder:7b"', config)
        self.assertIn('"model": "qwen2.5-coder:1.5b"', config)

    def test_weekly_sync_can_build_the_code_index(self):
        sync = (ROOT / "knowledge-base" / "sync" / "fastgpt-weekly-sync.sh").read_text(encoding="utf-8")
        self.assertIn('CODE_INDEX_ENABLED', sync)
        self.assertIn('index_codebase.py', sync)

    def test_lsp_completion_prompt_bounds_editor_context(self):
        prompt = lsp_server.completion_prompt("line0\nline1", 1, 5)
        self.assertIn("line1", prompt)
        self.assertIn("Complete only the next code tokens", prompt)
        self.assertIn('MAX_CACHE_ENTRIES', (ROOT / "code_intelligence" / "lsp_server.py").read_text(encoding="utf-8"))

    def test_codebert_embedder_consumes_ast_index(self):
        source = (ROOT / "code_intelligence" / "embed_chunks.py").read_text(encoding="utf-8")
        self.assertIn('microsoft/codebert-base', source)
        self.assertIn('source.get("chunks", [])', source)

    def test_codegen_evaluation_creates_its_output_directory(self):
        source = (ROOT / "code_intelligence" / "evaluate_codegen.py").read_text(encoding="utf-8")
        self.assertIn('args.output.parent.mkdir(parents=True, exist_ok=True)', source)

    def test_runner_setup_script_registers_ollama_label(self):
        source = (ROOT / "scripts" / "setup-actions-runner.ps1").read_text(encoding="utf-8")
        self.assertIn("actions/runners/registration-token", source)
        self.assertIn("--labels 'ollama,gpu'", source)

    def test_quality_workflow_uses_windows_powershell_on_windows_runner(self):
        workflow = (ROOT / ".github" / "workflows" / "code-quality-eval.yml").read_text(encoding="utf-8")
        self.assertIn("shell: powershell", workflow)
        self.assertIn("$env:BASELINE", workflow)

    def test_feedback_preparation_uses_only_approved_corrections_or_answers(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "feedback.jsonl"
            path.write_text('{"prompt":"fix it","response":"bad","rating":"down","correction":"good"}\n{"prompt":"explain","response":"answer","rating":"up"}\n', encoding="utf-8")
            result = feedback_prep.convert(path)
        self.assertEqual([item["output"] for item in result], ["good", "answer"])
