from sqlalchemy import select

from app.core.security import hash_password
from app.db.session import SessionLocal, init_db
from app.models.equipment import Equipment
from app.models.team import Team
from app.models.user import User, UserRole

DEFAULT_PASSWORD = "Manimaq@123"

TEAM_SEEDS = [
    {"name": "Administracao", "sector": "Administracao", "description": "Equipe administrativa"},
    {"name": "Producao", "sector": "Producao", "description": "Equipe operacional da producao"},
    {"name": "Expedicao", "sector": "Expedicao", "description": "Equipe de expedicao"},
    {"name": "Manutencao", "sector": "Manutencao", "description": "Equipe de manutencao"},
    {"name": "Utilidades", "sector": "Utilidades", "description": "Equipe de utilidades"},
]

USER_SEEDS = [
    {
        "name": "Otavio",
        "username": "otavio",
        "email": "otavio@manimaq.local",
        "role": UserRole.ADMIN,
        "team_name": "Administracao",
    },
    {
        "name": "Taina",
        "username": "taina",
        "email": "taina@manimaq.local",
        "role": UserRole.GERENTE,
        "team_name": "Manutencao",
    },
    {
        "name": "Michael",
        "username": "michael",
        "email": "michael@manimaq.local",
        "role": UserRole.OPERADOR,
        "team_name": "Producao",
    },
    {
        "name": "Leonardo",
        "username": "leonardo",
        "email": "leonardo@manimaq.local",
        "role": UserRole.OPERADOR,
        "team_name": "Manutencao",
    },
    {
        "name": "Murillo",
        "username": "murillo",
        "email": "murillo@manimaq.local",
        "role": UserRole.OPERADOR,
        "team_name": "Utilidades",
    },
]

EQUIPMENT_SEEDS = [
    {"tag": "PC-01", "name": "Computador administrativo", "sector": "Administracao", "team_name": "Administracao"},
    {"tag": "LAMP-01", "name": "Lampada corredor", "sector": "Administracao", "team_name": "Administracao"},
    {"tag": "TOM-01", "name": "Tomada sala reuniao", "sector": "Administracao", "team_name": "Administracao"},
    {"tag": "MAQ-01", "name": "Maquina principal", "sector": "Producao", "team_name": "Producao"},
    {"tag": "EMP-01", "name": "Esteira expedicao", "sector": "Expedicao", "team_name": "Expedicao"},
    {"tag": "PLT-01", "name": "Plataforma carga", "sector": "Expedicao", "team_name": "Expedicao"},
    {"tag": "COMP-01", "name": "Compressor principal", "sector": "Utilidades", "team_name": "Utilidades"},
    {"tag": "GER-01", "name": "Gerador reserva", "sector": "Utilidades", "team_name": "Utilidades"},
    {"tag": "AR-01", "name": "Ar-condicionado sala tecnica", "sector": "Utilidades", "team_name": "Utilidades"},
]


def run() -> None:
    init_db()
    db = SessionLocal()
    try:
        teams_by_name: dict[str, Team] = {}

        for team_payload in TEAM_SEEDS:
            team = db.execute(select(Team).where(Team.name == team_payload["name"])).scalar_one_or_none()
            if team is None:
                team = Team(**team_payload)
                db.add(team)
                db.flush()
            teams_by_name[team.name] = team

        for user_payload in USER_SEEDS:
            team = teams_by_name[user_payload["team_name"]]
            user = db.execute(select(User).where(User.email == user_payload["email"])).scalar_one_or_none()
            if user is None:
                user = User(
                    name=user_payload["name"],
                    username=user_payload["username"],
                    email=user_payload["email"],
                    role=user_payload["role"],
                    team_id=team.id,
                    password_hash=hash_password(DEFAULT_PASSWORD),
                    active=True,
                )
                db.add(user)

        for equipment_payload in EQUIPMENT_SEEDS:
            team = teams_by_name[equipment_payload["team_name"]]
            equipment = db.execute(
                select(Equipment).where(Equipment.tag == equipment_payload["tag"])
            ).scalar_one_or_none()
            if equipment is None:
                db.add(
                    Equipment(
                        tag=equipment_payload["tag"],
                        name=equipment_payload["name"],
                        sector=equipment_payload["sector"],
                        team_id=team.id,
                    )
                )

        db.commit()
        print(f"Seed concluido. Senha padrao dos usuarios: {DEFAULT_PASSWORD}")
    finally:
        db.close()


if __name__ == "__main__":
    run()
