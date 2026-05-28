from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Tenant(Base):
    __tablename__ = "tenants"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(180), nullable=False)
    slug: Mapped[str] = mapped_column(String(120), unique=True, index=True, nullable=False)
    tax_id: Mapped[str | None] = mapped_column(String(80))
    document_type: Mapped[str | None] = mapped_column(String(40))
    document_number: Mapped[str | None] = mapped_column(String(80), index=True)
    status: Mapped[str] = mapped_column(String(30), default="active", nullable=False)
    plan_id: Mapped[int | None] = mapped_column(ForeignKey("saas_plans.id"), index=True)
    logo_url: Mapped[str | None] = mapped_column(String(420))
    primary_color: Mapped[str] = mapped_column(String(20), default="#15956f", nullable=False)
    secondary_color: Mapped[str] = mapped_column(String(20), default="#2563eb", nullable=False)
    timezone: Mapped[str] = mapped_column(String(80), default="America/Bogota", nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    users = relationship("User", back_populates="tenant")
    projects = relationship("Project", back_populates="tenant")
    plan = relationship("SaasPlan")


class Project(Base):
    __tablename__ = "projects"
    __table_args__ = (UniqueConstraint("tenant_id", "code", name="uq_projects_tenant_code"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(180), nullable=False)
    code: Mapped[str] = mapped_column(String(80), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(30), default="active", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    tenant = relationship("Tenant", back_populates="projects")
    assignments = relationship("UserProjectAssignment", back_populates="project", cascade="all, delete-orphan")
