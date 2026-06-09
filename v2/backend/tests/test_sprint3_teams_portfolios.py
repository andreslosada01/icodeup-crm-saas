from __future__ import annotations

from typing import Any


def _first(items: list[dict[str, Any]], message: str) -> dict[str, Any]:
    assert items, message
    return items[0]


def test_admin_can_manage_project_user_assignments(client: Any, admin_headers: dict[str, str]) -> None:
    projects_response = client.get("/api/teams/projects", headers=admin_headers)
    assert projects_response.status_code == 200, projects_response.text
    project = _first(projects_response.json(), "Expected seeded demo projects.")

    agents_response = client.get("/api/teams/agents", headers=admin_headers)
    assert agents_response.status_code == 200, agents_response.text
    agent = _first(agents_response.json(), "Expected seeded demo agents.")

    assign_response = client.post(
        f"/api/teams/projects/{project['id']}/users",
        json={"user_id": agent["id"], "role_in_project": "agent", "is_active": True},
        headers=admin_headers,
    )
    assert assign_response.status_code in {200, 201}, assign_response.text
    payload = assign_response.json()
    assert payload["project_id"] == project["id"]
    assert payload["user_id"] == agent["id"]
    assert payload["role_in_project"] == "agent"
    assert payload["is_active"] is True


def test_admin_can_assign_agent_to_leader(client: Any, admin_headers: dict[str, str]) -> None:
    leaders = client.get("/api/teams/leaders", headers=admin_headers)
    assert leaders.status_code == 200, leaders.text
    leader = _first(leaders.json(), "Expected seeded leaders.")

    agents = client.get("/api/teams/agents", headers=admin_headers)
    assert agents.status_code == 200, agents.text
    agent = _first([item for item in agents.json() if item["id"] != leader["id"]], "Expected assignable agent.")

    response = client.post(
        f"/api/teams/leaders/{leader['id']}/agents",
        json={"agent_user_id": agent["id"]},
        headers=admin_headers,
    )
    assert response.status_code == 200, response.text
    assert response.json()["ok"] is True

    team_response = client.get(f"/api/teams/leaders/{leader['id']}/agents", headers=admin_headers)
    assert team_response.status_code == 200, team_response.text
    assert any(item["id"] == agent["id"] for item in team_response.json())


def test_leader_sees_team_scope_and_agent_cannot_administer(client: Any, leader_headers: dict[str, str], agent_headers: dict[str, str]) -> None:
    leader_projects = client.get("/api/teams/projects", headers=leader_headers)
    assert leader_projects.status_code == 200, leader_projects.text

    leader_dashboard = client.get("/api/teams/dashboard", headers=leader_headers)
    assert leader_dashboard.status_code == 200, leader_dashboard.text
    assert "total_agents" in leader_dashboard.json()

    agent_projects = client.get("/api/teams/projects", headers=agent_headers)
    assert agent_projects.status_code == 403, agent_projects.text


def test_agent_cannot_reassign_customers_or_obligations(client: Any, agent_headers: dict[str, str]) -> None:
    customers_response = client.get("/api/crm/customers?page_size=1", headers=agent_headers)
    assert customers_response.status_code == 200, customers_response.text
    customer = _first(customers_response.json().get("items", []), "Expected assigned customer for agent.")

    customer_assignment = client.patch(
        f"/api/crm/customers/{customer['id']}/assignment",
        json={"assigned_user_id": customer.get("assigned_user_id")},
        headers=agent_headers,
    )
    assert customer_assignment.status_code == 403, customer_assignment.text

    obligations_response = client.get(f"/api/crm/customers/{customer['id']}/obligations", headers=agent_headers)
    assert obligations_response.status_code == 200, obligations_response.text
    obligations = obligations_response.json()
    if obligations:
        obligation_assignment = client.patch(
            f"/api/crm/obligations/{obligations[0]['id']}/assignment",
            json={"assigned_user_id": obligations[0].get("assigned_user_id")},
            headers=agent_headers,
        )
        assert obligation_assignment.status_code == 403, obligation_assignment.text
