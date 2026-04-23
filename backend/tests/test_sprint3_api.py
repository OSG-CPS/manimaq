import os
import sys
import tempfile
import unittest
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))


class Sprint3ApiTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        cls.temp_db.close()

        os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
        os.environ["DATABASE_URL"] = f"sqlite:///{Path(cls.temp_db.name).as_posix()}"

        from fastapi.testclient import TestClient

        from app.core.security import hash_password
        from app.db.session import SessionLocal, init_db
        from app.main import app
        from app.models.equipment import Equipment
        from app.models.team import Team
        from app.models.user import User, UserRole

        cls.TestClient = TestClient
        cls.SessionLocal = SessionLocal
        cls.hash_password = hash_password
        cls.Team = Team
        cls.User = User
        cls.UserRole = UserRole
        cls.Equipment = Equipment

        init_db()

        db = SessionLocal()
        try:
            team = Team(name="Teste Operacao", sector="Producao", description="Equipe de teste", active=True)
            db.add(team)
            db.flush()

            admin = User(
                name="Admin Teste",
                username="admin.teste",
                email="admin.teste@manimaq.local",
                role=UserRole.ADMIN,
                active=True,
                team_id=team.id,
                password_hash=hash_password("Senha@123"),
            )
            operator = User(
                name="Operador Teste",
                username="operador.teste",
                email="operador.teste@manimaq.local",
                role=UserRole.OPERADOR,
                active=True,
                team_id=team.id,
                password_hash=hash_password("Senha@123"),
            )
            equipment = Equipment(
                tag="TEST-01",
                name="Equipamento Teste",
                sector="Producao",
                criticality="media",
                status="ativo",
                active=True,
                team_id=team.id,
            )
            db.add_all([admin, operator, equipment])
            db.commit()
        finally:
            db.close()

    @classmethod
    def tearDownClass(cls) -> None:
        try:
            Path(cls.temp_db.name).unlink(missing_ok=True)
        except PermissionError:
            pass

    def setUp(self) -> None:
        from app.main import app

        self.client = self.TestClient(app)

    def _login(self, login: str, password: str) -> str:
        response = self.client.post(
            "/api/auth/login",
            json={"login": login, "password": password},
        )
        self.assertEqual(response.status_code, 200, response.text)
        return response.json()["access_token"]

    def test_occurrence_measurement_and_history_flow(self) -> None:
        token = self._login("operador.teste", "Senha@123")
        headers = {"Authorization": f"Bearer {token}"}

        catalog_response = self.client.get("/api/equipment-history/catalog", headers=headers)
        self.assertEqual(catalog_response.status_code, 200, catalog_response.text)
        equipment_id = catalog_response.json()[0]["id"]

        occurrence_response = self.client.post(
            "/api/occurrences",
            headers=headers,
            json={
                "equipment_id": equipment_id,
                "severity": "alta",
                "safety_risk": True,
                "production_stop": True,
                "description": "Falha intermitente detectada na partida",
                "occurred_at": "2026-04-23T15:30:00Z",
            },
        )
        self.assertEqual(occurrence_response.status_code, 201, occurrence_response.text)
        self.assertEqual(occurrence_response.json()["author"]["username"], "operador.teste")
        self.assertEqual(occurrence_response.json()["occurred_at"], "2026-04-23T15:30:00Z")

        measurement_response = self.client.post(
            "/api/measurements",
            headers=headers,
            json={
                "equipment_id": equipment_id,
                "measurement_type": "temperatura",
                "value": 78.5,
                "unit": "C",
                "measured_at": "2026-04-23T15:35:00Z",
            },
        )
        self.assertEqual(measurement_response.status_code, 201, measurement_response.text)
        self.assertEqual(measurement_response.json()["measurement_type"], "temperatura")
        self.assertEqual(measurement_response.json()["measured_at"], "2026-04-23T15:35:00Z")

        history_response = self.client.get(f"/api/equipment-history/{equipment_id}", headers=headers)
        self.assertEqual(history_response.status_code, 200, history_response.text)
        payload = history_response.json()

        self.assertEqual(payload["equipment"]["tag"], "TEST-01")
        self.assertEqual(len(payload["occurrences"]), 1)
        self.assertEqual(len(payload["measurements"]), 1)
        self.assertTrue(payload["occurrences"][0]["production_stop"])
        self.assertEqual(payload["occurrences"][0]["occurred_at"], "2026-04-23T15:30:00Z")
        self.assertEqual(payload["measurements"][0]["measured_at"], "2026-04-23T15:35:00Z")

    def test_occurrence_rejects_unknown_equipment(self) -> None:
        token = self._login("admin.teste", "Senha@123")
        headers = {"Authorization": f"Bearer {token}"}

        response = self.client.post(
            "/api/occurrences",
            headers=headers,
            json={
                "equipment_id": 999999,
                "severity": "media",
                "safety_risk": False,
                "production_stop": False,
                "description": "Equipamento inexistente para validar erro",
            },
        )
        self.assertEqual(response.status_code, 404, response.text)


if __name__ == "__main__":
    unittest.main()
