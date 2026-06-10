from __future__ import annotations

from datetime import datetime, time, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.api.deps import current_user
from app.core.roles import AGENT, COORDINATOR, QUALITY_SUPERVISOR, TENANT_ADMIN
from app.db.session import get_db
from app.models import (
    Customer,
    CustomerObligation,
    ManagementActivity,
    Payment,
    PaymentAgreement,
    PaymentPromise,
    Project,
    Role,
    User,
    UserProfile,
    UserProjectAssignment,
)
from app.schemas.teams import (
    AssignmentUpdateResult,
    LeaderAgentAssignmentCreate,
    LeaderSummaryOut,
    ProjectUserAssignmentCreate,
    ProjectUserAssignmentOut,
    ProjectUserAssignmentPatch,
    TeamProjectOut,
    TeamUserOut,
)
from app.services.access_control import (
    get_profile_role_code,
    is_company_admin,
    is_platform_admin,
    require_module,
    require_permission,
    user_has_permission,
)
from app.services.audit_service import record_audit


router = APIRouter()

TEAM_PAGE_SIZE = 20
LEADER_PROFILE_CODES = {"collections_leader", "operational_leader", "sales_leader", "legal_director"}
AGENT_PROFILE_CODES = {"collections_agent", "sales_advisor", "lawyer", "tenant_auditor"}


def _require_any_permission(db: Session, user: User, *permission_codes: str) -> None:
    if any(user_has_permission(db, user, permission) for permission in permission_codes):
        return
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permiso insuficiente.")


def _has_manage_scope(db: Session, user: User) -> bool:
    return is_platform_admin(db, user) or is_company_admin(db, user) or user_has_permission(db, user, "teams.manage") or user_has_permission(db, user, "project_users.manage")


def _active_project_ids(db: Session, user: User) -> list[int]:
    return list(
        db.scalars(
            select(UserProjectAssignment.project_id).where(
                UserProjectAssignment.user_id == user.id,
                UserProjectAssignment.is_active.is_(True),
            )
        )
    )


def _team_user_ids(db: Session, leader: User) -> list[int]:
    ids = list(db.scalars(select(User.id).where(User.tenant_id == leader.tenant_id, User.leader_id == leader.id, User.status == "active")))
    return list(dict.fromkeys(ids))


def _profile_code_for_user(db: Session, user_id: int) -> str | None:
    return db.scalar(
        select(Role.code)
        .join(UserProfile, UserProfile.role_id == Role.id)
        .where(UserProfile.user_id == user_id, Role.is_active.is_(True))
    )


def _role_in_project_for(user: User, profile_code: str | None) -> str:
    if profile_code in {"collections_leader", "operational_leader", "sales_leader", "legal_director"} or user.role in {TENANT_ADMIN, COORDINATOR}:
        return "leader"
    if profile_code == "lawyer":
        return "lawyer"
    if profile_code in {"sales_advisor", "sales_leader"}:
        return "sales"
    if profile_code == "tenant_auditor" or user.role == QUALITY_SUPERVISOR:
        return "quality"
    return "agent"


