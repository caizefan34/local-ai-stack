import io
import time
import unittest
from unittest import mock

from control_plane.models import ModelError, ModelManager


class FakeProcess:
    def __init__(self, lines=("pulling\n",), return_code=0):
        self.stdout = io.StringIO("".join(lines))
        self.return_code = return_code

    def wait(self):
        return self.return_code


class ModelManagerTests(unittest.TestCase):
    def wait_for_job(self, manager):
        for _ in range(50):
            job = manager.jobs()[0]
            if job["status"] != "running":
                return job
            time.sleep(0.01)
        self.fail("job did not complete")

    def test_catalog_is_allowlisted_and_pull_uses_argument_vector(self):
        calls = []
        def popen(*args, **kwargs):
            calls.append((args, kwargs))
            return FakeProcess()
        manager = ModelManager(popen)
        job = manager.start_pull("coder-generation")
        self.assertIn(job["status"], {"running", "completed"})
        completed = self.wait_for_job(manager)
        self.assertEqual(completed["status"], "completed")
        self.assertEqual(calls[0][0][0], ["ollama", "pull", "qwen2.5-coder:7b"])
        with self.assertRaises(ModelError):
            manager.start_pull("arbitrary-command")

    def test_duplicate_download_is_rejected(self):
        class BlockingProcess(FakeProcess):
            def wait(self):
                time.sleep(0.2)
                return 0
        manager = ModelManager(lambda *_args, **_kwargs: BlockingProcess())
        manager.start_pull("qwen3-main")
        with self.assertRaisesRegex(ModelError, "already downloading"):
            manager.start_pull("qwen3-main")

    @mock.patch("control_plane.models.ollama.list_models", side_effect=Exception("offline"))
    def test_installed_models_reports_unavailable_ollama(self, _models):
        manager = ModelManager()
        self.assertEqual(manager.installed(), {"models": [], "error": "offline"})


if __name__ == "__main__":
    unittest.main()
