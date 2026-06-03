from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class CrmOption(BaseModel):
    id: int
    name: str
    label: str | None = None


class CrmOptions(BaseModel):
    tenants: list[CrmOption]
    projects: list[CrmOption]
    users: list[CrmOption]
    channels: list["CommunicationChannelOut"]


class CustomerCreate(BaseModel):
    tenant_id: int | None = None
    project_id: int
    assigned_user_id: int | None = None
    name: str = Field(min_length=2, max_length=220)
    document: str = Field(min_length=2, max_length=100)
    phone: str | None = None
    email: str | None = None
    city: str | None = None
    segment: str | None = None
    obligation: str | None = None
    balance: int = 0
    original_balance: int | None = None
    dpd: int = 0
    status: str = "Sin contacto"
    risk: str | None = None
    contactability: str = "Media"
    notes: str | None = None
    next_contact_at: datetime | None = None


class CustomerOut(BaseModel):
    id: int
    tenant_id: int
    tenant_name: str | None = None
    project_id: int | None = None
    project_name: str | None = None
    assigned_user_id: int | None = None
    assigned_user_name: str | None = None
    name: str
    document: str
    phone: str | None = None
    email: str | None = None
    city: str | None = None
    segment: str | None = None
    obligation: str | None = None
    balance: int
    original_balance: int
    dpd: int
    status: str
    risk: str
    priority: int
    next_action: str | None = None
    contactability: str
    notes: str | None = None
    last_contact_at: datetime | None = None
    next_contact_at: datetime | None = None
    created_at: datetime


class CustomerListResponse(BaseModel):
    items: list[CustomerOut]
    total: int
    page: int
    page_size: int
    total_pages: int


class CustomerObligationCreate(BaseModel):
    customer_id: int
    obligation_number: str = Field(min_length=2, max_length=160)
    project_id: int | None = None
    product_type: str | None = None
    portfolio_name: str | None = None
    purchase_number: str | None = None
    original_amount: int = 0
    current_balance: int = 0
    capital_amount: int | None = None
    interest_amount: int | None = None
    fees_amount: int | None = None
    days_past_due: int = 0
    status: str = "active"
    risk: str | None = None
    assigned_user_id: int | None = None
    assigned_leader_id: int | None = None
    metadata_json: str | None = None


class CustomerObligationPatch(BaseModel):
    product_type: str | None = None
    portfolio_name: str | None = None
    purchase_number: str | None = None
    original_amount: int | None = None
    current_balance: int | None = None
    capital_amount: int | None = None
    interest_amount: int | None = None
    fees_amount: int | None = None
    days_past_due: int | None = None
    status: str | None = None
    risk: str | None = None
    assigned_user_id: int | None = None
    assigned_leader_id: int | None = None
    metadata_json: str | None = None


class CustomerObligationOut(BaseModel):
    id: int
    tenant_id: int
    project_id: int | None = None
    customer_id: int
    customer_name: str | None = None
    obligation_number: str
    product_type: str | None = None
    portfolio_name: str | None = None
    purchase_number: str | None = None
    original_amount: int
    current_balance: int
    capital_amount: int | None = None
    interest_amount: int | None = None
    fees_amount: int | None = None
    days_past_due: int
    status: str
    risk: str
    assigned_user_id: int | None = None
    assigned_user_name: str | None = None
    assigned_leader_id: int | None = None
    assigned_leader_name: str | None = None
    metadata_json: str | None = None
    created_at: datetime
    updated_at: datetime


class ImportCustomersRequest(BaseModel):
    project_id: int
    assigned_user_id: int | None = None
    file_name: str | None = None
    csv_text: str = Field(min_length=5)


class ImportCustomersResponse(BaseModel):
    imported_count: int
    updated_count: int
    skipped_count: int
    batch_id: int


class ActivityCreate(BaseModel):
    obligation_id: int | None = None
    typification_id: int | None = None
    channel: str = "manual"
    result: str = "Gestion registrada"
    note: str | None = None
    next_contact_at: datetime | None = None
    promise_amount: int | None = None
    promise_due_date: datetime | None = None