def _project_for_access(db: Session, project_id: int, user: User, write: bool = False) -> Project:
    project = db.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cartera o proyecto no encontrado.")
    if is_platform_admin(db, user):
        return project
    if project.tenant_id != user.tenant_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Proyecto fuera de tu empresa.")
    if is_company_admin(db, user):
        return project
    if write and not _has_manage_scope(db, user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No puedes administrar asignaciones.")
    if project.id not in _active_project_ids(db, user) and not _has_manage_scope(db, user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Proyecto fuera de tu alcance operativo.")
    return project


def _user_for_tenant(db: Session, user_id: int, tenant_id: int, detail: str = "Usuario no valido para esta empresa.") -> User:
    target = db.get(User, user_id)
    if target is None or target.tenant_id != tenant_id:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=detail)
    return target


def _assignment_to_out(db: Session, assignment: UserProjectAssignment) -> ProjectUserAssignmentOut:
    project = db.get(Project, assignment.project_id)
    assigned_user = db.get(User, assignment.user_id)
    return ProjectUserAssignmentOut(
        id=assignment.id,
        tenant_id=assignment.tenant_id or project.tenant_id if project else assignment.tenant_id,
        project_id=assignment.project_id,
        project_name=project.name if project else None,
        user_id=assignment.user_id,
        user_name=assigned_user.name if assigned_user else None,
        user_email=assigned_user.email if assigned_user else None,
        user_role=assigned_user.role if assigned_user else None,
        profile_role=_profile_code_for_user(db, assigned_user.id) if assigned_user else None,
        role_in_project=assignment.role_in_project,
        is_active=assignment.is_active,
        created_at=assignment.created_at,
        updated_at=assignment.updated_at,
    )


def _user_to_out(db: Session, item: User) -> TeamUserOut:
    assignments = list(
        db.scalars(
            select(UserProjectAssignment)
            .where(UserProjectAssignment.user_id == item.id, UserProjectAssignment.is_active.is_(True))
            .order_by(UserProjectAssignment.id)
        )
    )
    projects = [db.get(Project, assignment.project_id) for assignment in assignments]
    leader = db.get(User, item.leader_id) if item.leader_id else None
    return TeamUserOut(
        id=item.id,
        tenant_id=item.tenant_id,
        name=item.name,
        email=item.email,
        role=item.role,
        profile_role=_profile_code_for_user(db, item.id),
        title=item.title,
        status=item.status,
        leader_id=item.leader_id,
        leader_name=leader.name if leader else None,
        project_ids=[project.id for project in projects if project],
        project_names=[project.name for project in projects if project],
    )


def _project_to_out(db: Session, project: Project) -> TeamProjectOut:
    active_assignments = select(UserProjectAssignment).where(UserProjectAssignment.project_id == project.id, UserProjectAssignment.is_active.is_(True))
    leader_count = db.scalar(select(func.count(UserProjectAssignment.id)).where(UserProjectAssignment.project_id == project.id, UserProjectAssignment.is_active.is_(True), UserProjectAssignment.role_in_project == "leader")) or 0
    agent_count = db.scalar(select(func.count(UserProjectAssignment.id)).where(UserProjectAssignment.project_id == project.id, UserProjectAssignment.is_active.is_(True), UserProjectAssignment.role_in_project == "agent")) or 0
    user_count = db.scalar(select(func.count()).select_from(active_assignments.subquery())) or 0
    customer_count = db.scalar(select(func.count(Customer.id)).where(Customer.project_id == project.id, Customer.tenant_id == project.tenant_id)) or 0
    obligation_count = db.scalar(select(func.count(CustomerObligation.id)).where(CustomerObligation.project_id == project.id, CustomerObligation.tenant_id == project.tenant_id)) or 0
    balance_total = db.scalar(select(func.coalesce(func.sum(CustomerObligation.current_balance), 0)).where(CustomerObligation.project_id == project.id, CustomerObligation.tenant_id == project.tenant_id)) or 0
    return TeamProjectOut(
        id=project.id,
        tenant_id=project.tenant_id,
        name=project.name,
        code=project.code,
        status=project.status,
        leader_count=leader_count,
        agent_count=agent_count,
        user_count=user_count,
        customer_count=customer_count,
        obligation_count=obligation_count,
        balance_total=int(balance_total),
    )


def _leader_for_access(db: Session, leader_id: int, user: User, write: bool = False) -> User:
    leader = db.get(User, leader_id)
    if leader is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lider no encontrado.")
    if not is_platform_admin(db, user) and leader.tenant_id != user.tenant_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Lider fuera de tu empresa.")
    if not write and (is_platform_admin(db, user) or is_company_admin(db, user) or leader.id == user.id or _has_manage_scope(db, user)):
        return leader
    if write and _has_manage_scope(db, user):
        return leader
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes alcance sobre este equipo.")


def _leader_summary(db: Session, leader: User) -> LeaderSummaryOut:
    team_ids = _team_user_ids(db, leader)
    visible_ids = team_ids or [leader.id]
    today_start = datetime.combine(datetime.now(timezone.utc).date(), time.min, tzinfo=timezone.utc)
    month_start = datetime(datetime.now(timezone.utc).year, datetime.now(timezone.utc).month, 1, tzinfo=timezone.utc)
    customer_scope = select(Customer.id).where(Customer.tenant_id == leader.tenant_id, Customer.assigned_user_id.in_(visible_ids))
    obligations_query = select(CustomerObligation).where(
        CustomerObligation.tenant_id == leader.tenant_id,
        or_(
            CustomerObligation.assigned_user_id.in_(visible_ids),
            CustomerObligation.assigned_leader_id == leader.id,
            CustomerObligation.customer_id.in_(customer_scope),
        ),
    )
    obligations_subquery = obligations_query.subquery()
    customers = db.scalar(select(func.count(Customer.id)).where(Customer.id.in_(customer_scope))) or 0
    obligations = db.scalar(select(func.count()).select_from(obligations_subquery)) or 0
    balance_total = db.scalar(select(func.coalesce(func.sum(obligations_subquery.c.current_balance), 0))) or 0
    activities_today = db.scalar(
        select(func.count(ManagementActivity.id)).where(
            ManagementActivity.tenant_id == leader.tenant_id,
            ManagementActivity.user_id.in_(visible_ids),
            ManagementActivity.created_at >= today_start,
        )
    ) or 0
    active_promises = db.scalar(select(func.count(PaymentPromise.id)).where(PaymentPromise.tenant_id == leader.tenant_id, PaymentPromise.user_id.in_(visible_ids), PaymentPromise.status == "Vigente")) or 0
    overdue_promises = db.scalar(select(func.count(PaymentPromise.id)).where(PaymentPromise.tenant_id == leader.tenant_id, PaymentPromise.user_id.in_(visible_ids), PaymentPromise.status == "Vencida")) or 0
    payments_month = db.scalar(select(func.coalesce(func.sum(Payment.amount), 0)).where(Payment.tenant_id == leader.tenant_id, Payment.user_id.in_(visible_ids), Payment.paid_at >= month_start)) or 0
    active_agreements = db.scalar(select(func.count(PaymentAgreement.id)).where(PaymentAgreement.tenant_id == leader.tenant_id, PaymentAgreement.user_id.in_(visible_ids), PaymentAgreement.status.in_(["active", "vigente", "al dia"]))) or 0
    stale_customers = db.scalar(
        select(func.count(Customer.id)).where(
            Customer.tenant_id == leader.tenant_id,
            Customer.assigned_user_id.in_(visible_ids),
            Customer.last_contact_at.is_(None),
        )
    ) or 0
    ranking = []
    for agent in db.scalars(select(User).where(User.id.in_(visible_ids)).order_by(User.name)).all():
        ranking.append(
            {
                "user_id": agent.id,
                "name": agent.name,
                "customers": db.scalar(select(func.count(Customer.id)).where(Customer.tenant_id == leader.tenant_id, Customer.assigned_user_id == agent.id)) or 0,
                "activities_today": db.scalar(select(func.count(ManagementActivity.id)).where(ManagementActivity.tenant_id == leader.tenant_id, ManagementActivity.user_id == agent.id, ManagementActivity.created_at >= today_start)) or 0,
                "payments_month": int(db.scalar(select(func.coalesce(func.sum(Payment.amount), 0)).where(Payment.tenant_id == leader.tenant_id, Payment.user_id == agent.id, Payment.paid_at >= month_start)) or 0),
            }
        )
    return LeaderSummaryOut(
        leader_id=leader.id,
        leader_name=leader.name,
        total_agents=len(team_ids),
        customers=customers,
        obligations=obligations,
        balance_total=int(balance_total),
        activities_today=activities_today,
        active_promises=active_promises,
        overdue_promises=overdue_promises,
        payments_month=int(payments_month),
        active_agreements=active_agreements,
        stale_customers=stale_customers,
        ranking=ranking,
    )


@router.get("/projects", response_model=list[TeamProjectOut])
def list_team_projects(
    tenant_id: int | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=TEAM_PAGE_SIZE, ge=1, le=TEAM_PAGE_SIZE),
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
) -> list[TeamProjectOut]:
    require_module(db, user, "administration")
    _require_any_permission(db, user, "teams.view", "project_users.view")
    query = select(Project).order_by(Project.name)
    if is_platform_admin(db, user):
        if tenant_id:
            query = query.where(Project.tenant_id == tenant_id)
    else:
        query = query.where(Project.tenant_id == user.tenant_id)
        if not is_company_admin(db, user) and not _has_manage_scope(db, user):
            project_ids = _active_project_ids(db, user)
            query = query.where(Project.id.in_(project_ids or [-1]))
    items = list(db.scalars(query.offset((page - 1) * page_size).limit(page_size)))
    return [_project_to_out(db, item) for item in items]


