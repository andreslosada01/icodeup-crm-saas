from pydantic import BaseModel


class LoginRequest(BaseModel):
    email: str
    password: str


class UserSession(BaseModel):
    id: int
    tenant_id: int
    tenant_name: str | None = None
    tenant_slug: str | None = None
    name: str
    email: str
    role: str
    is_platform_admin: bool = False
    is_company_admin: bool = False
    logo_url: str | None = None
    primary_color: str | None = None
    secondary_color: str | None = None


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserSession
