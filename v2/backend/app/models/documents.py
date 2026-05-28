from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"), index=True, nullable=False)
    project_id: Mapped[int | None] = mapped_column(ForeignKey("projects.id"), index=True)
    customer_id: Mapped[int | None] = mapped_column(ForeignKey("customers.id"), index=True)
    legal_case_id: Mapped[int | None] = mapped_column(ForeignKey("legal_cases.id"), index=True)
    payment_id: Mapped[int | None] = mapped_column(ForeignKey("payments.id"), index=True)
    agreement_id: Mapped[int | None] = mapped_column(ForeignKey("payment_agreements.id"), index=True)
    uploaded_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    document_type: Mapped[str] = mapped_column(String(120), nullable=False)
    original_name: Mapped[str] = mapped_column(String(240), nullable=False)
    storage_path: Mapped[str] = mapped_column(String(420), nullable=False)
    mime_type: Mapped[str | None] = mapped_column(String(120))
    size_bytes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    status: Mapped[str] = mapped_column(String(60), default="active", nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