@router.get("/projects/{project_id}/users", response_model=list[ProjectUserAssignmentOut])
def list_project_users(project_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)) -> list[ProjectUserAssignmentOut]:
    require_module(db, user, "administration")
    _require_any_permission(db, user, "teams.view", "project_users.view")
    _project_for_access(db, project_id, user)
    assignments = list(db.scalars(select(UserProjectAssignment).where(UserProjectAssignment.project_id == project_id).order_by(UserProjectAssignment.is_active.desc(), UserProjectAssignment.role_in_project, UserProjectAssignment.id).limit(TEAM_PAGE_SIZE)))
    return [_assignment_to_out(db, item) for item in assignments]


@router.post("/projects/{project_id}/users", response_model=ProjectUserAssignmentOut, status_code=status.HTTP_201_CREATED)
def assign_project_user(project_id: int, payload: ProjectUserAssignmentCreate, request: Request, db: Session = Depends(get_db), user: User = Depends(current_user)) -> ProjectUserAssignmentOut:
    require_module(db, user, "administration")
    require_permission(db, user, "project_users.manage")
    project = _project_for_access(db, project_id, user, write=True)
    target = _user_for_tenant(db, payload.user_id, project.tenant_id)
    assignment = db.scalar(select(UserProjectAssignment).where(UserProjectAssignment.user_id == target.id, UserProjectAssignment.project_id == project.id))
    if assignment is None:
        assignment = UserProjectAssignment(tenant_id=project.tenant_id, user_id=target.id, project_id=project.id)
        db.add(assignment)
        db.flush()
    before = {"role_in_project": assignment.role_in_project, "is_active": assignment.is_active}
    assignment.tenant_id = project.tenant_id
    assignment.role_in_project = payload.role_in_project
    assignment.is_active = payload.is_active
    record_audit(db, user, "project_user_assignment", "upsert", assignment.id, project.tenant_id, module="administration", before=before, after={"user_id": target.id, "project_id": project.id, "role_in_project": assignment.role_in_project, "is_active": assignment.is_active}, request=request)
    db.commit()
    db.refresh(assignment)
    return _assignment_to_out(db, assignment)


