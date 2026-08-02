from __future__ import annotations

import json

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import current_user
from app.core.roles import AGENT
from app.db.session import get_db
from app.models import CallRecording, Customer, ManagementActivity, RecordingAccessLog, User
from app.schemas.collection_ops import CallRecordingCreate, CallRecordingOut, RecordingLinkRequest
from app.services.access_control import get_profile_role_code, is_platform_admin, require_permission, require_tenant, user_has_permission
from app.services.audit_service import record_audit


router = APIRouter()


def _json(value: str | None) -> dict:
    return json.loads(value or "{}")


def _tenant_id(db: Session, user: User, requested: int | None = None) -> int:
    return require_tenant(db, user, requested).id


def _ensure_recordings_allowed(db: Session, user: User) -> None:
    if user.role == AGENT or get_profile_role_code(db, user) == "collections_agent":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Grabaciones no esta habilitado para gestores en esta demo.")


def _recording_to_out(item: CallRecording, include_playback: bool = False) -> CallRecordingOut:
    return CallRecordingOut(
        id=item.id,
        tenant_id=item.tenant_id,
        project_id=item.project_id,
        customer_id=item.customer_id,
        activity_id=item.activity_id,
        user_id=item.user_id,
        call_id=item.call_id,
        phone_number=item.phone_number,
        direction=item.direction,
        started_at=item.started_at,
        duration_seconds=item.duration_seconds,
        provider_code=item.provider_code,
        status=item.status,
        storage_path=item.storage_path if include_playback else None,
        playback_available=bool(item.recording_url or item.storage_path),
        metadata=_json(item.metadata_json),
        created_at=item.created_at,
    )


def _recording_for_access(db: Session, recording_id: int, user: User) -> CallRecording:
    recording = db.get(CallRecording, recording_id)
    if recording is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Grabacion no encontrada.")
    if not is_platform_admin(db, user) and recording.tenant_id != user.tenant_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Grabacion fuera de tu empresa.")
    if user_has_permission(db, user, "recordings.manage") or user_has_permission(db, user, "recordings.audit.view"):
        return recording
    if recording.user_id and recording.user_id != user.id and not user_has_permission(db, user, "recordings.view"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Grabacion no autorizada.")
    return recording


@router.get("", response_model=list[CallRecordingOut])
def list_recordings(
    tenant_id: int | None = None,
    customer_id: int | None = None,
    user_id: int | None = None,
    project_id: int | None = None,
    phone: str | None = None,
    status_filter: str | None = None,
    limit: int = Query(default=10, ge=1, le=10),
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
) -> list[CallRecordingOut]:
    _ensure_recordings_allowed(db, user)
    require_permission(db, user, "recordings.view")
    query = select(CallRecording).order_by(CallRecording.started_at.desc().nullslast(), CallRecording.created_at.desc()).limit(limit)
    if is_platform_admin(db, user):
        if tenant_id:
            query = query.where(CallRecording.tenant_id == tenant_id)
    else:
        query = query.where(CallRecording.tenant_id == user.tenant_id)
    if customer_id:
        query = query.where(CallRecording.customer_id == customer_id)
    if user_id:
        query = query.where(CallRecording.user_id == user_id)
    if project_id:
        query = query.where(CallRecording.project_id == project_id)
    if phone:
        query = query.where(CallRecording.phone_number.ilike(f"%{phone}%"))
    if status_filter:
        query = query.where(CallRecording.status == status_filter)
    return [_recording_to_out(item) for item in db.scalars(query)]


@router.post("", response_model=CallRecordingOut, status_code=status.HTTP_201_CREATED)
def create_recording(payload: CallRecordingCreate, request: Request, db: Session = Depends(get_db), user: User = Depends(current_user)) -> CallRecordingOut:
    _ensure_recordings_allowed(db, user)
    require_permission(db, user, "recordings.manage")
    tenant_id = _tenant_id(db, user, payload.tenant_id)
    if payload.customer_id:
        customer = db.get(Customer, payload.customer_id)
        if customer is None or customer.tenant_id != tenant_id:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Cliente fuera de la empresa.")
    item = CallRecording(**payload.model_dump(exclude={"tenant_id", "metadata"}), tenant_id=tenant_id, metadata_json=json.dumps(payload.metadata))
    db.add(item)
    db.flush()
    record_audit(db, user, "call_recording", "create", entity_id=item.id, tenant_id=tenant_id, module="recordings", after={"call_id": item.call_id, "status": item.status}, request=request)
    db.commit()
    db.refresh(item)
    return _recording_to_out(item)


@router.get("/access-logs")
def access_logs(recording_id: int | None = None, limit: int = Query(default=10, ge=1, le=10), db: Session = Depends(get_db), user: User = Depends(current_user)) -> list[dict]:
    _ensure_recordings_allowed(db, user)
    require_permission(db, user, "recordings.audit.view")
    query = select(RecordingAccessLog).order_by(RecordingAccessLog.created_at.desc()).limit(limit)
    if not is_platform_admin(db, user):
        query = query.where(RecordingAccessLog.tenant_id == user.tenant_id)
    if recording_id:
        query = query.where(RecordingAccessLog.recording_id == recording_id)
    return [
        {
            "id": item.id,
            "tenant_id": item.tenant_id,
            "recording_id": item.recording_id,
            "user_id": item.user_id,
            "action": item.action,
            "ip_address": item.ip_address,
            "created_at": item.created_at,
        }
        for item in db.scalars(query)
    ]


@router.get("/{recording_id}", response_model=CallRecordingOut)
def get_recording(recording_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)) -> CallRecordingOut:
    _ensure_recordings_allowed(db, user)
    require_permission(db, user, "recordings.view")
    return _recording_to_out(_recording_for_access(db, recording_id, user))


