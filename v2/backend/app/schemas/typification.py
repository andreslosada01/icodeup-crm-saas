from pydantic import BaseModel


class TypificationCreate(BaseModel):
    tenant_id: int
    project_id: int | None = None
    parent_id: int | None = None
    label: str
    code: str
    next_status: str | None = None
    requires_promise: bool = False
    requires_payment: bool = False
    channel: str | None = None
    sort_order: int = 0


class TypificationUpdate(BaseModel):
    project_id: int | None = None
    parent_id: int | None = None
    label: str | None = None
    code: str | None = None
    next_status: str | None = None
    requires_promise: bool | None = None
    requires_payment: bool | None = None
    channel: str | None = None
    sort_order: int | None = None


class TypificationOut(TypificationCreate):
    id: int

    model_config = {"from_attributes": True}
