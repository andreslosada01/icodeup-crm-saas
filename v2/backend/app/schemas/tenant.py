from pydantic import BaseModel


class TenantCreate(BaseModel):
    name: str
    slug: str
    tax_id: str | None = None


class TenantOut(BaseModel):
    id: int
    name: str
    slug: str
    tax_id: str | None = None
    status: str

    model_config = {"from_attributes": True}

