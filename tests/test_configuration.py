"""Fast, dependency-free checks for the local stack's critical configuration."""
from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parents[1]
COMPOSE = (ROOT / "docker" / "docker-compose.yml").read_text(encoding="utf-8")


class ConfigurationTests(unittest.TestCase):
    def test_compose_uses_repo_config_mount(self):
        mount_lines = [line.strip() for line in COMPOSE.splitlines() if "fastgpt-config.json:" in line]
        self.assertEqual(mount_lines, ["- ../config/fastgpt-config.json:/app/data/config.json:ro"])


    def test_compose_uses_service_dns_for_dependencies(self):
        for hostname in ("mongodb://mongo:27017/fastgpt", "PG_HOST: ${PG_HOST:-pg}", "redis://redis:6379"):
            self.assertIn(hostname, COMPOSE)
        self.assertIn("mongo:27017", COMPOSE)
        self.assertNotIn("fastgpt-mongo:27017", COMPOSE)


    def test_compose_requires_secrets_and_shell_healthcheck(self):
        self.assertIn("ADMIN_PASSWORD:?Set ADMIN_PASSWORD", COMPOSE)
        self.assertIn("TOKEN_KEY:?Set TOKEN_KEY", COMPOSE)
        self.assertIn('["CMD-SHELL", "wget --no-verbose', COMPOSE)


    def test_json_configs_are_valid(self):
        for path in (ROOT / "config").glob("*.json"):
            json.loads(path.read_text(encoding="utf-8"))

    def test_reranker_has_request_limits(self):
        reranker = (ROOT / "reranker" / "server.py").read_text(encoding="utf-8")
        self.assertIn("RERANKER_MAX_DOCUMENTS", reranker)
        self.assertIn("max_length=8192", reranker)

    def test_login_helper_has_no_default_password(self):
        helper = (ROOT / "scripts" / "automation" / "fastgpt_login.py").read_text(encoding="utf-8")
        self.assertNotIn('"1234"', helper)
        self.assertIn("timeout=10", helper)

    def test_example_environment_documents_reranker_limit(self):
        example = (ROOT / ".env.example").read_text(encoding="utf-8-sig")
        self.assertIn("RERANKER_MAX_DOCUMENTS=256", example)