class ActivityOut(BaseModel):
    id: int
    customer_id: int
    obligation_id: int | None = None
    obligation_number: str | None = None
    user_id: int
    user_name: str | None = None
    typification_id: int | None = None
    typification_label: str | None = None
    channel: str
    result: str
    note: str | None = None
    next_contact_at: datetime | None = None
    created_at: datetime


class PromiseCreate(BaseModel):
    customer_id: int
    obligation_id: int | None = None
    amount: int = Field(gt=0)
    due_date: datetime
    channel: str | None = None


class PromiseOut(BaseModel):
    id: int
    customer_id: int
    customer_name: str | None = None
    obligation_id: int | None = None
    obligation_number: str | None = None
    amount: int
    due_date: datetime
    channel: str | None = None
    status: str
    created_at: datetime


class PaymentCreate(BaseModel):
    customer_id: int
    amount: int = Field(gt=0)
    paid_at: datetime
    method: str = "No especificado"
    reference: str | None = None


class PaymentOut(BaseModel):
    id: int
    customer_id: int
    customer_name: str | None = None
    amount: int
    paid_at: datetime
    method: str
    reference: str | None = None
    created_at: datetime


class AgreementInstallmentCreate(BaseModel):
    due_date: datetime
    amount: int = Field(gt=0)


class AgreementInstallmentPatch(BaseModel):
    paid_amount: int | None = Field(default=None, ge=0)
    status: str | None = None


class AgreementInstallmentOut(BaseModel):
    id: int
    agreement_id: int
    due_date: datetime
    amount: int
    paid_amount: int
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class PaymentAgreementCreate(BaseModel):
    customer_id: int
    obligation_id: int | None = None
    total_amount: int = Field(gt=0)
    installment_count: int = Field(gt=0)
    start_date: datetime
    status: str = "active"
    notes: str | None = None
    installments: list[AgreementInstallmentCreate] | None = None


class PaymentAgreementOut(BaseModel):
    id: int
    tenant_id: int
    project_id: int | None = None
    customer_id: int
    customer_name: str | None = None
    obligation_id: int | None = None
    obligation_number: str | None = None
    user_id: int
    total_amount: int
    installment_count: int
    start_date: datetime
    status: str
    notes: str | None = None
    created_at: datetime
    installments: list[AgreementInstallmentOut] = Field(default_factory=list)

    model_config = {"from_attributes": True}


class CommunicationChannelCreate(BaseModel):
    tenant_id: int | None = None
    project_id: int | None = None
    kind: str
    label: str = Field(min_length=2, max_length=160)
    value: str = Field(min_length=2, max_length=220)
    provider: str | None = None
    is_default: bool = False
    status: str = "active"
    config_json: str | None = None

    @field_validator("kind")
    @classmethod
    def validate_kind(cls, value: str) -> str:
        allowed = {"whatsapp", "email", "telephony"}
        if value not in allowed:
            raise ValueError("Canal no soportado.")
        return value


class CommunicationChannelOut(CommunicationChannelCreate):
    id: int
    tenant_id: int

    model_config = {"from_attributes": True}


class DashboardMetrics(BaseModel):
    customers: int
    total_balance: int
    recovered: int
    active_promises: int
    promise_value: int
    contact_rate: int
    high_risk: int
    overdue_promises: int
    due_today: int
    risk_distribution: dict[str, int]
    status_distribution: dict[str, int]
    recovery_by_project: list[dict]


class BIKpi(BaseModel):
    key: str
    label: str
    value: int | str
    detail: str
    status: str = "neutral"


class BISemaphore(BaseModel):
    label: str
    status: str
    score: int
    detail: str


class BIAlert(BaseModel):
    severity: str
    title: str
    body: str
    value: int = 0
    action: str


class BIInsight(BaseModel):
    title: str
    body: str
    impact_value: int = 0
    confidence: int = 70
    action: str


class BIResponse(BaseModel):
    generated_at: datetime
    horizon_days: int
    kpis: list[BIKpi]
    semaphores: list[BISemaphore]
    alerts: list[BIAlert]
    insights: list[BIInsight]
    prediction: dict
    aging_buckets: list[dict]
    project_performance: list[dict]
    agent_productivity: list[dict]
    funnel: list[dict]
    top_opportunities: list[dict]
    high_risk_cases: list[dict]
