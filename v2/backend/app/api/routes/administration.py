from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import require_platform_admin
from app.core.config import settings
from app.core.roles import can_be_direct_leader
from app.core.security import hash_password
from app.db.session import get_db
from app.models import Project, Tenant, User
from app.repositories.administration_repository import AdministrationRepository
from app.schemas.administration import (
    AdminOverview,
    ProjectAssignmentIn,
    ProjectCreate,
    ProjectOut,
    ProjectUpdate,
    RoleOption,
    TenantAdminOut,
    TenantCreate,
    TenantUpdate,
    UserCreate,
    UserOut,
    UserUpdate,
    role_options,
)


router = APIRouter(dependencies=[Depends(require_platform_admin)])


def commit_or_conflict(db: Session) -> None:
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un registro con esos datos unicos.",
        ) from exc


def validate_leader(db: Session, tenant_id: int, leader_id: int | None) -> User | None:
    if leader_id is None:
        return None
    leader = db.get(User, leader_id)
    if leader is None or leader.tenant_id != tenant_id or not can_be_direct_leader(leader.role):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="El lider debe pertenecer a la misma empresa y tener rol administrador o coordinador.",
        )
    return leader


def validate_business_tenant(tenant: Tenant | None) -> Tenant:
    if tenant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Empresa no encontrada.")
    if tenant.slug == settings.platform_tenant_slug:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="El tenant interno de IcodeUp no admite proyectos ni usuarios de cliente.")
    return tenant


@router.get("/overview", response_model=AdminOverview)
def overview(db: Session = Depends(get_db)) -> dict:
    return AdministrationRepository(db).overview()


@router.get("/roles", response_model=list[RoleOption])
def roles() -> list[RoleOption]:
    return role_options()


@router.get("/tenants", response_model=list[TenantAdminOut])
def list_tenants(db: Session = Depends(get_db)) -> list[dict]:
    return AdministrationRepository(db).list_tenants()


@router.post("/tenants", response_model=TenantAdminOut, status_code=status.HTTP_201_CREATED)
def create_tenant(payload: TenantCreate, db: Session = Depends(get_db)) -> dict:
    tenant = Tenant(name=payload.name.strip(), slug=payload.slug, tax_id=payload.tax_id, notes=payload.notes)
    db.add(tenant)
    commit_or_conflict(db)
    return next(row for row in AdministrationRepository(db).list_tenants() if row["id"] == tenant.id)


@router.patch("/tenants/{tenant_id}", response_model=TenantAdminOut)
def update_tenant(tenant_id: int, payload: TenantUpdate, db: Session = Depends(get_db)) -> dict:
    tenant = db.get(Tenant, tenant_id)
    if tenant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Empresa no encontrada.")
    updates = payload.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(tenant, field, value.strip() if isinstance(value, str) else value)
    commit_or_conflict(db)
    return next(row for row in AdministrationRepository(db).list_tenants() if row["id"] == tenant.id)


@router.get("/projects", response_model=list[ProjectOut])
def list_projects(tenant_id: int | None = None, db: Session = Depends(get_db)) -> list[dict]:
    return AdministrationRepository(db).list_projects(tenant_id)


@router.post("/projects", response_model=ProjectOut, status_code=status.HTTP_201_CREATED)
def create_project(payload: ProjectCreate, db: Session = Depends(get_db)) -> dict:
    validate_business_tenant(db.get(Tenant, payload.tenant_id))
    project = Project(
        tenant_id=payload.tenant_id,
        name=payload.name.strip(),
        code=payload.code,
        description=payload.description,
        status=payload.status,
    )
    db.add(project)
    commit_or_conflict(db)
    return next(row for row in AdministrationRepository(db).list_projects(project.tenant_id) if row["id"] == project.id)


@router.patch("/projects/{project_id}", response_model=ProjectOut)
def update_project(project_id: int, payload: ProjectUpdate, db: Session = Depends(get_db)) -> dict:
    project = db.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Proyecto no encontrado.")
    updates = payload.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(project, field, value.strip() if isinstance(value, str) else value)
    commit_or_conflict(db)
    return next(row for row in AdministrationRepository(db).list_projects(project.tenant_id) if row["id"] == project.id)


@router.get("/users", response_model=list[UserOut])
def list_users(tenant_id: int | None = None, db: Session = Depends(get_db)) -> list[dict]:
    return AdministrationRepository(db).list_users(tenant_id)


@router.post("/users", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate, db: Session = Depends(get_db)) -> dict:
    validate_business_tenant(db.get(Tenant, payload.tenant_id))
    validate_leader(db, payload.tenant_id, payload.leader_id)
    user = User(
        tenant_id=payload.tenant_id,
        name=payload.name.strip(),
        email=payload.email,
        role=payload.role,
        phone=payload.phone,
        title=payload.title,
        leader_id=payload.leader_id,
        password_hash=hash_password(payload.password),
    )
    db.add(user)
    try:
        db.flush()
        AdministrationRepository(db).set_user_projects(user, payload.project_ids)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ya existe un usuario con ese email.") from exc
    except ValueError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    commit_or_conflict(db)
    return next(row for row in AdministrationRepository(db).list_users(user.tenant_id) if row["id"] == user.id)


@router.patch("/users/{user_id}", response_model=UserOut)
def update_user(user_id: int, payload: UserUpdate, db: Session = Depends(get_db)) -> dict:
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado.")
    updates = payload.model_dump(exclude_unset=True)
    project_ids = updates.pop("project_ids", None)
    if "leader_id" in updates:
        validate_leader(db, user.tenant_id, updates["leader_id"])
    if "password" in updates:
        user.password_hash = hash_password(updates.pop("password"))
    for field, value in updates.items():
        setattr(user, field, value.strip() if isinstance(value, str) else value)
    if project_ids is not None:
        AdministrationRepository(db).set_user_projects(user, project_ids)
    commit_or_conflict(db)
    return next(row for row in AdministrationRepository(db).list_users(user.tenant_id) if row["id"] == user.id)


@router.put("/users/{user_id}/projects", response_model=UserOut)
def assign_user_projects(user_id: int, payload: ProjectAssignmentIn, db: Session = Depends(get_db)) -> dict:
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado.")
    try:
        AdministrationRepository(db).set_user_projects(user, payload.project_ids)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    commit_or_conflict(db)
    return next(row for row in AdministrationRepository(db).list_users(user.tenant_id) if row["id"] == user.id)
