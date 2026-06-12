from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.api.deps import current_user
from app.api.routes.crm.access import customer_for_access
from app.api.routes.crm.obligations import obligation_for_access
from app.core.roles import AGENT, COORDINATOR, TENANT_ADMIN
from app.db.session import get_db
from app.models import CallLog, Customer, CustomerObligation, ManagementActivity, TelephonyExtension, TelephonyProvider, User
from app.schemas.telephony import (
    CallLogOut,
    ClickToCallRequest,
    ClickToCallResponse,
    FinishCallLogRequest,
    TelephonyExtensionCreate,
    TelephonyExtensionOut,
    TelephonyExtensionPatch,
    TelephonyProviderCreate,
    TelephonyProviderOut,
    TelephonyProviderPatch,
)
from app.services.access_control import get_profile_role_code, is_company_admin, is_platform_admin, require_module, require_permission, require_tenant, user_has_permission
from app.services.audit_service import record_audit


router = APIRouter()

SENSITIVE_CONFIG_FRAGMENTS = ("password", "secret", "token", "api_key", "private_key", "credential")


def _json(value: str | None) -> dict[str, Any]:
    return json.loads(value or "{}")


def _assert_safe_config(value: Any, path: str = "config") -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            lowered = str(key).lower()
            if any(fragment in lowered for fragment in SENSITIVE_CONFIG_FRAGMENTS):
                raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"No guardes credenciales sensibles en {path}.{key}. Usa un vault en una fase posterior.")
            _assert_safe_config(item, f"{path}.{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _assert_safe_config(item, f"{path}[{index}]")


def _tenant_id_for_payload(db: Session, user: User, tenant_id: int | None = None) -> int:
    require_module(db, user, "telephony", tenant_id)
    return require_tenant(db, user, tenant_id).id


def _require_manage(db: Session, user: User) -> None:
    require_permission(db, user, "telephony.manage")


def _require_extension_manage(db: Session, user: User) -> None:
    if not user_has_permission(db, user, "telephony.extensions.manage"):
        require_permission(db, user, "telephony.manage")


def _provider_for_access(db: Session, provider_id: int, user: User) -> TelephonyProvider:
    provider = db.get(TelephonyProvider, provider_id)
    if provider is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Proveedor de telefonia no encontrado.")
    if not is_platform_admin(db, user) and provider.tenant_id != user.tenant_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Proveedor fuera de tu empresa.")
    return provider


def _extension_for_access(db: Session, extension_id: int, user: User) -> TelephonyExtension:
    extension = db.get(TelephonyExtension, extension_id)
    if extension is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Extension no encontrada.")
    if not is_platform_admin(db, user) and extension.tenant_id != user.tenant_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Extension fuera de tu empresa.")
    return extension


def _validate_user_in_tenant(db: Session, tenant_id: int, user_id: int) -> User:
    target = db.get(User, user_id)
    if target is None or target.tenant_id != tenant_id:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="El usuario de la extension no pertenece a la empresa.")
    return target


def _validate_provider_in_tenant(db: Session, tenant_id: int, provider_id: int | None) -> TelephonyProvider | None:
    if provider_id is None:
        return None
    provider = db.get(TelephonyProvider, provider_id)
    if provider is None or provider.tenant_id != tenant_id:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="El proveedor no pertenece a la empresa.")
    return provider


def _extension_query(db: Session, user: User, tenant_id: int | None = None):
    query = select(TelephonyExtension).order_by(TelephonyExtension.extension_number)
    if is_platform_admin(db, user):
        if tenant_id:
            query = query.where(TelephonyExtension.tenant_id == tenant_id)
        return query
    query = query.where(TelephonyExtension.tenant_id == user.tenant_id)
    if not (is_company_admin(db, user) or user_has_permission(db, user, "telephony.extensions.manage")):
        query = query.where(TelephonyExtension.user_id == user.id)
    return query


