"""careflow_360_mvp

Revision ID: 20260802_0008
Revises: 20260612_0007
Create Date: 2026-08-02

Migracion no destructiva para CareFlow 360:
casos de atencion, categorias y eventos/historial por tenant.
"""

from __future__ import annotations

from alembic import op


revision = "20260802_0008"
down_revision = "20260612_0007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS care_case_categories (
            id SERIAL PRIMARY KEY,
            tenant_id INTEGER NOT NULL REFERENCES tenants(id),
            name VARCHAR(160) NOT NULL,
            description TEXT,
            default_priority VARCHAR(30) NOT NULL DEFAULT 'media',
            default_sla_hours INTEGER NOT NULL DEFAULT 48,
            is_active BOOLEAN NOT NULL DEFAULT true,
            created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
            updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
        )
        """
    )
    op.execute("CREATE UNIQUE INDEX IF NOT EXISTS uq_care_case_category_tenant_name ON care_case_categories (tenant_id, name)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_care_case_categories_tenant_id ON care_case_categories (tenant_id)")

    op.execute(
        """
        CREATE TABLE IF NOT EXISTS care_cases (
            id SERIAL PRIMARY KEY,
            tenant_id INTEGER NOT NULL REFERENCES tenants(id),
            project_id INTEGER REFERENCES projects(id),
            customer_id INTEGER REFERENCES customers(id),
            case_number VARCHAR(80) NOT NULL,
            title VARCHAR(220) NOT NULL,
            description TEXT,
            channel VARCHAR(40) NOT NULL DEFAULT 'interno',
            case_type VARCHAR(120),
            category VARCHAR(120),
            priority VARCHAR(30) NOT NULL DEFAULT 'media',
            status VARCHAR(40) NOT NULL DEFAULT 'nuevo',
            origin VARCHAR(80),
            assigned_user_id INTEGER REFERENCES users(id),
            created_by_id INTEGER NOT NULL REFERENCES users(id),
            closed_by_id INTEGER REFERENCES users(id),
            due_at TIMESTAMP WITH TIME ZONE,
            resolved_at TIMESTAMP WITH TIME ZONE,
            closed_at TIMESTAMP WITH TIME ZONE,
            sla_status VARCHAR(40) NOT NULL DEFAULT 'en_tiempo',
            metadata_json TEXT,
            created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
            updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
        )
        """
    )
    op.execute("CREATE UNIQUE INDEX IF NOT EXISTS uq_care_case_tenant_number ON care_cases (tenant_id, case_number)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_care_cases_tenant_id ON care_cases (tenant_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_care_cases_project_id ON care_cases (project_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_care_cases_customer_id ON care_cases (customer_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_care_cases_case_number ON care_cases (case_number)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_care_cases_channel ON care_cases (channel)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_care_cases_case_type ON care_cases (case_type)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_care_cases_category ON care_cases (category)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_care_cases_priority ON care_cases (priority)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_care_cases_status ON care_cases (status)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_care_cases_assigned_user_id ON care_cases (assigned_user_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_care_cases_created_by_id ON care_cases (created_by_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_care_cases_closed_by_id ON care_cases (closed_by_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_care_cases_due_at ON care_cases (due_at)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_care_cases_sla_status ON care_cases (sla_status)")

    op.execute(
        """
        CREATE TABLE IF NOT EXISTS care_case_events (
            id SERIAL PRIMARY KEY,
            tenant_id INTEGER NOT NULL REFERENCES tenants(id),
            case_id INTEGER NOT NULL REFERENCES care_cases(id),
            event_type VARCHAR(40) NOT NULL DEFAULT 'nota',
            description TEXT NOT NULL,
            previous_value TEXT,
            new_value TEXT,
            created_by_id INTEGER NOT NULL REFERENCES users(id),
            created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
            metadata_json TEXT
        )
        """
    )
    op.execute("CREATE INDEX IF NOT EXISTS ix_care_case_events_tenant_id ON care_case_events (tenant_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_care_case_events_case_id ON care_case_events (case_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_care_case_events_event_type ON care_case_events (event_type)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_care_case_events_created_by_id ON care_case_events (created_by_id)")


def downgrade() -> None:
    # Migracion no destructiva: no se eliminan casos ni historial de atencion.
    pass
