from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class LegalCase(Base):
    __tablename__ = "legal_cases"

    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"), index=True, nullable=False)
    project_id: Mapped[int | None] = mapped_column(ForeignKey("projects.id"), index=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"), index=True, nullable=False)
    assigned_lawyer_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), index=True)
    case_number: Mapped[str | None] = mapped_column(String(120), index=True)
    process_type: Mapped[str] = mapped_column(String(120), nullable=False)
    court_name: Mapped[str | None] = mapped_column(String(220))
    amount: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    status: Mapped[str] = mapped_column(String(60), default="open", nullable=False)
    stage: Mapped[str | None] = mapped_column(String(120))
    risk: Mapped[str] = mapped_column(String(40), default="medium", nullable=False)
    next_action: Mapped[str | None] = mapped_column(String(240))
    next_deadline_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    actions = relationship("LegalAction", back_populates="legal_case", cascade="all, delete-orphan")
    hearings = relationship("LegalHearing", back_populates="legal_case", cascade="all, delete-orphan")
    deadlines = relationship("LegalDeadline", back_populates="legal_case", cascade="all, delete-orphan")


class LegalAction(Base):
    __tablename__ = "legal_actions"

    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"), index=True, nullable=False)
    legal_case_id: Mapped[int] = mapped_column(ForeignKey("legal_cases.id"), index=True, nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    action_type: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    action_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    next_deadline_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    legal_case = relationship("LegalCase", back_populates="actions")


class LegalHearing(Base):
    __tablename__ = "legal_hearings"

    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"), index=True, nullable=False)
    legal_case_id: Mapped[int] = mapped_column(ForeignKey("legal_cases.id"), index=True, nullable=False)
    hearing_type: Mapped[str] = mapped_column(String(120), nullable=False)
    scheduled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    location: Mapped[str | None] = mapped_column(String(220))
    status: Mapped[str] = mapped_column(String(60), default="scheduled", nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    legal_case = relationship("LegalCase", back_populates="hearings")


class LegalDeadline(Base):
    __tablename__ = "legal_deadlines"

    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"), index=True, nullable=False)
    legal_case_id: Mapped[int] = mapped_column(ForeignKey("legal_cases.id"), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    due_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[str] = mapped_column(String(60), default="open", nullable=False)
    priority: Mapped[str] = mapped_column(String(40), default="medium", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    legal_case = relationship("LegalCase", back_populates="deadlines")
