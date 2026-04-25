from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import (
    alerts,
    auth,
    dashboard,
    equipment_history,
    equipments,
    measurements,
    occurrences,
    protected,
    teams,
    users,
    work_orders,
)
from app.core.config import settings
from app.db.session import init_db

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_origin_regex=settings.cors_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(auth.router, prefix=settings.api_prefix)
app.include_router(protected.router, prefix=settings.api_prefix)
app.include_router(teams.router, prefix=settings.api_prefix)
app.include_router(equipments.router, prefix=settings.api_prefix)
app.include_router(users.router, prefix=settings.api_prefix)
app.include_router(occurrences.router, prefix=settings.api_prefix)
app.include_router(measurements.router, prefix=settings.api_prefix)
app.include_router(equipment_history.router, prefix=settings.api_prefix)
app.include_router(work_orders.router, prefix=settings.api_prefix)
app.include_router(alerts.router, prefix=settings.api_prefix)
app.include_router(dashboard.router, prefix=settings.api_prefix)