def _team_user_ids(db: Session, user: User) -> list[int]:
    ids = [user.id]
    ids.extend(db.scalars(select(User.id).where(User.tenant_id == user.tenant_id, User.leader_id == user.id)))
    return list(dict.fromkeys(ids))


def _call_log_query(db: Session, user: User, tenant_id: int | None = None):
    query = select(CallLog).order_by(CallLog.started_at.desc(), CallLog.id.desc())
    if is_platform_admin(db, user):
        if tenant_id:
            query = query.where(CallLog.tenant_id == tenant_id)
        return query
    query = query.where(CallLog.tenant_id == user.tenant_id)
    profile_role = get_profile_role_code(db, user)
    if is_company_admin(db, user) or user_has_permission(db, user, "telephony.manage"):
        return query
    if user.role == COORDINATOR or profile_role == "collections_leader":
        return query.where(CallLog.user_id.in_(_team_user_ids(db, user)))
    return query.where(CallLog.user_id == user.id)


def _provider_to_out(item: TelephonyProvider) -> TelephonyProviderOut:
    return TelephonyProviderOut(
        id=item.id,
        tenant_id=item.tenant_id,
        name=item.name,
        provider_type=item.provider_type,
        host=item.host,
        port=item.port,
        websocket_url=item.websocket_url,
        api_url=item.api_url,
        is_active=item.is_active,
        config=_json(item.config_json),
        created_at=item.created_at,
        updated_at=item.updated_at,
    )


def _extension_to_out(db: Session, item: TelephonyExtension) -> TelephonyExtensionOut:
    target = db.get(User, item.user_id)
    provider = db.get(TelephonyProvider, item.provider_id) if item.provider_id else None
    return TelephonyExtensionOut(
        id=item.id,
        tenant_id=item.tenant_id,
        user_id=item.user_id,
        user_name=target.name if target else None,
        provider_id=item.provider_id,
        provider_name=provider.name if provider else None,
        extension_number=item.extension_number,
        display_name=item.display_name,
        sip_username=item.sip_username,
        sip_domain=item.sip_domain,
        status=item.status,
        is_active=item.is_active,
        metadata=_json(item.metadata_json),
        created_at=item.created_at,
        updated_at=item.updated_at,
    )


def _call_log_to_out(db: Session, item: CallLog) -> CallLogOut:
    provider = db.get(TelephonyProvider, item.provider_id) if item.provider_id else None
    user = db.get(User, item.user_id)
    customer = db.get(Customer, item.customer_id) if item.customer_id else None
    obligation = db.get(CustomerObligation, item.obligation_id) if item.obligation_id else None
    return CallLogOut(
        id=item.id,
        tenant_id=item.tenant_id,
        provider_id=item.provider_id,
        provider_name=provider.name if provider else None,
        user_id=item.user_id,
        user_name=user.name if user else None,
        customer_id=item.customer_id,
        customer_name=customer.name if customer else None,
        obligation_id=item.obligation_id,
        obligation_number=obligation.obligation_number if obligation else None,
        phone_number=item.phone_number,
        direction=item.direction,
        call_status=item.call_status,
        started_at=item.started_at,
        answered_at=item.answered_at,
        ended_at=item.ended_at,
        duration_seconds=item.duration_seconds,
        external_call_id=item.external_call_id,
        recording_url=item.recording_url,
        management_activity_id=item.management_activity_id,
        metadata=_json(item.metadata_json),
    )


@router.get("/providers", response_model=list[TelephonyProviderOut])
def list_providers(tenant_id: int | None = None, db: Session = Depends(get_db), user: User = Depends(current_user)) -> list[TelephonyProviderOut]:
    require_module(db, user, "telephony", tenant_id)
    require_permission(db, user, "telephony.view")
    query = select(TelephonyProvider).order_by(TelephonyProvider.name)
    if is_platform_admin(db, user):
        if tenant_id:
            query = query.where(TelephonyProvider.tenant_id == tenant_id)
    else:
        query = query.where(TelephonyProvider.tenant_id == user.tenant_id)
    return [_provider_to_out(item) for item in db.scalars(query)]


