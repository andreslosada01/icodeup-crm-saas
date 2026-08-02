from __future__ import annotations

from datetime import date as date_type, datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class TypificationTree(Base):
    __tablename__ = "typification_trees"
    __table_args__ = (UniqueConstraint("tenant_id", "project_id", "module", "code", name="uq_typification_tree_scope_code"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"), index=True, nullable=False)
    project_id: Mapped[int | None] = mapped_column(ForeignKey("projects.id"), index=True)
    module: Mapped[str] = mapped_column(String(80), default="collections", index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(220), nullable=False)
    code: Mapped[str] = mapped_column(String(120), index=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(40), default="active", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class TypificationTreeNode(Base):
    __tablename__ = "typification_tree_nodes"
    __table_args__ = (UniqueConstraint("tree_id", "code", name="uq_typification_tree_node_code"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    tree_id: Mapped[int] = mapped_column(ForeignKey("typification_trees.id"), index=True, nullable=False)
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("typification_tree_nodes.id"), index=True)
    level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    code: Mapped[str] = mapped_column(String(120), index=True, nullable=False)
    label: Mapped[str] = mapped_column(String(220), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    color: Mapped[str | None] = mapped_column(String(20))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    requires_comment: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    requires_promise: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    requires_next_action: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    requires_amount: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    requires_document: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    closes_management: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    changes_customer_status: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    target_customer_status: Mapped[str | None] = mapped_column(String(80))
    generates_alert: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    escalates_to_legal: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class TypificationCombinationRule(Base):
    __tablename__ = "typification_combination_rules"

    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"), index=True, nullable=False)
    project_id: Mapped[int | None] = mapped_column(ForeignKey("projects.id"), index=True)
    tree_id: Mapped[int] = mapped_column(ForeignKey("typification_trees.id"), index=True, nullable=False)
    path_json: Mapped[str] = mapped_column(Text, nullable=False)
    required_fields_json: Mapped[str | None] = mapped_column(Text)
    effects_json: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class CustomerDemographic(Base):
    __tablename__ = "customer_demographics"

    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"), index=True, nullable=False)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"), index=True, nullable=False)
    source: Mapped[str] = mapped_column(String(120), default="demo", nullable=False)
    phone: Mapped[str | None] = mapped_column(String(80))
    email: Mapped[str | None] = mapped_column(String(180))
    address: Mapped[str | None] = mapped_column(String(240))
    city: Mapped[str | None] = mapped_column(String(120))
    state: Mapped[str | None] = mapped_column(String(120))
    employer: Mapped[str | None] = mapped_column(String(180))
    job_title: Mapped[str | None] = mapped_column(String(160))
    reference_name: Mapped[str | None] = mapped_column(String(180))
    reference_phone: Mapped[str | None] = mapped_column(String(80))
    score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    contactability: Mapped[str] = mapped_column(String(40), default="Media", nullable=False)
    priority: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    valid_from: Mapped[date_type | None] = mapped_column(Date)
    valid_until: Mapped[date_type | None] = mapped_column(Date)
    metadata_json: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class CallRecording(Base):
    __tablename__ = "call_recordings"
    __table_args__ = (UniqueConstraint("tenant_id", "call_id", name="uq_call_recording_tenant_call"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"), index=True, nullable=False)
    project_id: Mapped[int | None] = mapped_column(ForeignKey("projects.id"), index=True)
    customer_id: Mapped[int | None] = mapped_column(ForeignKey("customers.id"), index=True)
    activity_id: Mapped[int | None] = mapped_column(ForeignKey("management_activities.id"), index=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), index=True)
    call_id: Mapped[str] = mapped_column(String(160), index=True, nullable=False)
    phone_number: Mapped[str | None] = mapped_column(String(80))
    direction: Mapped[str] = mapped_column(String(40), default="outbound", nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    duration_seconds: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    recording_url: Mapped[str | None] = mapped_column(String(500))
    storage_path: Mapped[str | None] = mapped_column(String(500))
    provider_code: Mapped[str | None] = mapped_column(String(120))
    status: Mapped[str] = mapped_column(String(40), default="available", nullable=False)
    metadata_json: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class RecordingAccessLog(Base):
    __tablename__ = "recording_access_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"), index=True, nullable=False)
    recording_id: Mapped[int] = mapped_column(ForeignKey("call_recordings.id"), index=True, nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    action: Mapped[str] = mapped_column(String(60), nullable=False)
    ip_address: Mapped[str | None] = mapped_column(String(80))
    user_agent: Mapped[str | None] = mapped_column(String(300))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class UploadBatch(Base):
    __tablename__ = "upload_batches"

    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"), index=True, nullable=False)
    project_id: Mapped[int | None] = mapped_column(ForeignKey("projects.id"), index=True)
    uploaded_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    upload_type: Mapped[str] = mapped_column(String(80), index=True, nullable=False)
    original_filename: Mapped[str | None] = mapped_column(String(240))
    status: Mapped[str] = mapped_column(String(40), default="completed", nullable=False)
    total_rows: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    valid_rows: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    error_rows: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_rows: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    updated_rows: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    error_file_path: Mapped[str | None] = mapped_column(String(500))
    result_file_path: Mapped[str | None] = mapped_column(String(500))
    mapping_json: Mapped[str | None] = mapped_column(Text)
    summary_json: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class OperationalFile(Base):
    __tablename__ = "operational_files"

    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"), index=True, nullable=False)
    project_id: Mapped[int | None] = mapped_column(ForeignKey("projects.id"), index=True)
    customer_id: Mapped[int | None] = mapped_column(ForeignKey("customers.id"), index=True)
    uploaded_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    file_type: Mapped[str] = mapped_column(String(80), index=True, nullable=False)
    original_name: Mapped[str] = mapped_column(String(240), nullable=False)
    storage_path: Mapped[str] = mapped_column(String(500), nullable=False)
    mime_type: Mapped[str | None] = mapped_column(String(160))
    size_bytes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    status: Mapped[str] = mapped_column(String(40), default="registered", nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class SavedDataView(Base):
    __tablename__ = "saved_data_views"

    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"), index=True, nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(220), nullable=False)
    source: Mapped[str] = mapped_column(String(80), index=True, nullable=False)
    columns_json: Mapped[str | None] = mapped_column(Text)
    filters_json: Mapped[str | None] = mapped_column(Text)
    sort_json: Mapped[str | None] = mapped_column(Text)
    is_public: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_favorite: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class OperationalSheetRow(Base):
    __tablename__ = "operational_sheet_rows"

    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"), index=True, nullable=False)
    project_id: Mapped[int | None] = mapped_column(ForeignKey("projects.id"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    customer_id: Mapped[int | None] = mapped_column(ForeignKey("customers.id"), index=True)
    obligation_id: Mapped[int | None] = mapped_column(ForeignKey("customer_obligations.id"), index=True)
    date: Mapped[date_type | None] = mapped_column(Date)
    portfolio: Mapped[str | None] = mapped_column(String(180))
    customer_name: Mapped[str | None] = mapped_column(String(220))
    document: Mapped[str | None] = mapped_column(String(80))
    obligation_number: Mapped[str | None] = mapped_column(String(180))
    management_note: Mapped[str | None] = mapped_column(Text)
    commitment: Mapped[str | None] = mapped_column(Text)
    amount: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    status: Mapped[str] = mapped_column(String(60), default="Pendiente", index=True, nullable=False)
    next_action_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    metadata_json: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class DataExportLog(Base):
    __tablename__ = "data_export_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"), index=True, nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    source: Mapped[str] = mapped_column(String(80), index=True, nullable=False)
    filters_json: Mapped[str | None] = mapped_column(Text)
    columns_json: Mapped[str | None] = mapped_column(Text)
    row_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    status: Mapped[str] = mapped_column(String(40), default="completed", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class IntegrationProvider(Base):
    __tablename__ = "integration_providers"
    __table_args__ = (UniqueConstraint("tenant_id", "code", name="uq_integration_provider_tenant_code"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"), index=True, nullable=False)
    code: Mapped[str] = mapped_column(String(120), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(220), nullable=False)
    provider_type: Mapped[str] = mapped_column(String(80), index=True, nullable=False)
    status: Mapped[str] = mapped_column(String(40), default="configured", nullable=False)
    base_url: Mapped[str | None] = mapped_column(String(500))
    config_json: Mapped[str | None] = mapped_column(Text)
    secret_mask: Mapped[str | None] = mapped_column(String(120))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class ChannelConfiguration(Base):
    __tablename__ = "channel_configurations"

    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"), index=True, nullable=False)
    provider_id: Mapped[int | None] = mapped_column(ForeignKey("integration_providers.id"), index=True)
    channel_type: Mapped[str] = mapped_column(String(80), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(220), nullable=False)
    status: Mapped[str] = mapped_column(String(40), default="active", nullable=False)
    from_value: Mapped[str | None] = mapped_column(String(220))
    config_json: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class CommunicationTemplate(Base):
    __tablename__ = "communication_templates"

    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"), index=True, nullable=False)
    channel_type: Mapped[str] = mapped_column(String(80), index=True, nullable=False)
    code: Mapped[str] = mapped_column(String(120), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(220), nullable=False)
    subject: Mapped[str | None] = mapped_column(String(240))
    body: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(40), default="active", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class WebhookConfiguration(Base):
    __tablename__ = "webhook_configurations"

    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(220), nullable=False)
    event_type: Mapped[str] = mapped_column(String(120), index=True, nullable=False)
    target_url: Mapped[str] = mapped_column(String(500), nullable=False)
    status: Mapped[str] = mapped_column(String(40), default="active", nullable=False)
    secret_mask: Mapped[str | None] = mapped_column(String(120))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class ChannelEventLog(Base):
    __tablename__ = "channel_event_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"), index=True, nullable=False)
    provider_id: Mapped[int | None] = mapped_column(ForeignKey("integration_providers.id"), index=True)
    channel_type: Mapped[str] = mapped_column(String(80), index=True, nullable=False)
    event_type: Mapped[str] = mapped_column(String(120), nullable=False)
    entity_type: Mapped[str | None] = mapped_column(String(120))
    entity_id: Mapped[int | None] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(40), default="simulated", nullable=False)
    payload_json: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
