import os
import sys
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))


class Sprint6ApiTestCase(unittest.TestCase):
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
        from app.models.team import Team
        from app.models.user import User, UserRole

        cls.TestClient = TestClient
        cls.SessionLocal = SessionLocal
        cls.hash_password = hash_password
        cls.Team = Team
        cls.User = User
        cls.UserRole = UserRole
        cls.app = app

        init_db()

        db = SessionLocal()
        try:
            maintenance_team = Team(name="Manutencao S6", sector="Manutencao", description="Equipe principal", active=True)
            utilities_team = Team(name="Utilidades S6", sector="Utilidades", description="Equipe apoio", active=True)
            db.add_all([maintenance_team, utilities_team])
            db.flush()

            manager = User(
                name="Gerente S6",
                username="gerente.s6",
                email="gerente.s6@manimaq.local",
                role=UserRole.GERENTE,
                active=True,
                team_id=maintenance_team.id,
                password_hash=hash_password("Senha@123"),
            )
            operator = User(
                name="Operador S6",
                username="operador.s6",
                email="operador.s6@manimaq.local",
                role=UserRole.OPERADOR,
                active=True,
                team_id=maintenance_team.id,
                password_hash=hash_password("Senha@123"),
            )
            db.add_all([manager, operator])
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
        from app.models.alert import Alert
        from app.models.equipment import Equipment
        from app.models.measurement import Measurement
        from app.models.occurrence import Occurrence
        from app.models.work_order import WorkOrder
        from app.models.work_order_status_history import WorkOrderStatusHistory

        db = self.SessionLocal()
        try:
            db.query(Alert).delete()
            db.query(WorkOrderStatusHistory).delete()
            db.query(WorkOrder).delete()
            db.query(Measurement).delete()
            db.query(Occurrence).delete()
            db.query(Equipment).delete()
            db.commit()
        finally:
            db.close()

    def _login(self, login: str, password: str) -> str:
        response = self.client.post("/api/auth/login", json={"login": login, "password": password})
        self.assertEqual(response.status_code, 200, response.text)
        return response.json()["access_token"]

    def _seed_operational_data(self) -> None:
        manager_token = self._login("gerente.s6", "Senha@123")
        manager_headers = {"Authorization": f"Bearer {manager_token}"}

        equipment_a = self.client.post(
            "/api/equipments",
            headers=manager_headers,
            json={
                "tag": "S6-01",
                "name": "Compressor A",
                "sector": "Utilidades",
                "criticality": "alta",
                "status": "ativo",
                "team_id": 1,
                "alert_measurement_type": "temperatura",
                "measurement_unit": "C",
                "alert_threshold_low": 70,
                "alert_threshold_medium": 80,
                "alert_threshold_high": 90,
                "alert_threshold_critical": 100,
            },
        )
        self.assertEqual(equipment_a.status_code, 201, equipment_a.text)

        equipment_b = self.client.post(
            "/api/equipments",
            headers=manager_headers,
            json={
                "tag": "S6-02",
                "name": "Bomba B",
                "sector": "Utilidades",
                "criticality": "media",
                "status": "ativo",
                "team_id": 2,
                "alert_measurement_type": "vibracao",
                "measurement_unit": "mm/s",
                "alert_threshold_low": 2,
                "alert_threshold_medium": 3,
                "alert_threshold_high": 4,
                "alert_threshold_critical": 5,
            },
        )
        self.assertEqual(equipment_b.status_code, 201, equipment_b.text)

        occurrence_payloads = [
            {
                "equipment_id": 1,
                "severity": "alta",
                "safety_risk": False,
                "production_stop": True,
                "description": "Parada inesperada na linha do compressor",
                "occurred_at": "2026-04-24T08:00:00Z",
            },
            {
                "equipment_id": 1,
                "severity": "media",
                "safety_risk": False,
                "production_stop": False,
                "description": "Ruido acima do padrao",
                "occurred_at": "2026-04-24T09:00:00Z",
            },
            {
                "equipment_id": 2,
                "severity": "baixa",
                "safety_risk": False,
                "production_stop": False,
                "description": "Vibracao leve em monitoramento",
                "occurred_at": "2026-04-24T10:00:00Z",
            },
        ]
        for payload in occurrence_payloads:
            response = self.client.post("/api/occurrences", headers=manager_headers, json=payload)
            self.assertEqual(response.status_code, 201, response.text)

        measurement_response = self.client.post(
            "/api/measurements",
            headers=manager_headers,
            json={
                "equipment_id": 2,
                "measurement_type": "vibracao",
                "value": 4.2,
                "unit": "mm/s",
                "measured_at": "2026-04-24T11:00:00Z",
            },
        )
        self.assertEqual(measurement_response.status_code, 201, measurement_response.text)

        work_order_open = self.client.post(
            "/api/work-orders",
            headers=manager_headers,
            json={
                "equipment_id": 1,
                "team_id": 1,
                "type": "corretiva",
                "priority": "alta",
                "description": "Inspecionar compressor apos parada",
                "origin": "manual",
                "planned_start_at": "2026-04-24T08:30:00Z",
                "estimated_duration_hours": 4,
                "initial_note": "Abrir imediatamente",
            },
        )
        self.assertEqual(work_order_open.status_code, 201, work_order_open.text)

        work_order_done = self.client.post(
            "/api/work-orders",
            headers=manager_headers,
            json={
                "equipment_id": 2,
                "team_id": 2,
                "type": "preventiva",
                "priority": "media",
                "description": "Revisao preventiva da bomba",
                "origin": "manual",
                "planned_start_at": "2026-04-23T08:30:00Z",
                "estimated_duration_hours": 2,
                "initial_note": "Programada",
            },
        )
        self.assertEqual(work_order_done.status_code, 201, work_order_done.text)
        work_order_done_id = work_order_done.json()["id"]

        start_done = self.client.post(
            f"/api/work-orders/{work_order_done_id}/status",
            headers=manager_headers,
            json={
                "status": "em_execucao",
                "note": "Equipe iniciou atendimento",
                "transition_at": "2026-04-23T09:00:00Z",
            },
        )
        self.assertEqual(start_done.status_code, 200, start_done.text)

        conclude_done = self.client.post(
            f"/api/work-orders/{work_order_done_id}/status",
            headers=manager_headers,
            json={
                "status": "concluida",
                "note": "Servico finalizado",
                "transition_at": "2026-04-23T11:00:00Z",
            },
        )
        self.assertEqual(conclude_done.status_code, 200, conclude_done.text)

        alert_review = self.client.get("/api/alerts", headers=manager_headers)
        self.assertEqual(alert_review.status_code, 200, alert_review.text)
        reviewed_id = next(item["id"] for item in alert_review.json() if item["equipment_id"] == 1)
        review_response = self.client.post(f"/api/alerts/{reviewed_id}/review", headers=manager_headers)
        self.assertEqual(review_response.status_code, 200, review_response.text)

    def test_dashboard_overview_returns_real_kpis_and_rankings(self) -> None:
        self._seed_operational_data()
        manager_token = self._login("gerente.s6", "Senha@123")
        manager_headers = {"Authorization": f"Bearer {manager_token}"}

        response = self.client.get("/api/dashboard/overview?period_days=365", headers=manager_headers)
        self.assertEqual(response.status_code, 200, response.text)
        payload = response.json()

        self.assertEqual(payload["scope"], "global")
        self.assertEqual(payload["kpis"]["open_work_orders"], 1)
        self.assertEqual(payload["kpis"]["completed_work_orders"], 1)
        self.assertEqual(payload["kpis"]["work_order_backlog"], 1)
        self.assertEqual(payload["kpis"]["corrective_percentage"], 50.0)
        self.assertEqual(payload["kpis"]["preventive_percentage"], 50.0)
        self.assertEqual(payload["kpis"]["total_occurrences"], 3)
        self.assertEqual(payload["kpis"]["open_alerts"], 1)
        self.assertEqual(payload["kpis"]["reviewed_alerts"], 1)
        self.assertEqual(payload["top_failure_equipments"][0]["equipment_tag"], "S6-01")
        self.assertEqual(payload["top_failure_equipments"][0]["occurrences"], 2)
        self.assertEqual(payload["work_orders_by_team"][0]["work_orders"], 1)
        self.assertEqual(len(payload["work_orders_by_type"]), 2)

    def test_reports_apply_filters_and_operator_scope(self) -> None:
        self._seed_operational_data()
        manager_token = self._login("gerente.s6", "Senha@123")
        operator_token = self._login("operador.s6", "Senha@123")
        manager_headers = {"Authorization": f"Bearer {manager_token}"}
        operator_headers = {"Authorization": f"Bearer {operator_token}"}

        manager_report = self.client.get(
            "/api/dashboard/reports?period_days=365&team_id=1&maintenance_type=corretiva",
            headers=manager_headers,
        )
        self.assertEqual(manager_report.status_code, 200, manager_report.text)
        manager_payload = manager_report.json()
        self.assertEqual(manager_payload["kpis"]["open_work_orders"], 1)
        self.assertEqual(manager_payload["kpis"]["completed_work_orders"], 0)
        self.assertEqual(manager_payload["kpis"]["corrective_percentage"], 100.0)
        self.assertEqual(manager_payload["work_orders_by_team"][0]["team_id"], 1)
        self.assertEqual(manager_payload["occurrences_by_equipment"][0]["equipment_tag"], "S6-01")

        operator_report = self.client.get("/api/dashboard/reports?period_days=365", headers=operator_headers)
        self.assertEqual(operator_report.status_code, 200, operator_report.text)
        operator_payload = operator_report.json()
        self.assertEqual(operator_payload["scope"], "team")
        self.assertEqual(operator_payload["team_id"], 1)
        self.assertEqual(operator_payload["kpis"]["open_work_orders"], 1)
        self.assertEqual(operator_payload["kpis"]["completed_work_orders"], 0)
        self.assertEqual(operator_payload["kpis"]["total_occurrences"], 2)
        self.assertEqual(operator_payload["work_orders_by_team"][0]["team_id"], 1)

        forbidden_team = self.client.get("/api/dashboard/reports?team_id=2", headers=operator_headers)
        self.assertEqual(forbidden_team.status_code, 403, forbidden_team.text)

    def test_reports_include_fallback_analytical_reading_without_openai(self) -> None:
        self._seed_operational_data()
        manager_token = self._login("gerente.s6", "Senha@123")
        manager_headers = {"Authorization": f"Bearer {manager_token}"}

        response = self.client.get("/api/dashboard/reports?period_days=365", headers=manager_headers)
        self.assertEqual(response.status_code, 200, response.text)
        payload = response.json()

        self.assertEqual(payload["analytical_reading"]["source"], "fallback")
        self.assertIsNone(payload["analytical_reading"]["model"])
        self.assertTrue(payload["analytical_reading"]["summary"])
        self.assertGreaterEqual(len(payload["analytical_reading"]["attention_points"]), 2)
        self.assertIn("Nao substitui decisao humana", payload["analytical_reading"]["disclaimer"])

    def test_reports_include_ai_analytical_reading_when_openai_responds(self) -> None:
        self._seed_operational_data()
        manager_token = self._login("gerente.s6", "Senha@123")
        manager_headers = {"Authorization": f"Bearer {manager_token}"}

        with patch("app.services.analytics.settings.openai_api_key", "test-key"), patch(
            "app.services.analytics.request.urlopen"
        ) as mock_urlopen:
            mock_response = mock_urlopen.return_value.__enter__.return_value
            mock_response.read.return_value = (
                b'{"output_text":"{\\"summary\\":\\"Leitura sintetica.\\",\\"attention_points\\":[\\"Ponto 1\\",\\"Ponto 2\\"],\\"patterns\\":[\\"Padrao 1\\",\\"Padrao 2\\"],\\"recommendations\\":[\\"Recomendacao 1\\",\\"Recomendacao 2\\"]}"}'
            )

            response = self.client.get("/api/dashboard/reports?period_days=365", headers=manager_headers)
        self.assertEqual(response.status_code, 200, response.text)
        payload = response.json()

        self.assertEqual(payload["analytical_reading"]["source"], "ai")
        self.assertEqual(payload["analytical_reading"]["model"], "gpt-5.4-mini")
        self.assertEqual(payload["analytical_reading"]["summary"], "Leitura sintetica.")
        self.assertEqual(payload["analytical_reading"]["attention_points"][0], "Ponto 1")


if __name__ == "__main__":
    unittest.main()