@router.post("/providers", response_model=TelephonyProviderOut, status_code=status.HTTP_201_CREATED)
def create_provider(payload: TelephonyProviderCreate, request: Request, db: Session = Depends(get_db), user: User = Depends(current_user)) -> TelephonyProviderOut:
    _require_manage(db, user)
    tenant_id = _tenant_id_for_payload(db, user, payload.tenant_id)
    _assert_safe_config(payload.config)
    item = TelephonyProvider(
        tenant_id=tenant_id,
        name=payload.name.strip(),
        provider_type=payload.provider_type,
        host=payload.host,
        port=payload.port,
        websocket_url=payload.websocket_url,
        api_url=payload.api_url,
        is_active=payload.is_active,
        config_json=json.dumps(payload.config, ensure_ascii=True),
    )
    db.add(item)
    db.flush()
    record_audit(db, user, "telephony_provider", "create", item.id, tenant_id, module="telephony", after={"name": item.name, "provider_type": item.provider_type}, request=request)
    db.commit()
    db.refresh(item)
    return _provider_to_out(item)


@router.patch("/providers/{provider_id}", response_model=TelephonyProviderOut)
def update_provider(provider_id: int, payload: TelephonyProviderPatch, request: Request, db: Session = Depends(get_db), user: User = Depends(current_user)) -> TelephonyProviderOut:
    _require_manage(db, user)
    item = _provider_for_access(db, provider_id, user)
    require_module(db, user, "telephony", item.tenant_id)
    updates = payload.model_dump(exclude_unset=True)
    if "config" in updates and updates["config"] is not None:
        _assert_safe_config(updates["config"])
        item.config_json = json.dumps(updates.pop("config"), ensure_ascii=True)
    for field, value in updates.items():
        setattr(item, field, value.strip() if isinstance(value, str) else value)
    record_audit(db, user, "telephony_provider", "update", item.id, item.tenant_id, module="telephony", after=payload.model_dump(exclude_unset=True), request=request)
    db.commit()
    db.refresh(item)
    return _provider_to_out(item)


@router.get("/extensions", response_model=list[TelephonyExtensionOut])
def list_extensions(tenant_id: int | None = None, db: Session = Depends(get_db), user: User = Depends(current_user)) -> list[TelephonyExtensionOut]:
    require_module(db, user, "telephony", tenant_id)
    require_permission(db, user, "telephony.view")
    return [_extension_to_out(db, item) for item in db.scalars(_extension_query(db, user, tenant_id))]


@router.post("/extensions", response_model=TelephonyExtensionOut, status_code=status.HTTP_201_CREATED)
def create_extension(payload: TelephonyExtensionCreate, request: Request, db: Session = Depends(get_db), user: User = Depends(current_user)) -> TelephonyExtensionOut:
    _require_extension_manage(db, user)
    tenant_id = _tenant_id_for_payload(db, user, payload.tenant_id)
    _assert_safe_config(payload.metadata, "metadata")
    _validate_user_in_tenant(db, tenant_id, payload.user_id)
    _validate_provider_in_tenant(db, tenant_id, payload.provider_id)
    item = TelephonyExtension(
        tenant_id=tenant_id,
        user_id=payload.user_id,
        provider_id=payload.provider_id,
        extension_number=payload.extension_number.strip(),
        display_name=payload.display_name,
        sip_username=payload.sip_username,
        sip_domain=payload.sip_domain,
        status=payload.status,
        is_active=payload.is_active,
        metadata_json=json.dumps(payload.metadata, ensure_ascii=True),
    )
    db.add(item)
    db.flush()
    record_audit(db, user, "telephony_extension", "create", item.id, tenant_id, module="telephony", after={"user_id": item.user_id, "extension_number": item.extension_number}, request=request)
    db.commit()
    db.refresh(item)
    return _extension_to_out(db, item)