@router.get("/{recording_id}/playback")
def playback(recording_id: int, request: Request, db: Session = Depends(get_db), user: User = Depends(current_user)) -> dict:
    _ensure_recordings_allowed(db, user)
    require_permission(db, user, "recordings.playback")
    recording = _recording_for_access(db, recording_id, user)
    db.add(RecordingAccessLog(tenant_id=recording.tenant_id, recording_id=recording.id, user_id=user.id, action="playback", ip_address=request.client.host if request.client else None, user_agent=request.headers.get("user-agent")))
    record_audit(db, user, "call_recording", "playback", entity_id=recording.id, tenant_id=recording.tenant_id, module="recordings", request=request)
    db.commit()
    return {"recording_id": recording.id, "playback_url": recording.recording_url or "about:blank", "placeholder": not bool(recording.recording_url)}


@router.get("/{recording_id}/download")
def download(recording_id: int, request: Request, db: Session = Depends(get_db), user: User = Depends(current_user)) -> dict:
    _ensure_recordings_allowed(db, user)
    require_permission(db, user, "recordings.download")
    recording = _recording_for_access(db, recording_id, user)
    db.add(RecordingAccessLog(tenant_id=recording.tenant_id, recording_id=recording.id, user_id=user.id, action="download", ip_address=request.client.host if request.client else None, user_agent=request.headers.get("user-agent")))
    record_audit(db, user, "call_recording", "download", entity_id=recording.id, tenant_id=recording.tenant_id, module="recordings", request=request)
    db.commit()
    return {"recording_id": recording.id, "download_url": recording.recording_url or None, "message": "URL de descarga disponible solo cuando el proveedor la entregue de forma segura."}


@router.post("/link-activity")
def link_activity(payload: RecordingLinkRequest, request: Request, db: Session = Depends(get_db), user: User = Depends(current_user)) -> dict:
    _ensure_recordings_allowed(db, user)
    require_permission(db, user, "recordings.manage")
    recording = _recording_for_access(db, payload.recording_id, user)
    if payload.activity_id:
        activity = db.get(ManagementActivity, payload.activity_id)
        if activity is None or activity.tenant_id != recording.tenant_id:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Gestion fuera de la empresa.")
        recording.activity_id = activity.id
        recording.customer_id = activity.customer_id
    if payload.customer_id:
        customer = db.get(Customer, payload.customer_id)
        if customer is None or customer.tenant_id != recording.tenant_id:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Cliente fuera de la empresa.")
        recording.customer_id = customer.id
    record_audit(db, user, "call_recording", "link", entity_id=recording.id, tenant_id=recording.tenant_id, module="recordings", after=payload.model_dump(), request=request)
    db.commit()
    return {"ok": True, "recording_id": recording.id}
