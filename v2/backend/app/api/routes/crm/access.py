from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.roles import AGENT, COORDINATOR, PLATFORM_ADMIN, QUALITY_SUPERVISOR, TENANT_ADMIN
from app.models import Customer, CustomerObligation, LegalCase, ManagementActivity, Project, Tenant, TypificationNode, User, UserProjectAssignment
from app.schemas.crm import ActivityOut, CustomerOut
from app.services.access_control import get_profile_role_code


MANAGE_ROLES = {PLATFORM_ADMIN, TENANT_ADMIN, COORDINATOR}
READ_ROLES = {PLATFORM_ADMIN, TENANT_ADMIN, COORDINATOR, QUALITY_SUPERVISOR, AGENT}


def ensure_read_access(user: User) -> None:
    if user.role not in READ_ROLES:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Rol sin acceso al CRM.")


def ensure_manage_access(user: User) -> None:
    if user.role not in MANAGE_ROLES:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Rol sin permiso para modificar.")


def is_platform(user: User) -> bool:
    return user.role == PLATFORM_ADMIN


def business_tenant_query(db: Session):
    return select(Tenant).where(Tenant.slug != settings.platform_tenant_slug).order_by(Tenant.name)


def project_for_access(db: Session, project_id: int, user: User) -> Project:
    project = db.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Proyecto no encontrado.")
    if not is_platform(user) and project.tenant_id != user.tenant_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Proyecto fuera de tu empresa.")
    return project


def customer_for_access(db: Session, customer_id: int, user: User, write: bool = False) -> Customer:
    customer = db.get(Customer, customer_id)
    if customer is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente no encontrado.")
    if not is_platform(user) and customer.tenant_id != user.tenant_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cliente fuera de tu empresa.")
    profile_role = get_profile_role_code(db, user)
    if user.role == AGENT and customer.assigned_user_id != user.id:
        if not write and profile_role in {"sales_advisor", "sales_leader", "legal_director"}:
            return customer
        if not write and profile_role == "lawyer":
            has_case = db.scalar(select(LegalCase.id).where(LegalCase.customer_id == customer.id, LegalCase.assigned_lawyer_id == user.id))
            if has_case:
                return customer
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cliente no asignado al gestor.")
    if write and user.role == QUALITY_SUPERVISOR:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Calidad tiene acceso de lectura.")
    return customer


def validate_assigned_user(db: Session, tenant_id: int, assigned_user_id: int | None) -> None:
    if assigned_user_id is None:
        return
    assigned = db.get(User, assigned_user_id)
    if assigned is None or assigned.tenant_id != tenant_id:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="El gestor asignado no pertenece a la empresa.")


def _team_user_ids(db: Session, user: User) -> list[int]:
    ids = [user.id]
    ids.extend(db.scalars(select(User.id).where(User.tenant_id == user.tenant_id, User.leader_id == user.id)))
    return list(dict.fromkeys(ids))


def _active_project_ids(db: Session, user: User) -> list[int]:
    return list(
        db.scalars(
            select(UserProjectAssignment.project_id).where(
                UserProjectAssignment.user_id == user.id,
                UserProjectAssignment.is_active.is_(True),
            )
        )
    )


def customer_query(db: Session, user: User):
    query = select(Customer)
    if not is_platform(user):
        query = query.where(Customer.tenant_id == user.tenant_id)
    if user.role == TENANT_ADMIN:
        return query
    profile_role = get_profile_role_code(db, user)
    if user.role == COORDINATOR or profile_role == "collections_leader":
        team_ids = _team_user_ids(db, user)
        project_ids = _active_project_ids(db, user)
        conditions = [Customer.assigned_user_id.in_(team_ids)]
        if project_ids:
            conditions.append(Customer.project_id.in_(project_ids))
        return query.where(or_(*conditions))
    if user.role == AGENT:
        if profile_role in {"sales_advisor", "sales_leader", "legal_director"}:
            return query
        if profile_role == "lawyer":
            legal_customer_ids = select(LegalCase.customer_id).where(LegalCase.tenant_id == user.tenant_id, LegalCase.assigned_lawyer_id == user.id)
            return query.where(Customer.id.in_(legal_customer_ids))
        query = query.where(Customer.assigned_user_id == user.id)
    return query


def customer_to_out(db: Session, customer: Customer) -> CustomerOut:
    tenant = db.get(Tenant, customer.tenant_id) if customer.tenant_id else None
    project = db.get(Project, customer.project_id) if customer.project_id else None
    assigned = db.get(User, customer.assigned_user_id) if customer.assigned_user_id else None
    return CustomerOut(
        id=customer.id,
        tenant_id=customer.tenant_id,
        tenant_name=tenant.name if tenant else None,
        project_id=customer.project_id,
        project_name=project.name if project else None,
        assigned_user_id=customer.assigned_user_id,
        assigned_user_name=assigned.name if assigned else None,
        name=customer.name,
        document=customer.document,
        phone=customer.phone,
        email=customer.email,
        city=customer.city,
        segment=customer.segment,
        obligation=customer.obligation,
        balance=customer.balance,
        original_balance=customer.original_balance,
        dpd=customer.dpd,
        status=customer.status,
        risk=customer.risk,
        priority=customer.priority,
        next_action=customer.next_action,
        contactability=customer.contactability,
        notes=customer.notes,
        last_contact_at=customer.last_contact_at,
        next_contact_at=customer.next_contact_at,
        created_at=customer.created_at,
    )


def activity_to_out(db: Session, activity: ManagementActivity) -> ActivityOut:
    user = db.get(User, activity.user_id)
    typification = db.get(TypificationNode, activity.typification_id) if activity.typification_id else None
    obligation = db.get(CustomerObligation, activity.obligation_id) if activity.obligation_id else None
    return ActivityOut(
        id=activity.id,
        customer_id=activity.customer_id,
        obligation_id=activity.obligation_id,
        obligation_number=obligation.obligation_number if obligation else None,
        user_id=activity.user_id,
        user_name=user.name if user else None,
        typification_id=activity.typification_id,
        typification_label=typification.label if typification else None,
        channel=activity.channel,
        result=activity.result,
        note=activity.note,
        next_contact_at=activity.next_contact_at,
        created_at=activity.created_at,
    )
