from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Enum as SqlEnum, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base
from app.models.measurement import MeasurementType


class Equipment(Base):
    __tablename__ = "equipments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    tag: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    sector: Mapped[str] = mapped_column(String(100), nullable=False)
    criticality: Mapped[str] = mapped_column(String(50), default="media", nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="ativo", nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    team_id: Mapped[int | None] = mapped_column(ForeignKey("teams.id"), nullable=True)
    alert_measurement_type: Mapped[MeasurementType | None] = mapped_column(SqlEnum(MeasurementType), nullable=True)
    measurement_unit: Mapped[str | None] = mapped_column(String(20), nullable=True)
    alert_threshold_low: Mapped[float | None] = mapped_column(Float, nullable=True)
    alert_threshold_medium: Mapped[float | None] = mapped_column(Float, nullable=True)
    alert_threshold_high: Mapped[float | None] = mapped_column(Float, nullable=True)
    alert_threshold_critical: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    team = relationship("Team", back_populates="equipments")
    occurrences = relationship("Occurrence", back_populates="equipment")
    measurements = relationship("Measurement", back_populates="equipment")
    work_orders = relationship("WorkOrder", back_populates="equipment")
    alerts = relationship("Alert", back_populates="equipment")