@router.patch("/project-users/{assignment_id}", response_model=ProjectUserAssignmentOut)
def update_project_user(assignment_id: int, payload: ProjectUserAssignmentPatch, request: Request, db: Session = Depends(get_db), user: User = Depends(current_user)) -> ProjectUserAssignmentOut:
    require_module(db, user, "administration")
    require_permission(db, user, "project_users.manage")
    assignment = db.get(UserProjectAssignment, assignment_id)
    if assignment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asignacion no encontrada.")
    project = _project_for_access(db, assignment.project_id, user, write=True)
    before = {"role_in_project": assignment.role_in_project, "is_active": assignment.is_active}
    updates = payload.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(assignment, key, value)
    assignment.tenant_id = assignment.tenant_id or project.tenant_id
    record_audit(db, user, "project_user_assignment", "update", assignment.id, project.tenant_id, module="administration", before=before, after=updates, request=request)
    db.commit()
    db.refresh(assignment)
    return _assignment_to_out(db, assignment)


@router.get("/leaders", response_model=list[TeamUserOut])
def list_leaders(db: Session = Depends(get_db), user: User = Depends(current_user)) -> list[TeamUserOut]:
    require_module(db, user, "administration")
    _require_any_permission(db, user, "teams.view", "project_users.view")
    query = select(User).where(User.status == "active").order_by(User.name)
    if not is_platform_admin(db, user):
        query = query.where(User.tenant_id == user.tenant_id)
        if not is_company_admin(db, user) and not _has_manage_scope(db, user):
            query = query.where(User.id == user.id)
    users = list(db.scalars(query))
    leaders = []
    for item in users:
        profile = _profile_code_for_user(db, item.id)
        if item.role in {TENANT_ADMIN, COORDINATOR} or profile in LEADER_PROFILE_CODES:
            leaders.append(item)
    return [_user_to_out(db, item) for item in leaders[:TEAM_PAGE_SIZE]]


