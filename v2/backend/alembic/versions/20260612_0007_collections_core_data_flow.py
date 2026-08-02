"""collections_core_data_flow

Revision ID: 20260612_0007
Revises: 20260611_0006
Create Date: 2026-06-12

Migracion aditiva para completar el nucleo operativo de Collects 360:
- pagos asociados opcionalmente a obligaciones;
- prioridad y fechas operativas en obligaciones;
- prioridad, contactabilidad y vigencia en demograficos.
"""

from __future__ import annotations

from alembic import op


revision = "20260612_0007"
down_revision = "20260611_0006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TABLE IF EXISTS payments ADD COLUMN IF NOT EXISTS obligation_id INTEGER REFERENCES customer_obligations(id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_payments_obligation_id ON payments (obligation_id)")

    op.execute("ALTER TABLE IF EXISTS call_logs ADD COLUMN IF NOT EXISTS project_id INTEGER REFERENCES projects(id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_call_logs_project_id ON call_logs (project_id)")

    op.execute("ALTER TABLE IF EXISTS customer_obligations ADD COLUMN IF NOT EXISTS priority INTEGER NOT NULL DEFAULT 0")
    op.execute("ALTER TABLE IF EXISTS customer_obligations ADD COLUMN IF NOT EXISTS due_date TIMESTAMP WITH TIME ZONE")
    op.execute("ALTER TABLE IF EXISTS customer_obligations ADD COLUMN IF NOT EXISTS assignment_date TIMESTAMP WITH TIME ZONE")

    op.execute("ALTER TABLE IF EXISTS customer_demographics ADD COLUMN IF NOT EXISTS contactability VARCHAR(40) NOT NULL DEFAULT 'Media'")
    op.execute("ALTER TABLE IF EXISTS customer_demographics ADD COLUMN IF NOT EXISTS priority INTEGER NOT NULL DEFAULT 0")
    op.execute("ALTER TABLE IF EXISTS customer_demographics ADD COLUMN IF NOT EXISTS valid_from DATE")
    op.execute("ALTER TABLE IF EXISTS customer_demographics ADD COLUMN IF NOT EXISTS valid_until DATE")


def downgrade() -> None:
    # Migracion no destructiva: no se eliminan columnas para proteger datos operativos.
    pass
