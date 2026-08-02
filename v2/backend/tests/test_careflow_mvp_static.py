from __future__ import annotations

from pathlib import Path

import pytest


BACKEND_ROOT = Path(__file__).resolve().parents[1]
V2_ROOT = BACKEND_ROOT.parent


def read(relative_path: str) -> str:
    return (V2_ROOT / relative_path).read_text(encoding="utf-8")


@pytest.mark.safe_static
def test_careflow_backend_routes_models_and_activation_are_registered() -> None:
    route = read("backend/app/api/routes/careflow.py")
    models = read("backend/app/models/careflow.py")
    schemas = read("backend/app/schemas/careflow.py")
    main = read("backend/app/main.py")
    bootstrap = read("backend/app/services/bootstrap_service.py")
    subscriptions = read("backend/app/api/routes/subscriptions.py")
    migration = read("backend/alembic/versions/20260802_0008_careflow_360_mvp.py")

    for snippet in [
        '@router.get("/cases"',
        '@router.get("/cases/{case_id}"',
        '@router.post("/cases"',
        '@router.patch("/cases/{case_id}"',
        '@router.post("/cases/{case_id}/events"',
        '@router.post("/cases/{case_id}/assign"',
        '@router.post("/cases/{case_id}/close"',
        '@router.get("/summary"',
    ]:
        assert snippet in route

    assert 'CAREFLOW_MODULE = "careflow"' in route
    assert "CASE_PAGE_SIZE = 10" in route
    assert "le=CASE_PAGE_SIZE" in route
    assert "require_module(db, user, CAREFLOW_MODULE" in route
    assert "CareCase.assigned_user_id == user.id" in route
    assert "CareCase.created_by_id == user.id" in route
    assert "UserProjectAssignment.is_active.is_(True)" in route

    assert "class CareCase" in models
    assert "class CareCaseEvent" in models
    assert "class CareCaseCategory" in models
    assert "CareCaseListResponse" in schemas
    assert "app.include_router(careflow.router" in main
    assert '("careflow", "CareFlow 360"' in bootstrap
    assert '"careflow"' in subscriptions
    assert "CREATE TABLE IF NOT EXISTS care_cases" in migration
    assert "CREATE TABLE IF NOT EXISTS care_case_events" in migration


@pytest.mark.safe_static
def test_careflow_permissions_menu_seed_frontend_and_docs_are_in_place() -> None:
    access = read("backend/app/services/access_control.py")
    bootstrap = read("backend/app/services/bootstrap_service.py")
    seed = read("backend/app/seeds/careflow_demo.py")
    app_js = read("frontend/static/assets/app.js")
    index_html = read("frontend/static/index.html")
    docs = read("docs/CAREFLOW_360_MVP.md")
    self_service = read("backend/app/services/collections_self_service.py")
    alerts = read("backend/app/services/alert_engine.py")

    for permission in [
        "careflow.view",
        "careflow.create",
        "careflow.update",
        "careflow.assign",
        "careflow.close",
        "careflow.events.create",
        "careflow.configure",
        "careflow.reports.view",
    ]:
        assert permission in access
        assert permission in bootstrap

    assert '("CareFlow 360", "careflow", "careflow", "careflow.view", "company_admin"' in bootstrap
    assert '("Configuracion CareFlow", "careflow-config", "careflow", "careflow.configure", "company_admin"' in bootstrap
    assert '("Mis casos", "careflow", "careflow", "careflow.view", "operational_user"' in bootstrap
    assert '("Crear caso", "careflow-new", "careflow", "careflow.create", "operational_user"' in bootstrap
    assert '"careflow-config"' in app_js
    assert "careflowCanConfigure" in app_js
    assert 'id="careflow"' in index_html
    assert "/api/careflow/cases" in app_js
    assert "/api/careflow/summary" in app_js
    assert "data-careflow-open" in app_js

    assert "--confirm-test" in seed
    assert "DEFAULT_TENANT_SLUG" in seed
    assert "_activate_module" in seed
    assert "tenant_module.enabled = True" in seed
    assert "CF-DEMO-001" in seed
    assert "No borra datos" not in seed

    assert "_append_careflow_priorities" in self_service
    assert "_careflow_module_active" in self_service
    assert '"careflow"' in alerts
    assert "CareFlow se agrega a `Prioridades de hoy`" in docs
    assert "page_size` maximo 10" in docs
