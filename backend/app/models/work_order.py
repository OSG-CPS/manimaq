from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import DateTime, Enum as SqlEnum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


class WorkOrderType(str, Enum):
    CORRETIVA = "corretiva"
    PREVENTIVA = "preventiva"


class WorkOrderPriority(str, Enum):
    BAIXA = "baixa"
    MEDIA = "media"
    ALTA = "alta"
    CRITICA = "critica"


class WorkOrderStatus(str, Enum):
    ABERTA = "aberta"
    EM_EXECUCAO = "em_execucao"
    CONCLUIDA = "concluida"
    CANCELADA = "cancelada"


class WorkOrderOrigin(str, Enum):
    MANUAL = "manual"
    SUGERIDA = "sugerida"


class WorkOrder(Base):
    __tablename__ = "work_orders"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    equipment_id: Mapped[int] = mapped_column(ForeignKey("equipments.id"), nullable=False, index=True)
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), nullable=False, index=True)
    created_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    type: Mapped[WorkOrderType] = mapped_column(SqlEnum(WorkOrderType), nullable=False)
    priority: Mapped[WorkOrderPriority] = mapped_column(
        SqlEnum(WorkOrderPriority), default=WorkOrderPriority.MEDIA, nullable=False
    )
    status: Mapped[WorkOrderStatus] = mapped_column(
        SqlEnum(WorkOrderStatus), default=WorkOrderStatus.ABERTA, nullable=False
    )
    origin: Mapped[WorkOrderOrigin] = mapped_column(SqlEnum(WorkOrderOrigin), default=WorkOrderOrigin.MANUAL, nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    planned_start_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    estimated_duration_hours: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    equipment = relationship("Equipment", back_populates="work_orders")
    team = relationship("Team", back_populates="work_orders")
    created_by = relationship("User", back_populates="created_work_orders")
    status_history = relationship(
        "WorkOrderStatusHistory",
        back_populates="work_order",
        cascade="all, delete-orphan",
        order_by="WorkOrderStatusHistory.created_at.desc()",
    )
