from __future__ import annotations

from pathlib import Path

import pytest


BACKEND_ROOT = Path(__file__).resolve().parents[1]
V2_ROOT = BACKEND_ROOT.parent


def read(relative_path: str) -> str:
    return (V2_ROOT / relative_path).read_text(encoding="utf-8")


@pytest.mark.safe_static
def test_collections_core_models_and_migration_are_additive() -> None:
    crm_models = read("backend/app/models/crm.py")
    collection_models = read("backend/app/models/collection_ops.py")
    telephony_models = read("backend/app/models/telephony.py")
    migration = read("backend/alembic/versions/20260612_0007_collections_core_data_flow.py")

    assert "obligation_id: Mapped[int | None]" in crm_models
    assert "priority: Mapped[int]" in crm_models
    assert "due_date: Mapped[datetime | None]" in crm_models
    assert "assignment_date: Mapped[datetime | None]" in crm_models
    assert "contactability: Mapped[str]" in collection_models
    assert "valid_until: Mapped[date_type | None]" in collection_models
    assert "project_id: Mapped[int | None]" in telephony_models

    assert "ALTER TABLE IF EXISTS payments ADD COLUMN IF NOT EXISTS obligation_id" in migration
    assert "ALTER TABLE IF EXISTS call_logs ADD COLUMN IF NOT EXISTS project_id" in migration
    assert "ALTER TABLE IF EXISTS customer_obligations ADD COLUMN IF NOT EXISTS priority" in migration
    assert "ALTER TABLE IF EXISTS customer_demographics ADD COLUMN IF NOT EXISTS contactability" in migration
    assert "pass" in migration


@pytest.mark.safe_static
def test_collections_core_api_contracts_include_obligations_and_demographics() -> None:
    crm_schemas = read("backend/app/schemas/crm.py")
    collection_schemas = read("backend/app/schemas/collection_ops.py")
    payments_route = read("backend/app/api/routes/crm/payments.py")
    agreements_route = read("backend/app/api/routes/crm/agreements.py")
    uploads_route = read("backend/app/api/routes/uploads.py")
    telephony_route = read("backend/app/api/routes/telephony.py")

    assert "original_balance: int | None" in crm_schemas
    assert "obligation_id: int | None = None" in crm_schemas
    assert "obligation_number: str | None = None" in crm_schemas
    assert "contactability: str = \"Media\"" in collection_schemas
    assert "valid_from: date_type | None = None" in collection_schemas
    assert "IntegrationReadinessOut" in collection_schemas
    assert "PayControlPaymentSyncPreview" in collection_schemas
    assert "QAuditEvaluationPreview" in collection_schemas

    assert "obligation_for_access(db, payload.obligation_id" in payments_route
    assert "obligation_id=obligation.id if obligation else None" in payments_route
    assert "item.obligation_id" in payments_route
    assert "obligation.project_id if obligation" in agreements_route
    assert "customer_id: int | None = None" in agreements_route
    assert "\"contactability\"" in uploads_route
    assert "\"valid_until\"" in uploads_route
    assert "project_id=obligation.project_id if obligation" in telephony_route
    assert "project_id=call.project_id" in telephony_route


@pytest.mark.safe_static
def test_frontend_agreements_and_obligation_selectors_are_operational() -> None:
    app_js = read("frontend/static/assets/app.js")
    index_html = read("frontend/static/index.html")

    assert "agreements: []" in app_js
    assert "selectedDemographics" in app_js
    assert "selectedAgreements" in app_js
    assert "loadObligationsForForm" in app_js
    assert "renderAgreements()" in app_js
    assert "form.elements.obligation_id.value ? Number(form.elements.obligation_id.value) : null" in app_js
    assert "/api/crm/agreements" in app_js
    assert "/api/uploads/demographics" in app_js

    assert 'id="agreementForm"' in index_html
    assert 'id="agreementTable"' in index_html
    assert 'id="agreementInstallments"' in index_html
    assert 'name="obligation_id"' in index_html
    assert "Modulo en preparacion" not in index_html


@pytest.mark.safe_static
def test_seed_and_integration_readiness_stay_safe_and_idempotent() -> None:
    seed = read("backend/app/seeds/collects_core_demo.py")
    readiness_service = read("backend/app/services/integration_readiness.py")
    integrations_route = read("backend/app/api/routes/integrations.py")

    assert "SEED_MARKER" in seed
    assert "--confirm-test" in seed
    assert "--dry-run" in seed
    assert "db.rollback()" in seed
    assert "IpCom Demo TEST" in seed
    assert "real_credentials" in seed
    assert "settings.platform_tenant_slug" in seed
    assert "TenantModule" in seed
    assert "Module).where(Module.code == \"telephony\")" in seed
    assert "tenant_module.enabled = True" in seed
    assert "tenant_module.is_enabled = True" in seed
    assert "tenant_module.enabled_at = datetime.now(timezone.utc)" in seed
    assert "telephony_modules_active" in seed

    assert "PAYCONTROL_APP_PAGOS_ENABLED" in readiness_service
    assert "QAUDIT_360_ENABLED" in readiness_service
    assert "dependencies_required_now" in readiness_service
    assert "idempotency_key" in readiness_service
    assert "@router.post(\"/paycontrol/payments/dry-run\"" in integrations_route
    assert "@router.post(\"/qaudit/evaluations/dry-run\"" in integrations_route
    assert "No se llamo App Pagos" in integrations_route
    assert "No se llamo QAudit" in integrations_route


@pytest.mark.safe_static
def test_frontend_telephony_and_refresh_errors_do_not_look_like_logout() -> None:
    app_js = read("frontend/static/assets/app.js")

    assert "error.status = response.status" in app_js
    assert "error.transient = [502, 503, 504].includes(response.status)" in app_js
    assert "Servicio temporalmente no disponible. Reintenta en unos segundos." in app_js
    assert "if (error?.status === 401)" in app_js
    assert "logout();" in app_js
    assert "data-click-to-call-unavailable disabled" in app_js
    assert "Telefonia pendiente de configuracion" in app_js
    assert "normalized.includes(\"modulo no contratado\")" in app_js
    assert "normalized.includes(\"modulo inactivo\")" in app_js
