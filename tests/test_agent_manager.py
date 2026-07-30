from pathlib import Path
import tempfile
import time
import unittest

from control_plane.agents import AgentManager


class ScriptedModel:
    def complete(self, _prompt: str) -> str:
        return '{"type":"final","answer":"Workspace inspection completed."}'


class AgentManagerTests(unittest.TestCase):
    def test_runs_a_bounded_job_and_exposes_safe_result(self):
        with tempfile.TemporaryDirectory() as directory:
            manager = AgentManager(
                Path(directory),
                model_factory=lambda _model: ScriptedModel(),
                allowed_models=("qwen3:8b",),
            )
            job = manager.start("Inspect this workspace", "workspace-investigate", "qwen3:8b", 3)
            job_id = job["id"]
            for _ in range(100):
                job = manager.get(job_id)
                if job["status"] not in {"queued", "running"}:
                    break
                time.sleep(0.01)
            self.assertEqual(job["status"], "completed")
            self.assertEqual(job["answer"], "Workspace inspection completed.")
            self.assertEqual(job["workspace"], Path(directory).name)

    def test_rejects_unknown_model_and_empty_task(self):
        with tempfile.TemporaryDirectory() as directory:
            manager = AgentManager(Path(directory), allowed_models=("qwen3:8b",))
            with self.assertRaisesRegex(ValueError, "allowed"):
                manager.start("Inspect", "workspace-investigate", "unknown:model", 3)
            with self.assertRaisesRegex(ValueError, "task"):
                manager.start("", "workspace-investigate", "qwen3:8b", 3)


if __name__ == "__main__":
    unittest.main()
