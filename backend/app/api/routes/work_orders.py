from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_current_user, get_db, require_admin_or_manager
from app.models.equipment import Equipment
from app.models.team import Team
from app.models.user import User, UserRole
from app.models.work_order import WorkOrder, WorkOrderStatus
from app.models.work_order_status_history import WorkOrderStatusHistory
from app.schemas.common import EquipmentSummary, TeamSummary, UserSummary, ensure_utc_datetime
from app.schemas.work_orders import WorkOrderCreate, WorkOrderResponse, WorkOrderStatusHistoryResponse, WorkOrderStatusUpdate

router = APIRouter(prefix="/work-orders", tags=["work-orders"])

ALLOWED_STATUS_TRANSITIONS: dict[WorkOrderStatus, set[WorkOrderStatus]] = {
    WorkOrderStatus.ABERTA: {WorkOrderStatus.EM_EXECUCAO, WorkOrderStatus.CANCELADA},
    WorkOrderStatus.EM_EXECUCAO: {WorkOrderStatus.CONCLUIDA, WorkOrderStatus.CANCELADA},
    WorkOrderStatus.CONCLUIDA: set(),
    WorkOrderStatus.CANCELADA: set(),
}

OPERATOR_ALLOWED_STATUSES = {WorkOrderStatus.EM_EXECUCAO, WorkOrderStatus.CONCLUIDA}


def _get_equipment_or_404(equipment_id: int, db: Session) -> Equipment:
    equipment = db.get(Equipment, equipment_id)
    if equipment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Equipamento nao encontrado")
    return equipment


def _get_active_team_or_400(team_id: int, db: Session) -> Team:
    team = db.get(Team, team_id)
    if team is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Equipe nao encontrada")
    if not team.active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Equipe inativa nao pode receber OS")
    return team


def _work_order_query(db: Session):
    return db.query(WorkOrder).options(
        joinedload(WorkOrder.equipment),
        joinedload(WorkOrder.team),
        joinedload(WorkOrder.created_by),
        joinedload(WorkOrder.status_history).joinedload(WorkOrderStatusHistory.author),
    )


def _serialize_history(entry: WorkOrderStatusHistory) -> WorkOrderStatusHistoryResponse:
    return WorkOrderStatusHistoryResponse(
        id=entry.id,
        previous_status=entry.previous_status,
        new_status=entry.new_status,
        note=entry.note,
        transition_at=ensure_utc_datetime(entry.transition_at),
        created_at=ensure_utc_datetime(entry.created_at),
        author=UserSummary.model_validate(entry.author),
    )


def _serialize(work_order: WorkOrder) -> WorkOrderResponse:
    return WorkOrderResponse(
        id=work_order.id,
        equipment_id=work_order.equipment_id,
        team_id=work_order.team_id,
        type=work_order.type,
        priority=work_order.priority,
        status=work_order.status,
        description=work_order.description,
        origin=work_order.origin,
        planned_start_at=ensure_utc_datetime(work_order.planned_start_at) if work_order.planned_start_at else None,
        estimated_duration_hours=work_order.estimated_duration_hours,
        created_at=ensure_utc_datetime(work_order.created_at),
        updated_at=ensure_utc_datetime(work_order.updated_at),
        equipment=EquipmentSummary.model_validate(work_order.equipment),
        team=TeamSummary.model_validate(work_order.team),
        created_by=UserSummary.model_validate(work_order.created_by),
        status_history=[_serialize_history(entry) for entry in work_order.status_history],
    )


def _get_work_order_or_404(work_order_id: int, db: Session) -> WorkOrder:
    work_order = _work_order_query(db).filter(WorkOrder.id == work_order_id).first()
    if work_order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="OS nao encontrada")
    return work_order


def _ensure_can_view(work_order: WorkOrder, current_user: User) -> None:
    if current_user.role in {UserRole.ADMIN, UserRole.GERENTE}:
        return
    if current_user.team_id is None or current_user.team_id != work_order.team_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sem permissao para acessar esta OS")


