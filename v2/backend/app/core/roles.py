PLATFORM_ADMIN = "platform_admin"
TENANT_ADMIN = "tenant_admin"
COORDINATOR = "coordinator"
QUALITY_SUPERVISOR = "quality_supervisor"
AGENT = "agent"

TENANT_ROLES = {TENANT_ADMIN, COORDINATOR, QUALITY_SUPERVISOR, AGENT}
ALL_ROLES = {PLATFORM_ADMIN, *TENANT_ROLES}

ROLE_LABELS = {
    PLATFORM_ADMIN: "Super administrador IcodeUp",
    TENANT_ADMIN: "Administrador empresa",
    COORDINATOR: "Lider / Coordinador",
    QUALITY_SUPERVISOR: "Supervisor calidad",
    AGENT: "Gestor",
}


def is_valid_role(role: str) -> bool:
    return role in ALL_ROLES


def can_be_direct_leader(role: str) -> bool:
    return role in {TENANT_ADMIN, COORDINATOR}
