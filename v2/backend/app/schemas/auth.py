from pydantic import BaseModel


class LoginRequest(BaseModel):
    email: str
    password: str


class UserSession(BaseModel):
    id: int
    tenant_id: int
    name: str
    email: str
    role: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserSession
