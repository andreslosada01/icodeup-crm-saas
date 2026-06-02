from __future__ import annotations


def test_configuration_visible_to_admin(client, admin_headers):
    response = client.get("/api/configuration/catalogs", headers=admin_headers)
    assert response.status_code == 200, response.text
    assert isinstance(response.json(), list)


def test_configuration_blocked_for_agent(client, agent_headers):
    response = client.get("/api/configuration/catalogs", headers=agent_headers)
    assert response.status_code == 403, response.text


def test_alerts_respect_authenticated_scope(client, admin_headers, agent_headers):
    admin_response = client.get("/api/alerts?limit=20", headers=admin_headers)
    agent_response = client.get("/api/alerts?assigned_to_me=true&limit=20", headers=agent_headers)
    assert admin_response.status_code == 200, admin_response.text
    assert agent_response.status_code == 200, agent_response.text
    assert isinstance(admin_response.json(), list)
    assert isinstance(agent_response.json(), list)


def test_legal_dashboard_and_kanban(client, lawyer_headers):
    dashboard = client.get("/api/legal/dashboard", headers=lawyer_headers)
    kanban = client.get("/api/legal/kanban", headers=lawyer_headers)
    assert dashboard.status_code == 200, dashboard.text
    assert kanban.status_code == 200, kanban.text
    assert "kpis" in dashboard.json()
    assert "columns" in kanban.json()


def test_sales_pipeline_and_kanban(client, sales_headers):
    dashboard = client.get("/api/sales/dashboard", headers=sales_headers)
    pipeline = client.get("/api/sales/pipeline", headers=sales_headers)
    kanban = client.get("/api/sales/kanban", headers=sales_headers)
    assert dashboard.status_code == 200, dashboard.text
    assert pipeline.status_code == 200, pipeline.text
    assert kanban.status_code == 200, kanban.text
    assert "kpis" in dashboard.json()
    assert "stages" in pipeline.json()
    assert "columns" in kanban.json()
