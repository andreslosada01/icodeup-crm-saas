from __future__ import annotations

import base64
import hashlib
import hmac
import json
import mimetypes
import secrets
import sqlite3
from datetime import datetime, timedelta, timezone
from http import HTTPStatus
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
LEGACY_DB_PATH = DATA_DIR / "icodeup_crm.sqlite3"
PLATFORM_DB_PATH = DATA_DIR / "platform.sqlite3"
TENANT_DIR = DATA_DIR / "tenants"
DB_PATH = PLATFORM_DB_PATH
SESSION_COOKIE = "icodeup_session"
SESSION_HOURS = 12
HOST = "127.0.0.1"
PORT = 8010

TENANT_TABLES = (
    "companies",
    "users",
    "settings",
    "customers",
    "portfolios",
    "portfolio_users",
    "interactions",
    "promises",
    "payments",
    "campaigns",
    "typification_nodes",
    "channel_accounts",
    "audit_log",
)

PLATFORM_OPERATION_TABLES = (
    "settings",
    "portfolio_users",
    "interactions",
    "promises",
    "payments",
    "campaigns",
    "customers",
    "portfolios",
    "typification_nodes",
    "channel_accounts",
)


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def today() -> str:
    return datetime.now().date().isoformat()


def add_days(days: int) -> str:
    return (datetime.now().date() + timedelta(days=days)).isoformat()


def connect_database(path: Path) -> sqlite3.Connection:
    DATA_DIR.mkdir(exist_ok=True)
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def db() -> sqlite3.Connection:
    return connect_database(PLATFORM_DB_PATH)


def tenant_db_path(slug: str) -> Path:
    return TENANT_DIR / f"{normalize_slug(slug)}.sqlite3"


def tenant_db_for_slug(slug: str) -> sqlite3.Connection:
    return connect_database(tenant_db_path(slug))


def hash_password(password: str) -> str:
    iterations = 160_000
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return "pbkdf2_sha256${}${}${}".format(
        iterations,
        base64.b64encode(salt).decode("ascii"),
        base64.b64encode(digest).decode("ascii"),
    )


def verify_password(password: str, stored: str) -> bool:
    try:
        algorithm, iterations, salt, expected = stored.split("$", 3)
        if algorithm != "pbkdf2_sha256":
            return False
        digest = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            base64.b64decode(salt),
            int(iterations),
        )
        return hmac.compare_digest(base64.b64encode(digest).decode("ascii"), expected)
    except (ValueError, TypeError):
        return False


def json_dumps(value) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def json_loads(value, fallback):
    if not value:
        return fallback
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return fallback


def normalize_slug(value: str) -> str:
    slug = "".join(char.lower() if char.isalnum() else "-" for char in str(value or "").strip())
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug.strip("-") or secrets.token_hex(4)


