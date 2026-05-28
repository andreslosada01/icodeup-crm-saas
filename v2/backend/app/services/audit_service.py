from __future__ import annotations

import json
from typing import Any

from fastapi import Request
from sqlalchemy.orm import Session

from app.models import AuditLog, User


def _json_or_none(value: Any) -> str | None:
    if value is None:
        return None
    return json.dumps(value, default=str, ensure_ascii=True)


def record_audit(
    db: Session,
    user: User | None,
    entity_type: str,
    action: str,
    entity_id: int | None = None,
    tenant_id: int | None = None,
    module: str | None = None,
    object_type: str | None = None,
    object_id: int | None = None,
    before: Any | None = None,
    after: Any | None = None,
    request: Request | None = None,
) -> AuditLog:
    before_value = _json_or_none(before)
    after_value = _json_or_none(after)
    log = AuditLog(
        tenant_id=tenant_id if tenant_id is not None else user.tenant_id if user else None,
        user_id=user.id if user else None,
        module=module,
        object_type=object_type or entity_type,
        object_id=object_id if object_id is not None else entity_id,
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        old_value=before_value,
        new_value=after_value,
        before_json=before_value,
        after_json=after_value,
        ip_address=request.client.host if request and request.client else None,
        user_agent=request.headers.get("user-agent") if request else None,
    )
    db.add(log)
    return log
