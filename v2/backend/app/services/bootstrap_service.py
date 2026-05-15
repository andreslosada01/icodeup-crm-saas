from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import hash_password
from app.models import Tenant, User


def bootstrap_platform(db: Session) -> None:
    if not settings.enable_demo_seeds:
        return
    if not settings.platform_admin_email or not settings.platform_admin_password:
        return
    tenant = db.scalar(select(Tenant).where(Tenant.slug == settings.platform_tenant_slug))
    if tenant is None:
        tenant = Tenant(name="IcodeUp Platform", slug=settings.platform_tenant_slug, tax_id="PLATFORM")
        db.add(tenant)
        db.flush()
    user = db.scalar(select(User).where(User.email == settings.platform_admin_email.lower()))
    if user is None:
        db.add(
            User(
                tenant_id=tenant.id,
                name="IcodeUp Plataforma",
                email=settings.platform_admin_email.lower(),
                role="platform_admin",
                password_hash=hash_password(settings.platform_admin_password),
            )
        )
    db.commit()

