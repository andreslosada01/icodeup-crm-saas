from __future__ import annotations

import hashlib
from typing import Any

from app.schemas.collection_ops import PayControlPaymentSyncPreview, QAuditEvaluationPreview


PAYCONTROL_CONTRACT = {
    "integration": "paycontrol_360_app_pagos",
    "enabled": False,
    "mode": "dry_run",
    "required_feature_flag": "PAYCONTROL_APP_PAGOS_ENABLED",
    "contract_version": "2026-06-collections-core-v1",
    "dependencies_required_now": False,
    "tenant_isolated": True,
    "idempotency_keys": ["external_payment_id", "reference"],
    "required_fields": ["customer_document", "amount", "paid_at"],
    "optional_fields": ["tenant_id", "external_tenant_code", "project_id", "external_project_code", "obligation_number", "status", "reference", "support_url", "validation_status", "metadata"],
}

QAUDIT_CONTRACT = {
    "integration": "qaudit_360_quality",
    "enabled": False,
    "mode": "dry_run",
    "required_feature_flag": "QAUDIT_360_ENABLED",
    "contract_version": "2026-06-collections-core-v1",
    "dependencies_required_now": False,
    "tenant_isolated": True,
    "idempotency_keys": ["external_evaluation_id", "call_log_id", "activity_id"],
    "required_fields": ["score", "result", "evaluated_at"],
    "optional_fields": ["tenant_id", "user_id", "advisor_external_id", "call_log_id", "customer_id", "obligation_id", "activity_id", "findings", "evaluator", "metadata"],
}


def readiness_contracts() -> list[dict[str, Any]]:
    return [PAYCONTROL_CONTRACT, QAUDIT_CONTRACT]


def paycontrol_idempotency_key(tenant_id: int, payload: PayControlPaymentSyncPreview) -> str:
    key = payload.external_payment_id or payload.reference
    if key:
        return f"paycontrol:{tenant_id}:{key}"
    raw = f"{tenant_id}:{payload.customer_document}:{payload.obligation_number or ''}:{payload.amount}:{payload.paid_at.isoformat()}"
    return f"paycontrol:{tenant_id}:{hashlib.sha1(raw.encode('utf-8')).hexdigest()[:20]}"


def qaudit_idempotency_key(tenant_id: int, payload: QAuditEvaluationPreview) -> str:
    key = payload.external_evaluation_id or payload.call_log_id or payload.activity_id
    if key:
        return f"qaudit:{tenant_id}:{key}"
    raw = f"{tenant_id}:{payload.user_id or payload.advisor_external_id or ''}:{payload.customer_id or ''}:{payload.score}:{payload.evaluated_at.isoformat()}"
    return f"qaudit:{tenant_id}:{hashlib.sha1(raw.encode('utf-8')).hexdigest()[:20]}"
