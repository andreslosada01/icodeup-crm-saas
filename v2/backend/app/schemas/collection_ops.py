from __future__ import annotations

from datetime import date as date_type, datetime
from typing import Any

from pydantic import BaseModel, Field


class TypificationTreeCreate(BaseModel):
    tenant_id: int | None = None
    project_id: int | None = None
    module: str = "collections"
    name: str = Field(min_length=2, max_length=220)
    code: str = Field(min_length=2, max_length=120)
    description: str | None = None
    status: str = "active"


class TypificationTreeUpdate(BaseModel):
    project_id: int | None = None
    module: str | None = None
    name: str | None = None
    code: str | None = None
    description: str | None = None
    status: str | None = None


class TypificationTreeOut(TypificationTreeCreate):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TypificationTreeNodeCreate(BaseModel):
    parent_id: int | None = None
    level: int = Field(default=1, ge=1)
    code: str = Field(min_length=2, max_length=120)
    label: str = Field(min_length=2, max_length=220)
    description: str | None = None
    order: int = 0
    color: str | None = None
    is_active: bool = True
    requires_comment: bool = False
    requires_promise: bool = False
    requires_next_action: bool = False
    requires_amount: bool = False
    requires_document: bool = False
    closes_management: bool = False
    changes_customer_status: bool = False
    target_customer_status: str | None = None
    generates_alert: bool = False
    escalates_to_legal: bool = False


class TypificationTreeNodeUpdate(BaseModel):
    parent_id: int | None = None
    level: int | None = Field(default=None, ge=1)
    code: str | None = None
    label: str | None = None
    description: str | None = None
    order: int | None = None
    color: str | None = None
    is_active: bool | None = None
    requires_comment: bool | None = None
    requires_promise: bool | None = None
    requires_next_action: bool | None = None
    requires_amount: bool | None = None
    requires_document: bool | None = None
    closes_management: bool | None = None
    changes_customer_status: bool | None = None
    target_customer_status: str | None = None
    generates_alert: bool | None = None
    escalates_to_legal: bool | None = None


class TypificationTreeNodeOut(TypificationTreeNodeCreate):
    id: int
    tree_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TypificationCombinationCreate(BaseModel):
    tenant_id: int | None = None
    project_id: int | None = None
    tree_id: int
    path: list[int | str]
    required_fields: dict[str, Any] = Field(default_factory=dict)
    effects: dict[str, Any] = Field(default_factory=dict)
    is_active: bool = True


class TypificationCombinationOut(BaseModel):
    id: int
    tenant_id: int
    project_id: int | None = None
    tree_id: int
    path: list[int | str]
    required_fields: dict[str, Any]
    effects: dict[str, Any]
    is_active: bool
    created_at: datetime
    updated_at: datetime


class TypificationCombinationValidate(BaseModel):
    tree_id: int
    path: list[int | str]
    payload: dict[str, Any] = Field(default_factory=dict)


class UploadPreviewRequest(BaseModel):
    tenant_id: int | None = None
    project_id: int | None = None
    upload_type: str
    file_name: str | None = None
    csv_text: str = Field(min_length=5)
    mapping: dict[str, str] = Field(default_factory=dict)


class UploadConfirmRequest(UploadPreviewRequest):
    create_records: bool = True


class UploadPreviewResponse(BaseModel):
    upload_type: str
    file_name: str | None = None
    total_rows: int
    valid_rows: int
    error_rows: int
    columns: list[str]
    sample: list[dict[str, str]]
    suggested_mapping: dict[str, str] = Field(default_factory=dict)
    required_fields: list[str] = Field(default_factory=list)
    optional_fields: list[str] = Field(default_factory=list)
    summary: dict[str, Any] = Field(default_factory=dict)
    errors: list[dict[str, Any]]


class UploadBatchOut(BaseModel):
    id: int
    tenant_id: int
    project_id: int | None = None
    uploaded_by_id: int
    upload_type: str
    original_filename: str | None = None
    status: str
    total_rows: int
    valid_rows: int
    error_rows: int
    created_rows: int
    updated_rows: int
    summary_json: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class CustomerDemographicCreate(BaseModel):
    tenant_id: int | None = None
    customer_id: int
    source: str = "manual"
    phone: str | None = None
    email: str | None = None
    address: str | None = None
    city: str | None = None
    state: str | None = None
    employer: str | None = None
    job_title: str | None = None
    reference_name: str | None = None
    reference_phone: str | None = None
    score: int = 0
    metadata: dict[str, Any] = Field(default_factory=dict)


class CustomerDemographicOut(BaseModel):
    id: int
    tenant_id: int
    customer_id: int
    source: str
    phone: str | None = None
    email: str | None = None
    address: str | None = None
    city: str | None = None
    state: str | None = None
    employer: str | None = None
    job_title: str | None = None
    reference_name: str | None = None
    reference_phone: str | None = None
    score: int
    metadata: dict[str, Any]
    is_active: bool
    created_at: datetime


