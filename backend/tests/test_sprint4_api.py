import os
import sys
import tempfile
import unittest
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))


class Sprint4ApiTestCase(unittest.TestCase):
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
        cls.app = app

        init_db()

        db = SessionLocal()
        try:
            maintenance_team = Team(name="Manutencao Teste", sector="Manutencao", description="Equipe principal", active=True)
            support_team = Team(name="Apoio Teste", sector="Utilidades", description="Equipe secundaria", active=True)
            db.add_all([maintenance_team, support_team])
            db.flush()

            admin = User(
                name="Admin Teste",
                username="admin.s4",
                email="admin.s4@manimaq.local",
                role=UserRole.ADMIN,
                active=True,
                team_id=maintenance_team.id,
                password_hash=hash_password("Senha@123"),
            )
            operator = User(
                name="Operador Time",
                username="operador.s4",
                email="operador.s4@manimaq.local",
                role=UserRole.OPERADOR,
                active=True,
                team_id=maintenance_team.id,
                password_hash=hash_password("Senha@123"),
            )
            other_operator = User(
                name="Operador Outro Time",
                username="operador.outro",
                email="operador.outro@manimaq.local",
                role=UserRole.OPERADOR,
                active=True,
                team_id=support_team.id,
                password_hash=hash_password("Senha@123"),
            )
            equipment = Equipment(
                tag="S4-01",
                name="Prensa Hidraulica",
                sector="Producao",
                criticality="alta",
                status="ativo",
                active=True,
                team_id=maintenance_team.id,
            )
            db.add_all([admin, operator, other_operator, equipment])
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
        self.client = self.TestClient(self.app)

    def _login(self, login: str, password: str) -> str:
        response = self.client.post("/api/auth/login", json={"login": login, "password": password})
        self.assertEqual(response.status_code, 200, response.text)
        return response.json()["access_token"]

    def test_admin_creates_and_operator_executes_work_order(self) -> None:
        admin_token = self._login("admin.s4", "Senha@123")
        operator_token = self._login("operador.s4", "Senha@123")
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        operator_headers = {"Authorization": f"Bearer {operator_token}"}

        create_response = self.client.post(
            "/api/work-orders",
            headers=admin_headers,
            json={
                "equipment_id": 1,
                "team_id": 1,
                "type": "corretiva",
                "priority": "alta",
                "description": "Investigar vazamento no conjunto hidraulico",
                "origin": "manual",
                "planned_start_at": "2026-04-24T10:00:00Z",
                "estimated_duration_hours": 4,
                "initial_note": "Abrir atendimento ainda hoje",
            },
        )
        self.assertEqual(create_response.status_code, 201, create_response.text)
        payload = create_response.json()
        self.assertEqual(payload["status"], "aberta")
        self.assertEqual(payload["status_history"][0]["new_status"], "aberta")
        work_order_id = payload["id"]

        list_response = self.client.get("/api/work-orders", headers=operator_headers)
        self.assertEqual(list_response.status_code, 200, list_response.text)
        self.assertEqual(len(list_response.json()), 1)

        start_response = self.client.post(
            f"/api/work-orders/{work_order_id}/status",
            headers=operator_headers,
            json={
                "status": "em_execucao",
                "note": "Equipe iniciou desmontagem do conjunto",
                "transition_at": "2026-04-24T12:30:00Z",
            },
        )
        self.assertEqual(start_response.status_code, 200, start_response.text)
        self.assertEqual(start_response.json()["status"], "em_execucao")
        self.assertEqual(start_response.json()["status_history"][0]["transition_at"], "2026-04-24T12:30:00Z")

        finish_response = self.client.post(
            f"/api/work-orders/{work_order_id}/status",
            headers=operator_headers,
            json={
                "status": "concluida",
                "note": "Vedacao substituida e maquina liberada",
                "transition_at": "2026-04-24T14:15:00Z",
            },
        )
        self.assertEqual(finish_response.status_code, 200, finish_response.text)
        self.assertEqual(finish_response.json()["status"], "concluida")
        self.assertEqual(len(finish_response.json()["status_history"]), 3)
        self.assertEqual(finish_response.json()["status_history"][0]["author"]["username"], "operador.s4")
        self.assertEqual(finish_response.json()["status_history"][0]["transition_at"], "2026-04-24T14:15:00Z")

    def test_operator_cannot_cancel_and_other_team_cannot_view(self) -> None:
        admin_token = self._login("admin.s4", "Senha@123")
        operator_token = self._login("operador.s4", "Senha@123")
        other_operator_token = self._login("operador.outro", "Senha@123")
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        operator_headers = {"Authorization": f"Bearer {operator_token}"}
        other_operator_headers = {"Authorization": f"Bearer {other_operator_token}"}

        create_response = self.client.post(
            "/api/work-orders",
            headers=admin_headers,
            json={
                "equipment_id": 1,
                "team_id": 1,
                "type": "preventiva",
                "priority": "media",
                "description": "Inspecao preventiva antes do turno da noite",
                "origin": "manual",
            },
        )
        self.assertEqual(create_response.status_code, 201, create_response.text)
        work_order_id = create_response.json()["id"]

        cancel_response = self.client.post(
            f"/api/work-orders/{work_order_id}/status",
            headers=operator_headers,
            json={"status": "cancelada", "note": "Tentativa indevida"},
        )
        self.assertEqual(cancel_response.status_code, 403, cancel_response.text)

        detail_response = self.client.get(f"/api/work-orders/{work_order_id}", headers=other_operator_headers)
        self.assertEqual(detail_response.status_code, 403, detail_response.text)


if __name__ == "__main__":
    unittest.main()
