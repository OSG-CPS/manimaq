import os
import sys
import tempfile
import unittest
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))


class BootstrapAuthTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        cls.temp_db.close()

        os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
        os.environ["DATABASE_URL"] = f"sqlite:///{Path(cls.temp_db.name).as_posix()}"

        from fastapi.testclient import TestClient

        from app.db.session import SessionLocal, init_db
        from app.main import app
        from app.models.user import User

        cls.TestClient = TestClient
        cls.SessionLocal = SessionLocal
        cls.User = User
        cls.app = app

        init_db()

    @classmethod
    def tearDownClass(cls) -> None:
        try:
            Path(cls.temp_db.name).unlink(missing_ok=True)
        except PermissionError:
            pass

    def setUp(self) -> None:
        self.client = self.TestClient(self.app)
        db = self.SessionLocal()
        try:
            db.query(self.User).delete()
            db.commit()
        finally:
            db.close()

    def test_bootstrap_status_requires_admin_creation_when_database_is_empty(self) -> None:
        response = self.client.get("/api/auth/bootstrap-status")
        self.assertEqual(response.status_code, 200, response.text)
        payload = response.json()

        self.assertTrue(payload["bootstrap_required"])
        self.assertEqual(payload["users_count"], 0)

    def test_bootstrap_admin_creates_first_admin_and_returns_session(self) -> None:
        response = self.client.post(
            "/api/auth/bootstrap-admin",
            json={
                "name": "Primeiro Admin",
                "username": "Admin.Inicial",
                "email": "admin.inicial@manimaq.local",
                "password": "Senha@123",
            },
        )
        self.assertEqual(response.status_code, 201, response.text)
        payload = response.json()

        self.assertTrue(payload["access_token"])
        self.assertEqual(payload["user"]["role"], "admin")
        self.assertEqual(payload["user"]["username"], "admin.inicial")
        self.assertIsNone(payload["user"]["team_id"])

        login_response = self.client.post(
            "/api/auth/login",
            json={"login": "admin.inicial", "password": "Senha@123"},
        )
        self.assertEqual(login_response.status_code, 200, login_response.text)

    def test_bootstrap_admin_is_blocked_after_first_user_exists(self) -> None:
        first = self.client.post(
            "/api/auth/bootstrap-admin",
            json={
                "name": "Primeiro Admin",
                "username": "primeiro.admin",
                "email": "primeiro.admin@manimaq.local",
                "password": "Senha@123",
            },
        )
        self.assertEqual(first.status_code, 201, first.text)

        second = self.client.post(
            "/api/auth/bootstrap-admin",
            json={
                "name": "Segundo Admin",
                "username": "segundo.admin",
                "email": "segundo.admin@manimaq.local",
                "password": "Senha@123",
            },
        )
        self.assertEqual(second.status_code, 409, second.text)

        status_response = self.client.get("/api/auth/bootstrap-status")
        self.assertEqual(status_response.status_code, 200, status_response.text)
        self.assertFalse(status_response.json()["bootstrap_required"])


if __name__ == "__main__":
    unittest.main()
