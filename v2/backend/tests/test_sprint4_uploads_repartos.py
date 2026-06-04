from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def _first(items: list[dict[str, Any]], message: str) -> dict[str, Any]:
    assert items, message
    return items[0]


def _demo_context(client: Any, headers: dict[str, str]) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    projects = client.get("/api/teams/projects", headers=headers)
    assert projects.status_code == 200, projects.text
    project = _first(projects.json(), "Expected seeded projects.")

    agents = client.get("/api/teams/agents", headers=headers)
    assert agents.status_code == 200, agents.text
    agent = _first(agents.json(), "Expected seeded agents.")

    leaders = client.get("/api/teams/leaders", headers=headers)
    assert leaders.status_code == 200, leaders.text
    leader = _first(leaders.json(), "Expected seeded leaders.")
    return project, agent, leader


def test_admin_can_preview_confirm_reparto_and_download_result(client: Any, admin_headers: dict[str, str]) -> None:
    project, agent, leader = _demo_context(client, admin_headers)
    suffix = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    csv_text = "\n".join(
        [
            "documento,cliente,numero_obligacion,saldo_actual,dias_mora,gestor_email,lider_email,codigo_cartera",
            f"90099{suffix},Cliente Sprint 4,{suffix}-OBL,3500000,37,{agent['email']},{leader['email']},{project['code']}",
        ]
    )
    payload = {
        "project_id": project["id"],
        "upload_type": "reparto_cartera",
        "file_name": f"reparto_sprint4_{suffix}.csv",
        "csv_text": csv_text,
        "mapping": {},
        "create_records": True,
    }

    preview = client.post("/api/uploads/preview", json=payload, headers=admin_headers)
    assert preview.status_code == 200, preview.text
    preview_json = preview.json()
    assert preview_json["valid_rows"] == 1
    assert preview_json["suggested_mapping"]["document"] == "documento"

    confirm = client.post("/api/uploads/confirm", json=payload, headers=admin_headers)
    assert confirm.status_code == 201, confirm.text
    batch = confirm.json()
    assert batch["total_rows"] == 1
    assert batch["created_rows"] >= 1

    result = client.get(f"/api/uploads/batches/{batch['id']}/result", headers=admin_headers)
    assert result.status_code == 200, result.text
    assert "csv_text" in result.json()


def test_admin_can_load_demographics_for_existing_customer(client: Any, admin_headers: dict[str, str]) -> None:
    project, agent, leader = _demo_context(client, admin_headers)
    suffix = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")
    document = f"90188{suffix}"
    reparto = "\n".join(
        [
            "documento,cliente,numero_obligacion,saldo_actual,dias_mora,gestor_email,lider_email,codigo_cartera",
            f"{document},Cliente Demo Demografico,{suffix}-DEM,1800000,22,{agent['email']},{leader['email']},{project['code']}",
        ]
    )
    create_response = client.post(
        "/api/uploads/confirm",
        json={"project_id": project["id"], "upload_type": "reparto_cartera", "file_name": f"base_demo_{suffix}.csv", "csv_text": reparto, "mapping": {}, "create_records": True},
        headers=admin_headers,
    )
    assert create_response.status_code == 201, create_response.text

    demographics = "\n".join(
        [
            "documento,telefono,email,direccion,ciudad,fuente,score",
            f"{document},3000000999,cliente.sprint4@demo.local,Calle 4 Demo,Bogota,buro_demo,91",
        ]
    )
    payload = {"project_id": project["id"], "upload_type": "demograficos", "file_name": f"demograficos_{suffix}.csv", "csv_text": demographics, "mapping": {}, "create_records": True}

    preview = client.post("/api/uploads/preview", json=payload, headers=admin_headers)
    assert preview.status_code == 200, preview.text
    assert preview.json()["error_rows"] == 0

    confirm = client.post("/api/uploads/confirm", json=payload, headers=admin_headers)
    assert confirm.status_code == 201, confirm.text
    assert confirm.json()["created_rows"] >= 1


def test_agent_cannot_preview_or_confirm_general_uploads(client: Any, agent_headers: dict[str, str]) -> None:
    payload = {
        "upload_type": "reparto_cartera",
        "file_name": "reparto_bloqueado.csv",
        "csv_text": "documento,cliente\n900000000,Cliente Bloqueado",
        "mapping": {},
        "create_records": False,
    }
    preview = client.post("/api/uploads/preview", json=payload, headers=agent_headers)
    assert preview.status_code == 403, preview.text

    confirm = client.post("/api/uploads/confirm", json=payload, headers=agent_headers)
    assert confirm.status_code == 403, confirm.text


def test_upload_templates_are_available_for_authorized_user(client: Any, admin_headers: dict[str, str]) -> None:
    response = client.get("/api/uploads/templates/clientes", headers=admin_headers)
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["filename"].endswith(".csv")
    assert "documento" in payload["csv_text"]
