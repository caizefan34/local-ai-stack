from pathlib import Path
import tempfile
import unittest
from unittest import mock

from fastapi.testclient import TestClient

from control_plane.app import create_app
from control_plane.store import Store


class ControlPlaneTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.root = Path(self.directory.name) / "stack"
        self.root.mkdir()
        self.database = Path(self.directory.name) / "control.sqlite3"
        self.store = Store(self.database)
        self.store.initialize()
        self.store.create_user("admin", "correct-horse-battery-staple", "admin")
        self.app = create_app(self.database, self.root)
        self.client_context = TestClient(self.app)
        self.client = self.client_context.__enter__()

    def tearDown(self):
        self.client_context.__exit__(None, None, None)
        self.directory.cleanup()

    def login(self, username="admin", password="correct-horse-battery-staple"):
        response = self.client.post("/api/auth/login", json={"username": username, "password": password})
        self.assertEqual(response.status_code, 200)
        return {"Authorization": f"Bearer {response.json()['token']}"}

    def test_setup_endpoint_is_one_time_only(self):
        self.assertEqual(self.client.get("/api/setup/status").json(), {"initialized": True})
        response = self.client.post("/api/setup/bootstrap", json={"username": "late", "password": "long-enough-password"})
        self.assertEqual(response.status_code, 409)

    def test_setup_creates_first_administrator(self):
        first_db = Path(self.directory.name) / "first.sqlite3"
        app = create_app(first_db, self.root)
        with TestClient(app) as client:
            self.assertEqual(client.get("/api/setup/status").json(), {"initialized": False})
            response = client.post("/api/setup/bootstrap", json={"username": "first-admin", "password": "correct-horse-battery-staple"})
            self.assertEqual(response.status_code, 201)
            self.assertEqual(client.get("/api/setup/status").json(), {"initialized": True})
            self.assertEqual(client.post("/api/auth/login", json={"username": "first-admin", "password": "correct-horse-battery-staple"}).status_code, 200)

    def test_authentication_and_roles(self):
        self.assertEqual(self.client.get("/api/health").status_code, 401)
        admin_headers = self.login()
        created = self.client.post("/api/users", headers=admin_headers, json={"username": "operator", "password": "another-correct-password", "role": "operator"})
        self.assertEqual(created.status_code, 201)
        operator_headers = self.login("operator", "another-correct-password")
        self.assertEqual(self.client.get("/api/users", headers=operator_headers).status_code, 403)
        self.assertEqual(self.client.get("/api/users", headers=admin_headers).status_code, 200)

    @mock.patch("control_plane.app.run_action", return_value="completed")
    def test_only_operator_or_admin_can_run_allowlisted_actions(self, run_action):
        admin_headers = self.login()
        self.client.post("/api/users", headers=admin_headers, json={"username": "viewer", "password": "viewer-password-long", "role": "viewer"})
        viewer_headers = self.login("viewer", "viewer-password-long")
        self.assertEqual(self.client.post("/api/actions/start-all", headers=viewer_headers).status_code, 403)
        self.assertEqual(self.client.post("/api/actions/start-all", headers=admin_headers).json(), {"output": "completed"})
        run_action.assert_called_once_with("start-all", self.root)

    def test_disabling_user_invalidates_existing_session(self):
        headers = self.login()
        self.assertEqual(self.client.post("/api/users", headers=headers, json={"username": "backup-admin", "password": "another-admin-password", "role": "admin"}).status_code, 201)
        self.assertEqual(self.client.patch("/api/users/admin", headers=headers, json={"active": False}).status_code, 200)
        self.assertEqual(self.client.get("/api/auth/me", headers=headers).status_code, 401)

    def test_last_administrator_cannot_be_disabled(self):
        headers = self.login()
        self.assertEqual(self.client.patch("/api/users/admin", headers=headers, json={"active": False}).status_code, 400)

    def test_password_and_username_policy(self):
        headers = self.login()
        response = self.client.post("/api/users", headers=headers, json={"username": "bad name", "password": "long-enough-password", "role": "viewer"})
        self.assertEqual(response.status_code, 400)
        response = self.client.post("/api/users", headers=headers, json={"username": "short", "password": "too-short", "role": "viewer"})
        self.assertEqual(response.status_code, 422)

    def test_model_catalog_is_visible_to_viewers_but_download_requires_operator(self):
        class FakeManager:
            def catalog(self): return [{"id": "main"}]
            def installed(self): return {"models": [], "error": None}
            def jobs(self): return []
            def start_pull(self, model_id): return {"id": "job", "model_id": model_id, "status": "running"}
        self.client_context.__exit__(None, None, None)
        self.app = create_app(self.database, self.root, FakeManager())
        self.client_context = TestClient(self.app)
        self.client = self.client_context.__enter__()
        admin_headers = self.login()
        self.client.post("/api/users", headers=admin_headers, json={"username": "viewer", "password": "viewer-password-long", "role": "viewer"})
        viewer_headers = self.login("viewer", "viewer-password-long")
        self.assertEqual(self.client.get("/api/models", headers=viewer_headers).status_code, 200)
        self.assertEqual(self.client.post("/api/models/pull/main", headers=viewer_headers).status_code, 403)
        self.assertEqual(self.client.post("/api/models/pull/main", headers=admin_headers).status_code, 202)


if __name__ == "__main__":
    unittest.main()
