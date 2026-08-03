from __future__ import annotations

from importlib import import_module
from pathlib import Path

import pytest


BACKEND_ROOT = Path(__file__).resolve().parents[1]
V2_ROOT = BACKEND_ROOT.parent


def read(relative_path: str) -> str:
    return (V2_ROOT / relative_path).read_text(encoding="utf-8")


@pytest.mark.safe_static
def test_operational_reports_routes_are_registered_and_paginated() -> None:
    route = read("backend/app/api/routes/reports.py")
    service = read("backend/app/services/operational_reports.py")
    schemas = read("backend/app/schemas/reports.py")
    main = read("backend/app/main.py")

    for snippet in [
        '@router.get("/operational/clients"',
        '@router.get("/operational/activities"',
        '@router.get("/operational/promises"',
        '@router.get("/operational/payments"',
        '@router.get("/operational/agreements"',
        '@router.get("/operational/productivity-hourly"',
        '@router.get("/operational/productivity-advisor"',
        '@router.get("/operational/demographics"',
        '@router.get("/operational/tasks"',
        '@router.get("/operational/careflow"',
        '@router.get("/operational/{report_code}/export"',
    ]:
        assert snippet in route

    assert "app.include_router(reports.router" in main
    assert "REPORT_PAGE_SIZE = 10" in service
    assert "le=REPORT_PAGE_SIZE" in route
    assert "OperationalReportResponse" in schemas
    assert "OperationalReportsMeta" in schemas


@pytest.mark.safe_static
def test_operational_reports_enforce_scope_roles_and_modules() -> None:
    service = read("backend/app/services/operational_reports.py")
    bootstrap = read("backend/app/services/bootstrap_service.py")
    access = read("backend/app/services/access_control.py")

    assert 'require_permission(db, user, "reports.view")' in service
    assert 'require_module(db, user, "bi"' in service
    assert 'user.role == AGENT' in service
    assert "Los reportes operativos completos no estan disponibles para agentes" in service
    assert "Customer.tenant_id == user.tenant_id" in service
    assert "Customer.tenant_id == filters.tenant_id" in service
    assert "ManagementActivity.tenant_id.in_" in service
    assert "PaymentPromise.tenant_id.in_" in service
    assert "Payment.tenant_id.in_" in service
    assert "PaymentAgreement.tenant_id.in_" in service
    assert "CustomerDemographic.tenant_id.in_" in service
    assert "UserProjectAssignment.is_active.is_(True)" in service
    assert 'UserProjectAssignment.role_in_project == "agent"' in service
    assert "advisor.role != AGENT" in service
    assert "user_has_module(db, user, \"careflow\"" in service
    assert "CareFlow 360 no esta activo" in service

    assert '("Reportes operativos", "reports", "bi", "reports.view", "platform_admin"' in bootstrap
    assert '("Reportes operativos", "reports", "bi", "reports.view", "company_admin"' in bootstrap
    assert '("Reportes operativos", "reports", "bi", "reports.view", "operational_leader"' in bootstrap
    assert '("Reportes operativos", "reports", "bi", "reports.view", "operational_user"' not in bootstrap
    assert '"reports.view"' not in access.split("AGENT: {", 1)[1].split("}", 1)[0]


@pytest.mark.safe_static
def test_operational_reports_frontend_and_docs_are_in_place() -> None:
    app_js = read("frontend/static/assets/app.js")
    index_html = read("frontend/static/index.html")
    styles = read("frontend/static/assets/styles.css")
    docs = read("docs/REPORTES_OPERATIVOS_IEP_COLLECTS_360.md")

    assert 'reports: { meta: null, active: "clients"' in app_js
    assert "/api/reports/operational/meta" in app_js
    assert "/api/reports/operational/${active}" in app_js
    assert "/api/reports/operational/${state.reports.active}/export" in app_js
    assert "renderOperationalReports" in app_js
    assert "operationalReportParams" in app_js
    assert "data-operational-report-tab" in app_js
    assert "page_size: DEFAULT_TABLE_PAGE_SIZE" in app_js
    assert "CareFlow" in app_js

    assert 'id="operationalReportFilters"' in index_html
    assert 'id="operationalReportTabs"' in index_html
    assert 'id="operationalReportTable"' in index_html
    assert 'id="exportOperationalReport"' in index_html
    assert ".operational-reports-hero" in styles
    assert ".report-tabs" in styles

    assert "GET /api/reports/operational/clients" in docs
    assert "agent` / `collections_agent`: no ve el centro completo" in docs
    assert "`page_size` esta limitado a maximo 10" in docs
    assert "CareFlow se muestra solo si el modulo esta activo" in docs


@pytest.mark.safe_static
def test_operational_reports_runtime_imports_are_available() -> None:
    route = import_module("app.api.routes.reports")
    service = import_module("app.services.operational_reports")
    main = import_module("app.main")

    assert route.router is not None
    assert service.REPORT_PAGE_SIZE == 10
    assert "clients" in service.REPORT_LABELS
    assert any(item.path.startswith("/api/reports/operational") for item in main.app.routes)
