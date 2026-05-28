from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class Party(Base):
    __tablename__ = "parties"
    __table_args__ = (UniqueConstraint("tenant_id", "document_type", "document_number", name="uq_parties_tenant_document"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"), index=True, nullable=False)
    party_type: Mapped[str] = mapped_column(String(40), default="person", nullable=False)
    display_name: Mapped[str] = mapped_column(String(220), nullable=False)
    legal_name: Mapped[str | None] = mapped_column(String(240))
    document_type: Mapped[str | None] = mapped_column(String(40))
    document_number: Mapped[str | None] = mapped_column(String(100), index=True)
    email: Mapped[str | None] = mapped_column(String(180))
    phone: Mapped[str | None] = mapped_column(String(80))
    city: Mapped[str | None] = mapped_column(String(120))
    status: Mapped[str] = mapped_column(String(40), default="active", nullable=False)
    is_customer: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_debtor: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_supplier: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_employee: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_contact: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_prospect: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    external_ref: Mapped[str | None] = mapped_column(String(120), index=True)
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
