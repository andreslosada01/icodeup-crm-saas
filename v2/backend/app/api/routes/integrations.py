from __future__ import annotations

import json

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import current_user
from app.db.session import get_db
from app.models import ChannelConfiguration, ChannelEventLog, CommunicationTemplate, IntegrationProvider, User, WebhookConfiguration
from app.schemas.collection_ops import (
    ChannelConfigurationCreate,
    ChannelConfigurationOut,
    ChannelEventOut,
    CommunicationTemplateCreate,
    CommunicationTemplateOut,
    IntegrationProviderCreate,
    IntegrationProviderOut,
    WebhookConfigurationCreate,
    WebhookConfigurationOut,
)
from app.services.access_control import is_platform_admin, require_permission, require_tenant
from app.services.audit_service import record_audit


router = APIRouter()


def _mask_secret(secret: str | None) -> str | None:
    if not secret:
        return None
    if len(secret) <= 4:
        return "****"
    return f"{secret[:2]}****{secret[-2:]}"


def _tenant_id(db: Session, user: User, requested: int | None = None) -> int:
    return require_tenant(db, user, requested).id


def _config(value: str | None) -> dict:
    return json.loads(value or "{}")


def _provider_out(item: IntegrationProvider) -> IntegrationProviderOut:
    return IntegrationProviderOut(id=item.id, tenant_id=item.tenant_id, code=item.code, name=item.name, provider_type=item.provider_type, status=item.status, base_url=item.base_url, config=_config(item.config_json), secret_mask=item.secret_mask, created_at=item.created_at)


def _channel_out(item: ChannelConfiguration) -> ChannelConfigurationOut:
    return ChannelConfigurationOut(id=item.id, tenant_id=item.tenant_id, provider_id=item.provider_id, channel_type=item.channel_type, name=item.name, status=item.status, from_value=item.from_value, config=_config(item.config_json), created_at=item.created_at)


def _webhook_out(item: WebhookConfiguration) -> WebhookConfigurationOut:
    return WebhookConfigurationOut(id=item.id, tenant_id=item.tenant_id, name=item.name, event_type=item.event_type, target_url=item.target_url, status=item.status, secret_mask=item.secret_mask, created_at=item.created_at)


def _event_out(item: ChannelEventLog) -> ChannelEventOut:
    return ChannelEventOut(id=item.id, tenant_id=item.tenant_id, provider_id=item.provider_id, channel_type=item.channel_type, event_type=item.event_type, entity_type=item.entity_type, entity_id=item.entity_id, status=item.status, payload=_config(item.payload_json), created_at=item.created_at)


@router.get("/providers", response_model=list[IntegrationProviderOut])
def list_providers(tenant_id: int | None = None, provider_type: str | None = None, db: Session = Depends(get_db), user: User = Depends(current_user)) -> list[IntegrationProviderOut]:
    require_permission(db, user, "integrations.providers.view")
    query = select(IntegrationProvider).order_by(IntegrationProvider.provider_type, IntegrationProvider.name)
    if is_platform_admin(db, user):
        if tenant_id:
            query = query.where(IntegrationProvider.tenant_id == tenant_id)
    else:
        query = query.where(IntegrationProvider.tenant_id == user.tenant_id)
    if provider_type:
        query = query.where(IntegrationProvider.provider_type == provider_type)
    return [_provider_out(item) for item in db.scalars(query)]


@router.post("/providers", response_model=IntegrationProviderOut, status_code=status.HTTP_201_CREATED)
def create_provider(payload: IntegrationProviderCreate, request: Request, db: Session = Depends(get_db), user: User = Depends(current_user)) -> IntegrationProviderOut:
    require_permission(db, user, "integrations.providers.manage")
    tenant_id = _tenant_id(db, user, payload.tenant_id)
    provider = IntegrationProvider(tenant_id=tenant_id, code=payload.code, name=payload.name, provider_type=payload.provider_type, status=payload.status, base_url=payload.base_url, config_json=json.dumps(payload.config), secret_mask=_mask_secret(payload.secret))
    db.add(provider)
    db.flush()
    record_audit(db, user, "integration_provider", "create", entity_id=provider.id, tenant_id=tenant_id, module="integrations", after={"code": provider.code, "type": provider.provider_type}, request=request)
    db.commit()
    db.refresh(provider)
    return _provider_out(provider)


