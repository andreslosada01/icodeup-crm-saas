from __future__ import annotations

from pathlib import Path

import pytest


BACKEND_ROOT = Path(__file__).resolve().parents[1]
V2_ROOT = BACKEND_ROOT.parent


def read(relative_path: str) -> str:
    return (V2_ROOT / relative_path).read_text(encoding="utf-8")


@pytest.mark.safe_static
def test_self_service_reuses_existing_tables_and_routes() -> None:
    service = read("backend/app/services/collections_self_service.py")
    teams_route = read("backend/app/api/routes/teams.py")
    alerts_route = read("backend/app/api/routes/alerts.py")
    activities_route = read("backend/app/api/routes/crm/activities.py")

    for model_name in [
        "UserProjectAssignment",
        "ManagementActivity",
        "PaymentPromise",
        "Payment",
        "PaymentAgreement",
        "CustomerObligation",
        "BusinessRule",
        "AlertRule",
    ]:
        assert model_name in service

    assert '@router.get("/operational-center"' in teams_route
    assert '@router.get("/users/{user_id}/projects"' in teams_route
    assert '@router.get("/session-summary"' in alerts_route
    assert '@router.get("/customers/{customer_id}/management-insights"' in activities_route
    assert '@router.get("/users/{user_id}/management-insights"' in activities_route
    assert "limit(TEAM_PAGE_SIZE)" in teams_route
    assert "PRIORITY_LIMIT = 10" in service


@pytest.mark.safe_static
def test_frontend_self_service_panels_are_optional_and_visible() -> None:
    app_js = read("frontend/static/assets/app.js")
    index_html = read("frontend/static/index.html")
    styles = read("frontend/static/assets/styles.css")

    assert "sessionSummary" in app_js
    assert "/api/alerts/session-summary" in app_js
    assert "renderSessionPriorities" in app_js
    assert "data-close-session-priorities" in app_js
    assert "/api/teams/operational-center" in app_js
    assert "renderOperationalCenter" in app_js
    assert "data-project-user-role" in app_js
    assert "/api/crm/customers/${customer.id}/management-insights" in app_js
    assert "renderManagementInsightsMini" in app_js

    assert 'id="sessionPriorities"' in index_html
    assert 'id="operationalCenterPanel"' in index_html
    assert ".session-priorities" in styles
    assert ".operational-center" in styles
    assert ".score-chip" in styles


@pytest.mark.safe_static
def test_qa_hardens_operational_roles_dashboard_and_scoring_defaults() -> None:
    app_js = read("frontend/static/assets/app.js")
    index_html = read("frontend/static/index.html")
    teams_schema = read("backend/app/schemas/teams.py")
    teams_route = read("backend/app/api/routes/teams.py")
    self_service = read("backend/app/services/collections_self_service.py")
    bootstrap = read("backend/app/services/bootstrap_service.py")
    seed = read("backend/app/seeds/collects_core_demo.py")
    scale_seed = read("backend/app/seeds/scale_demo.py")
    repository = read("backend/app/repositories/administration_repository.py")

    assert "visibleMenuItemsForCurrentRole" in app_js
    assert 'audience !== "operational_user"' in app_js
    assert 'new Set(["documents", "telephony", "excel-web"])' in app_js
    assert 'audience === "operational_user"' in app_js
    assert 'document.querySelector("#experienceModules")' in app_js
    assert 'value="coordinator"' in index_html
    assert 'value="quality_supervisor"' in index_html

    assert '"coordinator"' in teams_schema
    assert '"quality_supervisor"' in teams_schema
    assert '"admin"' in teams_schema
    assert 'role_in_project.in_(["leader", "coordinator"])' in teams_route
    assert "_require_teams_module" in teams_route
    assert 'user_has_module(db, user, "administration") or user_has_module(db, user, "collections")' in teams_route

    assert 'SCORING_RULE_TYPES = {"management_scoring", "activity_scoring", "scoring"}' in self_service
    for code in [
        "SCORING_EFFECTIVE_CONTACT",
        "SCORING_PROMISE_CREATED",
        "SCORING_PAYMENT_REPORTED",
        "SCORING_AGREEMENT_CREATED",
        "SCORING_LEGAL_ESCALATION",
        "SCORING_NO_ANSWER",
        "SCORING_WRONG_NUMBER",
        "SCORING_CLIENT_WITHOUT_CONTACT",
        "SCORING_SUPPORT_UPLOADED",
    ]:
        assert code in bootstrap
        assert code in seed

    assert "project_role_for_user" in repository
    assert 'user.role == "coordinator"' in repository
    assert 'role_in_project=role_in_project' in repository
    assert "_ensure_project_assignments" in seed
    assert "_ensure_scoring_rules" in seed
    assert "project_role_for_user" in scale_seed
    assert "exists.role_in_project = role_in_project" in scale_seed


@pytest.mark.safe_static
def test_a2_prevents_demo_cross_portfolio_assignments_and_duplicate_scoring() -> None:
    seed = read("backend/app/seeds/collects_core_demo.py")
    scale_seed = read("backend/app/seeds/scale_demo.py")
    self_service = read("backend/app/services/collections_self_service.py")
    teams_route = read("backend/app/api/routes/teams.py")
    dashboard_service = read("backend/app/services/dashboard_service.py")
    bi_route = read("backend/app/api/routes/crm/bi.py")
    docs = read("docs/AUTOGESTION_EMPRESA_CARTERAS_ALERTAS_SCORING.md")

    assert "_project_scope_for_user" in seed
    assert 'email.endswith("@demo.icodeup.local")' in seed
    assert "assignment.is_active = False" in seed
    assert "assignments_cross_deactivated" in seed
    assert "compact(project.code) in local_email" in scale_seed
    assert "assignment.is_active = False" in scale_seed

    assert "prioritized.setdefault(item.code, item)" in self_service
    assert "rule.tenant_id == tenant_id" in self_service
    assert "tenant > global fallback" in docs

    assert 'role_in_project == "agent"' in teams_route
    assert "User.role == AGENT" in teams_route
    assert "User.role == AGENT" in dashboard_service
    assert 'User.role == "agent"' in bi_route