@router.patch("/extensions/{extension_id}", response_model=TelephonyExtensionOut)
def update_extension(extension_id: int, payload: TelephonyExtensionPatch, request: Request, db: Session = Depends(get_db), user: User = Depends(current_user)) -> TelephonyExtensionOut:
    _require_extension_manage(db, user)
    item = _extension_for_access(db, extension_id, user)
    require_module(db, user, "telephony", item.tenant_id)
    updates = payload.model_dump(exclude_unset=True)
    if "user_id" in updates and updates["user_id"] is not None:
        _validate_user_in_tenant(db, item.tenant_id, updates["user_id"])
    if "provider_id" in updates:
        _validate_provider_in_tenant(db, item.tenant_id, updates["provider_id"])
    if "metadata" in updates and updates["metadata"] is not None:
        _assert_safe_config(updates["metadata"], "metadata")
        item.metadata_json = json.dumps(updates.pop("metadata"), ensure_ascii=True)
    for field, value in updates.items():
        setattr(item, field, value.strip() if isinstance(value, str) else value)
    record_audit(db, user, "telephony_extension", "update", item.id, item.tenant_id, module="telephony", after=payload.model_dump(exclude_unset=True), request=request)
    db.commit()
    db.refresh(item)
    return _extension_to_out(db, item)


@router.get("/my-extension", response_model=TelephonyExtensionOut | None)
def my_extension(db: Session = Depends(get_db), user: User = Depends(current_user)) -> TelephonyExtensionOut | None:
    require_module(db, user, "telephony")
    require_permission(db, user, "telephony.view")
    item = db.scalar(select(TelephonyExtension).where(TelephonyExtension.tenant_id == user.tenant_id, TelephonyExtension.user_id == user.id, TelephonyExtension.is_active.is_(True)).order_by(TelephonyExtension.id.desc()).limit(1))
    return _extension_to_out(db, item) if item else None


@router.get("/call-logs", response_model=list[CallLogOut])
def list_call_logs(
    tenant_id: int | None = None,
    customer_id: int | None = None,
    user_id: int | None = None,
    limit: int = Query(default=30, ge=1, le=100),
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
) -> list[CallLogOut]:
    require_module(db, user, "telephony", tenant_id)
    require_permission(db, user, "telephony.logs.view")
    query = _call_log_query(db, user, tenant_id)
    if customer_id:
        customer_for_access(db, customer_id, user)
        query = query.where(CallLog.customer_id == customer_id)
    if user_id and (is_platform_admin(db, user) or is_company_admin(db, user) or user.role == COORDINATOR or get_profile_role_code(db, user) == "collections_leader"):
        query = query.where(CallLog.user_id == user_id)
    return [_call_log_to_out(db, item) for item in db.scalars(query.limit(limit))]