@router.patch("/providers/{provider_id}", response_model=IntegrationProviderOut)
def update_provider(provider_id: int, payload: IntegrationProviderCreate, request: Request, db: Session = Depends(get_db), user: User = Depends(current_user)) -> IntegrationProviderOut:
    require_permission(db, user, "integrations.providers.manage")
    provider = db.get(IntegrationProvider, provider_id)
    if provider is None or (not is_platform_admin(db, user) and provider.tenant_id != user.tenant_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Proveedor no encontrado.")
    provider.code = payload.code
    provider.name = payload.name
    provider.provider_type = payload.provider_type
    provider.status = payload.status
    provider.base_url = payload.base_url
    provider.config_json = json.dumps(payload.config)
    if payload.secret:
        provider.secret_mask = _mask_secret(payload.secret)
    record_audit(db, user, "integration_provider", "update", entity_id=provider.id, tenant_id=provider.tenant_id, module="integrations", after={"code": provider.code, "status": provider.status}, request=request)
    db.commit()
    db.refresh(provider)
    return _provider_out(provider)


@router.get("/channels", response_model=list[ChannelConfigurationOut])
def list_channels(tenant_id: int | None = None, channel_type: str | None = None, db: Session = Depends(get_db), user: User = Depends(current_user)) -> list[ChannelConfigurationOut]:
    require_permission(db, user, "integrations.channels.view")
    query = select(ChannelConfiguration).order_by(ChannelConfiguration.channel_type, ChannelConfiguration.name)
    if is_platform_admin(db, user):
        if tenant_id:
            query = query.where(ChannelConfiguration.tenant_id == tenant_id)
    else:
        query = query.where(ChannelConfiguration.tenant_id == user.tenant_id)
    if channel_type:
        query = query.where(ChannelConfiguration.channel_type == channel_type)
    return [_channel_out(item) for item in db.scalars(query)]


@router.post("/channels", response_model=ChannelConfigurationOut, status_code=status.HTTP_201_CREATED)
def create_channel(payload: ChannelConfigurationCreate, request: Request, db: Session = Depends(get_db), user: User = Depends(current_user)) -> ChannelConfigurationOut:
    require_permission(db, user, "integrations.channels.create")
    tenant_id = _tenant_id(db, user, payload.tenant_id)
    channel = ChannelConfiguration(tenant_id=tenant_id, provider_id=payload.provider_id, channel_type=payload.channel_type, name=payload.name, status=payload.status, from_value=payload.from_value, config_json=json.dumps(payload.config))
    db.add(channel)
    db.flush()
    record_audit(db, user, "channel_configuration", "create", entity_id=channel.id, tenant_id=tenant_id, module="integrations", after={"channel": channel.channel_type, "name": channel.name}, request=request)
    db.commit()
    db.refresh(channel)
    return _channel_out(channel)


@router.patch("/channels/{channel_id}", response_model=ChannelConfigurationOut)
def update_channel(channel_id: int, payload: ChannelConfigurationCreate, request: Request, db: Session = Depends(get_db), user: User = Depends(current_user)) -> ChannelConfigurationOut:
    require_permission(db, user, "integrations.channels.update")
    channel = db.get(ChannelConfiguration, channel_id)
    if channel is None or (not is_platform_admin(db, user) and channel.tenant_id != user.tenant_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Canal no encontrado.")
    channel.provider_id = payload.provider_id
    channel.channel_type = payload.channel_type
    channel.name = payload.name
    channel.status = payload.status
    channel.from_value = payload.from_value
    channel.config_json = json.dumps(payload.config)
    record_audit(db, user, "channel_configuration", "update", entity_id=channel.id, tenant_id=channel.tenant_id, module="integrations", after={"status": channel.status}, request=request)
    db.commit()
    db.refresh(channel)
    return _channel_out(channel)


@router.post("/channels/{channel_id}/test")
def test_channel(channel_id: int, request: Request, db: Session = Depends(get_db), user: User = Depends(current_user)) -> dict:
    require_permission(db, user, "integrations.channels.update")
    channel = db.get(ChannelConfiguration, channel_id)
    if channel is None or (not is_platform_admin(db, user) and channel.tenant_id != user.tenant_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Canal no encontrado.")
    event = ChannelEventLog(tenant_id=channel.tenant_id, provider_id=channel.provider_id, channel_type=channel.channel_type, event_type="test", entity_type="channel", entity_id=channel.id, status="simulated", payload_json=json.dumps({"message": "Prueba simulada exitosa"}))
    db.add(event)
    record_audit(db, user, "channel_configuration", "test", entity_id=channel.id, tenant_id=channel.tenant_id, module="integrations", request=request)
    db.commit()
    return {"ok": True, "message": "Prueba simulada registrada.", "channel_id": channel.id}


@router.get("/templates", response_model=list[CommunicationTemplateOut])
def list_templates(tenant_id: int | None = None, channel_type: str | None = None, db: Session = Depends(get_db), user: User = Depends(current_user)) -> list[CommunicationTemplate]:
    require_permission(db, user, "integrations.templates.view")
    query = select(CommunicationTemplate).order_by(CommunicationTemplate.channel_type, CommunicationTemplate.name)
    if is_platform_admin(db, user):
        if tenant_id:
            query = query.where(CommunicationTemplate.tenant_id == tenant_id)
    else:
        query = query.where(CommunicationTemplate.tenant_id == user.tenant_id)
    if channel_type:
        query = query.where(CommunicationTemplate.channel_type == channel_type)
    return list(db.scalars(query))


@router.post("/templates", response_model=CommunicationTemplateOut, status_code=status.HTTP_201_CREATED)
def create_template(payload: CommunicationTemplateCreate, db: Session = Depends(get_db), user: User = Depends(current_user)) -> CommunicationTemplate:
    require_permission(db, user, "integrations.templates.manage")
    template = CommunicationTemplate(**payload.model_dump(exclude={"tenant_id"}), tenant_id=_tenant_id(db, user, payload.tenant_id))
    db.add(template)
    db.commit()
    db.refresh(template)
    return template


@router.patch("/templates/{template_id}", response_model=CommunicationTemplateOut)
def update_template(template_id: int, payload: CommunicationTemplateCreate, db: Session = Depends(get_db), user: User = Depends(current_user)) -> CommunicationTemplate:
    require_permission(db, user, "integrations.templates.manage")
    template = db.get(CommunicationTemplate, template_id)
    if template is None or (not is_platform_admin(db, user) and template.tenant_id != user.tenant_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plantilla no encontrada.")
    for field, value in payload.model_dump(exclude={"tenant_id"}).items():
        setattr(template, field, value)
    db.commit()
    db.refresh(template)
    return template


@router.get("/webhooks", response_model=list[WebhookConfigurationOut])
def list_webhooks(tenant_id: int | None = None, db: Session = Depends(get_db), user: User = Depends(current_user)) -> list[WebhookConfigurationOut]:
    require_permission(db, user, "integrations.webhooks.view")
    query = select(WebhookConfiguration).order_by(WebhookConfiguration.name)
    if is_platform_admin(db, user):
        if tenant_id:
            query = query.where(WebhookConfiguration.tenant_id == tenant_id)
    else:
        query = query.where(WebhookConfiguration.tenant_id == user.tenant_id)
    return [_webhook_out(item) for item in db.scalars(query)]


@router.post("/webhooks", response_model=WebhookConfigurationOut, status_code=status.HTTP_201_CREATED)
def create_webhook(payload: WebhookConfigurationCreate, db: Session = Depends(get_db), user: User = Depends(current_user)) -> WebhookConfigurationOut:
    require_permission(db, user, "integrations.webhooks.manage")
    webhook = WebhookConfiguration(tenant_id=_tenant_id(db, user, payload.tenant_id), name=payload.name, event_type=payload.event_type, target_url=payload.target_url, status=payload.status, secret_mask=_mask_secret(payload.secret))
    db.add(webhook)
    db.commit()
    db.refresh(webhook)
    return _webhook_out(webhook)


@router.patch("/webhooks/{webhook_id}", response_model=WebhookConfigurationOut)
def update_webhook(webhook_id: int, payload: WebhookConfigurationCreate, db: Session = Depends(get_db), user: User = Depends(current_user)) -> WebhookConfigurationOut:
    require_permission(db, user, "integrations.webhooks.manage")
    webhook = db.get(WebhookConfiguration, webhook_id)
    if webhook is None or (not is_platform_admin(db, user) and webhook.tenant_id != user.tenant_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Webhook no encontrado.")
    webhook.name = payload.name
    webhook.event_type = payload.event_type
    webhook.target_url = payload.target_url
    webhook.status = payload.status
    if payload.secret:
        webhook.secret_mask = _mask_secret(payload.secret)
    db.commit()
    db.refresh(webhook)
    return _webhook_out(webhook)


@router.post("/webhooks/{webhook_id}/test")
def test_webhook(webhook_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)) -> dict:
    require_permission(db, user, "integrations.webhooks.manage")
    webhook = db.get(WebhookConfiguration, webhook_id)
    if webhook is None or (not is_platform_admin(db, user) and webhook.tenant_id != user.tenant_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Webhook no encontrado.")
    db.add(ChannelEventLog(tenant_id=webhook.tenant_id, channel_type="webhook", event_type=webhook.event_type, entity_type="webhook", entity_id=webhook.id, status="simulated", payload_json=json.dumps({"target": webhook.target_url, "message": "Webhook demo simulado"})))
    db.commit()
    return {"ok": True, "message": "Webhook simulado registrado."}


@router.get("/events", response_model=list[ChannelEventOut])
def list_events(tenant_id: int | None = None, channel_type: str | None = None, limit: int = Query(default=20, ge=1, le=20), db: Session = Depends(get_db), user: User = Depends(current_user)) -> list[ChannelEventOut]:
    require_permission(db, user, "integrations.events.view")
    query = select(ChannelEventLog)
    if is_platform_admin(db, user):
        if tenant_id:
            query = query.where(ChannelEventLog.tenant_id == tenant_id)
    else:
        query = query.where(ChannelEventLog.tenant_id == user.tenant_id)
    if channel_type:
        query = query.where(ChannelEventLog.channel_type == channel_type)
    return [_event_out(item) for item in db.scalars(query.order_by(ChannelEventLog.created_at.desc()).limit(limit))]
