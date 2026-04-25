import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))


class Sprint5ApiTestCase(unittest.TestCase):
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
        from app.models.measurement import MeasurementType
        from app.models.team import Team
        from app.models.user import User, UserRole
        from app.models.equipment import Equipment
        from app.services import alerts as alerts_service

        cls.TestClient = TestClient
        cls.SessionLocal = SessionLocal
        cls.hash_password = hash_password
        cls.Team = Team
        cls.User = User
        cls.UserRole = UserRole
        cls.Equipment = Equipment
        cls.MeasurementType = MeasurementType
        cls.alerts_service = alerts_service
        cls.app = app

        init_db()

        db = SessionLocal()
        try:
            maintenance_team = Team(name="Manutencao S5", sector="Manutencao", description="Equipe principal", active=True)
            utilities_team = Team(name="Utilidades S5", sector="Utilidades", description="Equipe apoio", active=True)
            db.add_all([maintenance_team, utilities_team])
            db.flush()

            manager = User(
                name="Gerente S5",
                username="gerente.s5",
                email="gerente.s5@manimaq.local",
                role=UserRole.GERENTE,
                active=True,
                team_id=maintenance_team.id,
                password_hash=hash_password("Senha@123"),
            )
            operator = User(
                name="Operador S5",
                username="operador.s5",
                email="operador.s5@manimaq.local",
                role=UserRole.OPERADOR,
                active=True,
                team_id=maintenance_team.id,
                password_hash=hash_password("Senha@123"),
            )
            other_operator = User(
                name="Operador Utilidades",
                username="operador.util.s5",
                email="operador.util.s5@manimaq.local",
                role=UserRole.OPERADOR,
                active=True,
                team_id=utilities_team.id,
                password_hash=hash_password("Senha@123"),
            )
            equipment = Equipment(
                tag="S5-01",
                name="Compressor Central",
                sector="Utilidades",
                criticality="alta",
                status="ativo",
                active=True,
                team_id=maintenance_team.id,
                alert_measurement_type=MeasurementType.TEMPERATURA,
                measurement_unit="C",
                alert_threshold_low=70,
                alert_threshold_medium=80,
                alert_threshold_high=90,
                alert_threshold_critical=100,
            )
            db.add_all([manager, operator, other_operator, equipment])
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
        self.alerts_service.settings.openai_api_key = ""
        from app.models.alert import Alert
        from app.models.equipment import Equipment
        from app.models.measurement import MeasurementType
        from app.models.measurement import Measurement
        from app.models.occurrence import Occurrence
        from app.models.work_order_status_history import WorkOrderStatusHistory
        from app.models.work_order import WorkOrder

        db = self.SessionLocal()
        try:
            db.query(Alert).delete()
            db.query(WorkOrderStatusHistory).delete()
            db.query(WorkOrder).delete()
            db.query(Measurement).delete()
            db.query(Occurrence).delete()
            equipment = db.get(Equipment, 1)
            if equipment is not None:
                equipment.alert_measurement_type = MeasurementType.TEMPERATURA
                equipment.measurement_unit = "C"
                equipment.alert_threshold_low = 70
                equipment.alert_threshold_medium = 80
                equipment.alert_threshold_high = 90
                equipment.alert_threshold_critical = 100
            db.commit()
        finally:
            db.close()

    def _login(self, login: str, password: str) -> str:
        response = self.client.post("/api/auth/login", json={"login": login, "password": password})
        self.assertEqual(response.status_code, 200, response.text)
        return response.json()["access_token"]

    def test_occurrence_creates_rule_alert_and_manager_can_review(self) -> None:
        manager_token = self._login("gerente.s5", "Senha@123")
        operator_token = self._login("operador.s5", "Senha@123")
        manager_headers = {"Authorization": f"Bearer {manager_token}"}
        operator_headers = {"Authorization": f"Bearer {operator_token}"}

        create_response = self.client.post(
            "/api/occurrences",
            headers=operator_headers,
            json={
                "equipment_id": 1,
                "severity": "alta",
                "safety_risk": True,
                "production_stop": False,
                "description": "Vazamento com risco de contato na linha principal",
                "occurred_at": "2026-04-24T12:00:00Z",
            },
        )
        self.assertEqual(create_response.status_code, 201, create_response.text)

        alerts_response = self.client.get("/api/alerts", headers=manager_headers)
        self.assertEqual(alerts_response.status_code, 200, alerts_response.text)
        alerts_payload = alerts_response.json()
        self.assertEqual(len(alerts_payload), 1)
        self.assertEqual(alerts_payload[0]["source"], "rule")
        self.assertEqual(alerts_payload[0]["severity"], "critica")
        self.assertTrue(alerts_payload[0]["suggested_work_order"]["suggested"])
        self.assertEqual(alerts_payload[0]["suggested_work_order"]["priority"], "critica")

        review_response = self.client.post(f"/api/alerts/{alerts_payload[0]['id']}/review", headers=manager_headers)
        self.assertEqual(review_response.status_code, 200, review_response.text)
        self.assertEqual(review_response.json()["status"], "revisado")

    def test_measurement_threshold_creates_alert_and_operator_scope_is_team_based(self) -> None:
        manager_token = self._login("gerente.s5", "Senha@123")
        operator_token = self._login("operador.s5", "Senha@123")
        other_operator_token = self._login("operador.util.s5", "Senha@123")
        manager_headers = {"Authorization": f"Bearer {manager_token}"}
        operator_headers = {"Authorization": f"Bearer {operator_token}"}
        other_operator_headers = {"Authorization": f"Bearer {other_operator_token}"}

        first_measurement = self.client.post(
            "/api/measurements",
            headers=operator_headers,
            json={
                "equipment_id": 1,
                "measurement_type": "temperatura",
                "value": 75,
                "unit": "C",
                "measured_at": "2026-04-24T10:00:00Z",
            },
        )
        self.assertEqual(first_measurement.status_code, 201, first_measurement.text)

        threshold_measurement = self.client.post(
            "/api/measurements",
            headers=operator_headers,
            json={
                "equipment_id": 1,
                "measurement_type": "temperatura",
                "value": 92,
                "unit": "C",
                "measured_at": "2026-04-24T11:00:00Z",
            },
        )
        self.assertEqual(threshold_measurement.status_code, 201, threshold_measurement.text)

        alerts_response = self.client.get("/api/alerts?severity=alta", headers=manager_headers)
        self.assertEqual(alerts_response.status_code, 200, alerts_response.text)
        alerts_payload = alerts_response.json()
        self.assertEqual(len(alerts_payload), 1)
        self.assertEqual(alerts_payload[0]["origin_type"], "measurement")
        self.assertIn("faixa alta", alerts_payload[0]["message"].lower())

        operator_list = self.client.get("/api/alerts", headers=operator_headers)
        self.assertEqual(operator_list.status_code, 200, operator_list.text)
        self.assertEqual(len(operator_list.json()), 2)

        other_operator_list = self.client.get("/api/alerts", headers=other_operator_headers)
        self.assertEqual(other_operator_list.status_code, 200, other_operator_list.text)
        self.assertEqual(other_operator_list.json(), [])

    def test_equipment_threshold_config_drives_alert_severity_and_suggestion(self) -> None:
        manager_token = self._login("gerente.s5", "Senha@123")
        manager_headers = {"Authorization": f"Bearer {manager_token}"}

        create_equipment = self.client.post(
            "/api/equipments",
            headers=manager_headers,
            json={
                "tag": "S5-02",
                "name": "Bomba de Teste",
                "sector": "Utilidades",
                "criticality": "media",
                "status": "ativo",
                "team_id": 1,
                "alert_measurement_type": "vibracao",
                "measurement_unit": "mm/s",
                "alert_threshold_low": 2,
                "alert_threshold_medium": 3,
                "alert_threshold_high": 4,
                "alert_threshold_critical": 5,
            },
        )
        self.assertEqual(create_equipment.status_code, 201, create_equipment.text)

        low_alert_measurement = self.client.post(
            "/api/measurements",
            headers=manager_headers,
            json={
                "equipment_id": 2,
                "measurement_type": "vibracao",
                "value": 2.5,
                "unit": "mm/s",
                "measured_at": "2026-04-24T13:00:00Z",
            },
        )
        self.assertEqual(low_alert_measurement.status_code, 201, low_alert_measurement.text)

        alerts_response = self.client.get("/api/alerts?equipment_id=2", headers=manager_headers)
        self.assertEqual(alerts_response.status_code, 200, alerts_response.text)
        alerts_payload = alerts_response.json()
        self.assertEqual(len(alerts_payload), 1)
        self.assertEqual(alerts_payload[0]["severity"], "baixa")
        self.assertFalse(alerts_payload[0]["suggested_work_order"]["suggested"])

    def test_ai_enrichment_uses_hybrid_source_when_openai_returns_json(self) -> None:
        manager_token = self._login("gerente.s5", "Senha@123")
        manager_headers = {"Authorization": f"Bearer {manager_token}"}
        self.alerts_service.settings.openai_api_key = "test-key"

        class FakeHttpResponse:
            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                return False

            def read(self):
                return json.dumps(
                    {
                        "output_text": json.dumps(
                            {
                                "risk": "alto",
                                "possible_cause": "Desalinhamento progressivo do conjunto rotativo",
                                "recommendation": "Planejar inspecao mecanica no proximo intervalo operacional.",
                                "suggest_work_order": True,
                            }
                        )
                    }
                ).encode("utf-8")

        with patch("app.services.alerts.request.urlopen", return_value=FakeHttpResponse()):
            update_equipment = self.client.put(
                "/api/equipments/1",
                headers=manager_headers,
                json={
                    "tag": "S5-01",
                    "name": "Compressor Central",
                    "sector": "Utilidades",
                    "criticality": "alta",
                    "status": "ativo",
                    "team_id": 1,
                    "active": True,
                    "alert_measurement_type": "vibracao",
                    "measurement_unit": "mm/s",
                    "alert_threshold_low": 3,
                    "alert_threshold_medium": 4,
                    "alert_threshold_high": 5,
                    "alert_threshold_critical": 6,
                },
            )
            self.assertEqual(update_equipment.status_code, 200, update_equipment.text)

            create_response = self.client.post(
                "/api/measurements",
                headers=manager_headers,
                json={
                    "equipment_id": 1,
                    "measurement_type": "vibracao",
                    "value": 6.8,
                    "unit": "mm/s",
                    "measured_at": "2026-04-24T16:00:00Z",
                },
            )
            self.assertEqual(create_response.status_code, 201, create_response.text)

        alerts_response = self.client.get("/api/alerts?source=hybrid", headers=manager_headers)
        self.assertEqual(alerts_response.status_code, 200, alerts_response.text)
        alerts_payload = alerts_response.json()
        self.assertEqual(len(alerts_payload), 1)
        self.assertEqual(alerts_payload[0]["source"], "hybrid")
        self.assertEqual(
            alerts_payload[0]["possible_cause"],
            "Desalinhamento progressivo do conjunto rotativo",
        )
        self.assertTrue(alerts_payload[0]["suggested_work_order"]["suggested"])


if __name__ == "__main__":
    unittest.main()
