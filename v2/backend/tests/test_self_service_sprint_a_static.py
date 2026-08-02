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
