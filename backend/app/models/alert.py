from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import Boolean, DateTime, Enum as SqlEnum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base
from app.models.work_order import WorkOrderPriority, WorkOrderType


class AlertSeverity(str, Enum):
    BAIXA = "baixa"
    MEDIA = "media"
    ALTA = "alta"
    CRITICA = "critica"


class AlertSource(str, Enum):
    RULE = "rule"
    AI = "ai"
    HYBRID = "hybrid"


class AlertOriginType(str, Enum):
    OCCURRENCE = "occurrence"
    MEASUREMENT = "measurement"
    SYSTEM = "system"


class AlertStatus(str, Enum):
    ABERTO = "aberto"
    REVISADO = "revisado"


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    equipment_id: Mapped[int] = mapped_column(ForeignKey("equipments.id"), nullable=False, index=True)
    origin_type: Mapped[AlertOriginType] = mapped_column(SqlEnum(AlertOriginType), nullable=False, index=True)
    origin_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    source: Mapped[AlertSource] = mapped_column(SqlEnum(AlertSource), nullable=False, index=True)
    severity: Mapped[AlertSeverity] = mapped_column(SqlEnum(AlertSeverity), nullable=False, index=True)
    status: Mapped[AlertStatus] = mapped_column(SqlEnum(AlertStatus), default=AlertStatus.ABERTO, nullable=False)
    title: Mapped[str] = mapped_column(String(160), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    recommendation: Mapped[str | None] = mapped_column(Text, nullable=True)
    possible_cause: Mapped[str | None] = mapped_column(Text, nullable=True)
    suggested_work_order: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    suggested_work_order_type: Mapped[WorkOrderType | None] = mapped_column(SqlEnum(WorkOrderType), nullable=True)
    suggested_work_order_priority: Mapped[WorkOrderPriority | None] = mapped_column(
        SqlEnum(WorkOrderPriority), nullable=True
    )
    event_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    equipment = relationship("Equipment", back_populates="alerts")