@router.get("/agents", response_model=list[TeamUserOut])
def list_agents(db: Session = Depends(get_db), user: User = Depends(current_user)) -> list[TeamUserOut]:
    require_module(db, user, "administration")
    _require_any_permission(db, user, "teams.view", "project_users.view")
    query = select(User).where(User.status == "active").order_by(User.name)
    if not is_platform_admin(db, user):
        query = query.where(User.tenant_id == user.tenant_id)
        if not is_company_admin(db, user) and not _has_manage_scope(db, user):
            query = query.where(or_(User.leader_id == user.id, User.id == user.id))
    users = list(db.scalars(query))
    agents = []
    for item in users:
        profile = _profile_code_for_user(db, item.id)
        if item.role in {AGENT, QUALITY_SUPERVISOR} or profile in AGENT_PROFILE_CODES:
            agents.append(item)
    return [_user_to_out(db, item) for item in agents[:TEAM_PAGE_SIZE]]


@router.get("/leaders/{leader_id}/agents", response_model=list[TeamUserOut])
def list_leader_agents(
    leader_id: int,
    project_id: int | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
) -> list[TeamUserOut]:
    require_module(db, user, "administration")
    _require_any_permission(db, user, "teams.view", "project_users.view")
    leader = _leader_for_access(db, leader_id, user)
    query = select(User).where(User.tenant_id == leader.tenant_id, User.leader_id == leader.id, User.status == "active").order_by(User.name)
    if project_id:
        _project_for_access(db, project_id, user)
        query = query.where(User.id.in_(select(UserProjectAssignment.user_id).where(UserProjectAssignment.project_id == project_id, UserProjectAssignment.is_active.is_(True))))
    return [_user_to_out(db, item) for item in db.scalars(query).all()[:TEAM_PAGE_SIZE]]


@router.post("/leaders/{leader_id}/agents", response_model=AssignmentUpdateResult)
def assign_leader_agent(leader_id: int, payload: LeaderAgentAssignmentCreate, request: Request, db: Session = Depends(get_db), user: User = Depends(current_user)) -> AssignmentUpdateResult:
    require_module(db, user, "administration")
    require_permission(db, user, "teams.manage")
    leader = _leader_for_access(db, leader_id, user, write=True)
    agent = _user_for_tenant(db, payload.agent_user_id, leader.tenant_id, "El agente debe pertenecer a la misma empresa del lider.")
    if agent.id == leader.id:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Un lider no puede asignarse como su propio agente.")
    before = {"leader_id": agent.leader_id}
    agent.leader_id = leader.id
    if payload.project_id:
        project = _project_for_access(db, payload.project_id, user, write=True)
        for target, role in ((leader, "leader"), (agent, _role_in_project_for(agent, _profile_code_for_user(db, agent.id)))):
            assignment = db.scalar(select(UserProjectAssignment).where(UserProjectAssignment.user_id == target.id, UserProjectAssignment.project_id == project.id))
            if assignment is None:
                assignment = UserProjectAssignment(tenant_id=project.tenant_id, user_id=target.id, project_id=project.id)
                db.add(assignment)
            assignment.tenant_id = project.tenant_id
            assignment.role_in_project = role
            assignment.is_active = True
    record_audit(db, user, "leader_agent_assignment", "upsert", agent.id, leader.tenant_id, module="administration", before=before, after={"leader_id": leader.id, "agent_id": agent.id, "project_id": payload.project_id}, request=request)
    db.commit()
    return AssignmentUpdateResult(detail="Agente asociado al lider correctamente.")


@router.get("/leaders/{leader_id}/summary", response_model=LeaderSummaryOut)
def leader_summary(leader_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)) -> LeaderSummaryOut:
    require_module(db, user, "administration")
    _require_any_permission(db, user, "teams.view", "project_users.view")
    leader = _leader_for_access(db, leader_id, user)
    return _leader_summary(db, leader)


@router.get("/dashboard", response_model=LeaderSummaryOut)
def my_team_dashboard(db: Session = Depends(get_db), user: User = Depends(current_user)) -> LeaderSummaryOut:
    require_module(db, user, "administration")
    _require_any_permission(db, user, "teams.view", "project_users.view")
    if is_company_admin(db, user):
        leader = db.scalar(select(User).where(User.tenant_id == user.tenant_id, User.role == COORDINATOR).order_by(User.id))
        if leader is None:
            leader = user
    else:
        leader = user
    return _leader_summary(db, leader)
