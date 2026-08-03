from __future__ import annotations

from importlib import import_module
from pathlib import Path

import pytest


BACKEND_ROOT = Path(__file__).resolve().parents[1]
V2_ROOT = BACKEND_ROOT.parent


def read(relative_path: str) -> str:
    return (V2_ROOT / relative_path).read_text(encoding="utf-8")


@pytest.mark.safe_static
def test_contact_compliance_backend_is_registered_and_uses_business_rules() -> None:
    route = read("backend/app/api/routes/compliance.py")
    service = read("backend/app/services/contact_compliance.py")
    main = read("backend/app/main.py")

    for snippet in [
        '@router.get("/contact-rules"',
        '@router.post("/contact-rules"',
        '@router.patch("/contact-rules/{rule_id}"',
        '@router.post("/contact-rules/{rule_id}/toggle"',
        '@router.post("/evaluate-contact"',
        '@router.get("/customer/{customer_id}/contact-status"',
    ]:
        assert snippet in route

    assert "app.include_router(compliance.router" in main
    assert 'CONTACT_RULE_TYPE = "contact_compliance"' in service
    assert 'CONTACT_RULE_MODULE = "collections"' in service
    assert "BusinessRule" in route
    assert "BusinessRule" in service
    assert "ManagementActivity" in service
    assert "max_attempts_per_day" in service
    assert "max_attempts_per_week" in service
    assert "record_audit" in service
    assert "Ley 2300" not in service


@pytest.mark.safe_static
def test_contact_compliance_permissions_menu_frontend_seed_and_docs() -> None:
    access = read("backend/app/services/access_control.py")
    bootstrap = read("backend/app/services/bootstrap_service.py")
    seed = read("backend/app/seeds/contact_compliance_demo.py")
    app_js = read("frontend/static/assets/app.js")
    index_html = read("frontend/static/index.html")
    docs = read("docs/CONTACT_COMPLIANCE_RULES_MVP.md")
    alerts = read("backend/app/services/alert_engine.py")

    for permission in ["contact_compliance.view", "contact_compliance.manage", "contact_compliance.evaluate"]:
        assert permission in access
        assert permission in bootstrap

    assert '("Cumplimiento y contacto", "contact-compliance", "collections", "contact_compliance.view", "company_admin"' in bootstrap
    assert '("Cumplimiento y contacto", "contact-compliance", "collections", "contact_compliance.view", "operational_leader"' in bootstrap
    assert '("Cumplimiento y contacto", "contact-compliance", "collections", "contact_compliance.view", "operational_user"' not in bootstrap
    assert '"contact-compliance": "Cumplimiento y contacto"' in app_js
    assert 'id="contact-compliance"' in index_html
    assert "/api/compliance/contact-rules" in app_js
    assert "/api/compliance/evaluate-contact" in app_js
    assert "/api/compliance/customer/" in app_js
    assert "renderContactStatusPanel" in app_js
    assert "data-contact-action" in app_js
    assert "contact_compliance_demo_seed" in seed
    assert "--confirm-test" in seed
    assert "_contact_compliance_alerts" in alerts
    assert "audit_logs" in docs


@pytest.mark.safe_static
def test_contact_compliance_runtime_imports_are_available() -> None:
    service = import_module("app.services.contact_compliance")
    route = import_module("app.api.routes.compliance")
    seed = import_module("app.seeds.contact_compliance_demo")
    main = import_module("app.main")

    assert service.CONTACT_RULE_TYPE == "contact_compliance"
    assert route.router is not None
    assert seed.SEED_MARKER == "iep_contact_compliance_demo_seed"
    assert any(item.path.startswith("/api/compliance") for item in main.app.routes)
