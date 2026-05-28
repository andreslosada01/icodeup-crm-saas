from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class SaasPlan(Base):
    __tablename__ = "saas_plans"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    code: Mapped[str] = mapped_column(String(80), unique=True, index=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    base_price: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    monthly_price: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    max_users: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    max_projects: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    max_customers: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    max_storage_mb: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    max_records: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    includes_ai: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    includes_advanced_bi: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    includes_sales: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    includes_collections: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    includes_legal: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    includes_documents: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    includes_bi: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    includes_integrations: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    status: Mapped[str] = mapped_column(String(40), default="active", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    subscriptions = relationship("TenantSubscription", back_populates="plan")


class TenantSubscription(Base):
    __tablename__ = "tenant_subscriptions"

    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"), index=True, nullable=False)
    plan_id: Mapped[int] = mapped_column(ForeignKey("saas_plans.id"), index=True, nullable=False)
    start_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    end_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    renewal_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(40), default="active", nullable=False)
    billing_cycle: Mapped[str] = mapped_column(String(40), default="monthly", nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    plan = relationship("SaasPlan", back_populates="subscriptions")


class TenantModule(Base):
    __tablename__ = "tenant_modules"

    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"), index=True, nullable=False)
    module_id: Mapped[int | None] = mapped_column(ForeignKey("modules.id"), index=True)
    module_code: Mapped[str] = mapped_column(String(80), index=True, nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    enabled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    configuration_json: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    module = relationship("Module")


class Module(Base):
    __tablename__ = "modules"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(80), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    category: Mapped[str] = mapped_column(String(80), default="core", nullable=False)
    base_price: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    icon: Mapped[str | None] = mapped_column(String(80))
    order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
