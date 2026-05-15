from sqlalchemy import text
from sqlalchemy.engine import Engine


def apply_compatibility_migrations(engine: Engine) -> None:
    statements = [
        "ALTER TABLE IF EXISTS projects ADD COLUMN IF NOT EXISTS description TEXT",
        "ALTER TABLE IF EXISTS users ADD COLUMN IF NOT EXISTS phone VARCHAR(80)",
        "ALTER TABLE IF EXISTS users ADD COLUMN IF NOT EXISTS title VARCHAR(120)",
        "ALTER TABLE IF EXISTS users ADD COLUMN IF NOT EXISTS leader_id INTEGER REFERENCES users(id)",
        "CREATE INDEX IF NOT EXISTS ix_users_leader_id ON users (leader_id)",
        "ALTER TABLE IF EXISTS customers ADD COLUMN IF NOT EXISTS assigned_user_id INTEGER REFERENCES users(id)",
        "ALTER TABLE IF EXISTS customers ADD COLUMN IF NOT EXISTS city VARCHAR(120)",
        "ALTER TABLE IF EXISTS customers ADD COLUMN IF NOT EXISTS segment VARCHAR(120)",
        "ALTER TABLE IF EXISTS customers ADD COLUMN IF NOT EXISTS obligation VARCHAR(180)",
        "ALTER TABLE IF EXISTS customers ADD COLUMN IF NOT EXISTS original_balance INTEGER DEFAULT 0 NOT NULL",
        "ALTER TABLE IF EXISTS customers ADD COLUMN IF NOT EXISTS risk VARCHAR(40) DEFAULT 'Medio' NOT NULL",
        "ALTER TABLE IF EXISTS customers ADD COLUMN IF NOT EXISTS priority INTEGER DEFAULT 0 NOT NULL",
        "ALTER TABLE IF EXISTS customers ADD COLUMN IF NOT EXISTS next_action VARCHAR(240)",
        "ALTER TABLE IF EXISTS customers ADD COLUMN IF NOT EXISTS contactability VARCHAR(40) DEFAULT 'Media' NOT NULL",
        "ALTER TABLE IF EXISTS customers ADD COLUMN IF NOT EXISTS notes TEXT",
        "ALTER TABLE IF EXISTS customers ADD COLUMN IF NOT EXISTS last_contact_at TIMESTAMP WITH TIME ZONE",
        "ALTER TABLE IF EXISTS customers ADD COLUMN IF NOT EXISTS next_contact_at TIMESTAMP WITH TIME ZONE",
        "UPDATE customers SET original_balance = balance WHERE original_balance = 0 AND balance > 0",
        "CREATE INDEX IF NOT EXISTS ix_customers_assigned_user_id ON customers (assigned_user_id)",
        "CREATE INDEX IF NOT EXISTS ix_management_activities_customer_id ON management_activities (customer_id)",
        "CREATE INDEX IF NOT EXISTS ix_management_activities_tenant_id ON management_activities (tenant_id)",
        "CREATE INDEX IF NOT EXISTS ix_payment_promises_customer_id ON payment_promises (customer_id)",
        "CREATE INDEX IF NOT EXISTS ix_payments_customer_id ON payments (customer_id)",
        "CREATE INDEX IF NOT EXISTS ix_user_project_assignments_user_id ON user_project_assignments (user_id)",
        "CREATE INDEX IF NOT EXISTS ix_user_project_assignments_project_id ON user_project_assignments (project_id)",
    ]
    with engine.begin() as connection:
        for statement in statements:
            connection.execute(text(statement))
