from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class DocumentCreate(BaseModel):
    tenant_id: int | None = None
    project_id: int | None = None
    customer_id: int | None = None
    legal_case_id: int | None = None
    payment_id: int | None = None
    agreement_id: int | None = None
    document_type: str = Field(min_length=2, max_length=120)
    original_name: str = Field(min_length=2, max_length=240)
    storage_path: str | None = None
    mime_type: str | None = None
    size_bytes: int = 0
    status: str = "active"
    notes: str | None = None


class DocumentPatch(BaseModel):
    document_type: str | None = None
    original_name: str | None = None
    storage_path: str | None = None
    mime_type: str | None = None
    size_bytes: int | None = None
    status: str | None = None
    notes: str | None = None


class DocumentOut(BaseModel):
    id: int
    tenant_id: int
    project_id: int | None = None
    customer_id: int | None = None
    legal_case_id: int | None = None
    payment_id: int | None = None
    agreement_id: int | None = None
    uploaded_by_id: int
    document_type: str
    original_name: str
    storage_path: str
    mime_type: str | None = None
    size_bytes: int
    status: str
    notes: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
