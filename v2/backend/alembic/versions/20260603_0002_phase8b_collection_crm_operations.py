"""phase8b_collection_crm_operations

Revision ID: 20260603_0002
Revises: 20260528_0001
Create Date: 2026-06-03

Migracion no destructiva para tablas operativas de Fase 8B:
tipificaciones avanzadas, demograficos, grabaciones, cargas,
Mi Excel Web e integraciones.
"""

from __future__ import annotations

from alembic import op

from app.db.session import Base
from app.models import collection_ops  # noqa: F401


revision = "20260603_0002"
down_revision = "20260528_0001"
branch_labels = None
depends_on = None


PHASE8B_TABLES = [
    "typification_trees",
    "typification_tree_nodes",
    "typification_combination_rules",
    "customer_demographics",
    "call_recordings",
    "recording_access_logs",
    "upload_batches",
    "operational_files",
    "saved_data_views",
    "data_export_logs",
    "integration_providers",
    "channel_configurations",
    "communication_templates",
    "webhook_configurations",
    "channel_event_logs",
]


def upgrade() -> None:
    bind = op.get_bind()
    for table_name in PHASE8B_TABLES:
        Base.metadata.tables[table_name].create(bind=bind, checkfirst=True)


def downgrade() -> None:
    # Migracion no destructiva: no se eliminan tablas ni datos.
    pass
