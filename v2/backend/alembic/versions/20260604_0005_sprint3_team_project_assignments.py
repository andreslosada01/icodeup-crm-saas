"""sprint3_team_project_assignments

Revision ID: 20260604_0005
Revises: 20260603_0004
Create Date: 2026-06-04

Migracion no destructiva para fortalecer asignaciones de usuarios a
proyectos/carteras con tenant, rol operativo y estado activo.
"""

from __future__ import annotations

from alembic import op


revision = "20260604_0005"
down_revision = "20260603_0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TABLE IF EXISTS user_project_assignments ADD COLUMN IF NOT EXISTS tenant_id INTEGER REFERENCES tenants(id)")
    op.execute("ALTER TABLE IF EXISTS user_project_assignments ADD COLUMN IF NOT EXISTS role_in_project VARCHAR(40) DEFAULT 'agent' NOT NULL")
    op.execute("ALTER TABLE IF EXISTS user_project_assignments ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT true NOT NULL")
    op.execute("ALTER TABLE IF EXISTS user_project_assignments ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL")
    op.execute(
        """
        UPDATE user_project_assignments upa
        SET tenant_id = projects.tenant_id
        FROM projects
        WHERE upa.project_id = projects.id AND upa.tenant_id IS NULL
        """
    )
    op.execute("UPDATE user_project_assignments SET role_in_project = 'agent' WHERE role_in_project IS NULL")
    op.execute("UPDATE user_project_assignments SET is_active = true WHERE is_active IS NULL")
    op.execute("CREATE INDEX IF NOT EXISTS ix_user_project_assignments_tenant_id ON user_project_assignments (tenant_id)")


def downgrade() -> None:
    # Migracion no destructiva: no se eliminan columnas ni indices para proteger historico operativo.
    pass
