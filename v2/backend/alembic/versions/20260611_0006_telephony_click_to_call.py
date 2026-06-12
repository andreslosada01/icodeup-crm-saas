"""telephony_click_to_call

Revision ID: 20260611_0006
Revises: 20260604_0005
Create Date: 2026-06-11

Migracion no destructiva para base de telefonia/click-to-call:
proveedores, extensiones por usuario e historial de llamadas.
"""

from __future__ import annotations

from alembic import op


revision = "20260611_0006"
down_revision = "20260604_0005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS telephony_providers (
            id SERIAL PRIMARY KEY,
            tenant_id INTEGER NOT NULL REFERENCES tenants(id),
            name VARCHAR(180) NOT NULL,
            provider_type VARCHAR(40) NOT NULL DEFAULT 'manual',
            host VARCHAR(180),
            port INTEGER,
            websocket_url VARCHAR(500),
            api_url VARCHAR(500),
            is_active BOOLEAN NOT NULL DEFAULT true,
            config_json TEXT,
            created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
            updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
        )
        """
    )
    op.execute("CREATE UNIQUE INDEX IF NOT EXISTS uq_telephony_provider_tenant_name ON telephony_providers (tenant_id, name)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_telephony_providers_tenant_id ON telephony_providers (tenant_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_telephony_providers_provider_type ON telephony_providers (provider_type)")

    op.execute(
        """
        CREATE TABLE IF NOT EXISTS telephony_extensions (
            id SERIAL PRIMARY KEY,
            tenant_id INTEGER NOT NULL REFERENCES tenants(id),
            user_id INTEGER NOT NULL REFERENCES users(id),
            provider_id INTEGER REFERENCES telephony_providers(id),
            extension_number VARCHAR(40) NOT NULL,
            display_name VARCHAR(180),
            sip_username VARCHAR(160),
            sip_domain VARCHAR(180),
            status VARCHAR(40) NOT NULL DEFAULT 'not_connected',
            is_active BOOLEAN NOT NULL DEFAULT true,
            metadata_json TEXT,
            created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
            updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
        )
        """
    )
    op.execute("CREATE UNIQUE INDEX IF NOT EXISTS uq_telephony_extension_tenant_number ON telephony_extensions (tenant_id, extension_number)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_telephony_extensions_tenant_id ON telephony_extensions (tenant_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_telephony_extensions_user_id ON telephony_extensions (user_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_telephony_extensions_provider_id ON telephony_extensions (provider_id)")

    op.execute(
        """
        CREATE TABLE IF NOT EXISTS call_logs (
            id SERIAL PRIMARY KEY,
            tenant_id INTEGER NOT NULL REFERENCES tenants(id),
            provider_id INTEGER REFERENCES telephony_providers(id),
            user_id INTEGER NOT NULL REFERENCES users(id),
            customer_id INTEGER REFERENCES customers(id),
            obligation_id INTEGER REFERENCES customer_obligations(id),
            phone_number VARCHAR(80) NOT NULL,
            direction VARCHAR(40) NOT NULL DEFAULT 'outbound',
            call_status VARCHAR(40) NOT NULL DEFAULT 'initiated',
            started_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
            answered_at TIMESTAMP WITH TIME ZONE,
            ended_at TIMESTAMP WITH TIME ZONE,
            duration_seconds INTEGER NOT NULL DEFAULT 0,
            external_call_id VARCHAR(180),
            recording_url VARCHAR(500),
            management_activity_id INTEGER REFERENCES management_activities(id),
            metadata_json TEXT
        )
        """
    )
    op.execute("CREATE INDEX IF NOT EXISTS ix_call_logs_tenant_id ON call_logs (tenant_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_call_logs_provider_id ON call_logs (provider_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_call_logs_user_id ON call_logs (user_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_call_logs_customer_id ON call_logs (customer_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_call_logs_obligation_id ON call_logs (obligation_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_call_logs_direction ON call_logs (direction)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_call_logs_call_status ON call_logs (call_status)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_call_logs_external_call_id ON call_logs (external_call_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_call_logs_management_activity_id ON call_logs (management_activity_id)")


def downgrade() -> None:
    # Migracion no destructiva: no se eliminan tablas para proteger historico de llamadas.
    pass
