from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum as SqlEnum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base
from app.models.work_order import WorkOrderStatus


class WorkOrderStatusHistory(Base):
    __tablename__ = "work_order_status_history"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    work_order_id: Mapped[int] = mapped_column(ForeignKey("work_orders.id"), nullable=False, index=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    previous_status: Mapped[WorkOrderStatus | None] = mapped_column(SqlEnum(WorkOrderStatus), nullable=True)
    new_status: Mapped[WorkOrderStatus] = mapped_column(SqlEnum(WorkOrderStatus), nullable=False)
    note: Mapped[str | None] = mapped_column(String(500), nullable=True)
    transition_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    work_order = relationship("WorkOrder", back_populates="status_history")
    author = relationship("User", back_populates="work_order_status_updates")
