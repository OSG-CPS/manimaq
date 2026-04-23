from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.db.base import Base

if settings.database_url.startswith("sqlite:///"):
    sqlite_path = settings.database_url.replace("sqlite:///", "", 1)
    if sqlite_path:
        from pathlib import Path

        Path(sqlite_path).parent.mkdir(parents=True, exist_ok=True)

connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}

engine = create_engine(settings.database_url, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