def init_db() -> None:
    with db() as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS companies (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              name TEXT NOT NULL,
              slug TEXT NOT NULL UNIQUE,
              tax_id TEXT,
              status TEXT NOT NULL DEFAULT 'active',
              created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS users (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              company_id INTEGER NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
              name TEXT NOT NULL,
              email TEXT NOT NULL,
              role TEXT NOT NULL,
              leader_id INTEGER REFERENCES users(id),
              password_hash TEXT NOT NULL,
              active INTEGER NOT NULL DEFAULT 1,
              created_at TEXT NOT NULL,
              UNIQUE(company_id, email)
            );

            CREATE TABLE IF NOT EXISTS sessions (
              id TEXT PRIMARY KEY,
              user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
              expires_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS settings (
              company_id INTEGER PRIMARY KEY REFERENCES companies(id) ON DELETE CASCADE,
              monthly_goal INTEGER NOT NULL,
              promise_alert_days INTEGER NOT NULL,
              critical_dpd INTEGER NOT NULL
            );

            CREATE TABLE IF NOT EXISTS customers (
              id TEXT NOT NULL,
              company_id INTEGER NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
              name TEXT NOT NULL,
              document TEXT NOT NULL,
              phone TEXT NOT NULL,
              email TEXT,
              city TEXT,
              segment TEXT NOT NULL,
              agent TEXT NOT NULL,
              balance INTEGER NOT NULL,
              original_balance INTEGER NOT NULL,
              dpd INTEGER NOT NULL,
              status TEXT NOT NULL,
              risk TEXT NOT NULL,
              priority INTEGER NOT NULL,
              next_action TEXT,
              last_contact TEXT,
              next_contact TEXT,
              contactability TEXT,
              accounts_json TEXT,
              tags_json TEXT,
              portfolio_id TEXT,
              demographic_json TEXT,
              financial_json TEXT,
              notes TEXT,
              PRIMARY KEY (company_id, id)
            );

            CREATE TABLE IF NOT EXISTS portfolios (
              id TEXT NOT NULL,
              company_id INTEGER NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
              name TEXT NOT NULL,
              code TEXT NOT NULL,
              leader_user_id INTEGER REFERENCES users(id),
              status TEXT NOT NULL DEFAULT 'active',
              created_at TEXT NOT NULL,
              PRIMARY KEY (company_id, id)
            );

            CREATE TABLE IF NOT EXISTS portfolio_users (
              company_id INTEGER NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
              portfolio_id TEXT NOT NULL,
              user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
              role TEXT NOT NULL DEFAULT 'agent',
              PRIMARY KEY (company_id, portfolio_id, user_id),
              FOREIGN KEY (company_id, portfolio_id) REFERENCES portfolios(company_id, id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS interactions (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              company_id INTEGER NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
              customer_id TEXT NOT NULL,
              type TEXT NOT NULL,
              note TEXT,
              agent TEXT,
              channel TEXT,
              created_at TEXT NOT NULL,
              FOREIGN KEY (company_id, customer_id) REFERENCES customers(company_id, id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS promises (
              id TEXT NOT NULL,
              company_id INTEGER NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
              customer_id TEXT NOT NULL,
              amount INTEGER NOT NULL,
              date TEXT NOT NULL,
              channel TEXT NOT NULL,
              status TEXT NOT NULL,
              created_at TEXT NOT NULL,
              PRIMARY KEY (company_id, id),
              FOREIGN KEY (company_id, customer_id) REFERENCES customers(company_id, id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS payments (
              id TEXT NOT NULL,
              company_id INTEGER NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
              customer_id TEXT NOT NULL,
              amount INTEGER NOT NULL,
              date TEXT NOT NULL,
              method TEXT NOT NULL,
              reference TEXT,
              PRIMARY KEY (company_id, id),
              FOREIGN KEY (company_id, customer_id) REFERENCES customers(company_id, id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS campaigns (
              id TEXT NOT NULL,
              company_id INTEGER NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
              name TEXT NOT NULL,
              segment TEXT NOT NULL,
              channel TEXT NOT NULL,
              template TEXT NOT NULL,
              created_at TEXT NOT NULL,
              sent INTEGER NOT NULL DEFAULT 0,
              contacted INTEGER NOT NULL DEFAULT 0,
              promises INTEGER NOT NULL DEFAULT 0,
              payments INTEGER NOT NULL DEFAULT 0,
              PRIMARY KEY (company_id, id)
            );

            CREATE TABLE IF NOT EXISTS typification_nodes (
              id TEXT NOT NULL,
              company_id INTEGER NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
              parent_id TEXT,
              label TEXT NOT NULL,
              code TEXT NOT NULL,
              next_status TEXT,
              requires_promise INTEGER NOT NULL DEFAULT 0,
              requires_payment INTEGER NOT NULL DEFAULT 0,
              channel TEXT,
              sort_order INTEGER NOT NULL DEFAULT 0,
              PRIMARY KEY (company_id, id)
            );

            CREATE TABLE IF NOT EXISTS channel_accounts (
              id TEXT NOT NULL,
              company_id INTEGER NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
              type TEXT NOT NULL CHECK (type IN ('whatsapp','email','telephony')),
              label TEXT NOT NULL,
              value TEXT NOT NULL,
              provider TEXT,
              status TEXT NOT NULL DEFAULT 'active',
              is_default INTEGER NOT NULL DEFAULT 0,
              config_json TEXT,
              created_at TEXT NOT NULL,
              PRIMARY KEY (company_id, id)
            );

            CREATE TABLE IF NOT EXISTS audit_log (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              company_id INTEGER,
              user_id INTEGER,
              action TEXT NOT NULL,
              entity TEXT,
              entity_id TEXT,
              detail_json TEXT,
              created_at TEXT NOT NULL
            );

            CREATE INDEX IF NOT EXISTS idx_customers_company_status ON customers(company_id, status);
            CREATE INDEX IF NOT EXISTS idx_customers_company_agent ON customers(company_id, agent);
            CREATE INDEX IF NOT EXISTS idx_interactions_customer ON interactions(company_id, customer_id);
            CREATE INDEX IF NOT EXISTS idx_promises_company_status ON promises(company_id, status);
            """
        )

        ensure_schema_updates(connection)
        connection.execute("CREATE INDEX IF NOT EXISTS idx_customers_company_portfolio ON customers(company_id, portfolio_id)")
        if connection.execute("SELECT COUNT(*) FROM companies").fetchone()[0] == 0:
            if LEGACY_DB_PATH.exists():
                migrate_legacy_database(connection, LEGACY_DB_PATH)
            else:
                seed_database(connection)
        ensure_channel_defaults(connection)
        ensure_operational_defaults(connection)
        ensure_platform_defaults(connection)
        ensure_tenant_databases(connection)
        purge_platform_operational_data(connection)


def table_columns(connection: sqlite3.Connection, table: str) -> set[str]:
    return {row["name"] for row in connection.execute(f"PRAGMA table_info({table})")}


def ensure_schema_updates(connection: sqlite3.Connection) -> None:
    migrate_users_table_if_needed(connection)
    ensure_column(connection, "customers", "portfolio_id", "TEXT")
    ensure_column(connection, "customers", "demographic_json", "TEXT")
    ensure_column(connection, "customers", "financial_json", "TEXT")
    ensure_column(connection, "users", "leader_id", "INTEGER")


def ensure_column(connection: sqlite3.Connection, table: str, column: str, definition: str) -> None:
    if column not in table_columns(connection, table):
        connection.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")


def migrate_legacy_database(platform_connection: sqlite3.Connection, legacy_path: Path) -> None:
    with connect_database(legacy_path) as legacy:
        ensure_schema_updates(legacy)
        platform_connection.execute("PRAGMA foreign_keys = OFF")
        for table in TENANT_TABLES:
            copy_table_rows(legacy, platform_connection, table)
        platform_connection.execute("PRAGMA foreign_keys = ON")
    platform_connection.commit()


def copy_table_rows(
    source: sqlite3.Connection,
    target: sqlite3.Connection,
    table: str,
    where: str = "",
    params: tuple = (),
) -> int:
    source_columns = table_columns(source, table)
    target_columns = table_columns(target, table)
    columns = [column for column in source_columns if column in target_columns]
    if not columns:
        return 0
    column_sql = ", ".join(columns)
    placeholders = ", ".join("?" for _ in columns)
    rows = source.execute(f"SELECT {column_sql} FROM {table} {where}", params).fetchall()
    for row in rows:
        target.execute(
            f"INSERT OR IGNORE INTO {table} ({column_sql}) VALUES ({placeholders})",
            tuple(row[column] for column in columns),
        )
    return len(rows)


def install_schema_from_template(source: sqlite3.Connection, target: sqlite3.Connection) -> None:
    objects = source.execute(
        """
        SELECT type, name, sql
        FROM sqlite_master
        WHERE sql IS NOT NULL
          AND name NOT LIKE 'sqlite_%'
        ORDER BY CASE type WHEN 'table' THEN 1 WHEN 'index' THEN 2 ELSE 3 END, name
        """
    ).fetchall()
    for item in objects:
        try:
            target.execute(item["sql"])
        except sqlite3.OperationalError as error:
            if "already exists" not in str(error):
                raise
    ensure_schema_updates(target)
    target.execute("CREATE INDEX IF NOT EXISTS idx_customers_company_portfolio ON customers(company_id, portfolio_id)")


def tenant_company_row(platform_connection: sqlite3.Connection, company_id: int) -> sqlite3.Row | None:
    return platform_connection.execute(
        "SELECT id, name, slug, tax_id, status, created_at FROM companies WHERE id = ? AND slug <> 'icodeup-platform'",
        (company_id,),
    ).fetchone()


def mirror_company_and_users(platform_connection: sqlite3.Connection, tenant_connection: sqlite3.Connection, company_id: int) -> None:
    company = platform_connection.execute(
        "SELECT id, name, slug, tax_id, status, created_at FROM companies WHERE id = ?",
        (company_id,),
    ).fetchone()
    if not company:
        return
    tenant_connection.execute(
        """
        INSERT INTO companies (id, name, slug, tax_id, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
          name = excluded.name,
          slug = excluded.slug,
          tax_id = excluded.tax_id,
          status = excluded.status
        """,
        (company["id"], company["name"], company["slug"], company["tax_id"], company["status"], company["created_at"]),
    )
    user_rows = platform_connection.execute("SELECT * FROM users WHERE company_id = ? ORDER BY id", (company_id,)).fetchall()
    for row in user_rows:
        tenant_connection.execute(
            """
            INSERT INTO users (id, company_id, name, email, role, leader_id, password_hash, active, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
              name = excluded.name,
              email = excluded.email,
              role = excluded.role,
              password_hash = excluded.password_hash,
              active = excluded.active
            """,
            (
                row["id"],
                row["company_id"],
                row["name"],
                row["email"],
                row["role"],
                None,
                row["password_hash"],
                row["active"],
                row["created_at"],
            ),
        )
    for row in user_rows:
        tenant_connection.execute(
            "UPDATE users SET leader_id = ? WHERE id = ? AND company_id = ?",
            (row["leader_id"], row["id"], company_id),
        )


def ensure_tenant_databases(platform_connection: sqlite3.Connection) -> None:
    TENANT_DIR.mkdir(parents=True, exist_ok=True)
    companies = platform_connection.execute(
        "SELECT id, name, slug, tax_id, status, created_at FROM companies WHERE slug <> 'icodeup-platform' ORDER BY id"
    ).fetchall()
    for company in companies:
        with tenant_db_for_slug(company["slug"]) as tenant_connection:
            install_schema_from_template(platform_connection, tenant_connection)
            mirror_company_and_users(platform_connection, tenant_connection, company["id"])
            if tenant_connection.execute("SELECT COUNT(*) FROM settings WHERE company_id = ?", (company["id"],)).fetchone()[0] == 0:
                copy_tenant_rows_from_platform(platform_connection, tenant_connection, company["id"])
            ensure_tenant_defaults(tenant_connection, company["id"], company["name"], company["slug"])
            tenant_connection.commit()


def copy_tenant_rows_from_platform(
    platform_connection: sqlite3.Connection,
    tenant_connection: sqlite3.Connection,
    company_id: int,
) -> None:
    for table in TENANT_TABLES:
        if table in ("companies", "users"):
            continue
        if "company_id" in table_columns(platform_connection, table):
            copy_table_rows(platform_connection, tenant_connection, table, "WHERE company_id = ?", (company_id,))


def ensure_tenant_defaults(connection: sqlite3.Connection, company_id: int, company_name: str, slug: str) -> None:
    ensure_tenant_basics(connection, company_id, company_name)
    if connection.execute("SELECT COUNT(*) FROM portfolios WHERE company_id = ?", (company_id,)).fetchone()[0] == 0:
        leader = connection.execute(
            "SELECT id FROM users WHERE company_id = ? AND role IN ('coordinator','admin','superadmin') ORDER BY CASE role WHEN 'coordinator' THEN 1 WHEN 'admin' THEN 2 ELSE 3 END LIMIT 1",
            (company_id,),
        ).fetchone()
        portfolio_id = "CAR-BASE"
        connection.execute(
            """
            INSERT INTO portfolios (id, company_id, name, code, leader_user_id, status, created_at)
            VALUES (?, ?, ?, ?, ?, 'active', ?)
            """,
            (portfolio_id, company_id, "Cartera base cobranzas", "BASE", leader["id"] if leader else None, utc_now()),
        )
        if leader:
            connection.execute(
                "INSERT OR IGNORE INTO portfolio_users (company_id, portfolio_id, user_id, role) VALUES (?, ?, ?, 'leader')",
                (company_id, portfolio_id, leader["id"]),
            )


def ensure_tenant_basics(connection: sqlite3.Connection, company_id: int, company_name: str) -> None:
    if connection.execute("SELECT COUNT(*) FROM settings WHERE company_id = ?", (company_id,)).fetchone()[0] == 0:
        connection.execute(
            "INSERT INTO settings (company_id, monthly_goal, promise_alert_days, critical_dpd) VALUES (?, ?, ?, ?)",
            (company_id, 85000000, 2, 60),
        )
    if connection.execute("SELECT COUNT(*) FROM typification_nodes WHERE company_id = ?", (company_id,)).fetchone()[0] == 0:
        seed_typifications(connection, company_id)
    if connection.execute("SELECT COUNT(*) FROM channel_accounts WHERE company_id = ?", (company_id,)).fetchone()[0] == 0:
        seed_channel_accounts(connection, company_id, company_name)


def purge_platform_operational_data(connection: sqlite3.Connection) -> None:
    company_ids = [
        row["id"]
        for row in connection.execute("SELECT id FROM companies WHERE slug <> 'icodeup-platform'")
    ]
    if not company_ids:
        return
    placeholders = ",".join("?" for _ in company_ids)
    for table in PLATFORM_OPERATION_TABLES:
        if "company_id" in table_columns(connection, table):
            connection.execute(f"DELETE FROM {table} WHERE company_id IN ({placeholders})", tuple(company_ids))
    connection.commit()


def operational_db_for_user(user: sqlite3.Row) -> sqlite3.Connection:
    if user["role"] == "platform_admin" or user["company_slug"] == "icodeup-platform":
        return db()
    with db() as platform_connection:
        company = tenant_company_row(platform_connection, user["company_id"])
        if company:
            ensure_tenant_databases(platform_connection)
    return tenant_db_for_slug(user["company_slug"])


def operational_db_for_company(platform_connection: sqlite3.Connection, company_id: int) -> sqlite3.Connection:
    company = tenant_company_row(platform_connection, company_id)
    if not company:
        raise ValueError("Empresa no encontrada.")
    ensure_tenant_databases(platform_connection)
    return tenant_db_for_slug(company["slug"])


def migrate_users_table_if_needed(connection: sqlite3.Connection) -> None:
    row = connection.execute("SELECT sql FROM sqlite_master WHERE type = 'table' AND name = 'users'").fetchone()
    if not row:
        return
    sql = row["sql"] or ""
    columns = table_columns(connection, "users")
    if "CHECK" not in sql and "leader_id" in columns:
        return

    connection.execute("PRAGMA foreign_keys = OFF")
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS users_new (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          company_id INTEGER NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
          name TEXT NOT NULL,
          email TEXT NOT NULL,
          role TEXT NOT NULL,
          leader_id INTEGER REFERENCES users(id),
          password_hash TEXT NOT NULL,
          active INTEGER NOT NULL DEFAULT 1,
          created_at TEXT NOT NULL,
          UNIQUE(company_id, email)
        )
        """
    )
    leader_expr = "leader_id" if "leader_id" in columns else "NULL"
    connection.execute(
        f"""
        INSERT OR IGNORE INTO users_new
        (id, company_id, name, email, role, leader_id, password_hash, active, created_at)
        SELECT id, company_id, name, email, role, {leader_expr}, password_hash, active, created_at
        FROM users
        """
    )
    connection.execute("DROP TABLE users")
    connection.execute("ALTER TABLE users_new RENAME TO users")
    connection.execute("PRAGMA foreign_keys = ON")


def seed_database(connection: sqlite3.Connection) -> None:
    platform_id = create_company(connection, "IcodeUp Platform", "icodeup-platform", "PLATFORM")
    ensure_user(connection, platform_id, "IcodeUp Plataforma", "platform@icodeup.com", "platform_admin", "Platform123!")
    pepe_id = create_company(connection, "Pepe Perez", "pepe-perez", "NIT 901000111")
    martinez_id = create_company(connection, "Inversiones Martinez", "inversiones-martinez", "NIT 901222333")
    seed_users(connection, pepe_id, "pepeperez.com")
    seed_users(connection, martinez_id, "martinez.com")
    seed_company_state(connection, pepe_id, "Pepe Perez")
    seed_company_state(connection, martinez_id, "Inversiones Martinez")
    connection.commit()


def create_company(connection: sqlite3.Connection, name: str, slug: str, tax_id: str) -> int:
    cursor = connection.execute(
        "INSERT INTO companies (name, slug, tax_id, created_at) VALUES (?, ?, ?, ?)",
        (name, slug, tax_id, utc_now()),
    )
    return int(cursor.lastrowid)


def seed_users(connection: sqlite3.Connection, company_id: int, domain: str) -> None:
    users = [
        ("Super Usuario", f"super@{domain}", "superadmin", "Super123!"),
        ("Administrador Operativo", f"admin@{domain}", "admin", "Admin123!"),
        ("Coordinador Cobranzas", f"lider@{domain}", "coordinator", "Lider123!"),
        ("Gestor Estandar", f"gestor@{domain}", "agent", "Gestor123!"),
        ("Supervisor Calidad", f"calidad@{domain}", "quality", "Calidad123!"),
    ]
    for name, email, role, password in users:
        connection.execute(
            """
            INSERT INTO users (company_id, name, email, role, password_hash, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (company_id, name, email, role, hash_password(password), utc_now()),
        )
    leader = connection.execute(
        "SELECT id FROM users WHERE company_id = ? AND role = 'coordinator' LIMIT 1",
        (company_id,),
    ).fetchone()
    if leader:
        connection.execute(
            "UPDATE users SET leader_id = ? WHERE company_id = ? AND role = 'agent'",
            (leader["id"], company_id),
        )


def seed_company_state(connection: sqlite3.Connection, company_id: int, company_name: str) -> None:
    connection.execute(
        "INSERT INTO settings (company_id, monthly_goal, promise_alert_days, critical_dpd) VALUES (?, ?, ?, ?)",
        (company_id, 85000000 if "Pepe" in company_name else 120000000, 2, 60),
    )

    if "Pepe" in company_name:
        customers = [
            customer("C-1001", "Mariana Torres", "CC 1002457891", "+57 300 456 7788", "mariana.torres@email.com", "Bogota", "Consumo", "Gestor Estandar", 6420000, 8400000, 18, "Contactado", "Medio", 81, "Enviar link de pago y confirmar promesa", add_days(-1), add_days(1), "Alta", ["Credito libre inversion 8842"], ["Mora temprana"], "Prefiere WhatsApp despues de las 6 p.m."),
            customer("C-1002", "Alimentos La Quinta SAS", "NIT 901221334", "+57 601 772 1188", "tesoreria@laquinta.co", "Medellin", "Pyme", "Administrador", 28400000, 32000000, 74, "Promesa", "Alto", 94, "Confirmar pago prometido y escalar si incumple", add_days(-3), today(), "Media", ["Credito capital trabajo 1120"], ["Cuenta clave", "Promesa critica"], "Pagos dependen de recaudo semanal."),
            customer("C-1003", "Julian Herrera", "CC 80222333", "+57 310 889 4400", "julian.h@correo.com", "Cali", "Tarjeta", "Gestor Estandar", 3180000, 5100000, 41, "Sin contacto", "Medio", 72, "Intentar llamada antes de SMS preventivo", add_days(-9), today(), "Baja", ["Tarjeta credito 4412"], ["Telefono intermitente"], "No responde llamadas en horario laboral."),
        ]
    else:
        customers = [
            customer("C-2001", "Ferreteria El Norte SAS", "NIT 900551212", "+57 604 771 4421", "pagos@elnorte.co", "Medellin", "Pyme", "Administrador", 37600000, 42000000, 82, "Disputa", "Alto", 91, "Revisar soporte de pago no aplicado", add_days(-2), today(), "Alta", ["Credito proveedor 8801"], ["Disputa abierta"], "Reporta transferencia pendiente por aplicar."),
            customer("C-2002", "Ana Maria Castillo", "CC 43211098", "+57 301 228 9901", "ana.castillo@email.com", "Pereira", "Consumo", "Gestor Estandar", 2320000, 3900000, 12, "Contactado", "Bajo", 49, "Enviar recordatorio de normalizacion", today(), add_days(3), "Alta", ["Credito consumo 2210"], ["Mora temprana"], "Solicita link por email."),
            customer("C-2003", "Grupo Comercial Rivera", "NIT 901774410", "+57 601 444 9012", "contabilidad@rivera.co", "Bogota", "Pyme", "Supervisor Calidad", 68100000, 68100000, 131, "Escalado", "Alto", 99, "Comite de normalizacion y ruta juridica", add_days(-7), add_days(1), "Media", ["Credito rotativo 4410"], ["Alto valor"], "Pendiente acuerdo formal con gerencia."),
        ]

    for item in customers:
        insert_customer(connection, company_id, item)
        insert_interaction(connection, company_id, item["id"], "Caso creado", item["notes"], item["agent"], "Sistema", add_days(-7))

    insert_promise(connection, company_id, promise("P-2001", customers[1]["id"], 8000000, today(), "WhatsApp", "Vigente"))
    insert_promise(connection, company_id, promise("P-2002", customers[0]["id"], 900000, add_days(-2), "WhatsApp", "Vencida"))
    insert_payment(connection, company_id, payment("PAY-3001", customers[0]["id"], 1080000, add_days(-10), "Transferencia", "TRF-55380"))
    insert_campaign(connection, company_id, campaign("CAM-4001", "Mora temprana WhatsApp", "Consumo", "WhatsApp", "Hola {{nombre}}, tu saldo vencido es {{saldo}}. Responde para acordar pago.", add_days(-6), 120, 54, 18, 9))
    seed_typifications(connection, company_id)
    seed_channel_accounts(connection, company_id, company_name)


def customer(id_, name, document, phone, email, city, segment, agent, balance, original_balance, dpd, status, risk, priority, next_action, last_contact, next_contact, contactability, accounts, tags, notes):
    return locals() | {"id": id_}


def promise(id_, customer_id, amount, date, channel, status):
    return {"id": id_, "customerId": customer_id, "amount": amount, "date": date, "channel": channel, "status": status, "createdAt": today()}


def payment(id_, customer_id, amount, date, method, reference):
    return {"id": id_, "customerId": customer_id, "amount": amount, "date": date, "method": method, "reference": reference}


def campaign(id_, name, segment, channel, template, created_at, sent, contacted, promises_, payments_):
    return {"id": id_, "name": name, "segment": segment, "channel": channel, "template": template, "createdAt": created_at, "sent": sent, "contacted": contacted, "promises": promises_, "payments": payments_}


def seed_typifications(connection: sqlite3.Connection, company_id: int) -> None:
    nodes = [
        ("T-CONTACTO", None, "Contacto", "CONTACTO", None, 0, 0, None, 1),
        ("T-NOCONTACTO", None, "No contacto", "NO_CONTACTO", "Sin contacto", 0, 0, None, 2),
        ("T-DISPUTA", None, "Disputa o reclamo", "DISPUTA", "Disputa", 0, 0, None, 3),
        ("T-CON-TITULAR", "T-CONTACTO", "Titular contactado", "TITULAR", "Contactado", 0, 0, None, 1),
        ("T-CON-TERCERO", "T-CONTACTO", "Tercero contactado", "TERCERO", "Contactado", 0, 0, None, 2),
        ("T-PROMESA", "T-CON-TITULAR", "Promesa de pago", "PROMESA", "Promesa", 1, 0, None, 1),
        ("T-PAGO", "T-CON-TITULAR", "Pago realizado", "PAGO", "Contactado", 0, 1, None, 2),
        ("T-RENEGOCIAR", "T-CON-TITULAR", "Solicita refinanciacion", "RENEGOCIAR", "Contactado", 0, 0, None, 3),
        ("T-NO-PUEDE", "T-CON-TITULAR", "No puede pagar", "NO_PUEDE_PAGAR", "Escalado", 0, 0, None, 4),
        ("T-MENSAJE", "T-CON-TERCERO", "Mensaje dejado", "MENSAJE_TERCERO", "Contactado", 0, 0, None, 1),
        ("T-NO-CONTESTA", "T-NOCONTACTO", "No contesta", "NO_CONTESTA", "Sin contacto", 0, 0, "Telefono", 1),
        ("T-NUMERO-ERRADO", "T-NOCONTACTO", "Numero errado", "NUMERO_ERRADO", "Sin contacto", 0, 0, "Telefono", 2),
        ("T-WA-SIN-RESPUESTA", "T-NOCONTACTO", "WhatsApp sin respuesta", "WA_SIN_RESPUESTA", "Sin contacto", 0, 0, "WhatsApp", 3),
        ("T-SOPORTE-PAGO", "T-DISPUTA", "Pago no aplicado", "PAGO_NO_APLICADO", "Disputa", 0, 0, None, 1),
        ("T-COBRO-NO-RECONOCIDO", "T-DISPUTA", "No reconoce obligacion", "NO_RECONOCE", "Disputa", 0, 0, None, 2),
    ]
    for node in nodes:
        connection.execute(
            """
            INSERT INTO typification_nodes
            (id, company_id, parent_id, label, code, next_status, requires_promise, requires_payment, channel, sort_order)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (node[0], company_id, node[1], node[2], node[3], node[4], node[5], node[6], node[7], node[8]),
        )


def ensure_channel_defaults(connection: sqlite3.Connection) -> None:
    connection.commit()


def ensure_operational_defaults(connection: sqlite3.Connection) -> None:
    companies = connection.execute("SELECT id, name, slug FROM companies").fetchall()
    for company in companies:
        if company["slug"] == "icodeup-platform":
            continue
        if company["slug"] not in ("pepe-perez", "inversiones-martinez"):
            continue
        domain = "pepeperez.com" if company["slug"] == "pepe-perez" else "martinez.com"
        ensure_user(connection, company["id"], "Super Usuario", f"super@{domain}", "superadmin", "Super123!")
        admin = ensure_user(connection, company["id"], "Administrador Operativo", f"admin@{domain}", "admin", "Admin123!")
        leader = ensure_user(connection, company["id"], "Coordinador Cobranzas", f"lider@{domain}", "coordinator", "Lider123!")
        ensure_user(connection, company["id"], "Gestor Estandar", f"gestor@{domain}", "agent", "Gestor123!", leader_id=leader)
        ensure_user(connection, company["id"], "Supervisor Calidad", f"calidad@{domain}", "quality", "Calidad123!", leader_id=leader)
        connection.execute(
            "UPDATE users SET leader_id = ? WHERE company_id = ? AND role = 'agent' AND leader_id IS NULL",
            (leader, company["id"]),
        )
    connection.commit()


def ensure_platform_defaults(connection: sqlite3.Connection) -> None:
    row = connection.execute("SELECT id FROM companies WHERE slug = 'icodeup-platform'").fetchone()
    if row:
        platform_id = row["id"]
    else:
        platform_id = create_company(connection, "IcodeUp Platform", "icodeup-platform", "PLATFORM")
    ensure_user(connection, platform_id, "IcodeUp Plataforma", "platform@icodeup.com", "platform_admin", "Platform123!")
    connection.commit()


def ensure_user(connection: sqlite3.Connection, company_id: int, name: str, email: str, role: str, password: str, leader_id: int | None = None) -> int:
    existing = connection.execute(
        "SELECT id FROM users WHERE company_id = ? AND email = ?",
        (company_id, email),
    ).fetchone()
    if existing:
        connection.execute(
            "UPDATE users SET name = ?, role = ?, leader_id = COALESCE(leader_id, ?), active = 1 WHERE id = ?",
            (name, role, leader_id, existing["id"]),
        )
        return int(existing["id"])
    cursor = connection.execute(
        """
        INSERT INTO users (company_id, name, email, role, leader_id, password_hash, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (company_id, name, email, role, leader_id, hash_password(password), utc_now()),
    )
    return int(cursor.lastrowid)


def seed_channel_accounts(connection: sqlite3.Connection, company_id: int, company_name: str) -> None:
    slug = "pepeperez" if "Pepe" in company_name else "martinez"
    accounts = [
        channel_account("WA-1", "whatsapp", "Linea principal cobranzas", "+57 300 555 0101", "WhatsApp Web / Cloud API pendiente", 1, {"mode": "link", "businessProfile": company_name}),
        channel_account("WA-2", "whatsapp", "Linea acuerdos de pago", "+57 300 555 0102", "WhatsApp Web / Cloud API pendiente", 0, {"mode": "link", "businessProfile": company_name}),
        channel_account("EMAIL-1", "email", "Correo cobranzas", f"cobranzas@{slug}.com", "SMTP/API pendiente", 1, {"signature": f"Equipo de cobranzas {company_name}"}),
        channel_account("EMAIL-2", "email", "Correo acuerdos", f"acuerdos@{slug}.com", "SMTP/API pendiente", 0, {"signature": f"Equipo de normalizacion {company_name}"}),
        channel_account("TEL-1", "telephony", "Telefonia WebRTC futura", "PBX no configurada", "SIP/WebRTC pendiente", 1, {"mode": "planned", "sipDomain": "", "webSocketUrl": ""}),
    ]
    for item in accounts:
        insert_channel_account(connection, company_id, item)


def channel_account(id_, type_, label, value, provider, is_default, config):
    return {
        "id": id_,
        "type": type_,
        "label": label,
        "value": value,
        "provider": provider,
        "status": "active",
        "isDefault": bool(is_default),
        "config": config,
    }


def insert_customer(connection: sqlite3.Connection, company_id: int, item: dict) -> None:
    connection.execute(
        """
        INSERT INTO customers
        (id, company_id, name, document, phone, email, city, segment, agent, balance, original_balance,
         dpd, status, risk, priority, next_action, last_contact, next_contact, contactability,
         accounts_json, tags_json, portfolio_id, demographic_json, financial_json, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            item["id"],
            company_id,
            item["name"],
            item["document"],
            item.get("phone", ""),
            item.get("email", ""),
            item.get("city", ""),
            item.get("segment", ""),
            item.get("agent", ""),
            int(item.get("balance", 0)),
            int(item.get("originalBalance", item.get("original_balance", item.get("balance", 0)))),
            int(item.get("dpd", 0)),
            item.get("status", "Sin contacto"),
            item.get("risk", "Medio"),
            int(item.get("priority", 0)),
            item.get("nextAction", item.get("next_action", "")),
            item.get("lastContact", item.get("last_contact", "")),
            item.get("nextContact", item.get("next_contact", "")),
            item.get("contactability", "Media"),
            json_dumps(item.get("accounts", [])),
            json_dumps(item.get("tags", [])),
            item.get("portfolioId", item.get("portfolio_id", "CAR-BASE")),
            json_dumps(item.get("demographic", {})),
            json_dumps(item.get("financial", {})),
            item.get("notes", ""),
        ),
    )


def insert_interaction(connection: sqlite3.Connection, company_id: int, customer_id: str, type_: str, note: str, agent: str, channel: str, created_at: str) -> None:
    connection.execute(
        """
        INSERT INTO interactions (company_id, customer_id, type, note, agent, channel, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (company_id, customer_id, type_, note or "", agent or "Sistema", channel or "Sistema", created_at or today()),
    )


def insert_promise(connection: sqlite3.Connection, company_id: int, item: dict) -> None:
    connection.execute(
        """
        INSERT INTO promises (id, company_id, customer_id, amount, date, channel, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (item["id"], company_id, item["customerId"], int(item["amount"]), item["date"], item["channel"], item["status"], item.get("createdAt", today())),
    )


def insert_payment(connection: sqlite3.Connection, company_id: int, item: dict) -> None:
    connection.execute(
        """
        INSERT INTO payments (id, company_id, customer_id, amount, date, method, reference)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (item["id"], company_id, item["customerId"], int(item["amount"]), item["date"], item["method"], item.get("reference", "")),
    )


def insert_campaign(connection: sqlite3.Connection, company_id: int, item: dict) -> None:
    connection.execute(
        """
        INSERT INTO campaigns (id, company_id, name, segment, channel, template, created_at, sent, contacted, promises, payments)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            item["id"],
            company_id,
            item["name"],
            item["segment"],
            item["channel"],
            item["template"],
            item.get("createdAt", today()),
            int(item.get("sent", 0)),
            int(item.get("contacted", 0)),
            int(item.get("promises", 0)),
            int(item.get("payments", 0)),
        ),
    )


def insert_channel_account(connection: sqlite3.Connection, company_id: int, item: dict) -> None:
    connection.execute(
        """
        INSERT INTO channel_accounts
        (id, company_id, type, label, value, provider, status, is_default, config_json, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            item["id"],
            company_id,
            item["type"],
            item["label"],
            item["value"],
            item.get("provider", ""),
            item.get("status", "active"),
            1 if item.get("isDefault") else 0,
            json_dumps(item.get("config", {})),
            item.get("createdAt", utc_now()),
        ),
    )


def build_state(connection: sqlite3.Connection, company_id: int, user: sqlite3.Row | None = None) -> dict:
    settings = connection.execute(
        "SELECT monthly_goal, promise_alert_days, critical_dpd FROM settings WHERE company_id = ?",
        (company_id,),
    ).fetchone()
    scope_sql, scope_params = customer_scope_sql(connection, company_id, user)
    customers = []
    for row in connection.execute(f"SELECT * FROM customers WHERE {scope_sql} ORDER BY priority DESC", scope_params):
        timeline = [
            {
                "type": item["type"],
                "note": item["note"],
                "agent": item["agent"],
                "date": item["created_at"][:10],
                "channel": item["channel"],
            }
            for item in connection.execute(
                """
                SELECT type, note, agent, channel, created_at
                FROM interactions
                WHERE company_id = ? AND customer_id = ?
                ORDER BY created_at DESC, id DESC
                LIMIT 20
                """,
                (company_id, row["id"]),
            )
        ]
        customers.append(
            {
                "id": row["id"],
                "name": row["name"],
                "document": row["document"],
                "phone": row["phone"],
                "email": row["email"],
                "city": row["city"],
                "segment": row["segment"],
                "agent": row["agent"],
                "balance": row["balance"],
                "originalBalance": row["original_balance"],
                "dpd": row["dpd"],
                "status": row["status"],
                "risk": row["risk"],
                "priority": row["priority"],
                "nextAction": row["next_action"],
                "lastContact": row["last_contact"],
                "nextContact": row["next_contact"],
                "contactability": row["contactability"],
                "accounts": json_loads(row["accounts_json"], []),
                "tags": json_loads(row["tags_json"], []),
                "portfolioId": row["portfolio_id"] if "portfolio_id" in row.keys() else "",
                "demographic": json_loads(row["demographic_json"] if "demographic_json" in row.keys() else "", {}),
                "financial": json_loads(row["financial_json"] if "financial_json" in row.keys() else "", {}),
                "notes": row["notes"],
                "timeline": timeline,
            }
        )

    visible_user_rows = visible_users(connection, company_id, user)
    users = [
        {
            "id": row["id"],
            "name": row["name"],
            "email": row["email"],
            "role": row["role"],
            "leaderId": row["leader_id"],
            "active": bool(row["active"]),
        }
        for row in visible_user_rows
    ]
    agents = sorted(
        {row["name"] for row in visible_user_rows if row["role"] in ("agent", "admin", "coordinator") and row["active"]}
        | {customer["agent"] for customer in customers if customer.get("agent")}
    )
    segments = sorted({row["segment"] for row in connection.execute("SELECT DISTINCT segment FROM customers WHERE company_id = ?", (company_id,))} | {"Consumo", "Microcredito", "Hipotecario", "Pyme", "Tarjeta"})
    customer_ids = {customer["id"] for customer in customers}
    promises = [
        {
            "id": row["id"],
            "customerId": row["customer_id"],
            "amount": row["amount"],
            "date": row["date"],
            "channel": row["channel"],
            "status": row["status"],
            "createdAt": row["created_at"],
        }
        for row in connection.execute("SELECT * FROM promises WHERE company_id = ? ORDER BY date ASC", (company_id,))
        if row["customer_id"] in customer_ids
    ]
    payments = [
        {
            "id": row["id"],
            "customerId": row["customer_id"],
            "amount": row["amount"],
            "date": row["date"],
            "method": row["method"],
            "reference": row["reference"],
        }
        for row in connection.execute("SELECT * FROM payments WHERE company_id = ? ORDER BY date DESC", (company_id,))
        if row["customer_id"] in customer_ids
    ]
    campaigns = [
        {
            "id": row["id"],
            "name": row["name"],
            "segment": row["segment"],
            "channel": row["channel"],
            "template": row["template"],
            "createdAt": row["created_at"],
            "sent": row["sent"],
            "contacted": row["contacted"],
            "promises": row["promises"],
            "payments": row["payments"],
        }
        for row in connection.execute("SELECT * FROM campaigns WHERE company_id = ? ORDER BY created_at DESC", (company_id,))
    ]
    typifications = [
        {
            "id": row["id"],
            "parentId": row["parent_id"],
            "label": row["label"],
            "code": row["code"],
            "nextStatus": row["next_status"],
            "requiresPromise": bool(row["requires_promise"]),
            "requiresPayment": bool(row["requires_payment"]),
            "channel": row["channel"],
            "sortOrder": row["sort_order"],
        }
        for row in connection.execute("SELECT * FROM typification_nodes WHERE company_id = ? ORDER BY sort_order, label", (company_id,))
    ]
    portfolios = [
        {
            "id": row["id"],
            "name": row["name"],
            "code": row["code"],
            "leaderUserId": row["leader_user_id"],
            "status": row["status"],
            "createdAt": row["created_at"],
            "members": [
                {
                    "userId": member["user_id"],
                    "name": member["name"],
                    "email": member["email"],
                    "role": member["portfolio_role"],
                    "userRole": member["user_role"],
                }
                for member in connection.execute(
                    """
                    SELECT portfolio_users.user_id, portfolio_users.role AS portfolio_role,
                           users.name, users.email, users.role AS user_role
                    FROM portfolio_users
                    JOIN users ON users.id = portfolio_users.user_id
                    WHERE portfolio_users.company_id = ? AND portfolio_users.portfolio_id = ?
                    ORDER BY portfolio_users.role, users.name
                    """,
                    (company_id, row["id"]),
                )
            ],
        }
        for row in connection.execute("SELECT * FROM portfolios WHERE company_id = ? ORDER BY name", (company_id,))
    ]
    channel_accounts = [
        {
            "id": row["id"],
            "type": row["type"],
            "label": row["label"],
            "value": row["value"],
            "provider": row["provider"],
            "status": row["status"],
            "isDefault": bool(row["is_default"]),
            "config": json_loads(row["config_json"], {}),
            "createdAt": row["created_at"],
        }
        for row in connection.execute("SELECT * FROM channel_accounts WHERE company_id = ? ORDER BY is_default DESC, label", (company_id,))
    ]

    return {
        "settings": {
            "monthlyGoal": settings["monthly_goal"] if settings else 85000000,
            "promiseAlertDays": settings["promise_alert_days"] if settings else 2,
            "criticalDpd": settings["critical_dpd"] if settings else 60,
        },
        "agents": agents,
        "users": users,
        "portfolios": portfolios,
        "segments": segments,
        "customers": customers,
        "promises": promises,
        "payments": payments,
        "campaigns": campaigns,
        "typifications": typifications,
        "communication": {
            "whatsappNumbers": [item for item in channel_accounts if item["type"] == "whatsapp"],
            "emailAccounts": [item for item in channel_accounts if item["type"] == "email"],
            "telephonyAccounts": [item for item in channel_accounts if item["type"] == "telephony"],
        },
        "companies": platform_company_summary(connection) if user and user["role"] == "platform_admin" else [],
    }


def platform_company_summary(connection: sqlite3.Connection) -> list[dict]:
    rows = []
    for company in connection.execute("SELECT id, name, slug, tax_id, status, created_at FROM companies WHERE slug <> 'icodeup-platform' ORDER BY name"):
        with tenant_db_for_slug(company["slug"]) as tenant_connection:
            install_schema_from_template(connection, tenant_connection)
            mirror_company_and_users(connection, tenant_connection, company["id"])
            ensure_tenant_defaults(tenant_connection, company["id"], company["name"], company["slug"])
            tenant_connection.commit()
            users = [
                {
                    "id": row["id"],
                    "name": row["name"],
                    "email": row["email"],
                    "role": row["role"],
                    "leaderId": row["leader_id"],
                    "active": bool(row["active"]),
                }
                for row in tenant_connection.execute(
                    "SELECT id, name, email, role, leader_id, active FROM users WHERE company_id = ? ORDER BY role, name",
                    (company["id"],),
                )
            ]
            portfolios = []
            for portfolio in tenant_connection.execute(
                "SELECT id, name, code, leader_user_id, status, created_at FROM portfolios WHERE company_id = ? ORDER BY name",
                (company["id"],),
            ):
                customer_count = tenant_connection.execute(
                    "SELECT COUNT(*) FROM customers WHERE company_id = ? AND portfolio_id = ?",
                    (company["id"], portfolio["id"]),
                ).fetchone()[0]
                member_count = tenant_connection.execute(
                    "SELECT COUNT(*) FROM portfolio_users WHERE company_id = ? AND portfolio_id = ?",
                    (company["id"], portfolio["id"]),
                ).fetchone()[0]
                leader = tenant_connection.execute(
                    "SELECT name FROM users WHERE company_id = ? AND id = ?",
                    (company["id"], portfolio["leader_user_id"]),
                ).fetchone()
                portfolios.append({
                    "id": portfolio["id"],
                    "name": portfolio["name"],
                    "code": portfolio["code"],
                    "leaderUserId": portfolio["leader_user_id"],
                    "leaderName": leader["name"] if leader else "",
                    "status": portfolio["status"],
                    "createdAt": portfolio["created_at"],
                    "customers": customer_count,
                    "members": member_count,
                })
            counts = {
                "users": len(users),
                "portfolios": len(portfolios),
                "customers": tenant_connection.execute("SELECT COUNT(*) FROM customers WHERE company_id = ?", (company["id"],)).fetchone()[0],
            }
            typifications = [
                {
                    "id": row["id"],
                    "parentId": row["parent_id"],
                    "label": row["label"],
                    "code": row["code"],
                    "nextStatus": row["next_status"],
                    "requiresPromise": bool(row["requires_promise"]),
                    "requiresPayment": bool(row["requires_payment"]),
                    "channel": row["channel"],
                    "sortOrder": row["sort_order"],
                }
                for row in tenant_connection.execute(
                    "SELECT * FROM typification_nodes WHERE company_id = ? ORDER BY sort_order, label",
                    (company["id"],),
                )
            ]
            counts["typifications"] = len(typifications)
        rows.append({
            "id": company["id"],
            "name": company["name"],
            "slug": company["slug"],
            "taxId": company["tax_id"],
            "status": company["status"],
            "createdAt": company["created_at"],
            "counts": counts,
            "users": users,
            "portfolios": portfolios,
            "typifications": typifications,
        })
    return rows


def customer_scope_sql(connection: sqlite3.Connection, company_id: int, user: sqlite3.Row | None) -> tuple[str, tuple]:
    if not user or user["role"] in ("superadmin", "admin", "quality"):
        return "company_id = ?", (company_id,)
    if user["role"] == "agent":
        return "company_id = ? AND agent = ?", (company_id, user["name"])
    if user["role"] == "coordinator":
        team_names = [
            row["name"]
            for row in connection.execute(
                "SELECT name FROM users WHERE company_id = ? AND (leader_id = ? OR id = ?) AND active = 1",
                (company_id, user["id"], user["id"]),
            )
        ]
        if not team_names:
            return "company_id = ? AND agent = ?", (company_id, user["name"])
        placeholders = ",".join("?" for _ in team_names)
        return f"company_id = ? AND agent IN ({placeholders})", (company_id, *team_names)
    return "company_id = ?", (company_id,)


def visible_users(connection: sqlite3.Connection, company_id: int, user: sqlite3.Row | None) -> list[sqlite3.Row]:
    if not user or user["role"] in ("superadmin", "admin", "quality"):
        return connection.execute(
            "SELECT id, name, email, role, leader_id, active FROM users WHERE company_id = ? ORDER BY role, name",
            (company_id,),
        ).fetchall()
    if user["role"] == "agent":
        return connection.execute(
            "SELECT id, name, email, role, leader_id, active FROM users WHERE company_id = ? AND id = ?",
            (company_id, user["id"]),
        ).fetchall()
    if user["role"] == "coordinator":
        return connection.execute(
            """
            SELECT id, name, email, role, leader_id, active
            FROM users
            WHERE company_id = ? AND (id = ? OR leader_id = ?)
            ORDER BY role, name
            """,
            (company_id, user["id"], user["id"]),
        ).fetchall()
    return []


def replace_state(connection: sqlite3.Connection, company_id: int, state: dict, user: sqlite3.Row) -> None:
    if user["role"] == "quality":
        raise PermissionError("El rol de calidad es de solo lectura en esta fase.")

    full_company_write = user["role"] in ("superadmin", "admin")
    operational_write = user["role"] in ("superadmin", "admin", "coordinator")

    if user["role"] == "superadmin":
        settings = state.get("settings", {})
        connection.execute(
            """
            INSERT INTO settings (company_id, monthly_goal, promise_alert_days, critical_dpd)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(company_id) DO UPDATE SET
              monthly_goal = excluded.monthly_goal,
              promise_alert_days = excluded.promise_alert_days,
              critical_dpd = excluded.critical_dpd
            """,
            (
                company_id,
                int(settings.get("monthlyGoal", 85000000)),
                int(settings.get("promiseAlertDays", 2)),
                int(settings.get("criticalDpd", 60)),
            ),
        )

    if user["role"] in ("superadmin", "admin"):
        connection.execute("DELETE FROM channel_accounts WHERE company_id = ?", (company_id,))
        communication = state.get("communication", {})
        for item in communication.get("whatsappNumbers", []):
            insert_channel_account(connection, company_id, normalize_channel_account(item, "whatsapp"))
        for item in communication.get("emailAccounts", []):
            insert_channel_account(connection, company_id, normalize_channel_account(item, "email"))
        for item in communication.get("telephonyAccounts", []):
            insert_channel_account(connection, company_id, normalize_channel_account(item, "telephony"))

    if operational_write:
        for portfolio in state.get("portfolios", []):
            upsert_portfolio(connection, company_id, portfolio)

    if full_company_write:
        connection.execute("DELETE FROM interactions WHERE company_id = ?", (company_id,))
        connection.execute("DELETE FROM promises WHERE company_id = ?", (company_id,))
        connection.execute("DELETE FROM payments WHERE company_id = ?", (company_id,))
        connection.execute("DELETE FROM campaigns WHERE company_id = ?", (company_id,))
        connection.execute("DELETE FROM customers WHERE company_id = ?", (company_id,))
    else:
        existing_scope_sql, existing_scope_params = customer_scope_sql(connection, company_id, user)
        scoped_ids = {
            row["id"]
            for row in connection.execute(f"SELECT id FROM customers WHERE {existing_scope_sql}", existing_scope_params)
        }
        scoped_ids.update(item.get("id") for item in state.get("customers", []) if item.get("id"))
        delete_scoped_customer_data(connection, company_id, scoped_ids)

    for item in state.get("customers", []):
        if user["role"] == "agent":
            item["agent"] = user["name"]
        insert_customer(connection, company_id, item)
        for entry in reversed(item.get("timeline", [])):
            insert_interaction(
                connection,
                company_id,
                item["id"],
                entry.get("type", "Gestion"),
                entry.get("note", ""),
                entry.get("agent", user["name"]),
                entry.get("channel", "CRM"),
                entry.get("date", today()),
            )
    for item in state.get("promises", []):
        insert_promise(connection, company_id, item)
    for item in state.get("payments", []):
        insert_payment(connection, company_id, item)
    for item in state.get("campaigns", []):
        if full_company_write:
            insert_campaign(connection, company_id, item)

    audit(connection, company_id, user["id"], "sync_state", "company", str(company_id), {"customers": len(state.get("customers", []))})


def delete_scoped_customer_data(connection: sqlite3.Connection, company_id: int, customer_ids: set[str]) -> None:
    if not customer_ids:
        return
    placeholders = ",".join("?" for _ in customer_ids)
    params = (company_id, *customer_ids)
    connection.execute(f"DELETE FROM interactions WHERE company_id = ? AND customer_id IN ({placeholders})", params)
    connection.execute(f"DELETE FROM promises WHERE company_id = ? AND customer_id IN ({placeholders})", params)
    connection.execute(f"DELETE FROM payments WHERE company_id = ? AND customer_id IN ({placeholders})", params)
    connection.execute(f"DELETE FROM customers WHERE company_id = ? AND id IN ({placeholders})", params)


def upsert_portfolio(connection: sqlite3.Connection, company_id: int, item: dict) -> None:
    portfolio_id = item.get("id") or f"CAR-{secrets.token_hex(3).upper()}"
    connection.execute(
        """
        INSERT INTO portfolios (id, company_id, name, code, leader_user_id, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(company_id, id) DO UPDATE SET
          name = excluded.name,
          code = excluded.code,
          leader_user_id = excluded.leader_user_id,
          status = excluded.status
        """,
        (
            portfolio_id,
            company_id,
            item.get("name") or "Cartera sin nombre",
            item.get("code") or portfolio_id,
            item.get("leaderUserId"),
            item.get("status") or "active",
            item.get("createdAt") or utc_now(),
        ),
    )


def normalize_channel_account(item: dict, type_: str) -> dict:
    return {
        "id": item.get("id") or f"{type_.upper()}-{secrets.token_hex(3)}",
        "type": type_,
        "label": item.get("label") or "Canal sin nombre",
        "value": item.get("value") or "",
        "provider": item.get("provider") or "",
        "status": item.get("status") or "active",
        "isDefault": bool(item.get("isDefault")),
        "config": item.get("config") or {},
        "createdAt": item.get("createdAt") or utc_now(),
    }


def next_text_id(connection: sqlite3.Connection, table: str, company_id: int, prefix: str) -> str:
    rows = connection.execute(f"SELECT id FROM {table} WHERE company_id = ?", (company_id,)).fetchall()
    numbers = [
        int("".join(char for char in str(row["id"]) if char.isdigit()) or 0)
        for row in rows
    ]
    return f"{prefix}-{max(numbers or [1000]) + 1}"


def risk_from_dpd(dpd: int, balance: int) -> str:
    if dpd >= 61 or balance >= 20000000:
        return "Alto"
    if dpd >= 16 or balance >= 4000000:
        return "Medio"
    return "Bajo"


def score_customer_payload(dpd: int, balance: int, status: str, contactability: str) -> int:
    risk = risk_from_dpd(dpd, balance)
    risk_score = 28 if risk == "Alto" else 16 if risk == "Medio" else 7
    dpd_score = min(35, round(dpd / 3))
    balance_score = min(25, round(balance / 2000000))
    status_score = 10 if status == "Promesa" else 7 if status == "Sin contacto" else 9 if status == "Escalado" else 3
    contact_score = 5 if contactability == "Alta" else 3 if contactability == "Media" else 1
    return min(99, risk_score + dpd_score + balance_score + status_score + contact_score)


def normalize_typification_node(connection: sqlite3.Connection, company_id: int, item: dict) -> dict:
    label = (item.get("label") or "").strip()
    code = (item.get("code") or label).strip().upper()
    node_id = (item.get("id") or f"T-{normalize_slug(code).upper()[:28]}").strip()
    if not label or not code:
        raise ValueError("Nombre y codigo de tipificacion son obligatorios.")
    original_id = node_id
    suffix = 1
    while not item.get("id") and connection.execute(
        "SELECT id FROM typification_nodes WHERE company_id = ? AND id = ?",
        (company_id, node_id),
    ).fetchone():
        suffix += 1
        node_id = f"{original_id}-{suffix}"
    parent_id = item.get("parentId") or None
    if parent_id == node_id:
        raise ValueError("Un nodo no puede ser padre de si mismo.")
    if parent_id and not connection.execute(
        "SELECT id FROM typification_nodes WHERE company_id = ? AND id = ?",
        (company_id, parent_id),
    ).fetchone():
        raise ValueError("El nodo padre no existe en esta empresa.")
    return {
        "id": node_id,
        "parentId": parent_id,
        "label": label,
        "code": code,
        "nextStatus": (item.get("nextStatus") or "").strip(),
        "requiresPromise": bool(item.get("requiresPromise")),
        "requiresPayment": bool(item.get("requiresPayment")),
        "channel": (item.get("channel") or "").strip(),
        "sortOrder": int(item.get("sortOrder") or 0),
    }


def upsert_typification_node(connection: sqlite3.Connection, company_id: int, item: dict) -> dict:
    node = normalize_typification_node(connection, company_id, item)
    connection.execute(
        """
        INSERT INTO typification_nodes
        (id, company_id, parent_id, label, code, next_status, requires_promise, requires_payment, channel, sort_order)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(company_id, id) DO UPDATE SET
          parent_id = excluded.parent_id,
          label = excluded.label,
          code = excluded.code,
          next_status = excluded.next_status,
          requires_promise = excluded.requires_promise,
          requires_payment = excluded.requires_payment,
          channel = excluded.channel,
          sort_order = excluded.sort_order
        """,
        (
            node["id"],
            company_id,
            node["parentId"],
            node["label"],
            node["code"],
            node["nextStatus"],
            1 if node["requiresPromise"] else 0,
            1 if node["requiresPayment"] else 0,
            node["channel"],
            node["sortOrder"],
        ),
    )
    return node


def audit(connection: sqlite3.Connection, company_id: int | None, user_id: int | None, action: str, entity: str, entity_id: str, detail: dict) -> None:
    connection.execute(
        """
        INSERT INTO audit_log (company_id, user_id, action, entity, entity_id, detail_json, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (company_id, user_id, action, entity, entity_id, json_dumps(detail), utc_now()),
    )


def get_session_user(handler: BaseHTTPRequestHandler) -> sqlite3.Row | None:
    raw_cookie = handler.headers.get("Cookie", "")
    cookie = SimpleCookie(raw_cookie)
    token = cookie.get(SESSION_COOKIE)
    if not token:
        return None
    session_id = token.value
    with db() as connection:
        row = connection.execute(
            """
            SELECT users.*, companies.name AS company_name, companies.slug AS company_slug
            FROM sessions
            JOIN users ON users.id = sessions.user_id
            JOIN companies ON companies.id = users.company_id
            WHERE sessions.id = ? AND sessions.expires_at > ?
            """,
            (session_id, utc_now()),
        ).fetchone()
        return row


class CRMHandler(BaseHTTPRequestHandler):
    server_version = "IcodeUpCRM/0.1"

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/api/health":
            self.json({
                "ok": True,
                "platformDatabase": str(PLATFORM_DB_PATH),
                "tenantDirectory": str(TENANT_DIR),
            })
        elif parsed.path == "/api/companies":
            self.handle_companies()
        elif parsed.path == "/api/session":
            self.handle_session()
        elif parsed.path == "/api/state":
            self.require_user(self.handle_state_get)
        elif parsed.path == "/api/audit":
            self.require_user(self.handle_audit_get)
        else:
            self.serve_static(parsed.path)

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/api/login":
            self.handle_login()
        elif parsed.path == "/api/logout":
            self.handle_logout()
        elif parsed.path == "/api/users":
            self.require_user(self.handle_user_create)
        elif parsed.path == "/api/portfolio-users":
            self.require_user(self.handle_portfolio_user_assign)
        elif parsed.path == "/api/platform/companies":
            self.require_user(self.handle_platform_company_create)
        elif parsed.path == "/api/platform/portfolios":
            self.require_user(self.handle_platform_portfolio_create)
        elif parsed.path == "/api/platform/users":
            self.require_user(self.handle_platform_user_create)
        elif parsed.path == "/api/platform/users/status":
            self.require_user(self.handle_platform_user_status)
        elif parsed.path == "/api/platform/portfolios/status":
            self.require_user(self.handle_platform_portfolio_status)
        elif parsed.path == "/api/platform/typifications":
            self.require_user(self.handle_platform_typification_upsert)
        elif parsed.path == "/api/platform/typifications/delete":
            self.require_user(self.handle_platform_typification_delete)
        elif parsed.path == "/api/platform/customers":
            self.require_user(self.handle_platform_customer_create)
        else:
            self.error_json(HTTPStatus.NOT_FOUND, "Ruta no encontrada.")

    def do_PUT(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/api/state":
            self.require_user(self.handle_state_put)
        else:
            self.error_json(HTTPStatus.NOT_FOUND, "Ruta no encontrada.")

    def require_user(self, callback) -> None:
        user = get_session_user(self)
        if not user:
            self.error_json(HTTPStatus.UNAUTHORIZED, "Debes iniciar sesion.")
            return
        callback(user)

    def handle_companies(self) -> None:
        self.json({"companies": []})

    def handle_session(self) -> None:
        user = get_session_user(self)
        if not user:
            self.error_json(HTTPStatus.UNAUTHORIZED, "Debes iniciar sesion.")
            return
        self.json({"user": public_user(user)})

    def handle_login(self) -> None:
        data = self.read_json()
        email = (data.get("email") or "").strip().lower()
        password = data.get("password") or ""
        company_id = data.get("companyId")
        if not email or not password:
            self.error_json(HTTPStatus.BAD_REQUEST, "Email y contrasena son obligatorios.")
            return

        with db() as connection:
            if company_id:
                user = connection.execute(
                    """
                    SELECT users.*, companies.name AS company_name, companies.slug AS company_slug
                    FROM users
                    JOIN companies ON companies.id = users.company_id
                    WHERE users.email = ? AND users.company_id = ? AND users.active = 1
                    """,
                    (email, company_id),
                ).fetchone()
            else:
                matches = connection.execute(
                    """
                    SELECT users.*, companies.name AS company_name, companies.slug AS company_slug
                    FROM users
                    JOIN companies ON companies.id = users.company_id
                    WHERE users.email = ? AND users.active = 1
                    """,
                    (email,),
                ).fetchall()
                if len(matches) > 1:
                    self.error_json(HTTPStatus.CONFLICT, "Ese email existe en mas de una empresa. Usa un email corporativo unico por tenant.")
                    return
                user = matches[0] if matches else None

            if not user or not verify_password(password, user["password_hash"]):
                self.error_json(HTTPStatus.UNAUTHORIZED, "Credenciales invalidas.")
                return

            token = secrets.token_urlsafe(32)
            expires_at = (datetime.now(timezone.utc) + timedelta(hours=SESSION_HOURS)).replace(microsecond=0).isoformat()
            connection.execute("INSERT INTO sessions (id, user_id, expires_at) VALUES (?, ?, ?)", (token, user["id"], expires_at))
            audit(connection, user["company_id"], user["id"], "login", "user", str(user["id"]), {"email": email})
            connection.commit()

        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Set-Cookie", f"{SESSION_COOKIE}={token}; Path=/; HttpOnly; SameSite=Lax; Max-Age={SESSION_HOURS * 3600}")
        self.end_headers()
        self.wfile.write(json_dumps({"user": public_user(user)}).encode("utf-8"))

    def handle_logout(self) -> None:
        raw_cookie = self.headers.get("Cookie", "")
        cookie = SimpleCookie(raw_cookie)
        token = cookie.get(SESSION_COOKIE)
        if token:
            with db() as connection:
                connection.execute("DELETE FROM sessions WHERE id = ?", (token.value,))
                connection.commit()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Set-Cookie", f"{SESSION_COOKIE}=; Path=/; HttpOnly; SameSite=Lax; Max-Age=0")
        self.end_headers()
        self.wfile.write(json_dumps({"ok": True}).encode("utf-8"))

    def handle_state_get(self, user: sqlite3.Row) -> None:
        with operational_db_for_user(user) as connection:
            state = build_state(connection, user["company_id"], user)
        self.json({"state": state, "user": public_user(user)})

    def handle_state_put(self, user: sqlite3.Row) -> None:
        data = self.read_json()
        state = data.get("state")
        if not isinstance(state, dict):
            self.error_json(HTTPStatus.BAD_REQUEST, "Estado invalido.")
            return
        try:
            with operational_db_for_user(user) as connection:
                replace_state(connection, user["company_id"], state, user)
                connection.commit()
                refreshed = build_state(connection, user["company_id"], user)
            self.json({"state": refreshed, "user": public_user(user)})
        except PermissionError as error:
            self.error_json(HTTPStatus.FORBIDDEN, str(error))

    def handle_user_create(self, user: sqlite3.Row) -> None:
        if user["role"] not in ("superadmin", "admin"):
            self.error_json(HTTPStatus.FORBIDDEN, "Solo superusuarios y administradores pueden crear usuarios.")
            return
        data = self.read_json()
        name = (data.get("name") or "").strip()
        email = (data.get("email") or "").strip().lower()
        role = (data.get("role") or "agent").strip()
        password = data.get("password") or ""
        leader_id = data.get("leaderId") or None
        allowed_roles = {"superadmin", "admin", "coordinator", "agent", "quality"}
        if not name or not email or not password:
            self.error_json(HTTPStatus.BAD_REQUEST, "Nombre, email y contrasena son obligatorios.")
            return
        if role not in allowed_roles:
            self.error_json(HTTPStatus.BAD_REQUEST, "Rol invalido.")
            return
        if len(password) < 8:
            self.error_json(HTTPStatus.BAD_REQUEST, "La contrasena debe tener al menos 8 caracteres.")
            return

        with db() as connection:
            exists = connection.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
            if exists:
                self.error_json(HTTPStatus.CONFLICT, "Ya existe un usuario con ese email. En SaaS el email debe ser unico.")
                return
            cursor = connection.execute(
                """
                INSERT INTO users (company_id, name, email, role, leader_id, password_hash, active, created_at)
                VALUES (?, ?, ?, ?, ?, ?, 1, ?)
                """,
                (user["company_id"], name, email, role, leader_id, hash_password(password), utc_now()),
            )
            audit(connection, user["company_id"], user["id"], "create_user", "user", str(cursor.lastrowid), {"email": email, "role": role})
            connection.commit()
            with tenant_db_for_slug(user["company_slug"]) as tenant_connection:
                install_schema_from_template(connection, tenant_connection)
                mirror_company_and_users(connection, tenant_connection, user["company_id"])
                ensure_tenant_defaults(tenant_connection, user["company_id"], user["company_name"], user["company_slug"])
                tenant_connection.commit()
                state = build_state(tenant_connection, user["company_id"], user)
        self.json({"state": state, "user": public_user(user)})

    def handle_portfolio_user_assign(self, user: sqlite3.Row) -> None:
        if user["role"] not in ("superadmin", "admin", "coordinator"):
            self.error_json(HTTPStatus.FORBIDDEN, "Tu rol no puede asociar usuarios a carteras.")
            return
        data = self.read_json()
        portfolio_id = data.get("portfolioId")
        user_id = data.get("userId")
        assignment_role = data.get("assignmentRole") or "agent"
        leader_id = data.get("leaderId") or None
        if not portfolio_id or not user_id:
            self.error_json(HTTPStatus.BAD_REQUEST, "Cartera y usuario son obligatorios.")
            return
        if assignment_role not in ("admin", "leader", "agent", "quality"):
            self.error_json(HTTPStatus.BAD_REQUEST, "Rol de asociacion invalido.")
            return

        with operational_db_for_user(user) as connection:
            portfolio_row = connection.execute(
                "SELECT id FROM portfolios WHERE company_id = ? AND id = ?",
                (user["company_id"], portfolio_id),
            ).fetchone()
            target_user = connection.execute(
                "SELECT id, role FROM users WHERE company_id = ? AND id = ?",
                (user["company_id"], user_id),
            ).fetchone()
            if not portfolio_row or not target_user:
                self.error_json(HTTPStatus.NOT_FOUND, "No se encontro la cartera o el usuario.")
                return
            connection.execute(
                """
                INSERT INTO portfolio_users (company_id, portfolio_id, user_id, role)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(company_id, portfolio_id, user_id) DO UPDATE SET role = excluded.role
                """,
                (user["company_id"], portfolio_id, user_id, assignment_role),
            )
            if leader_id:
                connection.execute(
                    "UPDATE users SET leader_id = ? WHERE company_id = ? AND id = ?",
                    (leader_id, user["company_id"], user_id),
                )
                with db() as platform_connection:
                    platform_connection.execute(
                        "UPDATE users SET leader_id = ? WHERE company_id = ? AND id = ?",
                        (leader_id, user["company_id"], user_id),
                    )
                    platform_connection.commit()
            if assignment_role == "leader":
                connection.execute(
                    "UPDATE portfolios SET leader_user_id = ? WHERE company_id = ? AND id = ?",
                    (user_id, user["company_id"], portfolio_id),
                )
            audit(connection, user["company_id"], user["id"], "assign_portfolio_user", "portfolio", portfolio_id, {"userId": user_id, "role": assignment_role, "leaderId": leader_id})
            connection.commit()
            state = build_state(connection, user["company_id"], user)
        self.json({"state": state, "user": public_user(user)})

    def handle_platform_company_create(self, user: sqlite3.Row) -> None:
        if user["role"] != "platform_admin":
            self.error_json(HTTPStatus.FORBIDDEN, "Solo IcodeUp plataforma puede crear empresas cliente.")
            return
        data = self.read_json()
        name = (data.get("name") or "").strip()
        slug = normalize_slug(data.get("slug") or name)
        tax_id = (data.get("taxId") or "").strip()
        admin_name = (data.get("adminName") or "Administrador Operativo").strip()
        admin_email = (data.get("adminEmail") or "").strip().lower()
        admin_password = data.get("adminPassword") or "Admin123!"
        project_name = (data.get("projectName") or "Cartera inicial").strip()
        project_code = (data.get("projectCode") or "BASE").strip().upper()
        if not name or not slug or not admin_email:
            self.error_json(HTTPStatus.BAD_REQUEST, "Nombre de empresa, slug y email administrador son obligatorios.")
            return
        with db() as connection:
            exists = connection.execute("SELECT id FROM companies WHERE slug = ?", (slug,)).fetchone()
            if exists:
                self.error_json(HTTPStatus.CONFLICT, "Ya existe una empresa con ese identificador.")
                return
            email_exists = connection.execute("SELECT id FROM users WHERE email = ?", (admin_email,)).fetchone()
            if email_exists:
                self.error_json(HTTPStatus.CONFLICT, "El email administrador ya existe en la plataforma.")
                return
            company_id = create_company(connection, name, slug, tax_id)
            admin_id = ensure_user(connection, company_id, admin_name, admin_email, "superadmin", admin_password)
            leader_id = ensure_user(connection, company_id, "Coordinador Cobranzas", f"lider@{slug}.com", "coordinator", "Lider123!")
            agent_id = ensure_user(connection, company_id, "Gestor Estandar", f"gestor@{slug}.com", "agent", "Gestor123!", leader_id=leader_id)
            ensure_user(connection, company_id, "Supervisor Calidad", f"calidad@{slug}.com", "quality", "Calidad123!", leader_id=leader_id)
            connection.commit()
            with tenant_db_for_slug(slug) as tenant_connection:
                install_schema_from_template(connection, tenant_connection)
                mirror_company_and_users(connection, tenant_connection, company_id)
                ensure_tenant_basics(tenant_connection, company_id, name)
                portfolio_id = f"CAR-{normalize_slug(project_code).upper()[:18] or 'BASE'}"
                tenant_connection.execute(
                    """
                    INSERT INTO portfolios (id, company_id, name, code, leader_user_id, status, created_at)
                    VALUES (?, ?, ?, ?, ?, 'active', ?)
                    ON CONFLICT(company_id, id) DO UPDATE SET
                      name = excluded.name,
                      code = excluded.code,
                      leader_user_id = excluded.leader_user_id
                    """,
                    (portfolio_id, company_id, project_name, project_code, leader_id, utc_now()),
                )
                for member_id, member_role in [(admin_id, "admin"), (leader_id, "leader"), (agent_id, "agent")]:
                    tenant_connection.execute(
                        "INSERT INTO portfolio_users (company_id, portfolio_id, user_id, role) VALUES (?, ?, ?, ?)",
                        (company_id, portfolio_id, member_id, member_role),
                    )
                tenant_connection.commit()
            audit(connection, company_id, user["id"], "platform_create_company", "company", str(company_id), {"name": name, "slug": slug})
            connection.commit()
            state = build_state(connection, user["company_id"], user)
        self.json({"state": state, "user": public_user(user)})

    def handle_platform_portfolio_create(self, user: sqlite3.Row) -> None:
        if user["role"] != "platform_admin":
            self.error_json(HTTPStatus.FORBIDDEN, "Solo IcodeUp plataforma puede crear proyectos para empresas.")
            return
        data = self.read_json()
        company_id = data.get("companyId")
        name = (data.get("name") or "").strip()
        code = (data.get("code") or "").strip().upper()
        if not company_id or not name or not code:
            self.error_json(HTTPStatus.BAD_REQUEST, "Empresa, nombre y codigo son obligatorios.")
            return
        with db() as connection:
            company = connection.execute("SELECT id FROM companies WHERE id = ? AND slug <> 'icodeup-platform'", (company_id,)).fetchone()
            if not company:
                self.error_json(HTTPStatus.NOT_FOUND, "Empresa no encontrada.")
                return
            leader = connection.execute(
                "SELECT id FROM users WHERE company_id = ? AND role IN ('coordinator','admin','superadmin') ORDER BY CASE role WHEN 'coordinator' THEN 1 WHEN 'admin' THEN 2 ELSE 3 END LIMIT 1",
                (company_id,),
            ).fetchone()
            tenant_connection = operational_db_for_company(connection, company_id)
        with tenant_connection as tenant:
            portfolio_id = f"CAR-{normalize_slug(code).upper()[:18]}"
            suffix = 1
            original_id = portfolio_id
            while tenant.execute("SELECT id FROM portfolios WHERE company_id = ? AND id = ?", (company_id, portfolio_id)).fetchone():
                suffix += 1
                portfolio_id = f"{original_id}-{suffix}"
            tenant.execute(
                """
                INSERT INTO portfolios (id, company_id, name, code, leader_user_id, status, created_at)
                VALUES (?, ?, ?, ?, ?, 'active', ?)
                """,
                (portfolio_id, company_id, name, code, leader["id"] if leader else None, utc_now()),
            )
            if leader:
                tenant.execute(
                    "INSERT OR IGNORE INTO portfolio_users (company_id, portfolio_id, user_id, role) VALUES (?, ?, ?, 'leader')",
                    (company_id, portfolio_id, leader["id"]),
                )
            tenant.commit()
        with db() as connection:
            audit(connection, company_id, user["id"], "platform_create_portfolio", "portfolio", portfolio_id, {"name": name, "code": code})
            connection.commit()
            state = build_state(connection, user["company_id"], user)
        self.json({"state": state, "user": public_user(user)})

    def handle_platform_user_create(self, user: sqlite3.Row) -> None:
        if user["role"] != "platform_admin":
            self.error_json(HTTPStatus.FORBIDDEN, "Solo IcodeUp plataforma puede crear usuarios tenant.")
            return
        data = self.read_json()
        company_id = data.get("companyId")
        name = (data.get("name") or "").strip()
        email = (data.get("email") or "").strip().lower()
        role = (data.get("role") or "agent").strip()
        password = data.get("password") or ""
        leader_id = data.get("leaderId") or None
        allowed_roles = {"superadmin", "admin", "coordinator", "agent", "quality"}
        if not company_id or not name or not email or not password:
            self.error_json(HTTPStatus.BAD_REQUEST, "Empresa, nombre, email y contrasena son obligatorios.")
            return
        if role not in allowed_roles:
            self.error_json(HTTPStatus.BAD_REQUEST, "Rol invalido.")
            return
        if len(password) < 8:
            self.error_json(HTTPStatus.BAD_REQUEST, "La contrasena debe tener al menos 8 caracteres.")
            return

        with db() as connection:
            company = tenant_company_row(connection, int(company_id))
            if not company:
                self.error_json(HTTPStatus.NOT_FOUND, "Empresa no encontrada.")
                return
            if connection.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone():
                self.error_json(HTTPStatus.CONFLICT, "Ya existe un usuario con ese email en la plataforma.")
                return
            if leader_id:
                leader = connection.execute(
                    "SELECT id FROM users WHERE company_id = ? AND id = ? AND role IN ('superadmin','admin','coordinator')",
                    (company_id, leader_id),
                ).fetchone()
                if not leader:
                    self.error_json(HTTPStatus.BAD_REQUEST, "El lider seleccionado no pertenece a la empresa o no tiene rol lider.")
                    return
            cursor = connection.execute(
                """
                INSERT INTO users (company_id, name, email, role, leader_id, password_hash, active, created_at)
                VALUES (?, ?, ?, ?, ?, ?, 1, ?)
                """,
                (company_id, name, email, role, leader_id, hash_password(password), utc_now()),
            )
            audit(connection, company_id, user["id"], "platform_create_user", "user", str(cursor.lastrowid), {"email": email, "role": role})
            connection.commit()
            with tenant_db_for_slug(company["slug"]) as tenant_connection:
                install_schema_from_template(connection, tenant_connection)
                mirror_company_and_users(connection, tenant_connection, int(company_id))
                tenant_connection.commit()
            state = build_state(connection, user["company_id"], user)
        self.json({"state": state, "user": public_user(user)})

    def handle_platform_user_status(self, user: sqlite3.Row) -> None:
        if user["role"] != "platform_admin":
            self.error_json(HTTPStatus.FORBIDDEN, "Solo IcodeUp plataforma puede modificar usuarios tenant.")
            return
        data = self.read_json()
        company_id = data.get("companyId")
        target_user_id = data.get("userId")
        active = 1 if data.get("active") else 0
        if not company_id or not target_user_id:
            self.error_json(HTTPStatus.BAD_REQUEST, "Empresa y usuario son obligatorios.")
            return

        with db() as connection:
            company = tenant_company_row(connection, int(company_id))
            if not company:
                self.error_json(HTTPStatus.NOT_FOUND, "Empresa no encontrada.")
                return
            target = connection.execute(
                "SELECT id, email, role FROM users WHERE company_id = ? AND id = ?",
                (company_id, target_user_id),
            ).fetchone()
            if not target:
                self.error_json(HTTPStatus.NOT_FOUND, "Usuario no encontrado.")
                return
            connection.execute(
                "UPDATE users SET active = ? WHERE company_id = ? AND id = ?",
                (active, company_id, target_user_id),
            )
            audit(connection, company_id, user["id"], "platform_update_user_status", "user", str(target_user_id), {"active": bool(active), "email": target["email"]})
            connection.commit()
            with tenant_db_for_slug(company["slug"]) as tenant_connection:
                install_schema_from_template(connection, tenant_connection)
                mirror_company_and_users(connection, tenant_connection, int(company_id))
                tenant_connection.commit()
            state = build_state(connection, user["company_id"], user)
        self.json({"state": state, "user": public_user(user)})

    def handle_platform_portfolio_status(self, user: sqlite3.Row) -> None:
        if user["role"] != "platform_admin":
            self.error_json(HTTPStatus.FORBIDDEN, "Solo IcodeUp plataforma puede modificar proyectos tenant.")
            return
        data = self.read_json()
        company_id = data.get("companyId")
        portfolio_id = data.get("portfolioId")
        status = (data.get("status") or "active").strip()
        if not company_id or not portfolio_id:
            self.error_json(HTTPStatus.BAD_REQUEST, "Empresa y proyecto son obligatorios.")
            return
        if status not in {"active", "paused", "closed"}:
            self.error_json(HTTPStatus.BAD_REQUEST, "Estado de proyecto invalido.")
            return

        with db() as platform_connection:
            company = tenant_company_row(platform_connection, int(company_id))
            if not company:
                self.error_json(HTTPStatus.NOT_FOUND, "Empresa no encontrada.")
                return
            with tenant_db_for_slug(company["slug"]) as tenant_connection:
                project = tenant_connection.execute(
                    "SELECT id FROM portfolios WHERE company_id = ? AND id = ?",
                    (company_id, portfolio_id),
                ).fetchone()
                if not project:
                    self.error_json(HTTPStatus.NOT_FOUND, "Proyecto no encontrado.")
                    return
                tenant_connection.execute(
                    "UPDATE portfolios SET status = ? WHERE company_id = ? AND id = ?",
                    (status, company_id, portfolio_id),
                )
                tenant_connection.commit()
            audit(platform_connection, company_id, user["id"], "platform_update_portfolio_status", "portfolio", portfolio_id, {"status": status})
            platform_connection.commit()
            state = build_state(platform_connection, user["company_id"], user)
        self.json({"state": state, "user": public_user(user)})

    def handle_platform_typification_upsert(self, user: sqlite3.Row) -> None:
        if user["role"] != "platform_admin":
            self.error_json(HTTPStatus.FORBIDDEN, "Solo IcodeUp plataforma puede parametrizar tipificaciones tenant.")
            return
        data = self.read_json()
        company_id = data.get("companyId")
        item = data.get("typification") or {}
        if not company_id or not isinstance(item, dict):
            self.error_json(HTTPStatus.BAD_REQUEST, "Empresa y tipificacion son obligatorias.")
            return
        try:
            with db() as platform_connection:
                company = tenant_company_row(platform_connection, int(company_id))
                if not company:
                    self.error_json(HTTPStatus.NOT_FOUND, "Empresa no encontrada.")
                    return
                with tenant_db_for_slug(company["slug"]) as tenant_connection:
                    install_schema_from_template(platform_connection, tenant_connection)
                    mirror_company_and_users(platform_connection, tenant_connection, int(company_id))
                    ensure_tenant_defaults(tenant_connection, int(company_id), company["name"], company["slug"])
                    node = upsert_typification_node(tenant_connection, int(company_id), item)
                    tenant_connection.commit()
                audit(platform_connection, int(company_id), user["id"], "platform_upsert_typification", "typification", node["id"], {"label": node["label"], "code": node["code"]})
                platform_connection.commit()
                state = build_state(platform_connection, user["company_id"], user)
            self.json({"state": state, "user": public_user(user)})
        except ValueError as error:
            self.error_json(HTTPStatus.BAD_REQUEST, str(error))

    def handle_platform_typification_delete(self, user: sqlite3.Row) -> None:
        if user["role"] != "platform_admin":
            self.error_json(HTTPStatus.FORBIDDEN, "Solo IcodeUp plataforma puede eliminar tipificaciones tenant.")
            return
        data = self.read_json()
        company_id = data.get("companyId")
        node_id = data.get("id")
        if not company_id or not node_id:
            self.error_json(HTTPStatus.BAD_REQUEST, "Empresa y nodo son obligatorios.")
            return
        with db() as platform_connection:
            company = tenant_company_row(platform_connection, int(company_id))
            if not company:
                self.error_json(HTTPStatus.NOT_FOUND, "Empresa no encontrada.")
                return
            with tenant_db_for_slug(company["slug"]) as tenant_connection:
                child = tenant_connection.execute(
                    "SELECT id FROM typification_nodes WHERE company_id = ? AND parent_id = ? LIMIT 1",
                    (company_id, node_id),
                ).fetchone()
                if child:
                    self.error_json(HTTPStatus.CONFLICT, "No puedes eliminar un nodo con hijos. Reasigna o elimina primero sus subtipificaciones.")
                    return
                target = tenant_connection.execute(
                    "SELECT label FROM typification_nodes WHERE company_id = ? AND id = ?",
                    (company_id, node_id),
                ).fetchone()
                if not target:
                    self.error_json(HTTPStatus.NOT_FOUND, "Tipificacion no encontrada.")
                    return
                tenant_connection.execute(
                    "DELETE FROM typification_nodes WHERE company_id = ? AND id = ?",
                    (company_id, node_id),
                )
                tenant_connection.commit()
            audit(platform_connection, int(company_id), user["id"], "platform_delete_typification", "typification", str(node_id), {"label": target["label"]})
            platform_connection.commit()
            state = build_state(platform_connection, user["company_id"], user)
        self.json({"state": state, "user": public_user(user)})

    def handle_platform_customer_create(self, user: sqlite3.Row) -> None:
        if user["role"] != "platform_admin":
            self.error_json(HTTPStatus.FORBIDDEN, "Solo IcodeUp plataforma puede crear clientes tenant.")
            return
        data = self.read_json()
        company_id = data.get("companyId")
        name = (data.get("name") or "").strip()
        document = (data.get("document") or "").strip()
        if not company_id or not name or not document:
            self.error_json(HTTPStatus.BAD_REQUEST, "Empresa, nombre y documento son obligatorios.")
            return
        balance = int(data.get("balance") or 0)
        dpd = int(data.get("dpd") or 0)
        if balance <= 0:
            self.error_json(HTTPStatus.BAD_REQUEST, "El saldo debe ser mayor a cero.")
            return
        with db() as platform_connection:
            company = tenant_company_row(platform_connection, int(company_id))
            if not company:
                self.error_json(HTTPStatus.NOT_FOUND, "Empresa no encontrada.")
                return
            with tenant_db_for_slug(company["slug"]) as tenant_connection:
                install_schema_from_template(platform_connection, tenant_connection)
                mirror_company_and_users(platform_connection, tenant_connection, int(company_id))
                ensure_tenant_defaults(tenant_connection, int(company_id), company["name"], company["slug"])
                portfolio_id = data.get("portfolioId") or "CAR-BASE"
                portfolio = tenant_connection.execute(
                    "SELECT id FROM portfolios WHERE company_id = ? AND id = ?",
                    (company_id, portfolio_id),
                ).fetchone()
                if not portfolio:
                    self.error_json(HTTPStatus.BAD_REQUEST, "El proyecto seleccionado no existe para esta empresa.")
                    return
                agent = (data.get("agent") or "").strip()
                if not agent:
                    row = tenant_connection.execute(
                        "SELECT name FROM users WHERE company_id = ? AND role IN ('agent','coordinator','admin') AND active = 1 ORDER BY role, name LIMIT 1",
                        (company_id,),
                    ).fetchone()
                    agent = row["name"] if row else "Sin asignar"
                customer_id = next_text_id(tenant_connection, "customers", int(company_id), "C")
                status = "Sin contacto"
                contactability = data.get("contactability") or "Media"
                risk = risk_from_dpd(dpd, balance)
                item = {
                    "id": customer_id,
                    "name": name,
                    "document": document,
                    "phone": data.get("phone") or "",
                    "email": data.get("email") or "",
                    "city": data.get("city") or "",
                    "segment": data.get("segment") or "Consumo",
                    "agent": agent,
                    "balance": balance,
                    "originalBalance": int(data.get("originalBalance") or balance),
                    "dpd": dpd,
                    "status": status,
                    "risk": risk,
                    "priority": score_customer_payload(dpd, balance, status, contactability),
                    "nextAction": "Primer contacto y validacion de datos",
                    "lastContact": "",
                    "nextContact": today(),
                    "contactability": contactability,
                    "accounts": [data.get("account") or "Cuenta principal"],
                    "tags": ["Creado por IcodeUp plataforma"],
                    "portfolioId": portfolio_id,
                    "demographic": {},
                    "financial": {},
                    "notes": data.get("notes") or "",
                }
                insert_customer(tenant_connection, int(company_id), item)
                insert_interaction(tenant_connection, int(company_id), customer_id, "Caso creado", item["notes"] or "Creado desde parametrizacion IcodeUp.", user["name"], "CRM", today())
                tenant_connection.commit()
            audit(platform_connection, int(company_id), user["id"], "platform_create_customer", "customer", customer_id, {"name": name, "document": document})
            platform_connection.commit()
            state = build_state(platform_connection, user["company_id"], user)
        self.json({"state": state, "user": public_user(user)})

    def handle_audit_get(self, user: sqlite3.Row) -> None:
        if user["role"] not in ("superadmin", "admin"):
            self.error_json(HTTPStatus.FORBIDDEN, "Solo administradores pueden ver auditoria.")
            return
        with operational_db_for_user(user) as connection:
            rows = [
                {
                    "action": row["action"],
                    "entity": row["entity"],
                    "entityId": row["entity_id"],
                    "detail": json_loads(row["detail_json"], {}),
                    "createdAt": row["created_at"],
                }
                for row in connection.execute(
                    """
                    SELECT action, entity, entity_id, detail_json, created_at
                    FROM audit_log
                    WHERE company_id = ?
                    ORDER BY created_at DESC
                    LIMIT 100
                    """,
                    (user["company_id"],),
                )
            ]
        self.json({"audit": rows})

    def serve_static(self, path: str) -> None:
        clean_path = unquote(path).lstrip("/") or "index.html"
        target = (BASE_DIR / clean_path).resolve()
        if not str(target).startswith(str(BASE_DIR)) or not target.exists() or target.is_dir():
            target = BASE_DIR / "index.html"
        content_type = mimetypes.guess_type(str(target))[0] or "application/octet-stream"
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.end_headers()
        self.wfile.write(target.read_bytes())

    def read_json(self) -> dict:
        length = int(self.headers.get("Content-Length", "0") or "0")
        if length == 0:
            return {}
        raw = self.rfile.read(length).decode("utf-8")
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return {}

    def json(self, payload: dict, status: HTTPStatus = HTTPStatus.OK) -> None:
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(json_dumps(payload).encode("utf-8"))

    def error_json(self, status: HTTPStatus, message: str) -> None:
        self.json({"error": message}, status)

    def log_message(self, format, *args) -> None:
        print("[IcodeUp CRM]", format % args)


def public_user(user: sqlite3.Row) -> dict:
    return {
        "id": user["id"],
        "name": user["name"],
        "email": user["email"],
        "role": user["role"],
        "leaderId": user["leader_id"],
        "companyId": user["company_id"],
        "companyName": user["company_name"],
        "companySlug": user["company_slug"],
    }


def main() -> None:
    init_db()
    server = ThreadingHTTPServer((HOST, PORT), CRMHandler)
    print(f"IcodeUp CRM backend en http://{HOST}:{PORT}")
    print(f"Base plataforma: {PLATFORM_DB_PATH}")
    print(f"Bases tenant: {TENANT_DIR}")
    server.serve_forever()


if __name__ == "__main__":
    main()
