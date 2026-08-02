from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class TelephonyProvider(Base):
    __tablename__ = "telephony_providers"
    __table_args__ = (UniqueConstraint("tenant_id", "name", name="uq_telephony_provider_tenant_name"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(180), nullable=False)
    provider_type: Mapped[str] = mapped_column(String(40), default="manual", index=True, nullable=False)
    host: Mapped[str | None] = mapped_column(String(180))
    port: Mapped[int | None] = mapped_column(Integer)
    websocket_url: Mapped[str | None] = mapped_column(String(500))
    api_url: Mapped[str | None] = mapped_column(String(500))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    config_json: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class TelephonyExtension(Base):
    __tablename__ = "telephony_extensions"
    __table_args__ = (UniqueConstraint("tenant_id", "extension_number", name="uq_telephony_extension_tenant_number"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"), index=True, nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    provider_id: Mapped[int | None] = mapped_column(ForeignKey("telephony_providers.id"), index=True)
    extension_number: Mapped[str] = mapped_column(String(40), nullable=False)
    display_name: Mapped[str | None] = mapped_column(String(180))
    sip_username: Mapped[str | None] = mapped_column(String(160))
    sip_domain: Mapped[str | None] = mapped_column(String(180))
    status: Mapped[str] = mapped_column(String(40), default="not_connected", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    metadata_json: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class CallLog(Base):
    __tablename__ = "call_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"), index=True, nullable=False)
    provider_id: Mapped[int | None] = mapped_column(ForeignKey("telephony_providers.id"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    project_id: Mapped[int | None] = mapped_column(ForeignKey("projects.id"), index=True)
    customer_id: Mapped[int | None] = mapped_column(ForeignKey("customers.id"), index=True)
    obligation_id: Mapped[int | None] = mapped_column(ForeignKey("customer_obligations.id"), index=True)
    phone_number: Mapped[str] = mapped_column(String(80), nullable=False)
    direction: Mapped[str] = mapped_column(String(40), default="outbound", index=True, nullable=False)
    call_status: Mapped[str] = mapped_column(String(40), default="initiated", index=True, nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    answered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    duration_seconds: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    external_call_id: Mapped[str | None] = mapped_column(String(180), index=True)
    recording_url: Mapped[str | None] = mapped_column(String(500))
    management_activity_id: Mapped[int | None] = mapped_column(ForeignKey("management_activities.id"), index=True)
    metadata_json: Mapped[str | None] = mapped_column(Text)