@router.post("/click-to-call", response_model=ClickToCallResponse, status_code=status.HTTP_201_CREATED)
def click_to_call(payload: ClickToCallRequest, request: Request, db: Session = Depends(get_db), user: User = Depends(current_user)) -> ClickToCallResponse:
    require_module(db, user, "telephony")
    require_permission(db, user, "telephony.call")
    extension = db.scalar(select(TelephonyExtension).where(TelephonyExtension.tenant_id == user.tenant_id, TelephonyExtension.user_id == user.id, TelephonyExtension.is_active.is_(True)).order_by(TelephonyExtension.id.desc()).limit(1))
    if extension is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "ok": False,
                "code": "extension_not_configured",
                "message": "No tienes una extension telefonica configurada. Solicita al administrador configurarla en Telefonia > Extensiones.",
            },
        )
    customer = customer_for_access(db, payload.customer_id, user, write=False)
    obligation = obligation_for_access(db, payload.obligation_id, user, write=False) if payload.obligation_id else None
    if obligation and obligation.customer_id != customer.id:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="La obligacion no pertenece al cliente seleccionado.")
    phone_number = (payload.phone_number or customer.phone or "").strip()
    if not phone_number:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="El cliente no tiene telefono disponible para llamar.")
    provider = db.get(TelephonyProvider, extension.provider_id) if extension.provider_id else None
    mode = "manual"
    message = "Llamada registrada en modo simulado."
    if provider and provider.is_active and provider.provider_type != "manual":
        mode = "simulated"
        message = "Llamada registrada en modo simulado. El proveedor esta configurado, pero la marcacion real queda pendiente de la integracion PBX/WebRTC."
    now = datetime.now(timezone.utc)
    call = CallLog(
        tenant_id=customer.tenant_id,
        provider_id=provider.id if provider else None,
        user_id=user.id,
        customer_id=customer.id,
        obligation_id=obligation.id if obligation else None,
        phone_number=phone_number,
        direction="outbound",
        call_status="initiated",
        started_at=now,
        metadata_json=json.dumps(
            {
                "mode": mode,
                "extension_id": extension.id,
                "extension_number": extension.extension_number,
                "provider_type": provider.provider_type if provider else "manual",
                "real_call_executed": False,
                "source": payload.source or "crm_customer_drawer",
            },
            ensure_ascii=True,
        ),
    )
    db.add(call)
    db.flush()
    activity = ManagementActivity(
        tenant_id=customer.tenant_id,
        project_id=customer.project_id,
        customer_id=customer.id,
        obligation_id=obligation.id if obligation else None,
        user_id=user.id,
        channel="phone",
        result="Click to call iniciado",
        note=message,
    )
    db.add(activity)
    db.flush()
    call.management_activity_id = activity.id
    record_audit(db, user, "call_log", "click_to_call", call.id, customer.tenant_id, module="telephony", after={"customer_id": customer.id, "obligation_id": call.obligation_id, "mode": mode, "real_call_executed": False, "source": payload.source or "crm_customer_drawer"}, request=request)
    db.commit()
    db.refresh(call)
    return ClickToCallResponse(ok=True, mode=mode, message=message, call_log_id=call.id, call_log=_call_log_to_out(db, call))


@router.post("/call-logs/{call_log_id}/finish", response_model=CallLogOut)
def finish_call(call_log_id: int, payload: FinishCallLogRequest, request: Request, db: Session = Depends(get_db), user: User = Depends(current_user)) -> CallLogOut:
    require_module(db, user, "telephony")
    require_permission(db, user, "telephony.call")
    call = db.get(CallLog, call_log_id)
    if call is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Llamada no encontrada.")
    if not is_platform_admin(db, user) and call.tenant_id != user.tenant_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Llamada fuera de tu empresa.")
    if call.user_id != user.id and not (is_company_admin(db, user) or user_has_permission(db, user, "telephony.manage") or get_profile_role_code(db, user) == "collections_leader"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No puedes finalizar llamadas de otro usuario.")
    _assert_safe_config(payload.metadata, "metadata")
    call.call_status = payload.call_status
    call.ended_at = datetime.now(timezone.utc)
    if payload.call_status in {"answered", "completed"} and call.answered_at is None:
        call.answered_at = call.started_at
    if payload.duration_seconds is not None:
        call.duration_seconds = payload.duration_seconds
    if payload.external_call_id:
        call.external_call_id = payload.external_call_id
    if payload.recording_url:
        call.recording_url = payload.recording_url
    metadata = _json(call.metadata_json)
    metadata.update(payload.metadata)
    call.metadata_json = json.dumps(metadata, ensure_ascii=True)
    record_audit(db, user, "call_log", "finish", call.id, call.tenant_id, module="telephony", after={"call_status": call.call_status, "duration_seconds": call.duration_seconds}, request=request)
    db.commit()
    db.refresh(call)
    return _call_log_to_out(db, call)