def _ensure_can_update_status(work_order: WorkOrder, next_status: WorkOrderStatus, current_user: User) -> None:
    _ensure_can_view(work_order, current_user)

    if next_status not in ALLOWED_STATUS_TRANSITIONS[work_order.status]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Transicao de status invalida")

    if current_user.role in {UserRole.ADMIN, UserRole.GERENTE}:
        return

    if next_status not in OPERATOR_ALLOWED_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operador pode apenas iniciar execucao ou concluir OS da propria equipe",
        )


def _append_history(
    work_order: WorkOrder,
    previous_status: WorkOrderStatus | None,
    new_status: WorkOrderStatus,
    note: str | None,
    author_id: int,
    transition_at: datetime,
) -> None:
    history_entry = WorkOrderStatusHistory(
        work_order=work_order,
        previous_status=previous_status,
        new_status=new_status,
        note=note.strip() if note else None,
        author_id=author_id,
        transition_at=transition_at,
    )
    work_order.status_history.append(history_entry)


@router.get("", response_model=list[WorkOrderResponse])
def list_work_orders(
    status_filter: WorkOrderStatus | None = None,
    equipment_id: int | None = None,
    team_id: int | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[WorkOrderResponse]:
    query = _work_order_query(db)

    if status_filter is not None:
        query = query.filter(WorkOrder.status == status_filter)
    if equipment_id is not None:
        query = query.filter(WorkOrder.equipment_id == equipment_id)
    if team_id is not None:
        query = query.filter(WorkOrder.team_id == team_id)

    if current_user.role == UserRole.OPERADOR:
        if current_user.team_id is None:
            return []
        query = query.filter(WorkOrder.team_id == current_user.team_id)

    work_orders = query.order_by(WorkOrder.created_at.desc()).all()
    return [_serialize(work_order) for work_order in work_orders]


@router.get("/{work_order_id}", response_model=WorkOrderResponse)
def get_work_order(
    work_order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> WorkOrderResponse:
    work_order = _get_work_order_or_404(work_order_id, db)
    _ensure_can_view(work_order, current_user)
    return _serialize(work_order)


@router.post("", response_model=WorkOrderResponse, status_code=status.HTTP_201_CREATED)
def create_work_order(
    payload: WorkOrderCreate,
    current_user: User = Depends(require_admin_or_manager),
    db: Session = Depends(get_db),
) -> WorkOrderResponse:
    _get_equipment_or_404(payload.equipment_id, db)
    _get_active_team_or_400(payload.team_id, db)

    work_order = WorkOrder(
        equipment_id=payload.equipment_id,
        team_id=payload.team_id,
        created_by_id=current_user.id,
        type=payload.type,
        priority=payload.priority,
        status=payload.status,
        description=payload.description.strip(),
        origin=payload.origin,
        planned_start_at=payload.planned_start_at,
        estimated_duration_hours=payload.estimated_duration_hours,
    )
    db.add(work_order)
    db.flush()
    _append_history(work_order, None, work_order.status, payload.initial_note, current_user.id, work_order.created_at)
    db.commit()
    return get_work_order(work_order.id, current_user, db)


@router.post("/{work_order_id}/status", response_model=WorkOrderResponse)
def update_work_order_status(
    work_order_id: int,
    payload: WorkOrderStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> WorkOrderResponse:
    work_order = _get_work_order_or_404(work_order_id, db)
    _ensure_can_update_status(work_order, payload.status, current_user)

    previous_status = work_order.status
    work_order.status = payload.status
    _append_history(
        work_order,
        previous_status,
        payload.status,
        payload.note,
        current_user.id,
        payload.transition_at or datetime.now(timezone.utc),
    )
    db.commit()
    return get_work_order(work_order.id, current_user, db)
