from __future__ import annotations

import json
from typing import Any

from fastapi import Request
from sqlalchemy.orm import Session

from app.models import AuditLog, User


SENSITIVE_KEYS = {
    "authorization",
    "access_token",
    "refresh_token",
    "token",
    "secret",
    "secret_key",
    "password",
    "password_hash",
    "api_key",
    "private_key",
    "config_json",
    "configuration_json",
    "csv_text",
    "file_content",
}


def safe_audit_payload(value: Any, depth: int = 0) -> Any:
    if value is None:
        return None
    if depth > 4:
        return "[truncated]"
    if isinstance(value, dict):
        clean: dict[str, Any] = {}
        for key, item in value.items():
            key_text = str(key)
            key_normalized = key_text.lower()
            if key_normalized in SENSITIVE_KEYS or "password" in key_normalized or "token" in key_normalized or "secret" in key_normalized:
                clean[key_text] = "[redacted]"
            else:
                clean[key_text] = safe_audit_payload(item, depth + 1)
        return clean
    if isinstance(value, (list, tuple, set)):
        return [safe_audit_payload(item, depth + 1) for item in list(value)[:100]]
    if isinstance(value, str) and len(value) > 1000:
        return f"{value[:1000]}...[truncated]"
    return value


def _json_or_none(value: Any) -> str | None:
    if value is None:
        return None
    return json.dumps(safe_audit_payload(value), default=str, ensure_ascii=True)


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
