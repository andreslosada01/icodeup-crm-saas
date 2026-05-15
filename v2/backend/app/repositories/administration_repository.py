from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.core.config import settings
from app.core.roles import ROLE_LABELS
from app.models import Customer, Project, Tenant, User, UserProjectAssignment


class AdministrationRepository:
    def __init__(self, db: Session):
        self.db = db

    def overview(self) -> dict:
        tenant_scope = Tenant.slug != settings.platform_tenant_slug
        return {
            "tenants": self.db.scalar(select(func.count(Tenant.id)).where(tenant_scope)) or 0,
            "projects": self.db.scalar(select(func.count(Project.id))) or 0,
            "users": self.db.scalar(select(func.count(User.id))) or 0,
            "customers": self.db.scalar(select(func.count(Customer.id))) or 0,
            "active_tenants": self.db.scalar(select(func.count(Tenant.id)).where(tenant_scope, Tenant.status == "active")) or 0,
        }

    def list_tenants(self) -> list[dict]:
        tenants = list(self.db.scalars(select(Tenant).where(Tenant.slug != settings.platform_tenant_slug).order_by(Tenant.name)))
        rows = []
        for tenant in tenants:
            rows.append(
                {
                    "id": tenant.id,
                    "name": tenant.name,
                    "slug": tenant.slug,
                    "tax_id": tenant.tax_id,
                    "status": tenant.status,
                    "notes": tenant.notes,
                    "project_count": self.db.scalar(select(func.count(Project.id)).where(Project.tenant_id == tenant.id)) or 0,
                    "user_count": self.db.scalar(select(func.count(User.id)).where(User.tenant_id == tenant.id)) or 0,
                    "customer_count": self.db.scalar(select(func.count(Customer.id)).where(Customer.tenant_id == tenant.id)) or 0,
                }
            )
        return rows

    def list_projects(self, tenant_id: int | None = None) -> list[dict]:
        query = select(Project, Tenant.name).join(Tenant, Tenant.id == Project.tenant_id).order_by(Tenant.name, Project.name)
        if tenant_id is not None:
            query = query.where(Project.tenant_id == tenant_id)
        rows = []
        for project, tenant_name in self.db.execute(query).all():
            rows.append(
                {
                    "id": project.id,
                    "tenant_id": project.tenant_id,
                    "tenant_name": tenant_name,
                    "name": project.name,
                    "code": project.code,
                    "description": project.description,
                    "status": project.status,
                    "assigned_user_count": self.db.scalar(
                        select(func.count(UserProjectAssignment.id)).where(UserProjectAssignment.project_id == project.id)
                    )
                    or 0,
                    "customer_count": self.db.scalar(select(func.count(Customer.id)).where(Customer.project_id == project.id)) or 0,
                }
            )
        return rows

    def list_users(self, tenant_id: int | None = None) -> list[dict]:
        query = (
            select(User)
            .options(selectinload(User.tenant), selectinload(User.leader), selectinload(User.project_assignments).selectinload(UserProjectAssignment.project))
            .order_by(User.name)
        )
        if tenant_id is not None:
            query = query.where(User.tenant_id == tenant_id)
        users = list(self.db.scalars(query))
        rows = []
        for user in users:
            assignments = [assignment.project for assignment in user.project_assignments if assignment.project is not None]
            rows.append(
                {
                    "id": user.id,
                    "tenant_id": user.tenant_id,
                    "tenant_name": user.tenant.name if user.tenant else "",
                    "name": user.name,
                    "email": user.email,
                    "role": user.role,
                    "role_label": ROLE_LABELS.get(user.role, user.role),
                    "status": user.status,
                    "phone": user.phone,
                    "title": user.title,
                    "leader_id": user.leader_id,
                    "leader_name": user.leader.name if user.leader else None,
                    "project_ids": [project.id for project in assignments],
                    "project_names": [project.name for project in assignments],
                }
            )
        return rows

    def get_tenant(self, tenant_id: int) -> Tenant | None:
        return self.db.get(Tenant, tenant_id)

    def get_project(self, project_id: int) -> Project | None:
        return self.db.get(Project, project_id)

    def get_user(self, user_id: int) -> User | None:
        return self.db.get(User, user_id)

    def set_user_projects(self, user: User, project_ids: list[int]) -> None:
        project_ids = sorted(set(project_ids))
        if project_ids:
            valid_count = self.db.scalar(
                select(func.count(Project.id)).where(Project.tenant_id == user.tenant_id, Project.id.in_(project_ids))
            )
            if valid_count != len(project_ids):
                raise ValueError("Uno o mas proyectos no pertenecen a la empresa del usuario.")

        current = list(self.db.scalars(select(UserProjectAssignment).where(UserProjectAssignment.user_id == user.id)))
        current_by_project = {assignment.project_id: assignment for assignment in current}
        for assignment in current:
            if assignment.project_id not in project_ids:
                self.db.delete(assignment)
        for project_id in project_ids:
            if project_id not in current_by_project:
                self.db.add(UserProjectAssignment(user_id=user.id, project_id=project_id))
        self.db.flush()
