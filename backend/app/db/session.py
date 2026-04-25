from sqlalchemy import create_engine
from sqlalchemy import inspect, text
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
    _ensure_sprint3_columns()
    _ensure_sprint4_columns()


def _ensure_sprint3_columns() -> None:
    inspector = inspect(engine)

    expected_columns = {
        "occurrences": ("occurred_at",),
        "measurements": ("measured_at",),
    }

    with engine.begin() as connection:
        for table_name, columns in expected_columns.items():
            if table_name not in inspector.get_table_names():
                continue

            existing_columns = {column["name"] for column in inspector.get_columns(table_name)}

            if "occurred_at" in columns and "occurred_at" not in existing_columns:
                connection.execute(text("ALTER TABLE occurrences ADD COLUMN occurred_at DATETIME"))
                connection.execute(text("UPDATE occurrences SET occurred_at = created_at WHERE occurred_at IS NULL"))

            if "measured_at" in columns and "measured_at" not in existing_columns:
                connection.execute(text("ALTER TABLE measurements ADD COLUMN measured_at DATETIME"))
                connection.execute(text("UPDATE measurements SET measured_at = created_at WHERE measured_at IS NULL"))


def _ensure_sprint4_columns() -> None:
    inspector = inspect(engine)

    with engine.begin() as connection:
        table_name = "work_order_status_history"
        if table_name not in inspector.get_table_names():
            return

        existing_columns = {column["name"] for column in inspector.get_columns(table_name)}
        if "transition_at" not in existing_columns:
            connection.execute(text("ALTER TABLE work_order_status_history ADD COLUMN transition_at DATETIME"))
            connection.execute(
                text(
                    "UPDATE work_order_status_history SET transition_at = created_at WHERE transition_at IS NULL"
                )
            )