class CallRecordingCreate(BaseModel):
    tenant_id: int | None = None
    project_id: int | None = None
    customer_id: int | None = None
    activity_id: int | None = None
    user_id: int | None = None
    call_id: str
    phone_number: str | None = None
    direction: str = "outbound"
    started_at: datetime | None = None
    duration_seconds: int = 0
    recording_url: str | None = None
    storage_path: str | None = None
    provider_code: str | None = None
    status: str = "available"
    metadata: dict[str, Any] = Field(default_factory=dict)


class CallRecordingOut(BaseModel):
    id: int
    tenant_id: int
    project_id: int | None = None
    customer_id: int | None = None
    activity_id: int | None = None
    user_id: int | None = None
    call_id: str
    phone_number: str | None = None
    direction: str
    started_at: datetime | None = None
    duration_seconds: int
    provider_code: str | None = None
    status: str
    storage_path: str | None = None
    playback_available: bool
    metadata: dict[str, Any]
    created_at: datetime


class RecordingLinkRequest(BaseModel):
    recording_id: int
    activity_id: int | None = None
    customer_id: int | None = None


class SavedDataViewCreate(BaseModel):
    name: str
    source: str
    columns: list[str] = Field(default_factory=list)
    filters: dict[str, Any] = Field(default_factory=dict)
    sort: dict[str, Any] = Field(default_factory=dict)
    is_public: bool = False
    is_favorite: bool = False


class SavedDataViewOut(SavedDataViewCreate):
    id: int
    tenant_id: int
    user_id: int
    created_at: datetime
    updated_at: datetime


class ExcelWebQuery(BaseModel):
    source: str
    filters: dict[str, Any] = Field(default_factory=dict)
    columns: list[str] = Field(default_factory=list)
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=20)


class ExcelWebQueryResult(BaseModel):
    source: str
    columns: list[str]
    rows: list[dict[str, Any]]
    total: int
    page: int
    page_size: int
    total_pages: int


class OperationalSheetRowCreate(BaseModel):
    project_id: int | None = None
    customer_id: int | None = None
    obligation_id: int | None = None
    date: date_type | None = None
    portfolio: str | None = Field(default=None, max_length=180)
    customer_name: str | None = Field(default=None, max_length=220)
    document: str | None = Field(default=None, max_length=80)
    obligation_number: str | None = Field(default=None, max_length=180)
    management_note: str | None = None
    commitment: str | None = None
    amount: int = Field(default=0, ge=0)
    status: str = Field(default="Pendiente", max_length=60)
    next_action_at: datetime | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class OperationalSheetRowPatch(BaseModel):
    project_id: int | None = None
    customer_id: int | None = None
    obligation_id: int | None = None
    date: date_type | None = None
    portfolio: str | None = Field(default=None, max_length=180)
    customer_name: str | None = Field(default=None, max_length=220)
    document: str | None = Field(default=None, max_length=80)
    obligation_number: str | None = Field(default=None, max_length=180)
    management_note: str | None = None
    commitment: str | None = None
    amount: int | None = Field(default=None, ge=0)
    status: str | None = Field(default=None, max_length=60)
    next_action_at: datetime | None = None
    metadata: dict[str, Any] | None = None


class OperationalSheetRowOut(OperationalSheetRowCreate):
    id: int
    tenant_id: int
    user_id: int
    user_name: str | None = None
    created_at: datetime
    updated_at: datetime


class IntegrationProviderCreate(BaseModel):
    tenant_id: int | None = None
    code: str
    name: str
    provider_type: str
    status: str = "configured"
    base_url: str | None = None
    config: dict[str, Any] = Field(default_factory=dict)
    secret: str | None = None


class IntegrationProviderOut(BaseModel):
    id: int
    tenant_id: int
    code: str
    name: str
    provider_type: str
    status: str
    base_url: str | None = None
    config: dict[str, Any]
    secret_mask: str | None = None
    created_at: datetime


class ChannelConfigurationCreate(BaseModel):
    tenant_id: int | None = None
    provider_id: int | None = None
    channel_type: str
    name: str
    status: str = "active"
    from_value: str | None = None
    config: dict[str, Any] = Field(default_factory=dict)


class ChannelConfigurationOut(BaseModel):
    id: int
    tenant_id: int
    provider_id: int | None = None
    channel_type: str
    name: str
    status: str
    from_value: str | None = None
    config: dict[str, Any]
    created_at: datetime


class CommunicationTemplateCreate(BaseModel):
    tenant_id: int | None = None
    channel_type: str
    code: str
    name: str
    subject: str | None = None
    body: str
    status: str = "active"


class CommunicationTemplateOut(CommunicationTemplateCreate):
    id: int
    tenant_id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class WebhookConfigurationCreate(BaseModel):
    tenant_id: int | None = None
    name: str
    event_type: str
    target_url: str
    status: str = "active"
    secret: str | None = None


class WebhookConfigurationOut(BaseModel):
    id: int
    tenant_id: int
    name: str
    event_type: str
    target_url: str
    status: str
    secret_mask: str | None = None
    created_at: datetime


class ChannelEventOut(BaseModel):
    id: int
    tenant_id: int
    provider_id: int | None = None
    channel_type: str
    event_type: str
    entity_type: str | None = None
    entity_id: int | None = None
    status: str
    payload: dict[str, Any]
    created_at: datetime
