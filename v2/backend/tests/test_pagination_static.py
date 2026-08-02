from __future__ import annotations

from pathlib import Path

import pytest


BACKEND_ROOT = Path(__file__).resolve().parents[1]
V2_ROOT = BACKEND_ROOT.parent


@pytest.mark.safe_static
def test_frontend_global_tables_default_and_cap_at_ten_rows() -> None:
    app_js = V2_ROOT / "frontend" / "static" / "assets" / "app.js"
    content = app_js.read_text(encoding="utf-8")

    assert "const DEFAULT_TABLE_PAGE_SIZE = 10;" in content
    assert "const MAX_TABLE_PAGE_SIZE = 10;" in content
    assert "MAX_TABLE_PAGE_SIZE" in content

    forbidden_snippets = [
        "pageSize: 20",
        "page_size: 20",
        "page_size=20",
        "20 por pagina",
        'value="20"',
        "limit: 50",
    ]
    for snippet in forbidden_snippets:
        assert snippet not in content


@pytest.mark.safe_static
def test_visible_backend_list_endpoints_cap_pagination_at_ten() -> None:
    files = [
        "app/api/routes/administration.py",
        "app/api/routes/alerts.py",
        "app/api/routes/documents.py",
        "app/api/routes/excel_web.py",
        "app/api/routes/governance.py",
        "app/api/routes/integrations.py",
        "app/api/routes/legal.py",
        "app/api/routes/recordings.py",
        "app/api/routes/sales.py",
        "app/api/routes/teams.py",
        "app/api/routes/telephony.py",
        "app/api/routes/uploads.py",
        "app/api/routes/crm/agreements.py",
        "app/api/routes/crm/obligations.py",
        "app/api/routes/crm/payments.py",
        "app/api/routes/crm/promises.py",
        "app/schemas/collection_ops.py",
    ]

    for relative_path in files:
        content = (BACKEND_ROOT / relative_path).read_text(encoding="utf-8")
        assert "Query(default=20" not in content
        assert "le=20" not in content
        assert "page_size: int = 20" not in content
        assert "page_size = min(max(page_size, 1), 20)" not in content
        assert "EXCEL_PAGE_SIZE = 20" not in content
        assert "TEAM_PAGE_SIZE = 20" not in content
