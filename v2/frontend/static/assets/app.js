let token = localStorage.getItem("icodeup_v2_token") || "";
let currentUser = JSON.parse(localStorage.getItem("icodeup_v2_user") || "null");

const state = {
  core: { menu: null, roleDashboard: null },
  admin: { overview: null, tenants: [], projects: [], users: [], roles: [], typifications: [] },
  governance: { permissions: [], roles: [], users: [], modules: [], settings: null, audit: [], parties: [], plans: [], subscriptions: [], health: null, securityInsights: [], effectiveAccess: null },
  crm: { options: { tenants: [], projects: [], users: [], channels: [] }, dashboard: null, bi: null, customers: null, queue: null, promises: [], payments: [], channels: [], typifications: [] },
  configuration: { catalogs: [], rules: [], alertRules: [], workflows: [] },
  alerts: { items: [], summary: null },
  legal: { dashboard: null, kanban: null, cases: [] },
  sales: { dashboard: null, pipeline: null, kanban: null, leads: [], opportunities: [] },
  ops: { trees: [], combinations: [], recordings: [], uploads: [], demographics: [], excelSources: [], excelViews: [], excelResult: null, excelDraft: null, uploadPreview: null, uploadDraft: null, providers: [], integrationChannels: [], templates: [], webhooks: [], events: [] },
  selectedCustomer: null,
  selectedActivities: [],
  queuePage: 1,
  customerPage: 1
};

const titles = {
  dashboard: "Tablero ejecutivo",
  queue: "Cola de gestion",
  customers: "Clientes y repartos",
  promises: "Promesas de pago",
  payments: "Pagos",
  agreements: "Acuerdos de pago",
  legal: "Gestion juridica",
  documents: "Gestion documental",
  sales: "Ventas y CRM 360",
  reports: "Reportes BI",
  channels: "Canales",
  tenants: "Empresas",
  projects: "Proyectos",
  users: "Usuarios",
  typifications: "Tipificaciones",
  governance: "Gobierno SaaS",
  plans: "Planes",
  subscriptions: "Suscripciones",
  modules: "Modulos",
  configuration: "Centro de configuracion",
  alerts: "Alertas",
  "typification-trees": "Arboles de gestion",
  recordings: "Grabaciones",
  uploads: "Cargas y repartos",
  "excel-web": "Mi Excel Web",
  integrations: "Integraciones",
  "tenant-settings": "Mi empresa",
  "company-users": "Usuarios de empresa",
  "roles-permissions": "Roles y permisos",
  "tenant-modules": "Modulos contratados",
  branding: "Branding",
  audit: "Auditoria",
  "system-health": "Salud del sistema",
  parties: "Tercero maestro",
  tasks: "Mis tareas"
};

const roleLabels = {
  platform_admin: "SuperAdmin Icodeup",
  tenant_admin: "Admin empresa",
  coordinator: "Lider operativo",
  quality_supervisor: "Supervisor calidad",
  agent: "Usuario operativo",
  legal_director: "Director juridico",
  lawyer: "Abogado",
  sales_leader: "Lider comercial",
  sales_advisor: "Asesor comercial",
  collections_leader: "Lider de cobranzas",
  collections_agent: "Gestor de cobranzas",
  tenant_auditor: "Auditor"
};

const audienceLabels = {
  platform_admin: "Gobierno SaaS Icodeup",
  company_admin: "Administracion de empresa",
  operational_leader: "Liderazgo operativo",
  operational_user: "Operacion diaria"
};

const sectionCategories = {
  governance: "Gobierno SaaS",
  tenants: "Gobierno SaaS",
  plans: "Gobierno SaaS",
  subscriptions: "Gobierno SaaS",
  modules: "Gobierno SaaS",
  "system-health": "Gobierno SaaS",
  "tenant-settings": "Administracion",
  "company-users": "Administracion",
  "roles-permissions": "Administracion",
  "tenant-modules": "Administracion",
  branding: "Administracion",
  audit: "Administracion",
  configuration: "Administracion",
  users: "Administracion",
  projects: "Administracion",
  typifications: "Administracion",
  "typification-trees": "Administracion",
  dashboard: "Operacion",
  tasks: "Operacion",
  queue: "Operacion",
  customers: "Operacion",
  promises: "Operacion",
  payments: "Operacion",
  agreements: "Operacion",
  legal: "Operacion",
  documents: "Operacion",
  sales: "Operacion",
  channels: "Operacion",
  recordings: "Operacion",
  uploads: "Operacion",
  integrations: "Operacion",
  parties: "Operacion",
  reports: "Analitica",
  "excel-web": "Analitica",
  alerts: "Analitica"
};

const sectionModules = {
  dashboard: "core",
  governance: "administration",
  tenants: "administration",
  plans: "administration",
  subscriptions: "administration",
  modules: "administration",
  configuration: "administration",
  "tenant-settings": "administration",
  "company-users": "administration",
  "roles-permissions": "administration",
  "tenant-modules": "administration",
  branding: "administration",
  audit: "administration",
  "system-health": "administration",
  users: "administration",
  projects: "administration",
  typifications: "collections",
  "typification-trees": "collections",
  tasks: "collections",
  queue: "collections",
  customers: "collections",
  promises: "collections",
  payments: "collections",
  agreements: "collections",
  legal: "legal",
  documents: "documents",
  sales: "sales",
  channels: "integrations",
  recordings: "collections",
  uploads: "collections",
  integrations: "integrations",
  parties: "crm",
  reports: "bi",
  "excel-web": "bi",
  alerts: "bi"
};

const moduleCopy = {
  crm: { name: "CRM 360", category: "Operacion", description: "Terceros, clientes, relaciones y trazabilidad transversal." },
  core: { name: "Core SaaS", category: "Core", description: "Identidad, tenants, permisos, auditoria y base de operacion segura." },
  administration: { name: "Administracion", category: "Administracion", description: "Usuarios, roles, configuracion, branding y gobierno de empresa." },
  collections: { name: "Cobranzas", category: "Operacion", description: "Cola, clientes, promesas, pagos, acuerdos y recuperacion de cartera." },
  legal: { name: "Juridico", category: "Operacion", description: "Casos, actuaciones, audiencias, vencimientos y riesgo legal." },
  documents: { name: "Documentos", category: "Operacion", description: "Metadatos documentales asociados a terceros, pagos, acuerdos y casos." },
  sales: { name: "Ventas", category: "Expansion", description: "Leads, oportunidades y pipeline para evolucionar hacia CRM 360." },
  bi: { name: "BI y analitica", category: "Analitica", description: "KPIs, scoring, semaforos, alertas y tableros ejecutivos." },
  integrations: { name: "Integraciones", category: "Integraciones", description: "Base para WhatsApp, correo, telefonia, APIs y automatizaciones." }
};

const loginView = document.querySelector("#loginView");
const appView = document.querySelector("#appView");
const loginResult = document.querySelector("#loginResult");

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function money(value) {
  return new Intl.NumberFormat("es-CO", { style: "currency", currency: "COP", maximumFractionDigits: 0 }).format(Number(value) || 0);
}

function dateOnly(value) {
  if (!value) return "-";
  return new Intl.DateTimeFormat("es-CO", { year: "numeric", month: "short", day: "2-digit" }).format(new Date(value));
}

function toDateTime(value) {
  return value ? `${value}T00:00:00Z` : null;
}

function phoneDigits(value) {
  return String(value || "").replace(/\D/g, "");
}

function sumBy(items, selector) {
  return (items || []).reduce((total, item) => total + (Number(selector(item)) || 0), 0);
}

function countBy(items, predicate) {
  return (items || []).filter(predicate).length;
}

function pct(part, total) {
  return `${Math.round((Number(part) / Math.max(Number(total) || 0, 1)) * 100)}%`;
}

function dateValue(value) {
  return value ? new Date(value) : null;
}

function isOverdue(value) {
  const date = dateValue(value);
  return Boolean(date && date < new Date());
}

function isWithinDays(value, days) {
  const date = dateValue(value);
  if (!date) return false;
  const now = new Date();
  const limit = new Date(now);
  limit.setDate(now.getDate() + days);
  return date >= now && date <= limit;
}

function statusTone(score) {
  if (score >= 75) return "green";
  if (score >= 45) return "yellow";
  return "red";
}

function kpiByKey(key) {
  return (state.crm.bi?.kpis || []).find((item) => item.key === key);
}

function numberFromKpi(key) {
  const kpi = kpiByKey(key);
  return typeof kpi?.value === "number" ? kpi.value : 0;
}

function renderCardSet(selector, cards) {
  const container = document.querySelector(selector);
  if (!container) return;
  container.innerHTML = (cards || [])
    .map(
      (card) => `
        <article class="analysis-card ${escapeHtml(card.tone || "neutral")}">
          <span>${escapeHtml(card.label)}</span>
          <strong>${escapeHtml(card.value)}</strong>
          <p>${escapeHtml(card.detail || "")}</p>
          ${card.action ? `<small>${escapeHtml(card.action)}</small>` : ""}
        </article>
      `
    )
    .join("");
}

function renderAlertSet(selector, alerts, emptyMessage = "Sin alertas con los datos actuales.") {
  const container = document.querySelector(selector);
  if (!container) return;
  const rows = alerts || [];
  container.innerHTML = rows.length
    ? rows
        .map(
          (alert) => `
            <article class="mini-alert ${escapeHtml(alert.tone || alert.severity || "neutral")}">
              <strong>${escapeHtml(alert.title)}</strong>
              ${alert.value !== undefined && alert.value !== null && alert.value !== "" ? `<span>${escapeHtml(alert.value)}</span>` : ""}
              <p>${escapeHtml(alert.body || "")}</p>
              ${alert.action ? `<small>${escapeHtml(alert.action)}</small>` : ""}
            </article>
          `
        )
        .join("")
    : `<p class="empty">${escapeHtml(emptyMessage)}</p>`;
}

async function api(path, options = {}) {
  const response = await fetch(path, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(options.headers || {})
    }
  });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    if (response.status === 401) logout();
    throw new Error(payload.detail || "No fue posible completar la solicitud. Intenta nuevamente o contacta al administrador.");
  }
  return payload;
}

async function apiMaybe(path, fallback, options = {}) {
  try {
    return await api(path, options);
  } catch (error) {
    console.warn(`${path}: ${error.message}`);
    return fallback;
  }
}

function ensureToastContainer() {
  let container = document.querySelector("#toastContainer");
  if (!container) {
    container = document.createElement("div");
    container.id = "toastContainer";
    container.className = "toast-container";
    container.setAttribute("aria-live", "polite");
    document.body.appendChild(container);
  }
  return container;
}

function showToast(type = "info", message = "Accion procesada.") {
  const container = ensureToastContainer();
  const toast = document.createElement("article");
  toast.className = `toast toast-${type}`;
  toast.innerHTML = `<strong>${escapeHtml(typeLabel(type))}</strong><span>${escapeHtml(message)}</span>`;
  container.appendChild(toast);
  window.setTimeout(() => toast.classList.add("leaving"), 3600);
  window.setTimeout(() => toast.remove(), 4300);
}

function typeLabel(type) {
  return {
    success: "Operacion exitosa",
    error: "Accion no completada",
    warning: "Revisa la informacion",
    info: "Informacion"
  }[type] || "Informacion";
}

function setButtonLoading(button, loading, text = "Procesando...") {
  if (!button) return;
  if (loading) {
    button.dataset.originalText = button.textContent;
    button.disabled = true;
    button.textContent = text;
  } else {
    button.disabled = false;
    button.textContent = button.dataset.originalText || button.textContent;
    delete button.dataset.originalText;
  }
}

async function runAction(button, action, loadingText = "Procesando...") {
  setButtonLoading(button, true, loadingText);
  try {
    const result = await action();
    return result;
  } catch (error) {
    console.warn(error);
    showToast("error", error.message || "No fue posible completar la accion.");
    throw error;
  } finally {
    setButtonLoading(button, false);
  }
}

async function downloadCsv(path, fileName) {
  const response = await fetch(path, {
    headers: {
      ...(token ? { Authorization: `Bearer ${token}` } : {})
    }
  });
  if (!response.ok) {
    const payload = await response.json().catch(() => ({}));
    throw new Error(payload.detail || "No fue posible exportar.");
  }
  const blob = await response.blob();
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = fileName;
  link.click();
  URL.revokeObjectURL(url);
}

function isPlatform() {
  return currentUser?.role === "platform_admin";
}

function canManageCrm() {
  return ["platform_admin", "tenant_admin", "coordinator"].includes(currentUser?.role);
}

function menuUser() {
  return state.core.menu?.user || currentUser || {};
}

function canExportExcelWeb() {
  const audience = menuUser().audience;
  return ["platform_admin", "company_admin", "operational_leader"].includes(audience);
}

function activeTenant() {
  return state.core.menu?.tenant || currentUser || {};
}

function roleLabel(role = menuUser().profile_role || menuUser().role) {
  return roleLabels[role] || role || "Usuario";
}

function audienceLabel(audience = menuUser().audience) {
  return audienceLabels[audience] || audience || "Workspace";
}

function activePlanLabel() {
  const tenant = activeTenant();
  if (tenant.is_platform || menuUser().is_platform_admin || isPlatform()) return "Plataforma Icodeup";
  const subscription = (state.governance.subscriptions || []).find((item) => Number(item.tenant_id) === Number(tenant.id));
  return subscription?.plan || "Plan empresarial";
}

function isDemoContext() {
  const tenant = activeTenant();
  const user = menuUser();
  const email = String(user.email || currentUser?.email || "").toLowerCase();
  const tenantSlug = String(tenant.slug || "").toLowerCase();
  return email.endsWith("@demo.icodeup.local") || tenantSlug.includes("demo") || tenantSlug.includes("andina-servicios-financieros");
}

function sectionCategory(item) {
  return sectionCategories[item.section] || (item.audience === "platform_admin" ? "Gobierno SaaS" : "Operacion");
}

function moduleMeta(code, fallback = {}) {
  const key = code || fallback.code || sectionModules[fallback.section] || "core";
  return {
    code: key,
    name: fallback.name || moduleCopy[key]?.name || fallback.label || key,
    category: fallback.category || moduleCopy[key]?.category || "Modulo",
    description: fallback.description || moduleCopy[key]?.description || "Capacidad modular disponible bajo permisos y plan contratado.",
  };
}

function moduleEnabled(module) {
  return module.enabled !== false && module.is_enabled !== false;
}

function iconForSection(section) {
  const paths = {
    dashboard: '<path d="M3 10.5 12 3l9 7.5"/><path d="M5 10v10h14V10"/>',
    queue: '<path d="M4 6h16"/><path d="M4 12h10"/><path d="M4 18h7"/><path d="m16 16 2 2 4-5"/>',
    customers: '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>',
    promises: '<path d="M8 2v4"/><path d="M16 2v4"/><path d="M3 10h18"/><rect x="3" y="4" width="18" height="18" rx="2"/><path d="m8 16 2 2 5-5"/>',
    payments: '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 10h18"/><path d="M7 15h4"/>',
    agreements: '<path d="M6 2h9l5 5v15H6z"/><path d="M14 2v6h6"/><path d="M9 14h6"/><path d="M9 18h4"/>',
    legal: '<path d="M12 3v18"/><path d="M5 7h14"/><path d="m6 7-3 6h6z"/><path d="m18 7-3 6h6z"/>',
    documents: '<path d="M6 2h8l4 4v16H6z"/><path d="M14 2v5h4"/><path d="M9 13h6"/><path d="M9 17h6"/>',
    sales: '<path d="M4 19V5"/><path d="M4 19h16"/><path d="m7 15 4-4 3 3 5-7"/>',
    reports: '<path d="M4 19V5"/><path d="M9 19v-7"/><path d="M14 19V9"/><path d="M19 19V3"/>',
    channels: '<path d="M4 12h5"/><path d="M15 12h5"/><path d="M9 12a3 3 0 1 0 6 0 3 3 0 0 0-6 0z"/>',
    recordings: '<rect x="3" y="7" width="18" height="10" rx="3"/><circle cx="8" cy="12" r="2"/><circle cx="16" cy="12" r="2"/>',
    uploads: '<path d="M12 3v12"/><path d="m7 8 5-5 5 5"/><path d="M5 21h14"/>',
    integrations: '<path d="M8 7V3"/><path d="M16 7V3"/><path d="M7 7h10v5a5 5 0 0 1-10 0z"/><path d="M12 17v4"/>',
    configuration: '<circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.7 1.7 0 0 0 .34 1.88l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06A1.7 1.7 0 0 0 15 19.4a1.7 1.7 0 0 0-1 .6 1.7 1.7 0 0 0-.4 1V21a2 2 0 1 1-4 0v-.08a1.7 1.7 0 0 0-.4-1 1.7 1.7 0 0 0-1-.6 1.7 1.7 0 0 0-1.88.34l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06A1.7 1.7 0 0 0 4.6 15a1.7 1.7 0 0 0-.6-1 1.7 1.7 0 0 0-1-.4H3a2 2 0 1 1 0-4h.08a1.7 1.7 0 0 0 1-.4 1.7 1.7 0 0 0 .6-1 1.7 1.7 0 0 0-.34-1.88l-.06-.06A2 2 0 1 1 7.11 3.4l.06.06A1.7 1.7 0 0 0 9 4.6a1.7 1.7 0 0 0 1-.6 1.7 1.7 0 0 0 .4-1V3a2 2 0 1 1 4 0v.08a1.7 1.7 0 0 0 .4 1 1.7 1.7 0 0 0 1 .6 1.7 1.7 0 0 0 1.88-.34l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06A1.7 1.7 0 0 0 19.4 9c.2.35.4.65.6 1 .3.2.62.35 1 .4H21a2 2 0 1 1 0 4h-.08a1.7 1.7 0 0 0-1 .4 1.7 1.7 0 0 0-.52.6z"/>',
    alerts: '<path d="M18 8a6 6 0 0 0-12 0c0 7-3 7-3 7h18s-3 0-3-7"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/>',
    "excel-web": '<rect x="3" y="4" width="18" height="16" rx="2"/><path d="M3 10h18"/><path d="M9 4v16"/><path d="M15 4v16"/>',
    governance: '<path d="M12 3 4 6v6c0 5 3.5 8 8 9 4.5-1 8-4 8-9V6z"/><path d="m9 12 2 2 4-4"/>',
    tenants: '<path d="M3 21h18"/><path d="M5 21V7l7-4 7 4v14"/><path d="M9 21v-7h6v7"/>',
    users: '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M19 8v6"/><path d="M16 11h6"/>',
    audit: '<path d="M4 4h16v16H4z"/><path d="M8 8h8"/><path d="M8 12h8"/><path d="M8 16h5"/>'
  };
  const path = paths[section] || paths.dashboard;
  return `<span class="nav-icon"><svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">${path}</svg></span>`;
}

function limitText(value) {
  const numeric = Number(value);
  return numeric > 0 ? numeric.toLocaleString("es-CO") : "Sin limite definido";
}

function renderShellContext() {
  const tenant = activeTenant();
  const user = menuUser();
  const tenantName = tenant.name || currentUser?.tenant_name || "Workspace activo";
  const profile = roleLabel(user.profile_role || user.role || currentUser?.role);
  const audience = audienceLabel(user.audience);
  const plan = activePlanLabel();
  const sessionText = user.name ? `${user.name} - ${profile}` : currentUser ? `${currentUser.name} - ${profile}` : "Sesion activa";
  document.querySelector("#sessionUser") && (document.querySelector("#sessionUser").textContent = sessionText);
  document.querySelector("#sidebarTenant") && (document.querySelector("#sidebarTenant").textContent = tenantName);
  document.querySelector("#sidebarRole") && (document.querySelector("#sidebarRole").textContent = profile);
  document.querySelector("#sidebarPlanBadge") && (document.querySelector("#sidebarPlanBadge").textContent = plan);
  document.querySelector("#topbarTenant") && (document.querySelector("#topbarTenant").textContent = `${tenantName} · ${audience}`);
  document.querySelector("#systemStatusPill") && (document.querySelector("#systemStatusPill").textContent = "Sistema operativo");
  const demoBadge = document.querySelector("#demoModeBadge");
  if (demoBadge) demoBadge.classList.toggle("hidden", !isDemoContext());
}

function menuModules() {
  const modules = new Map();
  (state.core.menu?.items || []).forEach((item) => {
    const code = item.module_code || sectionModules[item.section] || "core";
    const meta = moduleMeta(code, { label: item.label, section: item.section });
    if (!modules.has(code)) modules.set(code, { ...meta, enabled: true, is_enabled: true, source: "menu" });
  });
  return Array.from(modules.values());
}

function renderQuickActions(selector, actions) {
  const container = document.querySelector(selector);
  if (!container) return;
  container.innerHTML = (actions || [])
    .map(
      (action) => `
        <button class="quick-action-card" data-section-jump="${escapeHtml(action.section)}" type="button">
          <span>${escapeHtml(action.label)}</span>
          <strong>${escapeHtml(action.title)}</strong>
          <small>${escapeHtml(action.detail || "")}</small>
        </button>
      `
    )
    .join("");
}

function renderModuleCatalog(selector, modules, options = {}) {
  const container = document.querySelector(selector);
  if (!container) return;
  const catalog = (modules || []).map((module) => {
    const meta = moduleMeta(module.code || module.module_code, module);
    return {
      ...meta,
      enabled: moduleEnabled(module),
      contracted: module.enabled !== false,
      selected: module.source === "menu",
      action: options.admin
        ? moduleEnabled(module)
          ? "Gestionar desde gobierno SaaS"
          : "Activacion comercial disponible"
        : moduleEnabled(module)
          ? "Disponible para este workspace"
          : "Solicita activacion a Icodeup Advisors"
    };
  });
  container.innerHTML = catalog.length
    ? catalog
        .map(
          (module) => `
            <article class="module-card ${module.enabled ? "enabled" : "locked"}">
              <div>
                <span>${escapeHtml(module.category)}</span>
                <strong>${escapeHtml(module.name)}</strong>
              </div>
              <p>${escapeHtml(module.description)}</p>
              <small>${module.enabled ? "Activo" : "No activo"} · ${escapeHtml(module.action)}</small>
            </article>
          `
        )
        .join("")
    : `<article class="empty-state"><strong>Sin modulos visibles</strong><p>Cuando tu plan tenga modulos activos, apareceran en este catalogo.</p></article>`;
}

function renderPlanCards(selector, plans) {
  const container = document.querySelector(selector);
  if (!container) return;
  container.innerHTML = (plans || []).length
    ? plans
        .map(
          (plan) => `
            <article class="plan-card">
              <span>${escapeHtml(plan.code || "plan")}</span>
              <strong>${escapeHtml(plan.name)}</strong>
              <p>${escapeHtml(plan.description || "Plan comercial para licenciar capacidades de Icodeup 360.")}</p>
              <div class="plan-limits">
                <small>Usuarios: ${escapeHtml(limitText(plan.max_users))}</small>
                <small>Proyectos: ${escapeHtml(limitText(plan.max_projects))}</small>
                <small>Registros: ${escapeHtml(limitText(plan.max_records || plan.max_customers))}</small>
              </div>
            </article>
          `
        )
        .join("")
    : `<article class="empty-state"><strong>Planes por configurar</strong><p>Los planes comerciales apareceran aqui cuando Icodeup los active para venta.</p></article>`;
}

function applyBranding(source = {}) {
  const primary = source.primary_color || currentUser?.primary_color || "#15956f";
  const secondary = source.secondary_color || currentUser?.secondary_color || "#2563eb";
  document.documentElement.style.setProperty("--primary", primary);
  document.documentElement.style.setProperty("--primary-dark", primary);
  document.documentElement.style.setProperty("--blue", secondary);
}

function renderDynamicMenu() {
  const nav = document.querySelector("#mainNav");
  if (!nav) return;
  const items = state.core.menu?.items || [];
  if (!items.length) return;
  const grouped = items.reduce((acc, item) => {
    const category = sectionCategory(item);
    if (!acc[category]) acc[category] = [];
    acc[category].push(item);
    return acc;
  }, {});
  nav.innerHTML = Object.entries(grouped)
    .map(
      ([category, groupItems]) => `
        <div class="nav-group">
          <p>${escapeHtml(category)}</p>
          ${groupItems
            .map((item, index) => `<button class="nav-item ${items.indexOf(item) === 0 && index === 0 ? "active" : ""}" data-section="${escapeHtml(item.section)}">${iconForSection(item.section)}<span class="nav-label">${escapeHtml(item.label)}</span></button>`)
            .join("")}
        </div>
      `
    )
    .join("");
  const allowedSections = new Set(items.map((item) => item.section));
  document.querySelectorAll(".section").forEach((section) => {
    section.classList.remove("active-section");
    section.classList.toggle("menu-disabled", !allowedSections.has(section.id));
  });
  const firstSection = items[0]?.section || "dashboard";
  document.querySelector(`#${firstSection}`)?.classList.add("active-section");
  document.querySelector("#sectionTitle").textContent = titles[firstSection] || items[0]?.label || "Icodeup 360";
  renderShellContext();
}

function menuHasSection(...sections) {
  const allowedSections = new Set((state.core.menu?.items || []).map((item) => item.section));
  return sections.some((section) => allowedSections.has(section));
}

async function optionalLoad(label, loader) {
  try {
    await loader();
  } catch (error) {
    console.warn(`${label}: ${error.message}`);
  }
}

function showApp() {
  loginView.classList.add("hidden");
  appView.classList.remove("hidden");
  renderShellContext();
  applyBranding(currentUser || {});
  document.querySelectorAll(".platform-only").forEach((item) => item.classList.toggle("hidden", !isPlatform()));
  document.querySelectorAll(".manager-only").forEach((item) => item.classList.toggle("hidden", !canManageCrm()));
  const canExport = ["platform_admin", "tenant_admin", "coordinator"].includes(currentUser?.role);
  document.querySelectorAll("#exportCustomers, #exportPayments").forEach((item) => item.classList.toggle("hidden", !canExport));
}

function showLogin() {
  appView.classList.add("hidden");
  loginView.classList.remove("hidden");
}

function logout() {
  token = "";
  currentUser = null;
  localStorage.removeItem("icodeup_v2_token");
  localStorage.removeItem("icodeup_v2_user");
  showLogin();
}

async function loadHealth() {
  const dot = document.querySelector("#healthDot");
  const text = document.querySelector("#healthText");
  const pill = document.querySelector("#systemStatusPill");
  try {
    const data = await api("/api/health");
    dot.className = data.database?.ok ? "status-ok" : "status-bad";
    text.textContent = data.database?.ok ? "PostgreSQL conectado" : "Base no conectada";
    if (pill) {
      pill.textContent = data.database?.ok ? "Sistema operativo" : "Revisar base de datos";
      pill.className = data.database?.ok ? "status-pill status-pill-ok" : "status-pill status-pill-warn";
    }
  } catch (error) {
    dot.className = "status-bad";
    text.textContent = error.message;
    if (pill) {
      pill.textContent = "Salud no disponible";
      pill.className = "status-pill status-pill-warn";
    }
  }
}

async function loadAdminData() {
  if (!isPlatform()) return;
  const [overview, roles, tenants, projects, users] = await Promise.all([
    api("/api/admin/overview"),
    api("/api/admin/roles"),
    api("/api/admin/tenants"),
    api("/api/admin/projects"),
    api("/api/admin/users")
  ]);
  state.admin = { overview, roles, tenants, projects, users };
}

async function loadGovernanceData() {
  const allowed = (...sections) => menuHasSection(...sections);
  const selectedModuleTenant = isPlatform() ? (document.querySelector("#moduleTenantFilter")?.value || state.admin.tenants[0]?.id || "") : "";
  const moduleTenant = selectedModuleTenant ? `?tenant_id=${selectedModuleTenant}` : "";
  const auditParams = queryParams({
    tenant_id: isPlatform() ? document.querySelector("#auditTenantFilter")?.value || "" : "",
    module: document.querySelector("#auditModuleFilter")?.value || ""
  });
  const [permissions, roles, users, modules, settings, audit, parties, plans, subscriptions, health, securityInsights] = await Promise.all([
    allowed("roles-permissions") ? apiMaybe("/api/governance/permissions", []) : [],
    allowed("roles-permissions") ? apiMaybe("/api/governance/roles", []) : [],
    allowed("company-users", "roles-permissions") ? apiMaybe("/api/governance/users", []) : [],
    allowed("modules", "tenant-modules") ? apiMaybe(`/api/governance/modules${moduleTenant}`, []) : [],
    allowed("tenant-settings", "branding") ? apiMaybe("/api/governance/settings", null) : null,
    allowed("audit", "governance") ? apiMaybe(`/api/governance/audit-logs?${auditParams}`, []) : [],
    allowed("parties") ? apiMaybe("/api/governance/parties", []) : [],
    allowed("plans") ? apiMaybe("/api/subscriptions/plans", []) : [],
    allowed("subscriptions", "governance") ? apiMaybe("/api/governance/subscriptions", []) : [],
    allowed("system-health", "governance") ? apiMaybe("/api/health", null) : null,
    allowed("company-users", "roles-permissions", "tenant-modules") ? apiMaybe("/api/governance/security-insights", []) : []
  ]);
  const selectedAccessId = state.governance.effectiveAccess?.user?.id;
  state.governance = { permissions, roles, users, modules, settings, audit, parties, plans, subscriptions, health, securityInsights, effectiveAccess: state.governance.effectiveAccess };
  if (selectedAccessId && !users.some((item) => Number(item.id) === Number(selectedAccessId))) {
    state.governance.effectiveAccess = null;
  }
  if (settings) applyBranding(settings);
  renderShellContext();
}

async function loadCoreData() {
  const [menu, roleDashboard] = await Promise.all([
    api("/api/menu/me"),
    api("/api/dashboard/me")
  ]);
  state.core.menu = menu;
  state.core.roleDashboard = roleDashboard;
  applyBranding(menu.tenant || {});
  renderShellContext();
}

async function loadTypifications() {
  if (!isPlatform()) return;
  const tenantId = document.querySelector('#typificationForm select[name="tenant_id"]')?.value || state.admin.tenants[0]?.id;
  state.admin.typifications = tenantId ? await api(`/api/typifications?tenant_id=${tenantId}`) : [];
}

function queryParams(params) {
  const search = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "") search.set(key, value);
  });
  return search.toString();
}

async function loadCrmData() {
  const allowed = (...sections) => menuHasSection(...sections);
  const [options, dashboard, promises, payments, channels, typifications] = await Promise.all([
    apiMaybe("/api/crm/options", { tenants: [], projects: [], users: [], channels: [] }),
    allowed("dashboard", "queue", "customers", "reports") ? apiMaybe("/api/crm/dashboard", null) : null,
    allowed("promises") ? apiMaybe("/api/crm/promises", []) : [],
    allowed("payments") ? apiMaybe("/api/crm/payments", []) : [],
    allowed("channels") ? apiMaybe("/api/crm/channels", []) : [],
    canManageCrm() || allowed("queue", "customers") ? apiMaybe("/api/crm/typifications", []) : []
  ]);
  state.crm.options = options;
  state.crm.dashboard = dashboard;
  state.crm.promises = promises;
  state.crm.payments = payments;
  state.crm.channels = channels;
  state.crm.typifications = typifications;
  await Promise.all([loadQueue(), loadCustomers()]);
}

async function loadQueue() {
  const params = queryParams({
    page: state.queuePage,
    page_size: 10,
    q: document.querySelector("#queueSearch")?.value || "",
    status: document.querySelector("#queueStatus")?.value || "",
    risk: document.querySelector("#queueRisk")?.value || ""
  });
  state.crm.queue = await api(`/api/crm/customers?${params}`);
}

async function loadCustomers() {
  const params = queryParams({
    page: state.customerPage,
    page_size: 10,
    q: document.querySelector("#customerSearch")?.value || ""
  });
  state.crm.customers = await api(`/api/crm/customers?${params}`);
}

async function loadBi() {
  const params = queryParams({
    tenant_id: document.querySelector("#biTenant")?.value || "",
    project_id: document.querySelector("#biProject")?.value || "",
    horizon_days: document.querySelector("#biHorizon")?.value || 30
  });
  state.crm.bi = await api(`/api/crm/bi?${params}`);
}

async function loadPhase8Data() {
  const allowed = (...sections) => menuHasSection(...sections);
  const [catalogs, rules, alertRules, workflows, alertItems, alertSummary, legalDashboard, legalKanban, legalCases, salesDashboard, salesPipeline, salesKanban, leads, opportunities] = await Promise.all([
    allowed("configuration") ? apiMaybe("/api/configuration/catalogs", []) : [],
    allowed("configuration") ? apiMaybe("/api/configuration/rules", []) : [],
    allowed("configuration") ? apiMaybe("/api/configuration/alert-rules", []) : [],
    allowed("configuration") ? apiMaybe("/api/configuration/workflows", []) : [],
    allowed("alerts", "dashboard", "reports") ? apiMaybe("/api/alerts?limit=50", []) : [],
    allowed("alerts", "dashboard", "reports") ? apiMaybe("/api/alerts/summary", null) : null,
    allowed("legal") ? apiMaybe("/api/legal/dashboard", null) : null,
    allowed("legal") ? apiMaybe("/api/legal/kanban", null) : null,
    allowed("legal") ? apiMaybe("/api/legal/cases", []) : [],
    allowed("sales") ? apiMaybe("/api/sales/dashboard", null) : null,
    allowed("sales") ? apiMaybe("/api/sales/pipeline", null) : null,
    allowed("sales") ? apiMaybe("/api/sales/kanban", null) : null,
    allowed("sales") ? apiMaybe("/api/sales/leads", []) : [],
    allowed("sales") ? apiMaybe("/api/sales/opportunities", []) : []
  ]);
  state.configuration = { catalogs, rules, alertRules, workflows };
  state.alerts = { items: alertItems, summary: alertSummary };
  state.legal = { dashboard: legalDashboard, kanban: legalKanban, cases: legalCases };
  state.sales = { dashboard: salesDashboard, pipeline: salesPipeline, kanban: salesKanban, leads, opportunities };
}

async function loadPhase8BData() {
  const allowed = (...sections) => menuHasSection(...sections);
  const [trees, combinations, recordings, uploads, demographics, excelSources, excelViews, excelResult, providers, integrationChannels, templates, webhooks, events] = await Promise.all([
    allowed("typification-trees", "typifications") ? apiMaybe("/api/typifications/trees", []) : [],
    allowed("typification-trees", "typifications") ? apiMaybe("/api/typifications/combinations", []) : [],
    allowed("recordings") ? apiMaybe("/api/recordings", []) : [],
    allowed("uploads") ? apiMaybe("/api/uploads/batches", []) : [],
    allowed("uploads", "queue", "customers") ? apiMaybe("/api/uploads/demographics?page_size=50", []) : [],
    allowed("excel-web") ? apiMaybe("/api/excel-web/sources", []) : [],
    allowed("excel-web") ? apiMaybe("/api/excel-web/views", []) : [],
    allowed("excel-web") ? apiMaybe("/api/excel-web/query", null, { method: "POST", body: JSON.stringify({ source: "customers", page: 1, page_size: 10, filters: {}, columns: [] }) }) : null,
    allowed("integrations", "channels") ? apiMaybe("/api/integrations/providers", []) : [],
    allowed("integrations", "channels") ? apiMaybe("/api/integrations/channels", []) : [],
    allowed("integrations") ? apiMaybe("/api/integrations/templates", []) : [],
    allowed("integrations") ? apiMaybe("/api/integrations/webhooks", []) : [],
    allowed("integrations") ? apiMaybe("/api/integrations/events", []) : []
  ]);
  state.ops = { ...state.ops, trees, combinations, recordings, uploads, demographics, excelSources, excelViews, excelResult: state.ops.excelResult || excelResult, providers, integrationChannels, templates, webhooks, events };
}

async function refreshAll() {
  await loadCoreData();
  renderDynamicMenu();
  await loadAdminData();
  await loadGovernanceData();
  await loadTypifications();
  if (menuHasSection("queue", "customers", "promises", "payments", "agreements", "channels", "reports")) {
    await optionalLoad("Datos CRM", loadCrmData);
  }
  if (menuHasSection("reports")) {
    await optionalLoad("BI", loadBi);
  }
  if (menuHasSection("configuration", "alerts", "legal", "sales", "dashboard", "reports")) {
    await optionalLoad("Fase 8", loadPhase8Data);
  }
  if (menuHasSection("typification-trees", "recordings", "uploads", "excel-web", "integrations")) {
    await optionalLoad("Fase 8B", loadPhase8BData);
  }
  renderAll();
}

function optionList(items, valueKey = "id", labelKey = "name", selected = "") {
  return items
    .map((item) => {
      const value = item[valueKey];
      const label = item[labelKey] || item.name;
      return `<option value="${escapeHtml(value)}" ${String(value) === String(selected) ? "selected" : ""}>${escapeHtml(label)}</option>`;
    })
    .join("");
}

function fillSelects() {
  const adminTenantOptions = optionList(state.admin.tenants);
  const crmTenantOptions = optionList(state.crm.options.tenants);
  const projectOptions = optionList(state.crm.options.projects, "id", "label");
  const userOptions = optionList(state.crm.options.users, "id", "label");
  const customerOptions = optionList(state.crm.customers?.items || [], "id", "name");
  const permissionOptions = optionList(state.governance.permissions, "code", "code");

  document.querySelectorAll('select[name="tenant_id"]').forEach((select) => {
    const current = select.value;
    const options = isPlatform() ? adminTenantOptions || crmTenantOptions : crmTenantOptions;
    select.innerHTML = `<option value="">Selecciona empresa</option>${options}`;
    if (current) select.value = current;
  });
  document.querySelectorAll('select[name="project_id"]').forEach((select) => {
    const current = select.value;
    select.innerHTML = `<option value="">Selecciona proyecto</option>${projectOptions}`;
    if (current) select.value = current;
  });
  document.querySelectorAll('select[name="assigned_user_id"]').forEach((select) => {
    const current = select.value;
    select.innerHTML = `<option value="">Sin gestor</option>${userOptions}`;
    if (current) select.value = current;
  });
  document.querySelectorAll('select[name="customer_id"]').forEach((select) => {
    const current = select.value;
    select.innerHTML = `<option value="">Selecciona cliente</option>${customerOptions}`;
    if (current) select.value = current;
  });

  const roleSelect = document.querySelector('#userForm select[name="role"]');
  if (roleSelect) roleSelect.innerHTML = optionList(state.admin.roles, "value", "label");
  document.querySelectorAll('#roleForm select[name="permission_codes"]').forEach((select) => {
    const selected = new Set(Array.from(select.selectedOptions).map((option) => option.value));
    select.innerHTML = permissionOptions;
    Array.from(select.options).forEach((option) => {
      option.selected = selected.has(option.value);
    });
  });
  ["#moduleTenantFilter", "#auditTenantFilter"].forEach((selector) => {
    const select = document.querySelector(selector);
    if (!select) return;
    const current = select.value || state.admin.tenants[0]?.id || "";
    select.innerHTML = `<option value="">${selector === "#auditTenantFilter" ? "Todas las empresas" : "Selecciona empresa"}</option>${adminTenantOptions}`;
    if (current) select.value = current;
  });

  const parentSelect = document.querySelector('#typificationForm select[name="parent_id"]');
  if (parentSelect) {
    const editId = document.querySelector('#typificationForm input[name="id"]').value;
    const nodes = state.admin.typifications.filter((node) => String(node.id) !== String(editId));
    parentSelect.innerHTML = `<option value="">Raiz / primera tipificacion</option>${nodes
      .map((node) => `<option value="${node.id}">${escapeHtml(`${"-- ".repeat(typificationLevel(node, state.admin.typifications))}${node.label}`)}</option>`)
      .join("")}`;
  }

  const userFilter = document.querySelector("#userTenantFilter");
  if (userFilter) userFilter.innerHTML = `<option value="">Todas las empresas</option>${adminTenantOptions}`;

  const biTenant = document.querySelector("#biTenant");
  if (biTenant) {
    const current = biTenant.value;
    biTenant.innerHTML = `<option value="">Todas las empresas</option>${crmTenantOptions}`;
    if (current) biTenant.value = current;
  }
  const biProject = document.querySelector("#biProject");
  if (biProject) {
    const current = biProject.value;
    biProject.innerHTML = `<option value="">Todos los proyectos</option>${projectOptions}`;
    if (current) biProject.value = current;
  }

  const statusSelect = document.querySelector("#queueStatus");
  const currentStatus = statusSelect.value;
  const statuses = Object.keys(state.crm.dashboard?.status_distribution || {});
  statusSelect.innerHTML = `<option value="">Todos los estados</option>${statuses.map((item) => `<option>${escapeHtml(item)}</option>`).join("")}`;
  statusSelect.value = currentStatus;

  refreshUserDependentSelects();
}

function refreshUserDependentSelects() {
  if (!isPlatform()) return;
  const form = document.querySelector("#userForm");
  const tenantId = Number(form.elements.tenant_id.value);
  const leaders = state.admin.users.filter((user) => user.tenant_id === tenantId && ["tenant_admin", "coordinator"].includes(user.role));
  const projects = state.admin.projects.filter((project) => project.tenant_id === tenantId && project.status === "active");
  form.elements.leader_id.innerHTML = `<option value="">Sin lider</option>${optionList(leaders)}`;
  form.elements.project_ids.innerHTML = optionList(projects);
}

function renderBars(container, data, labelKey = "label", valueKey = "value") {
  if (!container) return;
  const entries = Array.isArray(data) ? data : Object.entries(data || {}).map(([label, value]) => ({ label, value }));
  const max = Math.max(1, ...entries.map((item) => Number(item[valueKey]) || 0));
  container.innerHTML = entries.length
    ? entries
        .map((item) => {
          const value = Number(item[valueKey]) || 0;
          const width = Math.max(5, Math.round((value / max) * 100));
          return `<div class="bar-row"><span>${escapeHtml(item[labelKey])}</span><div><i style="width:${width}%"></i></div><strong>${escapeHtml(value)}</strong></div>`;
        })
        .join("")
    : `<p class="empty">Sin datos para graficar.</p>`;
}

function renderDashboardStacks() {
  const bi = state.crm.bi || {};
  const projects = (bi.project_performance || []).slice(0, 4);
  document.querySelector("#dashboardProjects").innerHTML = projects.length
    ? projects
        .map(
          (item) => `
            <article class="stack-card">
              <div>
                <strong>${escapeHtml(item.project)}</strong>
                <span class="badge sem-${escapeHtml(item.status)}">${item.score}</span>
              </div>
              <p>${item.customers} clientes - ${money(item.balance)} en cartera</p>
              <div class="mini-progress"><i style="width:${Math.max(5, item.score)}%"></i></div>
              <small>Esperado ${money(item.expected_recovery)} - Contacto ${item.contact_rate}%</small>
            </article>
          `
        )
        .join("")
    : `<p class="empty">Sin proyectos con cartera visible.</p>`;

  const agents = (bi.agent_productivity || []).slice(0, 4);
  document.querySelector("#dashboardTeam").innerHTML = agents.length
    ? agents
        .map(
          (item) => `
            <article class="stack-card">
              <div>
                <strong>${escapeHtml(item.agent)}</strong>
                <span class="badge">${item.score}</span>
              </div>
              <p>${item.assigned} asignados - ${item.activities} gestiones - ${item.promises} promesas</p>
              <div class="mini-progress"><i style="width:${Math.max(5, item.score)}%"></i></div>
              <small>Recuperado ${money(item.recovered)} - Contacto ${item.contact_rate}%</small>
            </article>
          `
        )
        .join("")
    : `<p class="empty">Sin productividad disponible por gestor.</p>`;

  const governance = [
    { label: "Aislamiento por empresa", detail: isPlatform() ? "IcodeUp visualiza todo; cada empresa solo ve su operacion." : "Tu sesion esta limitada a la empresa autenticada.", tone: "green" },
    { label: "Roles y alcance", detail: "Administrador, coordinador, supervisor de calidad y gestor con permisos diferenciados.", tone: "green" },
    { label: "Trazabilidad", detail: "Gestiones, promesas, pagos y canales quedan asociados a cliente, proyecto y usuario.", tone: "green" },
    { label: "Motor predictivo", detail: `Modelo ${escapeHtml(bi.prediction?.model || "scoring_operativo_v2")} con scoring, semaforos y valor esperado.`, tone: "blue" },
  ];
  document.querySelector("#dashboardGovernance").innerHTML = governance
    .map(
      (item) => `
        <article class="governance-item ${item.tone}">
          <strong>${item.label}</strong>
          <p>${item.detail}</p>
        </article>
      `
    )
    .join("");
}

function actionsForAudience(audience) {
  if (audience === "platform_admin") {
    return [
      { label: "Gobierno SaaS", title: "Empresas y suscripciones", detail: "Control comercial y operativo global.", section: "governance" },
      { label: "Licenciamiento", title: "Planes y modulos", detail: "Revisa capacidades contratadas por tenant.", section: "plans" },
      { label: "Control", title: "Auditoria global", detail: "Trazabilidad de acciones criticas.", section: "audit" },
    ];
  }
  if (audience === "company_admin") {
    return [
      { label: "Mi empresa", title: "Configuracion tenant", detail: "Branding, usuarios y parametros.", section: "tenant-settings" },
      { label: "Accesos", title: "Roles y permisos", detail: "Define acciones por modulo contratado.", section: "roles-permissions" },
      { label: "Operacion", title: "Reportes de empresa", detail: "Analitica y salud operativa.", section: "reports" },
    ];
  }
  if (audience === "operational_leader") {
    return [
      { label: "Equipo", title: "Cola de gestion", detail: "Prioriza casos por riesgo y SLA.", section: "queue" },
      { label: "Recuperacion", title: "Promesas y pagos", detail: "Controla compromisos y recaudo.", section: "promises" },
      { label: "Decision", title: "Reportes BI", detail: "Consulta semaforos y oportunidades.", section: "reports" },
    ];
  }
  return [
    { label: "Hoy", title: "Mis tareas", detail: "Pendientes y siguientes acciones.", section: "tasks" },
    { label: "Gestion", title: "Cola asignada", detail: "Clientes priorizados para contactar.", section: "queue" },
    { label: "Seguimiento", title: "Clientes", detail: "Consulta tu base operativa.", section: "customers" },
  ];
}

function renderRoleDashboard() {
  const container = document.querySelector("#roleDashboard");
  if (!container) return;
  const data = state.core.roleDashboard;
  if (!data) {
    container.innerHTML = "";
    return;
  }
  const user = menuUser();
  const tenant = activeTenant();
  const audience = user.audience || data.audience || "operational_user";
  container.innerHTML = `
    <article class="role-dashboard-head">
      <div>
        <p class="eyebrow">${escapeHtml(audienceLabel(audience))}</p>
        <h2>${escapeHtml(data.title || "Icodeup 360")}</h2>
        <p>Workspace: ${escapeHtml(tenant.name || "Empresa activa")} · Perfil: ${escapeHtml(roleLabel(user.profile_role || user.role))}</p>
      </div>
      <span>${dateOnly(data.generated_at)}</span>
    </article>
    <div class="intelligence-grid">
      ${(data.cards || [])
        .map(
          (card) => `
            <article class="analysis-card ${escapeHtml(card.tone || "neutral")}">
              <span>${escapeHtml(card.label)}</span>
              <strong>${escapeHtml(typeof card.value === "number" ? card.value.toLocaleString("es-CO") : card.value)}</strong>
              <p>${escapeHtml(card.detail || "")}</p>
            </article>
          `
        )
        .join("")}
    </div>
    <div class="compact-alert-list horizontal-alerts">
      ${(data.alerts || [])
        .map(
          (alert) => `
            <article class="mini-alert ${escapeHtml(alert.tone || "neutral")}">
              <strong>${escapeHtml(alert.title)}</strong>
              <p>${escapeHtml(alert.body || "")}</p>
            </article>
          `
        )
        .join("")}
    </div>
  `;
  renderQuickActions("#experienceActions", actionsForAudience(audience).filter((action) => menuHasSection(action.section)));
  renderModuleCatalog("#experienceModules", menuModules());
}

function renderDashboard() {
  const data = state.crm.dashboard || {};
  const bi = state.crm.bi || {};
  document.querySelector("#metricCustomers").textContent = data.customers || 0;
  document.querySelector("#metricBalance").textContent = money(data.total_balance);
  document.querySelector("#metricRecovered").textContent = money(data.recovered);
  document.querySelector("#metricContact").textContent = `${data.contact_rate || 0}%`;
  renderCardSet("#dashboardPulse", [
    {
      label: "Recuperacion esperada",
      value: money(bi.prediction?.expected_recovery || 0),
      detail: `Proyeccion a ${bi.horizon_days || 30} dias con motor predictivo.`,
      tone: (bi.prediction?.expected_recovery || 0) > 0 ? "green" : "yellow",
      action: "Convertir en meta por proyecto y lider."
    },
    {
      label: "Promesas vigentes",
      value: data.active_promises || 0,
      detail: `${money(data.promise_value || 0)} comprometidos en promesas abiertas.`,
      tone: data.overdue_promises ? "yellow" : "green",
      action: data.overdue_promises ? `${data.overdue_promises} promesas vencidas requieren contacto.` : "Control diario saludable."
    },
    {
      label: "Riesgo alto",
      value: data.high_risk || 0,
      detail: `${money(numberFromKpi("risk_value"))} concentrados en clientes criticos.`,
      tone: data.high_risk ? "red" : "green",
      action: "Priorizar casos de mayor exposicion."
    },
    {
      label: "Seguimientos hoy",
      value: data.due_today || 0,
      detail: "Clientes con fecha de contacto vencida o programada para hoy.",
      tone: data.due_today ? "yellow" : "green",
      action: "Mantener la cola limpia por SLA."
    },
  ]);
  renderBars(document.querySelector("#riskBars"), data.risk_distribution || {});
  renderBars(document.querySelector("#statusBars"), data.status_distribution || {});
  document.querySelector("#dashboardSemaphores").innerHTML = (bi.semaphores || [])
    .slice(0, 6)
    .map(
      (item) => `
        <article class="semaphore-card ${escapeHtml(item.status)}">
          <div><strong>${item.score}</strong><span>/100</span></div>
          <h3>${escapeHtml(item.label)}</h3>
          <p>${escapeHtml(item.detail)}</p>
        </article>
      `
    )
    .join("") || `<p class="empty">Sin semaforos calculados.</p>`;
  renderAlertSet(
    "#dashboardAgenda",
    (bi.alerts || []).slice(0, 4).map((alert) => ({
      title: alert.title,
      body: alert.body,
      value: money(alert.value || 0),
      action: alert.action,
      tone: alert.severity
    })),
    "Sin alertas criticas con la operacion actual."
  );
  renderDashboardStacks();
  const recommendedRows = (bi.top_opportunities || [])
    .slice(0, 10)
    .map(
      (item) => `
        <tr>
          <td><strong>${escapeHtml(item.customer)}</strong><small>${escapeHtml(item.project)}</small></td>
          <td>${money(item.balance)}</td>
          <td>${item.probability}%</td>
          <td>${money(item.expected_recovery)}</td>
          <td>${escapeHtml(item.next_action)}</td>
        </tr>
      `
    )
    .join("");
  document.querySelector("#dashboardRecommended").innerHTML = table(["Cliente", "Saldo", "Probabilidad", "Esperado", "Siguiente accion"], recommendedRows, "Sin casos recomendados por ahora.");
  if (isPlatform()) {
    renderBars(document.querySelector("#tenantBars"), state.admin.tenants.map((tenant) => ({ label: tenant.name, value: tenant.project_count })));
  }
}

function renderBiBar(container, rows, valueKey = "value", valueFormatter = (value) => value) {
  if (!container) return;
  const max = Math.max(1, ...rows.map((item) => Number(item[valueKey]) || 0));
  container.innerHTML = rows.length
    ? rows
        .map((item) => {
          const value = Number(item[valueKey]) || 0;
          const width = Math.max(5, Math.round((value / max) * 100));
          return `<div class="bar-row"><span>${escapeHtml(item.label)}</span><div><i style="width:${width}%"></i></div><strong>${escapeHtml(valueFormatter(value))}</strong></div>`;
        })
        .join("")
    : `<p class="empty">Sin datos para graficar.</p>`;
}

function formatKpiValue(kpi) {
  if (typeof kpi.value === "number" && ["expected_recovery", "risk_value", "no_contact_value", "overdue_promise_value"].includes(kpi.key)) {
    return money(kpi.value);
  }
  return escapeHtml(kpi.value);
}

function renderBI() {
  const bi = state.crm.bi;
  if (!bi) return;
  document.querySelector("#biKpis").innerHTML = (bi.kpis || [])
    .map(
      (kpi) => `
        <article class="metric-card bi-kpi ${escapeHtml(kpi.status)}">
          <span>${escapeHtml(kpi.label)}</span>
          <strong>${formatKpiValue(kpi)}</strong>
          <p>${escapeHtml(kpi.detail)}</p>
        </article>
      `
    )
    .join("");

  document.querySelector("#biExpectedRecovery").textContent = money(bi.prediction?.expected_recovery || 0);
  document.querySelector("#biPredictionRange").textContent = `Rango probable: ${money(bi.prediction?.expected_recovery_low || 0)} a ${money(bi.prediction?.expected_recovery_high || 0)} en ${bi.horizon_days} dias.`;
  document.querySelector("#biLeakageRisk").textContent = money(bi.prediction?.leakage_risk_value || 0);

  document.querySelector("#biSemaphores").innerHTML = (bi.semaphores || [])
    .map(
      (item) => `
        <article class="semaphore-card ${escapeHtml(item.status)}">
          <div><strong>${item.score}</strong><span>/100</span></div>
          <h3>${escapeHtml(item.label)}</h3>
          <p>${escapeHtml(item.detail)}</p>
        </article>
      `
    )
    .join("");

  document.querySelector("#biAlerts").innerHTML = (bi.alerts || [])
    .map(
      (alert) => `
        <article class="alert-card ${escapeHtml(alert.severity)}">
          <strong>${escapeHtml(alert.title)}</strong>
          <span>${money(alert.value)}</span>
          <p>${escapeHtml(alert.body)}</p>
          <small>${escapeHtml(alert.action)}</small>
        </article>
      `
    )
    .join("") || `<p class="empty">Sin alertas criticas con los filtros actuales.</p>`;

  renderBiBar(
    document.querySelector("#biAging"),
    (bi.aging_buckets || []).map((item) => ({ label: `${item.label} dias (${item.customers})`, value: item.balance, expected: item.expected_recovery })),
    "value",
    money
  );
  renderBiBar(document.querySelector("#biFunnel"), bi.funnel || [], "value", (value) => `${value} casos`);

  const projectRows = (bi.project_performance || [])
    .map(
      (item) => `
        <tr>
          <td><strong>${escapeHtml(item.project)}</strong><small>${item.customers} clientes</small></td>
          <td>${money(item.balance)}</td>
          <td>${money(item.recovered)}</td>
          <td>${money(item.expected_recovery)}</td>
          <td>${item.contact_rate}%</td>
          <td><span class="badge sem-${escapeHtml(item.status)}">${item.score}</span></td>
        </tr>
      `
    )
    .join("");
  document.querySelector("#biProjectPerformance").innerHTML = table(["Proyecto", "Saldo", "Recuperado", "Esperado", "Contacto", "Score"], projectRows, "Sin proyectos para analizar.");

  const agentRows = (bi.agent_productivity || [])
    .map(
      (item) => `
        <tr>
          <td><strong>${escapeHtml(item.agent)}</strong><small>${item.assigned} casos asignados</small></td>
          <td>${item.activities}</td>
          <td>${item.promises}</td>
          <td>${money(item.recovered)}</td>
          <td>${money(item.expected_recovery)}</td>
          <td>${item.contact_rate}%</td>
          <td><span class="badge">${item.score}</span></td>
        </tr>
      `
    )
    .join("");
  document.querySelector("#biAgentProductivity").innerHTML = table(["Gestor", "Gestiones", "Promesas", "Recuperado", "Esperado", "Contacto", "Score"], agentRows, "Sin gestores con cartera asignada.");

  const opportunityRows = (bi.top_opportunities || [])
    .map(
      (item) => `
        <tr>
          <td><strong>${escapeHtml(item.customer)}</strong><small>${escapeHtml(item.project)}</small></td>
          <td>${money(item.balance)}</td>
          <td>${item.probability}%</td>
          <td>${money(item.expected_recovery)}</td>
          <td>${escapeHtml(item.next_action)}</td>
        </tr>
      `
    )
    .join("");
  document.querySelector("#biOpportunities").innerHTML = table(["Cliente", "Saldo", "Prob.", "Esperado", "Accion"], opportunityRows, "Sin oportunidades calculadas.");

  const highRiskRows = (bi.high_risk_cases || [])
    .map(
      (item) => `
        <tr>
          <td><strong>${escapeHtml(item.customer)}</strong><small>${item.stale ? "Sin gestion reciente" : "Gestion reciente"}</small></td>
          <td>${money(item.balance)}</td>
          <td>${item.dpd}</td>
          <td>${escapeHtml(item.status)}</td>
          <td>${item.priority}</td>
        </tr>
      `
    )
    .join("");
  document.querySelector("#biHighRiskCases").innerHTML = table(["Cliente", "Saldo", "DPD", "Estado", "Prioridad"], highRiskRows, "Sin casos criticos.");

  document.querySelector("#biInsights").innerHTML = (bi.insights || [])
    .map(
      (item) => `
        <article class="insight-card">
          <span>${item.confidence}% confianza</span>
          <strong>${escapeHtml(item.title)}</strong>
          <p>${escapeHtml(item.body)}</p>
          <div>${money(item.impact_value)}</div>
          <small>${escapeHtml(item.action)}</small>
        </article>
      `
    )
    .join("");
}

function table(headers, rows, emptyMessage) {
  if (!rows) return `<p class="empty">${escapeHtml(emptyMessage)}</p>`;
  return `<table><thead><tr>${headers.map((item) => `<th>${escapeHtml(item)}</th>`).join("")}</tr></thead><tbody>${rows}</tbody></table>`;
}

function renderQueue() {
  const response = state.crm.queue || { items: [], page: 1, total_pages: 1, total: 0 };
  const rows = response.items
    .map(
      (customer) => `
        <tr>
          <td><strong>${customer.priority}</strong></td>
          <td><strong>${escapeHtml(customer.name)}</strong><small>${escapeHtml(customer.phone || "")}</small></td>
          <td>${escapeHtml(customer.document)}</td>
          <td>${money(customer.balance)}</td>
          <td>${customer.dpd}</td>
          <td><span class="badge risk-${escapeHtml(customer.risk).toLowerCase()}">${escapeHtml(customer.risk)}</span></td>
          <td>${escapeHtml(customer.status)}</td>
          <td><button class="table-button" data-open-customer="${customer.id}" type="button">Gestionar</button></td>
        </tr>
      `
    )
    .join("");
  document.querySelector("#queueTable").innerHTML = table(["Prioridad", "Cliente", "Documento", "Saldo", "DPD", "Riesgo", "Estado", ""], rows, "No hay clientes en cola.");
  document.querySelector("#queuePageLabel").textContent = `Pagina ${response.page} de ${response.total_pages} - ${response.total} casos`;
  document.querySelector("#queuePrev").disabled = response.page <= 1;
  document.querySelector("#queueNext").disabled = response.page >= response.total_pages;
  if (!state.selectedCustomer && response.items[0]) selectCustomer(response.items[0].id);
}

async function selectCustomer(customerId) {
  const customer = [...(state.crm.queue?.items || []), ...(state.crm.customers?.items || [])].find((item) => Number(item.id) === Number(customerId));
  state.selectedCustomer = customer || null;
  state.selectedActivities = customer ? await api(`/api/crm/customers/${customer.id}/activities`) : [];
  renderQueueDetail();
}

function channelHref(kind, customer) {
  if (kind === "whatsapp") {
    return `https://wa.me/${phoneDigits(customer.phone)}?text=${encodeURIComponent(`Hola ${customer.name}, te contactamos desde IcodeUp CRM para revisar alternativas de normalizacion de tu obligacion.`)}`;
  }
  if (kind === "email") {
    return `mailto:${customer.email || ""}?subject=${encodeURIComponent("Alternativas de normalizacion")}`;
  }
  return `tel:${customer.phone || ""}`;
}

function renderQueueDetail() {
  const customer = state.selectedCustomer;
  const panel = document.querySelector("#queueDetail");
  if (!customer) {
    panel.innerHTML = `<p class="empty">Selecciona un cliente para gestionar.</p>`;
    return;
  }
  const activityCards = state.selectedActivities
    .slice(0, 10)
    .map(
      (item) => `
        <article class="activity-card">
          <strong>${escapeHtml(item.result)}</strong>
          <span>${dateOnly(item.created_at)} - ${escapeHtml(item.user_name || "")}</span>
          <p>${escapeHtml(item.note || "Gestion registrada.")}</p>
        </article>
      `
    )
    .join("");
  panel.innerHTML = `
    <div class="case-header">
      <div>
        <h2>${escapeHtml(customer.name)}</h2>
        <p>${escapeHtml(customer.document)} - ${escapeHtml(customer.project_name || "")}</p>
      </div>
      <span class="badge">${escapeHtml(customer.status)}</span>
    </div>
    <div class="case-stats">
      <div><span>Saldo</span><strong>${money(customer.balance)}</strong></div>
      <div><span>Mora</span><strong>${customer.dpd} dias</strong></div>
      <div><span>Riesgo</span><strong>${escapeHtml(customer.risk)}</strong></div>
      <div><span>Gestor</span><strong>${escapeHtml(customer.assigned_user_name || "-")}</strong></div>
    </div>
    <div class="channel-actions">
      <a href="${channelHref("telephony", customer)}">Click to call</a>
      <a href="${channelHref("whatsapp", customer)}" target="_blank" rel="noreferrer">WhatsApp</a>
      <a href="${channelHref("email", customer)}">Email</a>
    </div>
    <form id="activityForm" class="form-grid management-grid" data-customer-id="${customer.id}">
      <label>Tipificacion<select name="typification_id">${typificationOptionsForCustomer(customer)}</select></label>
      <label>Canal<select name="channel"><option value="phone">Llamada</option><option value="whatsapp">WhatsApp</option><option value="email">Email</option><option value="manual">Manual</option></select></label>
      <label>Resultado<select name="result"><option>Contactado</option><option>Sin contacto</option><option>Promesa</option><option>Escalado</option><option>Disputa</option></select></label>
      <label>Siguiente fecha<input name="next_contact_at" type="date" /></label>
      <label>Promesa monto<input name="promise_amount" type="number" min="0" /></label>
      <label>Promesa fecha<input name="promise_due_date" type="date" /></label>
      <label class="wide">Nota<textarea name="note" placeholder="Resumen de conversacion, objecion o acuerdo."></textarea></label>
      <button type="submit">Guardar gestion</button>
      <p class="form-message wide" data-form-message></p>
    </form>
    <div class="activity-head"><strong>Actividad reciente</strong><span>Ultimas 10 gestiones</span></div>
    <div class="activity-matrix">${activityCards || `<p class="empty">Sin gestiones registradas.</p>`}</div>
  `;
  panel.querySelector("#activityForm").addEventListener("submit", submitActivity);
}

function ensureManagementDrawer() {
  let drawer = document.querySelector("#managementDrawer");
  if (!drawer) {
    drawer = document.createElement("aside");
    drawer.id = "managementDrawer";
    drawer.className = "management-drawer hidden";
    drawer.setAttribute("aria-label", "Gestion operativa de cliente");
    document.body.appendChild(drawer);
  }
  return drawer;
}

async function openCustomerDrawer(customerId) {
  await selectCustomer(customerId);
  renderManagementDrawer();
  ensureManagementDrawer().classList.remove("hidden");
  document.body.classList.add("drawer-open");
}

function closeManagementDrawer() {
  const drawer = document.querySelector("#managementDrawer");
  if (drawer) drawer.classList.add("hidden");
  document.body.classList.remove("drawer-open");
}

function relatedRows(items, render, emptyText) {
  return (items || []).length
    ? items.slice(0, 8).map(render).join("")
    : `<p class="empty">${escapeHtml(emptyText)}</p>`;
}

function renderManagementDrawer() {
  const customer = state.selectedCustomer;
  const drawer = ensureManagementDrawer();
  if (!customer) {
    drawer.innerHTML = `<button class="drawer-close" data-close-drawer type="button">Cerrar</button><p class="empty">Selecciona un cliente para gestionar.</p>`;
    return;
  }
  const activities = state.selectedActivities || [];
  const promises = (state.crm.promises || []).filter((item) => Number(item.customer_id) === Number(customer.id) || item.customer_name === customer.name);
  const payments = (state.crm.payments || []).filter((item) => Number(item.customer_id) === Number(customer.id) || item.customer_name === customer.name);
  const demographics = (state.ops.demographics || []).filter((item) => Number(item.customer_id) === Number(customer.id));
  const recordings = menuHasSection("recordings") ? (state.ops.recordings || []).filter((item) => Number(item.customer_id) === Number(customer.id)) : [];
  drawer.innerHTML = `
    <div class="drawer-backdrop" data-close-drawer></div>
    <section class="drawer-panel">
      <header class="drawer-header">
        <div>
          <span class="eyebrow">Gestion operativa</span>
          <h2>${escapeHtml(customer.name)}</h2>
          <p>${escapeHtml(customer.document)} - ${escapeHtml(customer.project_name || "Cartera")}</p>
        </div>
        <button class="drawer-close" data-close-drawer type="button" aria-label="Cerrar">Cerrar</button>
      </header>
      <div class="drawer-summary">
        <article><span>Saldo</span><strong>${money(customer.balance)}</strong></article>
        <article><span>Mora</span><strong>${customer.dpd} dias</strong></article>
        <article><span>Riesgo</span><strong>${escapeHtml(customer.risk)}</strong></article>
        <article><span>Gestor</span><strong>${escapeHtml(customer.assigned_user_name || "-")}</strong></article>
        <article><span>Estado</span><strong>${escapeHtml(customer.status || "-")}</strong></article>
      </div>
      <div class="drawer-actions">
        <a href="${channelHref("telephony", customer)}">Click to call</a>
        <a href="${channelHref("whatsapp", customer)}" target="_blank" rel="noreferrer">WhatsApp</a>
        <a href="${channelHref("email", customer)}">Email</a>
        <button type="button" data-prefill-result="Contactado">Registrar llamada</button>
        <button type="button" data-prefill-result="Promesa">Crear promesa</button>
        <button type="button" data-section-jump="agreements">Crear acuerdo</button>
        <button type="button" data-prefill-result="Escalado">Escalar juridico</button>
      </div>
      <div class="drawer-content-grid">
        <article class="drawer-card">
          <h3>Registrar gestion</h3>
          <form id="drawerActivityForm" class="form-grid management-grid" data-customer-id="${customer.id}">
            <label>Tipificacion<select name="typification_id">${typificationOptionsForCustomer(customer)}</select></label>
            <label>Canal<select name="channel"><option value="phone">Llamada</option><option value="whatsapp">WhatsApp</option><option value="email">Email</option><option value="manual">Manual</option></select></label>
            <label>Resultado<select name="result"><option>Contactado</option><option>Sin contacto</option><option>Promesa</option><option>Escalado</option><option>Disputa</option></select></label>
            <label>Siguiente fecha<input name="next_contact_at" type="date" /></label>
            <label>Promesa monto<input name="promise_amount" type="number" min="0" /></label>
            <label>Promesa fecha<input name="promise_due_date" type="date" /></label>
            <label class="wide">Nota<textarea name="note" placeholder="Resumen de conversacion, objecion o acuerdo." required></textarea></label>
            <button type="submit">Guardar gestion</button>
            <button type="button" class="secondary-button" data-close-drawer>Cancelar</button>
            <p class="form-message wide" data-form-message></p>
          </form>
        </article>
        <article class="drawer-card">
          <h3>Actividad reciente</h3>
          <div class="activity-matrix compact">${relatedRows(activities, (item) => `<article class="activity-card"><strong>${escapeHtml(item.result)}</strong><span>${dateOnly(item.created_at)} - ${escapeHtml(item.user_name || "")}</span><p>${escapeHtml(item.note || "Gestion registrada.")}</p></article>`, "Sin gestiones registradas.")}</div>
        </article>
        <article class="drawer-card">
          <h3>Promesas y pagos</h3>
          <div class="mini-list">${relatedRows(promises, (item) => `<p><strong>${money(item.amount)}</strong><span>${dateOnly(item.due_date)} - ${escapeHtml(item.status)}</span></p>`, "Sin promesas para este cliente.")}</div>
          <div class="mini-list">${relatedRows(payments, (item) => `<p><strong>${money(item.amount)}</strong><span>${dateOnly(item.paid_at)} - ${escapeHtml(item.method || "-")}</span></p>`, "Sin pagos para este cliente.")}</div>
        </article>
        <article class="drawer-card">
          <h3>Datos complementarios</h3>
          <div class="mini-list">${relatedRows(demographics, (item) => `<p><strong>${escapeHtml(item.source)}</strong><span>${escapeHtml(item.phone || item.email || item.city || "-")}</span></p>`, "Sin demograficos asociados.")}</div>
          ${menuHasSection("recordings") ? `<h3>Grabaciones</h3><div class="mini-list">${relatedRows(recordings, (item) => `<p><strong>${escapeHtml(item.call_id)}</strong><span>${Math.round((item.duration_seconds || 0) / 60)} min - ${escapeHtml(item.status)}</span></p>`, "Sin grabaciones asociadas.")}</div>` : ""}
        </article>
      </div>
    </section>
  `;
  drawer.querySelector("#drawerActivityForm")?.addEventListener("submit", submitActivity);
}

async function submitActivity(event) {
  event.preventDefault();
  const form = event.currentTarget;
  const button = form.querySelector("button[type='submit']");
  const message = form.querySelector("[data-form-message]");
  const customerId = form.dataset.customerId || state.selectedCustomer?.id;
  if (!customerId) {
    showToast("error", "No hay cliente seleccionado para guardar la gestion.");
    return;
  }
  const body = {
    typification_id: form.elements.typification_id.value ? Number(form.elements.typification_id.value) : null,
    channel: form.elements.channel.value,
    result: form.elements.result.value,
    note: form.elements.note.value,
    next_contact_at: toDateTime(form.elements.next_contact_at.value),
    promise_amount: form.elements.promise_amount.value ? Number(form.elements.promise_amount.value) : null,
    promise_due_date: toDateTime(form.elements.promise_due_date.value)
  };
  if (!body.result) {
    showToast("warning", "Selecciona un resultado de gestion.");
    return;
  }
  if (!String(body.note || "").trim()) {
    showToast("warning", "Registra una nota para guardar la gestion.");
    form.elements.note?.focus();
    return;
  }
  if (message) message.textContent = "";
  setButtonLoading(button, true, "Guardando...");
  try {
    await api(`/api/crm/customers/${customerId}/activities`, { method: "POST", body: JSON.stringify(body) });
  } catch (error) {
    console.warn(error);
    showToast("error", error.message || "No tienes permiso para gestionar este cliente.");
    return;
  } finally {
    setButtonLoading(button, false);
  }
  form.reset();
  await refreshCustomerAfterActivity(customerId);
  const activeMessage = document.querySelector("#drawerActivityForm [data-form-message]");
  if (activeMessage) activeMessage.textContent = "Gestion guardada correctamente.";
  showToast("success", "Gestion guardada correctamente.");
}

async function refreshCustomerAfterActivity(customerId) {
  const activityRequest = api(`/api/crm/customers/${customerId}/activities`);
  const [queueResult, customersResult, activitiesResult, promisesResult, paymentsResult] = await Promise.allSettled([
    loadQueue(),
    loadCustomers(),
    activityRequest,
    menuHasSection("promises") ? api("/api/crm/promises") : Promise.resolve(state.crm.promises || []),
    menuHasSection("payments") ? api("/api/crm/payments") : Promise.resolve(state.crm.payments || []),
  ]);
  [queueResult, customersResult, activitiesResult, promisesResult, paymentsResult].forEach((result) => {
    if (result.status === "rejected") console.warn("Refresh posterior a gestion omitido:", result.reason);
  });
  if (activitiesResult.status === "fulfilled") state.selectedActivities = activitiesResult.value;
  if (promisesResult.status === "fulfilled") state.crm.promises = promisesResult.value;
  if (paymentsResult.status === "fulfilled") state.crm.payments = paymentsResult.value;
  const refreshedCustomer = [...(state.crm.queue?.items || []), ...(state.crm.customers?.items || [])].find((item) => Number(item.id) === Number(customerId));
  if (refreshedCustomer) state.selectedCustomer = refreshedCustomer;
  renderQueue();
  renderCustomers();
  renderPromises();
  renderPayments();
  renderQueueDetail();
  if (!document.querySelector("#managementDrawer")?.classList.contains("hidden")) renderManagementDrawer();
}

function renderCustomers() {
  const response = state.crm.customers || { items: [], page: 1, total_pages: 1, total: 0 };
  const rows = response.items
    .map(
      (customer) => `
        <tr>
          <td><strong>${escapeHtml(customer.name)}</strong><small>${escapeHtml(customer.document)}</small></td>
          <td>${escapeHtml(customer.project_name || "-")}</td>
          <td>${escapeHtml(customer.assigned_user_name || "-")}</td>
          <td>${money(customer.balance)}</td>
          <td>${customer.dpd}</td>
          <td>${escapeHtml(customer.status)}</td>
          <td><button class="table-button" data-open-customer="${customer.id}" type="button">Gestionar</button></td>
        </tr>
      `
    )
    .join("");
  document.querySelector("#customerTable").innerHTML = table(["Cliente", "Proyecto", "Gestor", "Saldo", "DPD", "Estado", ""], rows, "No hay clientes.");
  document.querySelector("#customerPageLabel").textContent = `Pagina ${response.page} de ${response.total_pages} - ${response.total} clientes`;
  document.querySelector("#customerPrev").disabled = response.page <= 1;
  document.querySelector("#customerNext").disabled = response.page >= response.total_pages;
}

function renderPromises() {
  const rows = state.crm.promises
    .map(
      (item) => `
        <tr>
          <td>${escapeHtml(item.customer_name || "-")}</td>
          <td>${money(item.amount)}</td>
          <td>${dateOnly(item.due_date)}</td>
          <td>${escapeHtml(item.channel || "-")}</td>
          <td><span class="badge">${escapeHtml(item.status)}</span></td>
          <td>${item.status === "Vigente" ? `<button class="table-button" data-complete-promise="${item.id}" type="button">Cumplir</button>` : ""}</td>
        </tr>
      `
    )
    .join("");
  document.querySelector("#promiseTable").innerHTML = table(["Cliente", "Monto", "Fecha", "Canal", "Estado", ""], rows, "No hay promesas.");
}

function renderPayments() {
  const rows = state.crm.payments
    .map(
      (item) => `
        <tr>
          <td>${escapeHtml(item.customer_name || "-")}</td>
          <td>${money(item.amount)}</td>
          <td>${dateOnly(item.paid_at)}</td>
          <td>${escapeHtml(item.method)}</td>
          <td>${escapeHtml(item.reference || "-")}</td>
        </tr>
      `
    )
    .join("");
  document.querySelector("#paymentTable").innerHTML = table(["Cliente", "Monto", "Fecha", "Metodo", "Referencia"], rows, "No hay pagos.");
}

function renderChannels() {
  const rows = state.crm.channels
    .map(
      (item) => `
        <tr>
          <td><strong>${escapeHtml(item.label)}</strong><small>${escapeHtml(item.provider || "-")}</small></td>
          <td>${escapeHtml(item.kind)}</td>
          <td>${escapeHtml(item.value)}</td>
          <td>${item.is_default ? "Principal" : "-"}</td>
          <td>${escapeHtml(item.status)}</td>
        </tr>
      `
    )
    .join("");
  document.querySelector("#channelTable").innerHTML = table(["Canal", "Tipo", "Valor", "Uso", "Estado"], rows, "No hay canales configurados.");
}

function renderModuleInsights() {
  const dashboard = state.crm.dashboard || {};
  const bi = state.crm.bi || {};
  const queue = state.crm.queue || { items: [], total: 0 };
  const customers = state.crm.customers || { items: [], total: 0 };
  const promises = state.crm.promises || [];
  const payments = state.crm.payments || [];
  const channels = state.crm.channels || [];
  const activePromises = promises.filter((item) => item.status === "Vigente");
  const overduePromises = activePromises.filter((item) => isOverdue(item.due_date));
  const dueSoonPromises = activePromises.filter((item) => isWithinDays(item.due_date, 3));
  const totalPromiseValue = sumBy(activePromises, (item) => item.amount);
  const overduePromiseValue = sumBy(overduePromises, (item) => item.amount);
  const recoveredValue = sumBy(payments, (item) => item.amount);
  const paidThisMonth = sumBy(
    payments.filter((item) => {
      const paid = dateValue(item.paid_at);
      const now = new Date();
      return paid && paid.getMonth() === now.getMonth() && paid.getFullYear() === now.getFullYear();
    }),
    (item) => item.amount
  );
  const highRiskValue = numberFromKpi("risk_value");
  const noContactValue = numberFromKpi("no_contact_value");
  const topOpportunity = (bi.top_opportunities || [])[0];
  const firstAlert = (bi.alerts || [])[0];

  renderCardSet("#queueInsightCards", [
    { label: "Casos visibles", value: queue.total || 0, detail: "Clientes disponibles segun rol, empresa y asignacion.", tone: "blue", action: "La vista pagina maximo 10 para operar con foco." },
    { label: "Alta prioridad", value: bi.high_risk_cases?.length || dashboard.high_risk || 0, detail: `${money(highRiskValue)} en exposicion critica.`, tone: (dashboard.high_risk || 0) ? "red" : "green", action: "Atender primero por probabilidad, mora y saldo." },
    { label: "Seguimientos vencidos", value: dashboard.due_today || 0, detail: "Contactos vencidos o programados para hoy.", tone: dashboard.due_today ? "yellow" : "green", action: "Evita perdida de trazabilidad y promesas frias." },
    { label: "Mejor oportunidad", value: topOpportunity ? money(topOpportunity.expected_recovery) : "$ 0", detail: topOpportunity ? topOpportunity.customer : "Sin proyeccion activa.", tone: topOpportunity ? "green" : "yellow", action: topOpportunity?.next_action || "Cargar y gestionar cartera para activar scoring." },
  ]);
  renderAlertSet(
    "#queueInsightAlerts",
    [
      firstAlert
        ? { title: firstAlert.title, body: firstAlert.body, value: money(firstAlert.value || 0), action: firstAlert.action, tone: firstAlert.severity }
        : null,
      topOpportunity
        ? { title: "Siguiente mejor accion", body: topOpportunity.next_action, value: `${topOpportunity.probability}% prob.`, action: `Cliente sugerido: ${topOpportunity.customer}`, tone: "green" }
        : null,
    ].filter(Boolean)
  );

  renderCardSet("#customerInsightCards", [
    { label: "Clientes en cartera", value: dashboard.customers || customers.total || 0, detail: "Base visible para el usuario autenticado.", tone: "blue", action: "Segmentada por empresa, proyecto y rol." },
    { label: "Cartera pendiente", value: money(dashboard.total_balance || 0), detail: "Saldo activo de clientes cargados.", tone: dashboard.total_balance ? "yellow" : "green", action: "Analizar concentracion por mora y proyecto." },
    { label: "Sin contacto", value: money(noContactValue), detail: kpiByKey("no_contact_value")?.detail || "Casos sin gestion efectiva.", tone: noContactValue ? "red" : "green", action: "Cruzar canales antes de aumentar intensidad." },
    { label: "Contacto efectivo", value: `${dashboard.contact_rate || 0}%`, detail: "Porcentaje de clientes con gestion registrada.", tone: statusTone(dashboard.contact_rate || 0), action: "Meta recomendada: crecer por proyecto y gestor." },
  ]);
  renderAlertSet(
    "#customerInsightAlerts",
    (bi.alerts || [])
      .filter((alert) => ["Cartera sin contacto", "Clientes sin gestor", "Casos sin gestion reciente", "Alta concentracion de riesgo"].includes(alert.title))
      .slice(0, 3)
      .map((alert) => ({ title: alert.title, body: alert.body, value: money(alert.value || 0), action: alert.action, tone: alert.severity }))
  );

  renderCardSet("#promiseInsightCards", [
    { label: "Promesas vigentes", value: activePromises.length, detail: `${money(totalPromiseValue)} comprometidos.`, tone: activePromises.length ? "green" : "yellow", action: "Fuente de recuperacion de corto plazo." },
    { label: "Vencidas", value: overduePromises.length, detail: `${money(overduePromiseValue)} en riesgo por incumplimiento.`, tone: overduePromises.length ? "red" : "green", action: "Escalar contacto humano y confirmar causa." },
    { label: "Vencen 3 dias", value: dueSoonPromises.length, detail: "Promesas cercanas al vencimiento.", tone: dueSoonPromises.length ? "yellow" : "green", action: "Enviar recordatorio y dejar trazabilidad." },
    { label: "Valor esperado", value: money(bi.prediction?.expected_recovery || 0), detail: `Proyeccion a ${bi.horizon_days || 30} dias.`, tone: (bi.prediction?.expected_recovery || 0) ? "green" : "yellow", action: "Usar como meta operativa por lider." },
  ]);
  renderAlertSet(
    "#promiseInsightAlerts",
    [
      overduePromises.length
        ? { title: "Recuperacion en riesgo", body: `${overduePromises.length} promesas ya pasaron su fecha compromiso.`, value: money(overduePromiseValue), action: "Priorizar en la primera franja operativa.", tone: "red" }
        : null,
      dueSoonPromises.length
        ? { title: "Prevencion de incumplimiento", body: `${dueSoonPromises.length} promesas vencen en los proximos 3 dias.`, value: money(sumBy(dueSoonPromises, (item) => item.amount)), action: "Activar recordatorios por canal configurado.", tone: "yellow" }
        : null,
    ].filter(Boolean),
    "Promesas bajo control con los datos actuales."
  );

  renderCardSet("#paymentInsightCards", [
    { label: "Recuperado total", value: money(recoveredValue), detail: `${payments.length} pagos registrados.`, tone: recoveredValue ? "green" : "yellow", action: "Comparar contra meta de recuperacion esperada." },
    { label: "Recuperado mes", value: money(paidThisMonth), detail: "Pagos con fecha del mes actual.", tone: paidThisMonth ? "green" : "yellow", action: "Usar para seguimiento comercial y financiero." },
    { label: "Eficiencia", value: `${dashboard.total_balance || recoveredValue ? Math.round((recoveredValue / Math.max((dashboard.total_balance || 0) + recoveredValue, 1)) * 100) : 0}%`, detail: "Pagos frente a cartera inicial aproximada.", tone: statusTone(Math.round((recoveredValue / Math.max((dashboard.total_balance || 0) + recoveredValue, 1)) * 100) * 2), action: "Revisar por proyecto y gestor." },
    { label: "Fuga potencial", value: money(bi.prediction?.leakage_risk_value || 0), detail: "Valor estimado en riesgo por inactividad o vencimientos.", tone: (bi.prediction?.leakage_risk_value || 0) ? "red" : "green", action: "Convertir alertas en gestion priorizada." },
  ]);
  renderAlertSet(
    "#paymentInsightAlerts",
    (bi.insights || []).slice(0, 2).map((item) => ({ title: item.title, body: item.body, value: money(item.impact_value || 0), action: item.action, tone: "blue" })),
    "Sin hallazgos de recuperacion pendientes."
  );

  const channelKinds = {
    whatsapp: countBy(channels, (item) => item.kind === "whatsapp"),
    email: countBy(channels, (item) => item.kind === "email"),
    telephony: countBy(channels, (item) => item.kind === "telephony"),
  };
  const activeChannels = countBy(channels, (item) => item.status === "active");
  const missingKinds = Object.entries(channelKinds)
    .filter(([, count]) => count === 0)
    .map(([kind]) => kind);
  renderCardSet("#channelInsightCards", [
    { label: "Canales activos", value: activeChannels, detail: `${channels.length} canales configurados.`, tone: activeChannels ? "green" : "red", action: "Base para WhatsApp, correo y telefonia embebida." },
    { label: "WhatsApp", value: channelKinds.whatsapp, detail: "Lineas configuradas para contacto digital.", tone: channelKinds.whatsapp ? "green" : "yellow", action: "Preparar proveedor Cloud API cuando pasemos a integracion." },
    { label: "Email", value: channelKinds.email, detail: "Cuentas remitentes o SMTP configuradas.", tone: channelKinds.email ? "green" : "yellow", action: "Definir plantillas y reputacion de envio." },
    { label: "Telefonia", value: channelKinds.telephony, detail: "Canales SIP/WebRTC o click-to-call.", tone: channelKinds.telephony ? "green" : "yellow", action: "Luego conectamos PBX/WebRTC embebido." },
  ]);
  renderAlertSet(
    "#channelInsightAlerts",
    missingKinds.length
      ? [{ title: "Omnicanalidad incompleta", body: `Faltan canales: ${missingKinds.join(", ")}.`, value: "Pendiente", action: "Configurar al menos un canal por tipo para pruebas productivas.", tone: "yellow" }]
      : [{ title: "Preparacion omnicanal", body: "La empresa visible ya tiene los tres frentes base configurados.", value: "Completo", action: "Siguiente paso: proveedores reales y plantillas.", tone: "green" }]
  );

  if (!isPlatform()) return;
  const tenants = state.admin.tenants || [];
  const projects = state.admin.projects || [];
  const users = state.admin.users || [];
  const typifications = state.admin.typifications || [];
  const tenantsWithoutProjects = tenants.filter((tenant) => !tenant.project_count);
  const projectsWithoutUsers = projects.filter((project) => !project.assigned_user_count);
  const projectsWithoutCustomers = projects.filter((project) => !project.customer_count);
  const agents = users.filter((user) => user.role === "agent");
  const coordinators = users.filter((user) => user.role === "coordinator");
  const qualityUsers = users.filter((user) => user.role === "quality_supervisor");
  const usersWithoutProjects = users.filter((user) => user.role !== "tenant_admin" && !user.project_ids?.length);
  const usersWithoutLeader = users.filter((user) => ["agent", "quality_supervisor"].includes(user.role) && !user.leader_id);
  const rootTypifications = typifications.filter((node) => !node.parent_id);
  const automationNodes = typifications.filter((node) => node.requires_promise || node.requires_payment || node.channel);

  renderCardSet("#tenantInsightCards", [
    { label: "Empresas", value: tenants.length, detail: "Clientes SaaS registrados por IcodeUp.", tone: tenants.length ? "green" : "yellow", action: "Cada empresa conserva datos, usuarios y proyectos separados." },
    { label: "Activas", value: countBy(tenants, (tenant) => tenant.status === "active"), detail: "Empresas habilitadas para operar.", tone: "green", action: "Monitorear crecimiento y capacidad." },
    { label: "Proyectos", value: projects.length, detail: "Carteras operativas entre empresas.", tone: projects.length ? "green" : "yellow", action: "Crear proyectos antes de cargar repartos." },
    { label: "Clientes", value: sumBy(tenants, (tenant) => tenant.customer_count), detail: "Inventario de clientes cargados en tenants.", tone: "blue", action: "IcodeUp puede auditar todo el ecosistema." },
  ]);
  renderAlertSet(
    "#tenantInsightAlerts",
    tenantsWithoutProjects.length
      ? [{ title: "Empresas sin proyecto", body: `${tenantsWithoutProjects.length} empresas aun no tienen cartera activa.`, value: "Configurar", action: "Crear al menos un proyecto para iniciar operacion.", tone: "yellow" }]
      : [{ title: "Tenants operativos", body: "Las empresas registradas tienen estructura base para operar.", value: "OK", action: "Mantener revision de usuarios y cargas.", tone: "green" }]
  );

  renderCardSet("#projectInsightCards", [
    { label: "Proyectos activos", value: countBy(projects, (project) => project.status === "active"), detail: "Carteras disponibles para operar.", tone: "green", action: "Asociar lideres y agentes antes de cargas masivas." },
    { label: "Sin usuarios", value: projectsWithoutUsers.length, detail: "Proyectos sin equipo asignado.", tone: projectsWithoutUsers.length ? "red" : "green", action: "Asignar gestores o coordinadores." },
    { label: "Sin clientes", value: projectsWithoutCustomers.length, detail: "Proyectos sin reparto cargado.", tone: projectsWithoutCustomers.length ? "yellow" : "green", action: "Cargar CSV o crear clientes manuales." },
    { label: "Promedio clientes", value: projects.length ? Math.round(sumBy(projects, (project) => project.customer_count) / projects.length) : 0, detail: "Clientes promedio por proyecto.", tone: "blue", action: "Usar para balancear capacidad operativa." },
  ]);
  renderAlertSet(
    "#projectInsightAlerts",
    [
      projectsWithoutUsers.length ? { title: "Asignacion pendiente", body: `${projectsWithoutUsers.length} proyectos no tienen usuarios asignados.`, value: "Riesgo operativo", action: "Asignar equipo antes de iniciar gestion.", tone: "red" } : null,
      projectsWithoutCustomers.length ? { title: "Carga pendiente", body: `${projectsWithoutCustomers.length} proyectos no tienen clientes.`, value: "Sin reparto", action: "Cargar data financiera y demografica.", tone: "yellow" } : null,
    ].filter(Boolean),
    "Proyectos con estructura operativa completa."
  );

  renderCardSet("#userInsightCards", [
    { label: "Usuarios tenant", value: users.length, detail: "Usuarios de empresas administrados por IcodeUp.", tone: "blue", action: "El superusuario conserva control total." },
    { label: "Agentes", value: agents.length, detail: "Gestores responsables de la cartera.", tone: agents.length ? "green" : "yellow", action: "Asignar a proyectos para activar operacion." },
    { label: "Coordinadores", value: coordinators.length, detail: "Lideres operativos por empresa.", tone: coordinators.length ? "green" : "yellow", action: "Necesarios para seguimiento de equipos." },
    { label: "Calidad", value: qualityUsers.length, detail: "Supervision y auditoria de gestiones.", tone: qualityUsers.length ? "green" : "yellow", action: "Rol clave para gobierno corporativo." },
  ]);
  renderAlertSet(
    "#userInsightAlerts",
    [
      usersWithoutProjects.length ? { title: "Usuarios sin proyecto", body: `${usersWithoutProjects.length} usuarios no tienen proyectos asignados.`, value: "Ajustar", action: "Asociarlos desde el modulo de usuarios.", tone: "yellow" } : null,
      usersWithoutLeader.length ? { title: "Sin lider directo", body: `${usersWithoutLeader.length} usuarios operativos no tienen lider.`, value: "Gobierno", action: "Asignar coordinador o administrador tenant.", tone: "yellow" } : null,
    ].filter(Boolean),
    "Usuarios con gobierno de accesos completo."
  );

  renderCardSet("#typificationInsightCards", [
    { label: "Nodos activos", value: typifications.length, detail: "Reglas de clasificacion disponibles.", tone: typifications.length ? "green" : "yellow", action: "Se usan para guiar la gestion." },
    { label: "Raices", value: rootTypifications.length, detail: "Primer nivel de decision del arbol.", tone: rootTypifications.length ? "green" : "yellow", action: "Deben representar estados generales." },
    { label: "Reglas automaticas", value: automationNodes.length, detail: "Nodos que disparan promesa, pago o canal sugerido.", tone: automationNodes.length ? "green" : "yellow", action: "Reduce parametrizacion manual futura." },
    { label: "Empresas cubiertas", value: new Set(typifications.map((node) => node.tenant_id)).size, detail: "Tenants con arbol de tipificacion configurado.", tone: "blue", action: "Estandarizar plantillas por industria." },
  ]);
  renderAlertSet(
    "#typificationInsightAlerts",
    typifications.length
      ? [{ title: "Motor configurable", body: "Los superusuarios de IcodeUp pueden parametrizar arboles sin tocar base de datos.", value: "Autogestion", action: "Siguiente paso: versionamiento y aprobacion de cambios.", tone: "green" }]
      : [{ title: "Falta arbol de decision", body: "Sin tipificaciones los gestores pierden guia operativa y trazabilidad analitica.", value: "Pendiente", action: "Crear nodos raiz y subtipificaciones por empresa.", tone: "red" }]
  );
}

function renderAdminTables() {
  if (!isPlatform()) return;
  const tenantRows = state.admin.tenants.map((tenant) => `<tr><td><strong>${escapeHtml(tenant.name)}</strong><small>${escapeHtml(tenant.slug)}</small></td><td>${escapeHtml(tenant.tax_id || "-")}</td><td>${tenant.project_count}</td><td>${tenant.user_count}</td><td>${tenant.customer_count}</td></tr>`).join("");
  document.querySelector("#tenantTable").innerHTML = table(["Empresa", "NIT", "Proyectos", "Usuarios", "Clientes"], tenantRows, "No hay empresas.");
  const projectRows = state.admin.projects.map((project) => `<tr><td><strong>${escapeHtml(project.name)}</strong><small>${escapeHtml(project.code)}</small></td><td>${escapeHtml(project.tenant_name)}</td><td>${escapeHtml(project.status)}</td><td>${project.assigned_user_count}</td><td>${project.customer_count}</td></tr>`).join("");
  document.querySelector("#projectTable").innerHTML = table(["Proyecto", "Empresa", "Estado", "Usuarios", "Clientes"], projectRows, "No hay proyectos.");
  const filter = Number(document.querySelector("#userTenantFilter").value || 0);
  const users = filter ? state.admin.users.filter((user) => user.tenant_id === filter) : state.admin.users;
  const userRows = users.map((user) => `<tr><td><strong>${escapeHtml(user.name)}</strong><small>${escapeHtml(user.email)}</small></td><td>${escapeHtml(user.tenant_name)}</td><td>${escapeHtml(user.role_label)}</td><td>${escapeHtml(user.leader_name || "-")}</td><td>${user.project_names.map(escapeHtml).join(", ") || "-"}</td></tr>`).join("");
  document.querySelector("#userTable").innerHTML = table(["Usuario", "Empresa", "Rol", "Lider", "Proyectos"], userRows, "No hay usuarios.");
  renderTypifications();
}

function typificationLevel(node, nodes) {
  let level = 0;
  let parentId = node.parent_id;
  const seen = new Set([node.id]);
  while (parentId && !seen.has(parentId)) {
    seen.add(parentId);
    const parent = nodes.find((item) => item.id === parentId);
    if (!parent) break;
    level += 1;
    parentId = parent.parent_id;
  }
  return level;
}

function typificationOptionsForCustomer(customer) {
  const nodes = state.crm.typifications
    .filter((node) => node.tenant_id === customer.tenant_id && (!node.project_id || node.project_id === customer.project_id))
    .sort((a, b) => typificationLevel(a, state.crm.typifications) - typificationLevel(b, state.crm.typifications) || a.sort_order - b.sort_order || a.label.localeCompare(b.label));
  return `<option value="">Sin tipificacion</option>${nodes
    .map((node) => `<option value="${node.id}">${escapeHtml(`${"-- ".repeat(typificationLevel(node, state.crm.typifications))}${node.label}`)}</option>`)
    .join("")}`;
}

function renderTypifications() {
  const rows = state.admin.typifications
    .slice()
    .sort((a, b) => typificationLevel(a, state.admin.typifications) - typificationLevel(b, state.admin.typifications) || a.sort_order - b.sort_order || a.label.localeCompare(b.label))
    .map((node) => {
      const parent = state.admin.typifications.find((item) => item.id === node.parent_id);
      return `
        <tr>
          <td><strong>${escapeHtml(`${"-- ".repeat(typificationLevel(node, state.admin.typifications))}${node.label}`)}</strong><small>${escapeHtml(node.code)}</small></td>
          <td>${escapeHtml(parent?.label || "Raiz")}</td>
          <td>${escapeHtml(node.next_status || "-")}</td>
          <td>${[node.requires_promise ? "Promesa" : "", node.requires_payment ? "Pago" : "", node.channel || ""].filter(Boolean).join(", ") || "-"}</td>
          <td>
            <button class="table-button" data-edit-typification="${node.id}" type="button">Editar</button>
            <button class="table-button danger-button" data-delete-typification="${node.id}" type="button">Eliminar</button>
          </td>
        </tr>
      `;
    })
    .join("");
  document.querySelector("#typificationTable").innerHTML = table(["Tipificacion", "Padre", "Estado", "Reglas", ""], rows, "No hay tipificaciones configuradas.");
}

function severityClass(severity = "low") {
  return severity === "critical" || severity === "high" ? "risk-alto" : severity === "medium" ? "risk-medio" : "risk-bajo";
}

function permissionModuleSet(permissionCodes = []) {
  const modules = new Set();
  permissionCodes.forEach((code) => {
    if (code.includes(".")) modules.add(code.split(".")[0]);
  });
  return Array.from(modules).sort();
}

function permissionIsCritical(code = "") {
  return code.startsWith("platform.") || code.endsWith(".export") || ["users.create", "users.update", "users.assign", "roles.manage", "roles.configure", "modules.configure", "audit.logs.view", "tenant.settings.configure"].includes(code);
}

function renderSecurityInsights() {
  const container = document.querySelector("#securityInsights");
  if (!container) return;
  const insights = state.governance.securityInsights || [];
  container.innerHTML = insights.length
    ? insights.slice(0, 6).map((item) => `
      <article class="security-insight ${escapeHtml(item.severity || "low")}">
        <span>${escapeHtml(item.severity || "info")}</span>
        <strong>${escapeHtml(item.title)}</strong>
        <p>${escapeHtml(item.description || "")}</p>
        <small>${escapeHtml(item.action || "")}</small>
      </article>
    `).join("")
    : `<article class="empty-state"><strong>Sin alertas visibles</strong><p>Cuando existan riesgos de configuracion, permisos o modulos, se mostraran aqui.</p></article>`;
}

function renderCompanyUserCards() {
  const container = document.querySelector("#companyUserCards");
  if (!container) return;
  const users = state.governance.users || [];
  container.innerHTML = users.length
    ? users.map((user) => {
      const risk = user.risk_flags?.[0] || { severity: "low", label: "Sin alertas" };
      const modules = (user.visible_modules || []).slice(0, 5).map((module) => `<span>${escapeHtml(module)}</span>`).join("");
      return `
        <article class="effective-user-card">
          <div>
            <span class="badge ${severityClass(risk.severity)}">${escapeHtml(risk.label)}</span>
            <strong>${escapeHtml(user.name)}</strong>
            <small>${escapeHtml(user.email)}</small>
          </div>
          <p><b>Perfil:</b> ${escapeHtml(user.business_profile || user.role_name || user.role)}</p>
          <p><b>Legacy:</b> ${escapeHtml(user.legacy_role_label || user.role)} · <b>Especializado:</b> ${escapeHtml(user.specialized_role_code || "fallback")}</p>
          <div class="mini-chip-row">${modules || "<span>Sin modulos</span>"}</div>
          <footer>
            <small>${escapeHtml(String(user.permission_count || 0))} permisos · ${escapeHtml(String(user.visible_module_count || 0))} modulos</small>
            <button class="table-button" data-user-access="${user.id}" type="button">Ver perfil efectivo</button>
          </footer>
        </article>
      `;
    }).join("")
    : `<article class="empty-state"><strong>Sin usuarios visibles</strong><p>Cuando existan usuarios de la empresa, este panel explicara sus accesos.</p></article>`;
}

function renderEffectiveAccessPanel() {
  const container = document.querySelector("#effectiveAccessPanel");
  if (!container) return;
  const access = state.governance.effectiveAccess;
  if (!access) {
    container.innerHTML = `<article class="empty-state"><strong>Selecciona un usuario</strong><p>Abre el perfil efectivo para ver rol legacy, rol especializado, modulos visibles, restricciones y permisos efectivos.</p></article>`;
    return;
  }
  const permissionGroups = Object.entries(access.permission_groups || {});
  const modules = access.modules || [];
  const critical = access.critical_permissions || [];
  container.innerHTML = `
    <article class="effective-access-head">
      <div>
        <p class="eyebrow">Perfil efectivo</p>
        <h2>${escapeHtml(access.user.name)}</h2>
        <p>${escapeHtml(access.user.email)} · ${escapeHtml(access.tenant.name)}</p>
      </div>
      <span class="badge ${critical.length ? "risk-alto" : "risk-bajo"}">${critical.length ? `${critical.length} permisos criticos` : "Sin permisos criticos"}</span>
    </article>
    <div class="effective-access-grid">
      <article>
        <span>Rol legacy</span>
        <strong>${escapeHtml(access.legacy_role.label || access.legacy_role.code)}</strong>
        <p>${escapeHtml(access.legacy_role.description)}</p>
      </article>
      <article>
        <span>Rol especializado</span>
        <strong>${escapeHtml(access.specialized_role.name || "Fallback legacy")}</strong>
        <p>${escapeHtml(access.specialized_role.description || "Perfil funcional usado para permisos granulares.")}</p>
      </article>
      <article>
        <span>Permisos efectivos</span>
        <strong>${escapeHtml(String(access.permission_count || 0))}</strong>
        <p>Acciones permitidas por rol, modulos y tenant.</p>
      </article>
      <article>
        <span>Recomendacion</span>
        <strong>${escapeHtml(access.business_profile || "Usuario")}</strong>
        <p>${escapeHtml(access.recommendation || "")}</p>
      </article>
    </div>
    <div class="access-columns">
      <section>
        <h3>Permisos por modulo</h3>
        ${permissionGroups.length ? permissionGroups.map(([module, items]) => `
          <details open>
            <summary>${escapeHtml(module)} · ${items.length}</summary>
            <div class="mini-chip-row">${items.slice(0, 20).map((item) => `<span class="${item.critical ? "danger-chip" : ""}">${escapeHtml(item.code)}</span>`).join("")}</div>
          </details>
        `).join("") : `<p class="muted">Sin permisos efectivos.</p>`}
      </section>
      <section>
        <h3>Modulos visibles</h3>
        <div class="mini-module-list">
          ${modules.map((module) => `<article><strong>${escapeHtml(module.name)}</strong><span class="badge ${module.visible ? "risk-bajo" : "risk-medio"}">${module.visible ? "Visible" : "Oculto"}</span><p>${escapeHtml(module.reason)}</p></article>`).join("")}
        </div>
      </section>
    </div>
    <div class="permission-guide">
      ${(access.restrictions || []).map((item) => `<article><strong>Restriccion</strong><p>${escapeHtml(item)}</p></article>`).join("")}
      ${(access.risk_flags || []).map((item) => `<article><strong>${escapeHtml(item.label)}</strong><p>${escapeHtml(item.detail)}</p></article>`).join("")}
    </div>
  `;
}

function renderRoleMatrix() {
  const container = document.querySelector("#roleMatrixCards");
  if (!container) return;
  const moduleFilter = document.querySelector("#roleModuleFilter")?.value || "";
  const riskFilter = document.querySelector("#roleRiskFilter")?.value || "";
  const moduleSelect = document.querySelector("#roleModuleFilter");
  if (moduleSelect && !moduleSelect.dataset.loaded) {
    const moduleOptions = Array.from(new Set((state.governance.permissions || []).map((item) => item.module_code).filter(Boolean))).sort();
    moduleSelect.innerHTML = `<option value="">Todos</option>${moduleOptions.map((item) => `<option value="${escapeHtml(item)}">${escapeHtml(item)}</option>`).join("")}`;
    moduleSelect.dataset.loaded = "true";
  }
  const roles = (state.governance.roles || []).filter((role) => {
    const codes = role.permission_codes || [];
    if (moduleFilter && !codes.some((code) => code.startsWith(`${moduleFilter}.`) || code === moduleFilter)) return false;
    if (riskFilter === "critical" && !codes.some(permissionIsCritical)) return false;
    if (riskFilter === "export" && !codes.some((code) => code.endsWith(".export"))) return false;
    if (riskFilter === "admin" && !codes.some((code) => code.startsWith("users.") || code.startsWith("roles.") || code.startsWith("platform.") || code === "modules.configure")) return false;
    return true;
  });
  container.innerHTML = roles.length
    ? roles.map((role) => {
      const modules = permissionModuleSet(role.permission_codes || []);
      const criticalCount = (role.permission_codes || []).filter(permissionIsCritical).length;
      return `
        <article class="role-matrix-card">
          <span>${role.is_system_role ? "Sistema" : "Empresa"}</span>
          <strong>${escapeHtml(role.name)}</strong>
          <small>${escapeHtml(role.code)}</small>
          <p>${escapeHtml(role.description || "Rol sin descripcion.")}</p>
          <div class="mini-chip-row">${modules.slice(0, 8).map((module) => `<span>${escapeHtml(module)}</span>`).join("") || "<span>Sin modulos</span>"}</div>
          <footer>
            <small>${role.permission_codes.length} permisos · ${role.user_count} usuarios</small>
            <span class="badge ${criticalCount ? "risk-alto" : "risk-bajo"}">${criticalCount ? `${criticalCount} criticos` : "Sin criticos"}</span>
          </footer>
        </article>
      `;
    }).join("")
    : `<article class="empty-state"><strong>Sin roles para el filtro</strong><p>Ajusta el modulo o tipo de permiso para ver mas resultados.</p></article>`;
}

function renderTenantModuleInsights() {
  const container = document.querySelector("#tenantModuleInsights");
  if (!container) return;
  const modules = state.governance.modules || [];
  container.innerHTML = modules.length
    ? modules.slice(0, 8).map((module) => {
      const enabled = module.enabled && module.is_enabled;
      return `
        <article class="module-insight ${enabled ? "enabled" : "locked"}">
          <span>${escapeHtml(module.category || "Modulo")}</span>
          <strong>${escapeHtml(module.name)}</strong>
          <p>${escapeHtml(module.commercial_recommendation || "")}</p>
          <small>${escapeHtml(String(module.users_with_access || 0))} usuarios · ${escapeHtml(String(module.related_permission_count || 0))} permisos</small>
        </article>
      `;
    }).join("")
    : `<article class="empty-state"><strong>Sin modulos visibles</strong><p>Los modulos contratados apareceran aqui con impacto y recomendaciones.</p></article>`;
}

function renderGovernanceTables() {
  const governance = state.governance;
  const tenants = state.admin.tenants || [];
  const activeTenants = tenants.filter((tenant) => tenant.status === "active").length;
  const activeModules = governance.modules.filter((module) => module.enabled && module.is_enabled).length;
  renderSecurityInsights();
  renderCompanyUserCards();
  renderEffectiveAccessPanel();
  renderRoleMatrix();
  renderTenantModuleInsights();
  renderCardSet("#governanceCards", [
    { label: "Empresas activas", value: activeTenants, detail: "Tenants cliente con operacion habilitada.", tone: "green" },
    { label: "Suscripciones", value: governance.subscriptions.length, detail: "Contratos visibles para Icodeup plataforma.", tone: "blue" },
    { label: "Modulos activos", value: activeModules, detail: "Capacidades habilitadas en la empresa seleccionada.", tone: "yellow" },
    { label: "Eventos auditoria", value: governance.audit.length, detail: "Acciones recientes trazadas.", tone: "neutral" },
  ]);
  renderAlertSet("#governanceAlerts", [
    { title: "Gobierno separado", body: "El menu dinamico separa Icodeup, administracion de empresa y operacion final.", tone: "green" },
    { title: "Permisos por accion", body: "Las rutas criticas validan modulo, tenant y permiso antes de responder.", tone: "blue" },
  ]);
  renderQuickActions(
    "#governanceQuickActions",
    [
      { label: "Empresas", title: "Crear o revisar tenants", detail: "Inventario comercial y operativo.", section: "tenants" },
      { label: "Suscripciones", title: "Control de licencias", detail: "Planes, modulos y estado comercial.", section: "subscriptions" },
      { label: "Salud", title: "Ver sistema", detail: "Base de datos y servicio.", section: "system-health" },
    ].filter((action) => menuHasSection(action.section))
  );
  renderModuleCatalog("#governanceModuleCatalog", governance.modules, { admin: true });

  const planRows = governance.plans.map((plan) => `<tr><td><strong>${escapeHtml(plan.name)}</strong><small>${escapeHtml(plan.code)}</small></td><td>${money(plan.monthly_price || plan.base_price || 0)}</td><td>${plan.max_users || "Ilimitado"}</td><td>${plan.max_projects || "Ilimitado"}</td><td>${plan.max_records || plan.max_customers || "Ilimitado"}</td><td>${plan.includes_ai ? "Si" : "No"}</td></tr>`).join("");
  renderPlanCards("#planCards", governance.plans);
  document.querySelector("#planTable") && (document.querySelector("#planTable").innerHTML = table(["Plan", "Precio", "Usuarios", "Proyectos", "Registros", "IA"], planRows, "No hay planes configurados."));

  const subscriptionRows = governance.subscriptions.map((item) => `<tr><td><strong>${escapeHtml(item.tenant_name)}</strong><small>${escapeHtml(item.status)}</small></td><td>${escapeHtml(item.plan)}</td><td>${escapeHtml(item.billing_cycle)}</td><td>${item.active_modules}</td></tr>`).join("");
  document.querySelector("#subscriptionCards") && (document.querySelector("#subscriptionCards").innerHTML = governance.subscriptions.length
    ? governance.subscriptions
        .map(
          (item) => `
            <article class="plan-card">
              <span>${escapeHtml(item.status || "suscripcion")}</span>
              <strong>${escapeHtml(item.tenant_name)}</strong>
              <p>Plan ${escapeHtml(item.plan || "sin plan asignado")} con ${escapeHtml(item.active_modules || 0)} modulos activos.</p>
              <div class="plan-limits">
                <small>Ciclo: ${escapeHtml(item.billing_cycle || "-")}</small>
                <small>Estado: ${escapeHtml(item.status || "-")}</small>
              </div>
            </article>
          `
        )
        .join("")
    : `<article class="empty-state"><strong>Sin suscripciones visibles</strong><p>Cuando existan contratos activos, este panel resumira su estado comercial.</p></article>`);
  document.querySelector("#subscriptionTable") && (document.querySelector("#subscriptionTable").innerHTML = table(["Empresa", "Plan", "Ciclo", "Modulos"], subscriptionRows, "No hay suscripciones."));
  document.querySelector("#governanceSubscriptions") && (document.querySelector("#governanceSubscriptions").innerHTML = table(["Empresa", "Plan", "Estado", "Modulos"], subscriptionRows, "Sin datos comerciales."));

  const moduleRows = governance.modules.map((module) => {
    const enabled = module.enabled && module.is_enabled;
    const action = isPlatform() && document.querySelector("#moduleTenantFilter")?.value ? `<button class="table-button" data-toggle-module="${escapeHtml(module.code)}" data-enabled="${enabled}" type="button">${enabled ? "Desactivar" : "Activar"}</button>` : "";
    return `<tr><td><strong>${escapeHtml(module.name)}</strong><small>${escapeHtml(module.code)}</small></td><td>${escapeHtml(module.category)}</td><td><span class="badge ${enabled ? "risk-bajo" : "risk-alto"}">${enabled ? "Activo" : "Inactivo"}</span></td><td><strong>${escapeHtml(String(module.users_with_access || 0))}</strong><small>${escapeHtml(module.deactivation_impact || module.description || "")}</small></td><td>${escapeHtml((module.primary_roles || []).join(", ") || "-")}</td><td>${action}</td></tr>`;
  }).join("");
  ["#moduleTable", "#tenantModuleTable"].forEach((selector) => {
    const target = document.querySelector(selector);
    if (target) target.innerHTML = table(["Modulo", "Categoria", "Estado", "Usuarios", "Roles", ""], moduleRows, "No hay modulos disponibles.");
  });
  renderModuleCatalog("#moduleCatalog", governance.modules, { admin: true });
  renderModuleCatalog("#tenantModuleCatalog", governance.modules);

  const settings = governance.settings;
  if (settings) {
    const subscription = (governance.subscriptions || []).find((item) => Number(item.tenant_id) === Number(settings.id || settings.tenant_id || activeTenant().id));
    const summary = `
      <article><span>Empresa</span><strong>${escapeHtml(settings.name)}</strong><p>${escapeHtml(settings.slug)}</p></article>
      <article><span>Documento</span><strong>${escapeHtml(settings.document_number || "-")}</strong><p>${escapeHtml(settings.document_type || "-")}</p></article>
      <article><span>Zona horaria</span><strong>${escapeHtml(settings.timezone)}</strong><p>Configuracion local de la operacion.</p></article>
      <article><span>Colores</span><strong>${escapeHtml(settings.primary_color)}</strong><p>${escapeHtml(settings.secondary_color)}</p></article>
    `;
    const workspacePanel = `
      <article>
        <p class="eyebrow">Administracion tenant</p>
        <h2>${escapeHtml(settings.name || "Mi empresa")}</h2>
        <p>Este panel resume la identidad operativa de la empresa autenticada. La configuracion impacta solo este workspace.</p>
      </article>
      <article>
        <span>Plan actual</span>
        <strong>${escapeHtml(subscription?.plan || activePlanLabel())}</strong>
        <p>${escapeHtml(subscription?.status || "Operacion permitida por compatibilidad")}</p>
      </article>
    `;
    document.querySelector("#tenantWorkspacePanel") && (document.querySelector("#tenantWorkspacePanel").innerHTML = workspacePanel);
    document.querySelector("#tenantPlanSummary") && (document.querySelector("#tenantPlanSummary").innerHTML = `
      <article><span>Usuarios</span><strong>${escapeHtml(String(governance.users.length))}</strong><p>Usuarios visibles para este alcance.</p></article>
      <article><span>Roles</span><strong>${escapeHtml(String(governance.roles.length))}</strong><p>Roles activos y de sistema.</p></article>
      <article><span>Modulos</span><strong>${escapeHtml(String(governance.modules.filter(moduleEnabled).length))}</strong><p>Capacidades contratadas o habilitadas.</p></article>
      <article><span>Auditoria</span><strong>${escapeHtml(String(governance.audit.length))}</strong><p>Eventos recientes disponibles.</p></article>
    `);
    document.querySelector("#tenantSettingsSummary") && (document.querySelector("#tenantSettingsSummary").innerHTML = summary);
    const form = document.querySelector("#brandingForm");
    if (form && !form.dataset.loaded) {
      form.elements.name.value = settings.name || "";
      form.elements.logo_url.value = settings.logo_url || "";
      form.elements.primary_color.value = settings.primary_color || "#15956f";
      form.elements.secondary_color.value = settings.secondary_color || "#2563eb";
      form.elements.timezone.value = settings.timezone || "America/Bogota";
      form.elements.login_headline.value = settings.login_headline || "";
      form.elements.login_subheadline.value = settings.login_subheadline || "";
      form.dataset.loaded = "true";
    }
  }

  const roleRows = governance.roles.map((role) => {
    const modules = permissionModuleSet(role.permission_codes || []);
    const criticalCount = (role.permission_codes || []).filter(permissionIsCritical).length;
    const exportCount = (role.permission_codes || []).filter((code) => code.endsWith(".export")).length;
    return `<tr><td><strong>${escapeHtml(role.name)}</strong><small>${escapeHtml(role.code)}</small></td><td>${role.is_system_role ? "Sistema" : "Empresa"}</td><td>${modules.map(escapeHtml).join(", ") || "-"}</td><td>${role.permission_codes.length}</td><td><span class="badge ${criticalCount ? "risk-alto" : "risk-bajo"}">${criticalCount} criticos</span></td><td>${exportCount}</td><td>${role.user_count}</td><td>${role.is_active ? "Activo" : "Inactivo"}</td></tr>`;
  }).join("");
  document.querySelector("#rolePermissionGuide") && (document.querySelector("#rolePermissionGuide").innerHTML = `
    <article><strong>Permisos por accion</strong><p>Los permisos definen que puede ver, crear, editar, exportar, asignar o configurar cada rol dentro de los modulos contratados.</p></article>
    <article><strong>Rol legacy</strong><p>Rol tecnico heredado para compatibilidad con modulos antiguos.</p></article>
    <article><strong>Rol especializado</strong><p>Perfil funcional que define permisos reales dentro de la empresa.</p></article>
    <article><strong>Permiso critico</strong><p>Permiso sensible que puede afectar datos, exportes, usuarios o configuracion.</p></article>
  `);
  document.querySelector("#roleTable") && (document.querySelector("#roleTable").innerHTML = table(["Rol", "Tipo", "Modulos", "Permisos", "Criticos", "Exportes", "Usuarios", "Estado"], roleRows, "No hay roles."));

  const roleOptions = optionList(governance.roles.filter((role) => role.is_active), "id", "name");
  const userRows = governance.users.map((user) => {
    const risk = user.risk_flags?.[0] || { severity: "low", label: "Sin alertas" };
    return `<tr><td><strong>${escapeHtml(user.name)}</strong><small>${escapeHtml(user.email)}</small></td><td><strong>${escapeHtml(user.legacy_role_label || user.role)}</strong><small>${escapeHtml(user.legacy_role || user.role)}</small></td><td><strong>${escapeHtml(user.business_profile || user.role_name || "-")}</strong><small>${escapeHtml(user.specialized_role_code || "fallback")}</small></td><td>${escapeHtml((user.visible_modules || []).join(", ") || "-")}</td><td>${escapeHtml(String(user.permission_count || 0))}</td><td><span class="badge ${severityClass(risk.severity)}">${escapeHtml(risk.label)}</span></td><td>${escapeHtml(user.leader_name || "-")}</td><td><select data-user-role="${user.id}">${roleOptions}</select><button class="table-button" data-user-access="${user.id}" type="button">Detalle</button></td></tr>`;
  }).join("");
  document.querySelector("#companyUserTable") && (document.querySelector("#companyUserTable").innerHTML = table(["Usuario", "Legacy", "Perfil efectivo", "Modulos", "Permisos", "Riesgo", "Lider", "Acceso"], userRows, "No hay usuarios visibles."));
  document.querySelectorAll("[data-user-role]").forEach((select) => {
    const user = governance.users.find((item) => String(item.id) === String(select.dataset.userRole));
    if (user?.role_id) select.value = String(user.role_id);
  });

  const auditRows = governance.audit.map((item) => `<tr><td>${dateOnly(item.created_at)}</td><td>${escapeHtml(item.module || "-")}</td><td>${escapeHtml(item.action)}</td><td>${escapeHtml(item.object_type || item.entity_type)}</td><td>${escapeHtml(item.object_id || item.entity_id || "-")}</td><td>${escapeHtml(item.user_id || "-")}</td></tr>`).join("");
  document.querySelector("#auditTable") && (document.querySelector("#auditTable").innerHTML = table(["Fecha", "Modulo", "Accion", "Objeto", "ID", "Usuario"], auditRows, "No hay eventos de auditoria."));
  document.querySelector("#governanceAuditMini") && (document.querySelector("#governanceAuditMini").innerHTML = table(["Fecha", "Modulo", "Accion", "Objeto"], governance.audit.slice(0, 6).map((item) => `<tr><td>${dateOnly(item.created_at)}</td><td>${escapeHtml(item.module || "-")}</td><td>${escapeHtml(item.action)}</td><td>${escapeHtml(item.object_type || item.entity_type)}</td></tr>`).join(""), "Sin actividad reciente."));

  const partyRows = governance.parties.map((party) => `<tr><td><strong>${escapeHtml(party.display_name)}</strong><small>${escapeHtml(party.legal_name || "")}</small></td><td>${escapeHtml([party.document_type, party.document_number].filter(Boolean).join(" ") || "-")}</td><td>${escapeHtml(party.phone || "-")}</td><td>${escapeHtml(party.email || "-")}</td><td>${[party.is_customer ? "Cliente" : "", party.is_debtor ? "Deudor" : "", party.is_prospect ? "Prospecto" : ""].filter(Boolean).join(", ") || "-"}</td></tr>`).join("");
  document.querySelector("#partyTable") && (document.querySelector("#partyTable").innerHTML = table(["Tercero", "Documento", "Telefono", "Email", "Roles"], partyRows, "No hay terceros maestros."));

  const health = governance.health;
  if (health && document.querySelector("#systemHealthPanel")) {
    document.querySelector("#systemHealthPanel").innerHTML = `
      <article><span>Aplicacion</span><strong>${escapeHtml(health.app)}</strong><p>${escapeHtml(health.environment)}</p></article>
      <article><span>Puerto</span><strong>${escapeHtml(health.port)}</strong><p>Servicio FastAPI local.</p></article>
      <article><span>Base de datos</span><strong>${health.database?.ok ? "Conectada" : "Revisar"}</strong><p>${escapeHtml(health.database?.detail || "")}</p></article>
    `;
  }

  const tasks = (state.crm.queue?.items || []).slice(0, 10).map((item) => `<tr><td><strong>${escapeHtml(item.name)}</strong><small>${escapeHtml(item.document)}</small></td><td>${money(item.balance)}</td><td>${escapeHtml(item.risk)}</td><td>${escapeHtml(item.next_action || "Gestionar")}</td><td><button class="table-button" data-open-customer="${item.id}" type="button">Abrir</button></td></tr>`).join("");
  document.querySelector("#taskTable") && (document.querySelector("#taskTable").innerHTML = table(["Cliente", "Saldo", "Riesgo", "Siguiente accion", ""], tasks, "No hay tareas asignadas."));
}

function renderConfigurationCenter() {
  const catalogs = state.configuration.catalogs || [];
  const rules = state.configuration.rules || [];
  const alertRules = state.configuration.alertRules || [];
  const workflows = state.configuration.workflows || [];
  renderCardSet("#configurationKpis", [
    { label: "Catalogos", value: catalogs.length, detail: "Valores funcionales por modulo y tenant.", tone: catalogs.length ? "green" : "yellow", action: "Estados, riesgos, documentos, etapas y fuentes." },
    { label: "Reglas", value: rules.length, detail: "Reglas de negocio parametrizables.", tone: rules.length ? "blue" : "yellow", action: "SLAs, umbrales y escalamiento." },
    { label: "Alertas", value: alertRules.length, detail: "Condiciones activas para motor transversal.", tone: alertRules.length ? "green" : "yellow", action: "Severidad, rol destino y mensaje." },
    { label: "Workflows", value: workflows.length, detail: "Flujos de etapas por modulo.", tone: workflows.length ? "blue" : "yellow", action: "Juridico y ventas ya usan esta base." },
  ]);
  const tenantField = isPlatform() ? `<label>Tenant ID<input name="tenant_id" type="number" placeholder="Opcional para alcance global" /></label>` : "";
  const catalogRows = catalogs.slice(0, 40).map((item) => `<tr><td><strong>${escapeHtml(item.label)}</strong><small>${escapeHtml(item.code)}</small></td><td>${escapeHtml(item.module)}</td><td>${escapeHtml(item.catalog_type)}</td><td><span class="workflow-dot" style="background:${escapeHtml(item.color || "#94a3b8")}"></span>${item.is_active ? "Activo" : "Inactivo"}</td><td>${item.tenant_id ? "Tenant" : "Global"}</td><td><button class="table-button" data-config-edit="catalog" data-id="${item.id}" type="button">Editar</button></td></tr>`).join("");
  document.querySelector("#configurationCatalogs") && (document.querySelector("#configurationCatalogs").innerHTML = `
    <form id="catalogConfigForm" class="ops-form form-grid">
      <input name="id" type="hidden" />
      ${tenantField}
      <label>Modulo<input name="module" value="collections" required /></label>
      <label>Tipo catalogo<input name="catalog_type" placeholder="customer_status" required /></label>
      <label>Codigo<input name="code" placeholder="CONTACTADO" required /></label>
      <label>Etiqueta<input name="label" placeholder="Contactado" required /></label>
      <label>Color<input name="color" type="color" value="#15956f" /></label>
      <label>Orden<input name="order" type="number" value="0" /></label>
      <label class="wide">Descripcion<textarea name="description"></textarea></label>
      <label class="checkbox-row"><input name="is_active" type="checkbox" checked /> Activo</label>
      <button type="submit">Guardar catalogo</button>
      <button class="secondary-button" data-reset-form="#catalogConfigForm" type="button">Limpiar</button>
    </form>
    ${table(["Catalogo", "Modulo", "Tipo", "Estado", "Alcance", ""], catalogRows, "Sin catalogos configurados. Crea el primer catalogo para estandarizar la operacion.")}
  `);
  const ruleRows = rules.slice(0, 30).map((item) => `<tr><td><strong>${escapeHtml(item.name)}</strong><small>${escapeHtml(item.code)}</small></td><td>${escapeHtml(item.module)}</td><td>${escapeHtml(item.rule_type)}</td><td><span class="badge ${severityClass(item.severity)}">${escapeHtml(item.severity)}</span></td><td>${item.is_active ? "Activa" : "Inactiva"}</td><td><button class="table-button" data-config-edit="rule" data-id="${item.id}" type="button">Editar</button></td></tr>`).join("");
  document.querySelector("#configurationRules") && (document.querySelector("#configurationRules").innerHTML = `
    <form id="businessRuleForm" class="ops-form form-grid">
      <input name="id" type="hidden" />
      ${tenantField}
      <label>Modulo<input name="module" value="collections" required /></label>
      <label>Tipo regla<input name="rule_type" placeholder="sla" required /></label>
      <label>Codigo<input name="code" placeholder="SLA_PROMESA" required /></label>
      <label>Nombre<input name="name" placeholder="SLA promesas vencidas" required /></label>
      <label>Severidad<select name="severity"><option value="low">Baja</option><option value="medium" selected>Media</option><option value="high">Alta</option><option value="critical">Critica</option></select></label>
      <label class="wide">Condicion JSON<textarea name="condition_json" placeholder='{"dpd_gt":30}'></textarea></label>
      <label class="wide">Accion JSON<textarea name="action_json" placeholder='{"create_alert":true}'></textarea></label>
      <label class="wide">Descripcion<textarea name="description"></textarea></label>
      <label class="checkbox-row"><input name="is_active" type="checkbox" checked /> Activa</label>
      <button type="submit">Guardar regla</button>
      <button class="secondary-button" data-reset-form="#businessRuleForm" type="button">Limpiar</button>
    </form>
    ${table(["Regla", "Modulo", "Tipo", "Severidad", "Estado", ""], ruleRows, "Sin reglas configuradas. Define reglas para controlar SLAs, riesgos o escalamiento.")}
  `);
  const alertRows = alertRules.slice(0, 30).map((item) => `<tr><td><strong>${escapeHtml(item.name)}</strong><small>${escapeHtml(item.code)}</small></td><td>${escapeHtml(item.module)}</td><td>${escapeHtml(item.condition_type)}</td><td>${item.threshold_days} dias</td><td><span class="badge ${severityClass(item.severity)}">${escapeHtml(item.severity)}</span></td><td>${escapeHtml(item.target_role || "-")}</td><td><button class="table-button" data-config-edit="alert" data-id="${item.id}" type="button">Editar</button></td></tr>`).join("");
  document.querySelector("#configurationAlertRules") && (document.querySelector("#configurationAlertRules").innerHTML = `
    <form id="alertRuleForm" class="ops-form form-grid">
      <input name="id" type="hidden" />
      ${tenantField}
      <label>Modulo<input name="module" value="collections" required /></label>
      <label>Codigo<input name="code" placeholder="PROMESA_VENCIDA" required /></label>
      <label>Nombre<input name="name" placeholder="Promesa vencida" required /></label>
      <label>Condicion<input name="condition_type" placeholder="overdue_promise" required /></label>
      <label>Dias umbral<input name="threshold_days" type="number" value="1" /></label>
      <label>Severidad<select name="severity"><option value="low">Baja</option><option value="medium">Media</option><option value="high" selected>Alta</option><option value="critical">Critica</option></select></label>
      <label>Rol destino<input name="target_role" placeholder="collections_leader" /></label>
      <label class="wide">Plantilla mensaje<textarea name="message_template"></textarea></label>
      <label class="wide">Descripcion<textarea name="description"></textarea></label>
      <label class="checkbox-row"><input name="is_active" type="checkbox" checked /> Activa</label>
      <button type="submit">Guardar alerta</button>
      <button class="secondary-button" data-reset-form="#alertRuleForm" type="button">Limpiar</button>
    </form>
    ${table(["Alerta", "Modulo", "Condicion", "Umbral", "Severidad", "Rol", ""], alertRows, "Sin alertas configurables. Crea alertas para anticipar riesgos.")}
  `);
  document.querySelector("#configurationWorkflows") && (document.querySelector("#configurationWorkflows").innerHTML = workflows.length
    ? `<form id="workflowForm" class="ops-form form-grid">
        <input name="id" type="hidden" />
        ${tenantField}
        <label>Modulo<input name="module" value="collections" required /></label>
        <label>Codigo<input name="code" placeholder="COBRANZA_ADMIN" required /></label>
        <label>Nombre<input name="name" placeholder="Cobranza administrativa" required /></label>
        <label class="wide">Descripcion<textarea name="description"></textarea></label>
        <label class="checkbox-row"><input name="is_active" type="checkbox" checked /> Activo</label>
        <button type="submit">Guardar workflow</button>
        <button class="secondary-button" data-reset-form="#workflowForm" type="button">Limpiar</button>
      </form>
      <form id="workflowStageForm" class="ops-form form-grid compact-form">
        <label>Workflow<select name="workflow_id">${workflows.map((item) => `<option value="${item.id}">${escapeHtml(item.name)}</option>`).join("")}</select></label>
        <label>Codigo etapa<input name="code" placeholder="CONTACTO" required /></label>
        <label>Nombre etapa<input name="name" placeholder="Contacto efectivo" required /></label>
        <label>Orden<input name="order" type="number" value="0" /></label>
        <label>Color<input name="color" type="color" value="#2563eb" /></label>
        <label class="checkbox-row"><input name="is_final" type="checkbox" /> Etapa final</label>
        <button type="submit">Agregar etapa</button>
      </form>
      ${workflows.map((item) => `<article class="configuration-card"><span>${escapeHtml(item.module)}</span><strong>${escapeHtml(item.name)}</strong><p>${escapeHtml(item.description || "Workflow funcional parametrizable.")}</p><small>${item.tenant_id ? "Tenant" : "Plantilla global"} - ${item.is_active ? "Activo" : "Inactivo"}</small><button class="table-button" data-config-edit="workflow" data-id="${item.id}" type="button">Editar</button></article>`).join("")}`
    : `<form id="workflowForm" class="ops-form form-grid">
        ${tenantField}
        <label>Modulo<input name="module" value="collections" required /></label>
        <label>Codigo<input name="code" placeholder="COBRANZA_ADMIN" required /></label>
        <label>Nombre<input name="name" placeholder="Cobranza administrativa" required /></label>
        <label class="wide">Descripcion<textarea name="description"></textarea></label>
        <button type="submit">Guardar workflow</button>
      </form><article class="empty-state"><strong>Sin workflows</strong><p>Crea un workflow para administrar etapas operativas por modulo.</p></article>`);
}

function renderAlertsCenter() {
  const alerts = state.alerts.items || [];
  const summary = state.alerts.summary || { total: alerts.length, critical: 0, high: 0, medium: 0, low: 0, by_module: {} };
  const topbarBadge = document.querySelector("#alertTopBadge");
  if (topbarBadge) {
    topbarBadge.textContent = `${summary.critical || 0} criticas`;
    topbarBadge.className = (summary.critical || 0) ? "status-pill status-pill-warn" : "status-pill status-pill-ok";
  }
  renderCardSet("#alertSummaryCards", [
    { label: "Alertas abiertas", value: summary.total || alerts.length, detail: "Motor transversal por tenant, modulo y asignacion.", tone: summary.total ? "yellow" : "green", action: "Priorizar por severidad y fecha limite." },
    { label: "Criticas", value: summary.critical || 0, detail: "Requieren intervencion inmediata.", tone: summary.critical ? "red" : "green", action: "Escalar a responsable del modulo." },
    { label: "Altas", value: summary.high || 0, detail: "Riesgos operativos de corto plazo.", tone: summary.high ? "yellow" : "green", action: "Plan diario de control." },
    { label: "Modulos", value: Object.keys(summary.by_module || {}).length, detail: "Cobertura transversal del motor.", tone: "blue", action: "Cobranzas, juridico, ventas y administracion." },
  ]);
  const rows = alerts.map((item) => `<tr><td><strong>${escapeHtml(item.title)}</strong><small>${escapeHtml(item.message)}</small></td><td>${escapeHtml(item.module)}</td><td><span class="badge ${severityClass(item.severity)}">${escapeHtml(item.severity)}</span></td><td>${dateOnly(item.due_at)}</td><td>${escapeHtml(item.entity_type)} #${escapeHtml(item.entity_id || "-")}</td><td>${escapeHtml(item.action || "-")}</td></tr>`).join("");
  document.querySelector("#alertCenterTable") && (document.querySelector("#alertCenterTable").innerHTML = table(["Alerta", "Modulo", "Severidad", "Fecha", "Entidad", "Accion sugerida"], rows, "Sin alertas abiertas para tu alcance."));
}

function renderKanban(selector, columns, cardRenderer) {
  const container = document.querySelector(selector);
  if (!container) return;
  container.innerHTML = (columns || []).length
    ? columns.map((column) => `
      <article class="kanban-column">
        <header><span class="workflow-dot" style="background:${escapeHtml(column.stage?.color || "#94a3b8")}"></span><strong>${escapeHtml(column.stage?.name || column.stage?.code || "Etapa")}</strong><small>${column.count || 0}</small></header>
        <div>${(column.items || []).slice(0, 8).map(cardRenderer).join("") || `<p class="empty">Sin registros.</p>`}</div>
        <footer>${money(column.amount || 0)}</footer>
      </article>
    `).join("")
    : `<article class="empty-state"><strong>Sin columnas</strong><p>Cuando existan workflows o datos, el kanban se activara aqui.</p></article>`;
}

function renderLegalAdvanced() {
  const dashboard = state.legal.dashboard;
  const kanban = state.legal.kanban;
  if (!dashboard && !kanban) return;
  const kpis = dashboard?.kpis || {};
  renderCardSet("#legalKpis", [
    { label: "Casos activos", value: kpis.active_cases || 0, detail: "Expedientes abiertos en el alcance autorizado.", tone: "blue", action: "Gestionar por etapa y riesgo." },
    { label: "Vencidos", value: kpis.overdue_deadlines || 0, detail: "Terminos juridicos fuera de fecha.", tone: kpis.overdue_deadlines ? "red" : "green", action: "Priorizar revision procesal." },
    { label: "Audiencias", value: kpis.upcoming_hearings || 0, detail: "Audiencias futuras registradas.", tone: kpis.upcoming_hearings ? "yellow" : "green", action: "Preparar agenda y documentos." },
    { label: "Riesgo alto", value: kpis.high_risk_cases || 0, detail: "Casos con criticidad juridica.", tone: kpis.high_risk_cases ? "red" : "green", action: "Validar estrategia y responsable." },
  ]);
  renderKanban("#legalKanbanBoard", kanban?.columns || [], (item) => `
    <article class="kanban-card">
      <strong>${escapeHtml(item.case_number || `Caso ${item.id}`)}</strong>
      <p>${money(item.amount || 0)} - Riesgo ${escapeHtml(item.risk || "-")}</p>
      <small>Vence: ${dateOnly(item.next_deadline_at)}</small>
    </article>
  `);
  const deadlineRows = (dashboard?.upcoming_deadlines || []).map((item) => `<tr><td><strong>${escapeHtml(item.title)}</strong><small>Caso #${item.case_id}</small></td><td>${dateOnly(item.due_at)}</td><td><span class="badge ${severityClass(item.priority)}">${escapeHtml(item.priority)}</span></td><td>${escapeHtml(item.status)}</td></tr>`).join("");
  document.querySelector("#legalDeadlineTable") && (document.querySelector("#legalDeadlineTable").innerHTML = table(["Vencimiento", "Fecha", "Prioridad", "Estado"], deadlineRows, "Sin vencimientos juridicos visibles."));
  const caseRows = (state.legal.cases || []).slice(0, 12).map((item) => `<tr><td><strong>${escapeHtml(item.case_number || `Caso ${item.id}`)}</strong><small>${escapeHtml(item.process_type)}</small></td><td>${escapeHtml(item.stage || item.status)}</td><td>${money(item.amount)}</td><td><span class="badge ${severityClass(item.risk)}">${escapeHtml(item.risk)}</span></td><td>${dateOnly(item.next_deadline_at)}</td></tr>`).join("");
  document.querySelector("#legalCaseTable") && (document.querySelector("#legalCaseTable").innerHTML = table(["Caso", "Etapa", "Monto", "Riesgo", "Proximo vencimiento"], caseRows, "Sin casos juridicos."));
}

function renderSalesAdvanced() {
  const dashboard = state.sales.dashboard;
  const pipeline = state.sales.pipeline;
  const kanban = state.sales.kanban;
  if (!dashboard && !pipeline && !kanban) return;
  const kpis = dashboard?.kpis || {};
  renderCardSet("#salesKpis", [
    { label: "Leads activos", value: kpis.active_leads || 0, detail: "Prospectos visibles para tu rol.", tone: "blue", action: "Convertir los mas maduros a oportunidad." },
    { label: "Oportunidades", value: kpis.open_opportunities || 0, detail: "Pipeline comercial abierto.", tone: "green", action: "Gestionar por etapa y probabilidad." },
    { label: "Valor pipeline", value: money(kpis.pipeline_value || 0), detail: "Valor bruto de oportunidades abiertas.", tone: "yellow", action: "Priorizar valor y fecha esperada." },
    { label: "Ponderado", value: money(kpis.weighted_pipeline || 0), detail: `Tasa estimada ${kpis.estimated_rate || 0}%.`, tone: "green", action: "Usar para forecast comercial." },
  ]);
  renderKanban("#salesKanbanBoard", kanban?.columns || [], (item) => `
    <article class="kanban-card">
      <strong>${escapeHtml(item.name)}</strong>
      <p>${money(item.amount || 0)} - ${item.probability || 0}%</p>
      <small>Cierre: ${dateOnly(item.expected_close_date)}</small>
    </article>
  `);
  const pipelineRows = (pipeline?.stages || []).map((item) => `<tr><td><strong>${escapeHtml(item.stage?.name || item.stage?.code)}</strong></td><td>${item.count}</td><td>${money(item.amount)}</td><td>${money(item.weighted_amount)}</td><td>${item.probability_avg}%</td></tr>`).join("");
  document.querySelector("#salesPipelineTable") && (document.querySelector("#salesPipelineTable").innerHTML = table(["Etapa", "Oportunidades", "Valor", "Ponderado", "Prob. prom."], pipelineRows, "Sin pipeline comercial."));
  const leadRows = (state.sales.leads || []).slice(0, 12).map((item) => `<tr><td><strong>${escapeHtml(item.name)}</strong><small>${escapeHtml(item.company || "-")}</small></td><td>${escapeHtml(item.source || "-")}</td><td>${escapeHtml(item.interest || "-")}</td><td>${escapeHtml(item.status)}</td><td>${escapeHtml(item.priority)}</td></tr>`).join("");
  document.querySelector("#salesLeadTable") && (document.querySelector("#salesLeadTable").innerHTML = table(["Lead", "Fuente", "Interes", "Estado", "Prioridad"], leadRows, "Sin leads visibles."));
}

function renderTypificationTrees() {
  const trees = state.ops.trees || [];
  const combinations = state.ops.combinations || [];
  const treeOptions = trees.map((item) => `<option value="${item.id}">${escapeHtml(item.name)}</option>`).join("");
  const projectOptions = (state.crm.options.projects || []).map((item) => `<option value="${item.id}">${escapeHtml(item.name)}</option>`).join("");
  renderCardSet("#typificationTreeKpis", [
    { label: "Arboles", value: trees.length, detail: "Configurables por tenant, modulo y cartera.", tone: trees.length ? "green" : "yellow", action: "Administra la logica de gestion sin tocar codigo." },
    { label: "Combinaciones", value: combinations.length, detail: "Rutas validas con campos y efectos.", tone: combinations.length ? "blue" : "yellow", action: "Exige promesa, fecha, comentario o escalamiento." },
    { label: "Cobranzas", value: trees.filter((item) => item.module === "collections").length, detail: "Producto principal Collection CRM.", tone: "green", action: "Estandarizar resultados por cartera." },
    { label: "Activos", value: trees.filter((item) => item.status === "active").length, detail: "Disponibles para operacion.", tone: "blue", action: "Inactivar arboles obsoletos." },
  ]);
  const treeRows = trees.map((item) => `<tr><td><strong>${escapeHtml(item.name)}</strong><small>${escapeHtml(item.code)}</small></td><td>${escapeHtml(item.module)}</td><td>${escapeHtml(item.project_id || "Global tenant")}</td><td>${escapeHtml(item.status)}</td><td>${dateOnly(item.updated_at)}</td></tr>`).join("");
  document.querySelector("#typificationTreeTable") && (document.querySelector("#typificationTreeTable").innerHTML = `
    <form id="typificationTreeForm" class="ops-form form-grid">
      <label>Modulo<input name="module" value="collections" required /></label>
      <label>Proyecto<select name="project_id"><option value="">Global tenant</option>${projectOptions}</select></label>
      <label>Codigo<input name="code" placeholder="COBRANZA_ANDINA" required /></label>
      <label>Nombre<input name="name" placeholder="Arbol cobranza administrativa" required /></label>
      <label>Estado<select name="status"><option value="active">Activo</option><option value="inactive">Inactivo</option></select></label>
      <label class="wide">Descripcion<textarea name="description"></textarea></label>
      <button type="submit">Crear arbol</button>
    </form>
    <form id="typificationNodeForm" class="ops-form form-grid compact-form">
      <label>Arbol<select name="tree_id">${treeOptions}</select></label>
      <label>Nivel<input name="level" type="number" min="1" value="1" /></label>
      <label>Codigo nodo<input name="code" placeholder="CONTACTO" required /></label>
      <label>Etiqueta<input name="label" placeholder="Contacto efectivo" required /></label>
      <label>Orden<input name="order" type="number" value="0" /></label>
      <label>Color<input name="color" type="color" value="#15956f" /></label>
      <label class="checkbox-row"><input name="requires_promise" type="checkbox" /> Requiere promesa</label>
      <label class="checkbox-row"><input name="requires_next_action" type="checkbox" /> Requiere siguiente accion</label>
      <button type="submit" ${trees.length ? "" : "disabled"}>Agregar nodo</button>
    </form>
    ${table(["Arbol", "Modulo", "Proyecto", "Estado", "Actualizado"], treeRows, "No hay arboles configurados. Crea un arbol para guiar la gestion.")}
  `);
  const comboRows = combinations.map((item) => `<tr><td><strong>Regla #${item.id}</strong><small>${escapeHtml((item.path || []).join(" > "))}</small></td><td>${Object.keys(item.required_fields || {}).filter((key) => item.required_fields[key]).join(", ") || "-"}</td><td>${Object.keys(item.effects || {}).join(", ") || "-"}</td><td>${item.is_active ? "Activa" : "Inactiva"}</td></tr>`).join("");
  document.querySelector("#typificationCombinationTable") && (document.querySelector("#typificationCombinationTable").innerHTML = `
    <form id="typificationCombinationForm" class="ops-form form-grid">
      <label>Arbol<select name="tree_id">${treeOptions}</select></label>
      <label>Ruta<input name="path" placeholder='Contacto, Promesa' required /></label>
      <label class="wide">Campos requeridos JSON<textarea name="required_fields" placeholder='{"promise_amount":true,"note":true}'></textarea></label>
      <label class="wide">Efectos JSON<textarea name="effects" placeholder='{"status":"Promesa"}'></textarea></label>
      <label class="checkbox-row"><input name="is_active" type="checkbox" checked /> Activa</label>
      <button type="submit" ${trees.length ? "" : "disabled"}>Crear combinacion</button>
    </form>
    ${table(["Combinacion", "Campos requeridos", "Efectos", "Estado"], comboRows, "Sin combinaciones configuradas. Crea rutas validas para orientar al gestor.")}
  `);
}

function renderRecordings() {
  const filters = state.ops.recordingFilters || {};
  const text = String(filters.text || "").toLowerCase();
  const recordings = (state.ops.recordings || []).filter((item) => {
    if (!text) return true;
    return [item.call_id, item.phone_number, item.provider_code, item.status, item.direction].some((value) => String(value || "").toLowerCase().includes(text));
  });
  const totalSeconds = recordings.reduce((sum, item) => sum + (item.duration_seconds || 0), 0);
  renderCardSet("#recordingKpis", [
    { label: "Grabaciones", value: recordings.length, detail: "Metadatos asociados a clientes y gestiones.", tone: recordings.length ? "green" : "yellow", action: "Consultar por cliente, gestor, fecha o telefono." },
    { label: "Minutos", value: Math.round(totalSeconds / 60), detail: "Duracion acumulada visible.", tone: "blue", action: "Control de auditoria y calidad." },
    { label: "Disponibles", value: recordings.filter((item) => item.playback_available).length, detail: "Con placeholder o storage seguro.", tone: "green", action: "Playback auditable por permiso." },
    { label: "Proveedor", value: new Set(recordings.map((item) => item.provider_code).filter(Boolean)).size, detail: "Troncales o fuentes metadata.", tone: "blue", action: "Integrar PBX/API en fase posterior." },
  ]);
  const rows = recordings.slice(0, 50).map((item) => `<tr><td><strong>${escapeHtml(item.call_id)}</strong><small>${escapeHtml(item.phone_number || "-")}</small></td><td>${escapeHtml(item.direction)}</td><td>${Math.round((item.duration_seconds || 0) / 60)} min</td><td>${escapeHtml(item.provider_code || "-")}</td><td>${escapeHtml(item.status)}</td><td><button class="table-button" data-recording-detail="${item.id}" type="button">Detalle</button><button class="table-button" data-recording-playback="${item.id}" type="button">Playback</button><button class="table-button" data-recording-download="${item.id}" type="button">Descargar</button></td></tr>`).join("");
  document.querySelector("#recordingTable") && (document.querySelector("#recordingTable").innerHTML = `
    <div class="inline-filters">
      <label>Buscar<input id="recordingSearch" value="${escapeHtml(filters.text || "")}" placeholder="cliente, telefono, proveedor, estado" /></label>
      <button class="secondary-button" data-refresh-recordings type="button">Actualizar</button>
    </div>
    ${state.ops.recordingDetail ? `<article class="preview-panel"><header><strong>${escapeHtml(state.ops.recordingDetail.call_id)}</strong><span>${escapeHtml(state.ops.recordingDetail.status)}</span></header><p>${escapeHtml(state.ops.recordingDetail.phone_number || "-")} - ${Math.round((state.ops.recordingDetail.duration_seconds || 0) / 60)} min - ${escapeHtml(state.ops.recordingDetail.provider_code || "-")}</p></article>` : ""}
    ${table(["Llamada", "Direccion", "Duracion", "Proveedor", "Estado", ""], rows, "Sin grabaciones registradas para los filtros actuales.")}
  `);
}

function renderUploads() {
  const batches = state.ops.uploads || [];
  const demographics = state.ops.demographics || [];
  renderCardSet("#uploadKpis", [
    { label: "Lotes", value: batches.length, detail: "Repartos, demograficos y archivos operativos.", tone: batches.length ? "green" : "yellow", action: "Previsualizar, validar y confirmar." },
    { label: "Registros", value: batches.reduce((sum, item) => sum + (item.total_rows || 0), 0), detail: "Filas procesadas en lotes visibles.", tone: "blue", action: "Auditoria por carga y usuario." },
    { label: "Errores", value: batches.reduce((sum, item) => sum + (item.error_rows || 0), 0), detail: "Filas que requieren correccion.", tone: "yellow", action: "Descargar errores con permiso." },
    { label: "Demograficos", value: demographics.length, detail: "Datos complementarios para contactabilidad.", tone: demographics.length ? "green" : "yellow", action: "Cruzar telefonos, emails y fuentes." },
  ]);
  const projectOptions = (state.crm.options.projects || []).map((item) => `<option value="${item.id}">${escapeHtml(item.name)}</option>`).join("");
  const preview = state.ops.uploadPreview;
  const previewPanel = preview ? `
    <article class="preview-panel">
      <header><strong>Preview de carga</strong><span>${preview.valid_rows}/${preview.total_rows} validas</span></header>
      <p>${preview.error_rows ? `${preview.error_rows} filas requieren revision antes de confirmar.` : "Archivo validado sin errores criticos."}</p>
      <div class="inline-controls">
        <button data-confirm-upload type="button">Confirmar carga</button>
        <button class="secondary-button" data-clear-upload-preview type="button">Descartar preview</button>
      </div>
      ${table(preview.columns || [], (preview.sample || []).map((row) => `<tr>${(preview.columns || []).map((column) => `<td>${escapeHtml(row[column] || "-")}</td>`).join("")}</tr>`).join(""), "Sin filas de muestra.")}
    </article>
  ` : `<article class="empty-state compact"><strong>Sin preview activo</strong><p>Selecciona un CSV y previsualiza antes de confirmar. El sistema no guarda archivos reales en el repositorio.</p></article>`;
  const batchRows = batches.map((item) => `<tr><td><strong>${escapeHtml(item.original_filename || `Lote ${item.id}`)}</strong><small>${escapeHtml(item.upload_type)}</small></td><td>${escapeHtml(item.status)}</td><td>${item.total_rows}</td><td>${item.valid_rows}</td><td>${item.error_rows}</td><td>${dateOnly(item.created_at)}</td><td><button class="table-button" data-upload-result="${item.id}" type="button">Resultado</button><button class="table-button" data-upload-errors="${item.id}" type="button">Errores</button></td></tr>`).join("");
  document.querySelector("#uploadBatchTable") && (document.querySelector("#uploadBatchTable").innerHTML = `
    <form id="uploadPreviewForm" class="ops-form form-grid">
      <label>Tipo de carga<select name="upload_type"><option value="reparto_cartera">Reparto / cartera</option><option value="demograficos">Demograficos</option><option value="pagos">Pagos</option><option value="documentos">Documentos</option><option value="grabaciones_metadata">Grabaciones metadata</option><option value="generico">Generico</option></select></label>
      <label>Proyecto<select name="project_id"><option value="">Sin proyecto</option>${projectOptions}</select></label>
      <label class="wide">Archivo CSV<input name="csv_file" type="file" accept=".csv,text/csv" required /></label>
      <label class="wide">Mapeo JSON opcional<textarea name="mapping" placeholder='{"document":"documento","name":"cliente","balance":"saldo"}'></textarea></label>
      <label class="checkbox-row"><input name="create_records" type="checkbox" /> Crear/actualizar registros si aplica</label>
      <button type="submit">Previsualizar</button>
    </form>
    ${previewPanel}
    ${table(["Lote", "Estado", "Total", "Validas", "Errores", "Fecha", ""], batchRows, "Sin lotes de carga. Previsualiza y confirma el primer reparto.")}
  `);
  const demographicRows = demographics.slice(0, 30).map((item) => `<tr><td><strong>Cliente #${item.customer_id}</strong><small>${escapeHtml(item.source)}</small></td><td>${escapeHtml(item.phone || "-")}</td><td>${escapeHtml(item.email || "-")}</td><td>${escapeHtml(item.city || "-")}</td><td>${escapeHtml(item.employer || "-")}</td><td>${item.score}</td></tr>`).join("");
  document.querySelector("#demographicTable") && (document.querySelector("#demographicTable").innerHTML = table(["Cliente", "Telefono", "Email", "Ciudad", "Empleador", "Score"], demographicRows, "Sin demograficos cargados."));
}

function renderExcelWeb() {
  const sources = state.ops.excelSources || [];
  const views = state.ops.excelViews || [];
  const result = state.ops.excelResult;
  const selectedSource = state.ops.excelDraft?.source || result?.source || sources[0]?.code || "customers";
  const source = sources.find((item) => item.code === selectedSource) || sources[0] || { code: selectedSource, columns: [] };
  const selectedColumns = state.ops.excelDraft?.columns?.length ? state.ops.excelDraft.columns : (result?.columns || source.columns || []).slice(0, 8);
  const activeFilters = state.ops.excelDraft?.filters || {};
  const projectOptions = optionList(state.crm.options.projects || [], "id", "label", activeFilters.project_id || "");
  const userOptions = optionList(state.crm.options.users || [], "id", "label", activeFilters.assigned_user_id || activeFilters.user_id || "");
  const sourceOptions = sources.length
    ? sources.map((item) => `<option value="${escapeHtml(item.code)}" ${item.code === selectedSource ? "selected" : ""}>${escapeHtml(item.label)}</option>`).join("")
    : `<option value="customers">Clientes</option>`;
  const columnChecks = (source.columns || []).map((column) => `
    <label class="checkbox-chip">
      <input name="columns" type="checkbox" value="${escapeHtml(column)}" ${selectedColumns.includes(column) ? "checked" : ""} />
      <span>${escapeHtml(column)}</span>
    </label>
  `).join("");
  renderCardSet("#excelWebKpis", [
    { label: "Fuentes", value: sources.length, detail: "Tablas operativas seguras sin SQL libre.", tone: sources.length ? "green" : "yellow", action: "Clientes, gestiones, pagos, juridico y ventas." },
    { label: "Vistas", value: views.length, detail: "Consultas guardadas por usuario o tenant.", tone: views.length ? "blue" : "yellow", action: "Estandarizar reportes funcionales." },
    { label: "Resultado", value: result?.total || 0, detail: `Fuente actual: ${result?.source || "clientes"}.`, tone: result?.total ? "green" : "yellow", action: "Exportar solo con permiso." },
    { label: "Columnas", value: result?.columns?.length || 0, detail: "Configurables por vista.", tone: "blue", action: "Ocultar campos no requeridos." },
  ]);
  const sourceRows = sources.map((item) => `<tr><td><strong>${escapeHtml(item.label)}</strong><small>${escapeHtml(item.code)}</small></td><td>${(item.columns || []).length}</td><td>${escapeHtml((item.columns || []).slice(0, 6).join(", "))}</td><td><button class="table-button" data-excel-source="${escapeHtml(item.code)}" type="button">Usar</button></td></tr>`).join("");
  document.querySelector("#excelSourceTable") && (document.querySelector("#excelSourceTable").innerHTML = table(["Fuente", "Columnas", "Ejemplo", ""], sourceRows, "Sin fuentes configuradas."));
  const viewRows = views.map((item) => `<tr><td><strong>${escapeHtml(item.name)}</strong><small>${escapeHtml(item.source)}</small></td><td>${item.is_public ? "Publica" : "Privada"}</td><td>${item.is_favorite ? "Favorita" : "-"}</td><td>${dateOnly(item.updated_at)}</td><td><button class="table-button" data-excel-view="${item.id}" type="button">Cargar</button></td></tr>`).join("");
  document.querySelector("#excelViewTable") && (document.querySelector("#excelViewTable").innerHTML = `
    <form id="excelViewForm" class="ops-form form-grid">
      <label>Nombre vista<input name="name" placeholder="Mi vista de cartera" required /></label>
      <label class="checkbox-row"><input name="is_public" type="checkbox" /> Publica para tenant</label>
      <label class="checkbox-row"><input name="is_favorite" type="checkbox" checked /> Favorita</label>
      <button type="submit">Guardar vista</button>
    </form>
    ${table(["Vista", "Alcance", "Favorita", "Actualizada", ""], viewRows, "Sin vistas guardadas. Ejecuta una consulta y guardala para reutilizarla.")}
  `);
  const resultRows = (result?.rows || []).map((row) => `<tr>${(result.columns || []).map((column) => `<td>${escapeHtml(row[column] ?? "-")}</td>`).join("")}</tr>`).join("");
  document.querySelector("#excelResultTable") && (document.querySelector("#excelResultTable").innerHTML = `
    <form id="excelQueryForm" class="ops-form form-grid">
      <label>Fuente<select name="source">${sourceOptions}</select></label>
      <label>Busqueda texto<input name="q" placeholder="cliente, documento, estado..." value="${escapeHtml(activeFilters.text || activeFilters.q || "")}" /></label>
      <label>Estado<input name="status" placeholder="Vigente, Promesa, Activo..." value="${escapeHtml(activeFilters.status || "")}" /></label>
      <label>Riesgo<select name="risk"><option value="">Todos</option><option value="Alto" ${activeFilters.risk === "Alto" ? "selected" : ""}>Alto</option><option value="Medio" ${activeFilters.risk === "Medio" ? "selected" : ""}>Medio</option><option value="Bajo" ${activeFilters.risk === "Bajo" ? "selected" : ""}>Bajo</option></select></label>
      <label>Proyecto<select name="project_id"><option value="">Todos</option>${projectOptions}</select></label>
      <label>Gestor<select name="assigned_user_id"><option value="">Todos</option>${userOptions}</select></label>
      <label>Mora minima<input name="dpd_min" type="number" min="0" value="${escapeHtml(activeFilters.dpd_min ?? "")}" /></label>
      <label>Mora maxima<input name="dpd_max" type="number" min="0" value="${escapeHtml(activeFilters.dpd_max ?? "")}" /></label>
      <label>Pagina<input name="page" type="number" min="1" value="${result?.page || 1}" /></label>
      <label>Filas por pagina<input name="page_size" type="number" min="1" max="100" value="${result?.page_size || 25}" /></label>
      <label class="wide">Columnas visibles<div class="checkbox-grid">${columnChecks || "<p class='empty'>Selecciona una fuente para ver columnas.</p>"}</div></label>
      <button type="submit">Ejecutar consulta</button>
      ${canExportExcelWeb() ? `<button class="secondary-button" data-excel-export type="button">Exportar</button>` : `<p class="form-note">Exportacion no disponible para gestores. La consulta queda limitada a tu operacion.</p>`}
    </form>
    <p class="form-note">${result ? `${result.total} registros - pagina ${result.page} de ${result.total_pages}` : "Configura la fuente y ejecuta una consulta segura."}</p>
    ${table(result?.columns || selectedColumns, resultRows, "Ejecuta una consulta para ver resultados.")}
  `);
}

function renderIntegrations() {
  const providers = state.ops.providers || [];
  const channels = state.ops.integrationChannels || [];
  const templates = state.ops.templates || [];
  const webhooks = state.ops.webhooks || [];
  const events = state.ops.events || [];
  renderCardSet("#integrationKpis", [
    { label: "Proveedores", value: providers.length, detail: "Telefonia, WhatsApp, email y APIs.", tone: providers.length ? "green" : "yellow", action: "Secretos siempre enmascarados." },
    { label: "Canales", value: channels.length, detail: "Lineas y cuentas configuradas.", tone: channels.length ? "blue" : "yellow", action: "Pruebas simuladas antes de produccion." },
    { label: "Plantillas", value: templates.length, detail: "Mensajes por canal.", tone: templates.length ? "green" : "yellow", action: "Estandarizar comunicacion." },
    { label: "Eventos", value: events.length, detail: "Logs de pruebas y webhooks.", tone: "blue", action: "Auditoria de integraciones." },
  ]);
  const tenantField = isPlatform() ? `<label>Tenant ID<input name="tenant_id" type="number" placeholder="Tenant destino" /></label>` : "";
  const providerOptions = providers.map((item) => `<option value="${item.id}">${escapeHtml(item.name)} (${escapeHtml(item.provider_type)})</option>`).join("");
  const providerRows = providers.map((item) => `<tr><td><strong>${escapeHtml(item.name)}</strong><small>${escapeHtml(item.code)}</small></td><td>${escapeHtml(item.provider_type)}</td><td>${escapeHtml(item.status)}</td><td>${escapeHtml(item.secret_mask || "Sin secreto visible")}</td><td><button class="table-button" data-integration-edit="provider" data-id="${item.id}" type="button">Editar</button></td></tr>`).join("");
  document.querySelector("#providerTable") && (document.querySelector("#providerTable").innerHTML = `
    <form id="providerForm" class="ops-form form-grid">
      <input name="id" type="hidden" />
      ${tenantField}
      <label>Tipo<select name="provider_type"><option value="telephony">Telefonia</option><option value="whatsapp">WhatsApp</option><option value="email">Email</option><option value="sms">SMS</option><option value="webhook">Webhook</option></select></label>
      <label>Codigo<input name="code" placeholder="twilio_main" required /></label>
      <label>Nombre<input name="name" placeholder="Proveedor principal" required /></label>
      <label>Base URL<input name="base_url" placeholder="https://api.proveedor.com" /></label>
      <label>Estado<select name="status"><option value="configured">Configurado</option><option value="active">Activo</option><option value="inactive">Inactivo</option></select></label>
      <label>Secreto<input name="secret" type="password" placeholder="Se guarda enmascarado" /></label>
      <label class="wide">Configuracion JSON<textarea name="config" placeholder='{"account":"demo"}'></textarea></label>
      <button type="submit">Guardar proveedor</button>
      <button class="secondary-button" data-reset-form="#providerForm" type="button">Limpiar</button>
    </form>
    ${table(["Proveedor", "Tipo", "Estado", "Secreto", ""], providerRows, "Sin proveedores configurados. Crea un proveedor para habilitar canales.")}
  `);
  const channelRows = channels.map((item) => `<tr><td><strong>${escapeHtml(item.name)}</strong><small>${escapeHtml(item.from_value || "-")}</small></td><td>${escapeHtml(item.channel_type)}</td><td>${escapeHtml(item.status)}</td><td>${escapeHtml(item.provider_id || "-")}</td><td><button class="table-button" data-test-channel="${item.id}" type="button">Probar</button><button class="table-button" data-integration-edit="channel" data-id="${item.id}" type="button">Editar</button></td></tr>`).join("");
  document.querySelector("#integrationChannelTable") && (document.querySelector("#integrationChannelTable").innerHTML = `
    <form id="channelConfigForm" class="ops-form form-grid">
      <input name="id" type="hidden" />
      ${tenantField}
      <label>Proveedor<select name="provider_id"><option value="">Sin proveedor</option>${providerOptions}</select></label>
      <label>Tipo canal<select name="channel_type"><option value="telephony">Telefonia</option><option value="whatsapp">WhatsApp</option><option value="email">Email</option><option value="sms">SMS</option><option value="webhook">Webhook</option></select></label>
      <label>Nombre<input name="name" placeholder="Linea principal cobranzas" required /></label>
      <label>Valor/remitente<input name="from_value" placeholder="+570000000000" /></label>
      <label>Estado<select name="status"><option value="active">Activo</option><option value="configured">Configurado</option><option value="inactive">Inactivo</option></select></label>
      <label class="wide">Configuracion JSON<textarea name="config" placeholder='{"click_to_call":true}'></textarea></label>
      <button type="submit">Guardar canal</button>
      <button class="secondary-button" data-reset-form="#channelConfigForm" type="button">Limpiar</button>
    </form>
    ${table(["Canal", "Tipo", "Estado", "Proveedor", ""], channelRows, "Sin canales configurados. Crea un canal y ejecuta una prueba simulada.")}
  `);
  const templateRows = templates.map((item) => `<tr><td><strong>${escapeHtml(item.name)}</strong><small>${escapeHtml(item.code)}</small></td><td>${escapeHtml(item.channel_type)}</td><td>${escapeHtml(item.subject || "-")}</td><td>${escapeHtml(item.status)}</td><td><button class="table-button" data-integration-edit="template" data-id="${item.id}" type="button">Editar</button></td></tr>`).join("");
  document.querySelector("#templateTable") && (document.querySelector("#templateTable").innerHTML = `
    <form id="templateForm" class="ops-form form-grid">
      <input name="id" type="hidden" />
      ${tenantField}
      <label>Canal<select name="channel_type"><option value="whatsapp">WhatsApp</option><option value="email">Email</option><option value="sms">SMS</option><option value="telephony">Telefonia</option></select></label>
      <label>Codigo<input name="code" placeholder="promesa_recordatorio" required /></label>
      <label>Nombre<input name="name" placeholder="Recordatorio promesa" required /></label>
      <label>Asunto<input name="subject" placeholder="Solo para email" /></label>
      <label>Estado<select name="status"><option value="active">Activa</option><option value="draft">Borrador</option><option value="inactive">Inactiva</option></select></label>
      <label class="wide">Cuerpo<textarea name="body" required></textarea></label>
      <button type="submit">Guardar plantilla</button>
      <button class="secondary-button" data-reset-form="#templateForm" type="button">Limpiar</button>
    </form>
    ${table(["Plantilla", "Canal", "Asunto", "Estado", ""], templateRows, "Sin plantillas. Crea mensajes reutilizables por canal.")}
  `);
  const webhookRows = webhooks.map((item) => `<tr><td><strong>${escapeHtml(item.name)}</strong><small>${escapeHtml(item.event_type)}</small></td><td>${escapeHtml(item.target_url)}</td><td>${escapeHtml(item.status)}</td><td>${escapeHtml(item.secret_mask || "-")}</td><td><button class="table-button" data-test-webhook="${item.id}" type="button">Probar</button><button class="table-button" data-integration-edit="webhook" data-id="${item.id}" type="button">Editar</button></td></tr>`).join("");
  document.querySelector("#webhookTable") && (document.querySelector("#webhookTable").innerHTML = `
    <form id="webhookForm" class="ops-form form-grid">
      <input name="id" type="hidden" />
      ${tenantField}
      <label>Nombre<input name="name" placeholder="Webhook pagos" required /></label>
      <label>Evento<input name="event_type" placeholder="payment.created" required /></label>
      <label>URL destino<input name="target_url" placeholder="https://cliente.com/webhook" required /></label>
      <label>Estado<select name="status"><option value="active">Activo</option><option value="configured">Configurado</option><option value="inactive">Inactivo</option></select></label>
      <label>Secreto<input name="secret" type="password" placeholder="Se guarda enmascarado" /></label>
      <button type="submit">Guardar webhook</button>
      <button class="secondary-button" data-reset-form="#webhookForm" type="button">Limpiar</button>
    </form>
    ${table(["Webhook", "URL", "Estado", "Secreto", ""], webhookRows, "Sin webhooks. Crea un endpoint y registra prueba simulada.")}
  `);
  const eventRows = events.slice(0, 30).map((item) => `<tr><td><strong>${escapeHtml(item.event_type)}</strong><small>${escapeHtml(item.channel_type)}</small></td><td>${escapeHtml(item.status)}</td><td>${escapeHtml(item.entity_type || "-")}</td><td>${dateOnly(item.created_at)}</td></tr>`).join("");
  document.querySelector("#integrationEventTable") && (document.querySelector("#integrationEventTable").innerHTML = table(["Evento", "Estado", "Entidad", "Fecha"], eventRows, "Sin eventos de canal."));
}

function renderAll() {
  fillSelects();
  renderRoleDashboard();
  renderDashboard();
  renderBI();
  renderQueue();
  renderCustomers();
  renderPromises();
  renderPayments();
  renderChannels();
  renderAdminTables();
  renderGovernanceTables();
  renderModuleInsights();
  renderConfigurationCenter();
  renderAlertsCenter();
  renderLegalAdvanced();
  renderSalesAdvanced();
  renderTypificationTrees();
  renderRecordings();
  renderUploads();
  renderExcelWeb();
  renderIntegrations();
}

function formPayload(form) {
  return Object.fromEntries(new FormData(form).entries());
}

function parseJsonField(value, fallback = {}) {
  const text = String(value || "").trim();
  if (!text) return fallback;
  try {
    return JSON.parse(text);
  } catch (error) {
    throw new Error("El campo JSON no tiene un formato valido.");
  }
}

function optionalNumber(value) {
  return value === undefined || value === null || value === "" ? null : Number(value);
}

function platformTenantValue(form) {
  return isPlatform() && form.elements.tenant_id?.value ? Number(form.elements.tenant_id.value) : null;
}

async function submitJson(form, endpoint, buildPayload) {
  const button = form.querySelector("button[type='submit']");
  await runAction(button, async () => {
    await api(endpoint, { method: "POST", body: JSON.stringify(buildPayload(form)) });
    showToast("success", "Registro guardado correctamente.");
    form.reset();
    await refreshAll();
  }, "Guardando...");
}

function setupNavigation() {
  document.querySelector("#mainNav").addEventListener("click", (event) => {
    const button = event.target.closest(".nav-item");
    if (!button || button.classList.contains("hidden")) return;
    const section = document.querySelector(`#${button.dataset.section}`);
    if (!section) return;
    document.querySelectorAll(".nav-item").forEach((item) => item.classList.remove("active"));
    document.querySelectorAll(".section").forEach((item) => item.classList.remove("active-section"));
    button.classList.add("active");
    section.classList.remove("menu-disabled");
    section.classList.add("active-section");
    document.querySelector("#sectionTitle").textContent = titles[button.dataset.section] || button.textContent || "Icodeup 360";
  });
}

function setupForms() {
  document.querySelector("#tenantForm").addEventListener("submit", async (event) => {
    event.preventDefault();
    await submitJson(event.currentTarget, "/api/admin/tenants", (form) => formPayload(form));
  });
  document.querySelector("#projectForm").addEventListener("submit", async (event) => {
    event.preventDefault();
    await submitJson(event.currentTarget, "/api/admin/projects", (form) => ({ ...formPayload(form), tenant_id: Number(form.elements.tenant_id.value) }));
  });
  document.querySelector("#userForm").addEventListener("submit", async (event) => {
    event.preventDefault();
    await submitJson(event.currentTarget, "/api/admin/users", (form) => ({
      ...formPayload(form),
      tenant_id: Number(form.elements.tenant_id.value),
      leader_id: form.elements.leader_id.value ? Number(form.elements.leader_id.value) : null,
      project_ids: Array.from(form.elements.project_ids.selectedOptions).map((option) => Number(option.value))
    }));
  });
  document.querySelector('#userForm select[name="tenant_id"]').addEventListener("change", refreshUserDependentSelects);
  document.querySelector("#userTenantFilter").addEventListener("change", renderAdminTables);
  document.querySelector('#typificationForm select[name="tenant_id"]').addEventListener("change", async () => {
    await loadTypifications();
    fillSelects();
    renderTypifications();
  });
  document.querySelector("#typificationForm").addEventListener("submit", async (event) => {
    event.preventDefault();
    const form = event.currentTarget;
    const id = form.elements.id.value;
    const payload = {
      tenant_id: Number(form.elements.tenant_id.value),
      project_id: form.elements.project_id.value ? Number(form.elements.project_id.value) : null,
      parent_id: form.elements.parent_id.value ? Number(form.elements.parent_id.value) : null,
      label: form.elements.label.value,
      code: form.elements.code.value,
      next_status: form.elements.next_status.value || null,
      requires_promise: form.elements.requires_promise.checked,
      requires_payment: form.elements.requires_payment.checked,
      channel: form.elements.channel.value || null,
      sort_order: Number(form.elements.sort_order.value || 0)
    };
    if (id) {
      delete payload.tenant_id;
      await api(`/api/typifications/${id}`, { method: "PATCH", body: JSON.stringify(payload) });
    } else {
      await api("/api/typifications", { method: "POST", body: JSON.stringify(payload) });
    }
    resetTypificationForm();
    await loadTypifications();
    renderAll();
  });
  document.querySelector("#resetTypification").addEventListener("click", resetTypificationForm);

  document.querySelector("#customerForm").addEventListener("submit", async (event) => {
    event.preventDefault();
    await submitJson(event.currentTarget, "/api/crm/customers", (form) => ({
      ...formPayload(form),
      project_id: Number(form.elements.project_id.value),
      assigned_user_id: form.elements.assigned_user_id.value ? Number(form.elements.assigned_user_id.value) : null,
      balance: Number(form.elements.balance.value || 0),
      dpd: Number(form.elements.dpd.value || 0)
    }));
  });
  document.querySelector("#importForm").addEventListener("submit", async (event) => {
    event.preventDefault();
    const form = event.currentTarget;
    const file = form.elements.csv_file.files[0];
    const csvText = await file.text();
    const result = await api("/api/crm/customers/import", {
      method: "POST",
      body: JSON.stringify({
        project_id: Number(form.elements.project_id.value),
        assigned_user_id: form.elements.assigned_user_id.value ? Number(form.elements.assigned_user_id.value) : null,
        file_name: file.name,
        csv_text: csvText
      })
    });
    document.querySelector("#importResult").textContent = `Importados ${result.imported_count}, actualizados ${result.updated_count}, omitidos ${result.skipped_count}.`;
    form.reset();
    await refreshAll();
  });
  document.querySelector("#paymentForm").addEventListener("submit", async (event) => {
    event.preventDefault();
    await submitJson(event.currentTarget, "/api/crm/payments", (form) => ({
      customer_id: Number(form.elements.customer_id.value),
      amount: Number(form.elements.amount.value),
      paid_at: toDateTime(form.elements.paid_at.value),
      method: form.elements.method.value || "No especificado",
      reference: form.elements.reference.value
    }));
  });
  document.querySelector("#channelForm").addEventListener("submit", async (event) => {
    event.preventDefault();
    await submitJson(event.currentTarget, "/api/crm/channels", (form) => ({
      tenant_id: form.elements.tenant_id.value ? Number(form.elements.tenant_id.value) : null,
      project_id: form.elements.project_id.value ? Number(form.elements.project_id.value) : null,
      kind: form.elements.kind.value,
      label: form.elements.label.value,
      value: form.elements.value.value,
      provider: form.elements.provider.value,
      is_default: form.elements.is_default.checked
    }));
  });
  document.querySelector("#roleForm").addEventListener("submit", async (event) => {
    event.preventDefault();
    await submitJson(event.currentTarget, "/api/governance/roles", (form) => ({
      name: form.elements.name.value,
      code: form.elements.code.value || null,
      description: form.elements.description.value || null,
      permission_codes: Array.from(form.elements.permission_codes.selectedOptions).map((option) => option.value)
    }));
  });
  document.querySelector("#brandingForm").addEventListener("submit", async (event) => {
    event.preventDefault();
    const form = event.currentTarget;
    await api("/api/governance/settings", {
      method: "PATCH",
      body: JSON.stringify({
        name: form.elements.name.value,
        logo_url: form.elements.logo_url.value || null,
        primary_color: form.elements.primary_color.value || null,
        secondary_color: form.elements.secondary_color.value || null,
        timezone: form.elements.timezone.value || "America/Bogota",
        login_headline: form.elements.login_headline.value || null,
        login_subheadline: form.elements.login_subheadline.value || null
      })
    });
    form.dataset.loaded = "";
    await refreshAll();
  });
  document.querySelector("#partyForm").addEventListener("submit", async (event) => {
    event.preventDefault();
    await submitJson(event.currentTarget, "/api/governance/parties", (form) => ({
      party_type: form.elements.party_type.value,
      display_name: form.elements.display_name.value,
      document_type: form.elements.document_type.value || null,
      document_number: form.elements.document_number.value || null,
      email: form.elements.email.value || null,
      phone: form.elements.phone.value || null,
      city: form.elements.city.value || null,
      is_customer: form.elements.is_customer.checked,
      is_debtor: form.elements.is_debtor.checked,
      is_prospect: form.elements.is_prospect.checked,
      notes: form.elements.notes.value || null
    }));
  });
}

function setupEvents() {
  document.addEventListener("submit", async (event) => {
    const form = event.target;
    if (["catalogConfigForm", "businessRuleForm", "alertRuleForm", "workflowForm", "workflowStageForm"].includes(form.id)) {
      event.preventDefault();
      await handleConfigurationSubmit(form);
    }
    if (["providerForm", "channelConfigForm", "templateForm", "webhookForm"].includes(form.id)) {
      event.preventDefault();
      await handleIntegrationSubmit(form);
    }
    if (form.id === "uploadPreviewForm") {
      event.preventDefault();
      await handleUploadPreview(form);
    }
    if (form.id === "excelQueryForm") {
      event.preventDefault();
      await handleExcelQuery(form);
    }
    if (form.id === "excelViewForm") {
      event.preventDefault();
      await saveExcelView(form);
    }
    if (["typificationTreeForm", "typificationNodeForm", "typificationCombinationForm"].includes(form.id)) {
      event.preventDefault();
      await handleTypificationOpsSubmit(form);
    }
  });
  document.addEventListener("click", async (event) => {
    const open = event.target.closest("[data-open-customer]");
    if (open) {
      await openCustomerDrawer(open.dataset.openCustomer);
      return;
    }
    if (event.target.closest("[data-close-drawer]")) {
      closeManagementDrawer();
      return;
    }
    const prefill = event.target.closest("[data-prefill-result]");
    if (prefill) {
      const form = document.querySelector("#drawerActivityForm") || document.querySelector("#activityForm");
      if (form?.elements.result) {
        form.elements.result.value = prefill.dataset.prefillResult;
        form.elements.note?.focus();
      }
    }
    const resetForm = event.target.closest("[data-reset-form]");
    if (resetForm) {
      const form = document.querySelector(resetForm.dataset.resetForm);
      form?.reset();
      if (form?.elements.id) form.elements.id.value = "";
      return;
    }
    const configEdit = event.target.closest("[data-config-edit]");
    if (configEdit) {
      fillConfigurationForm(configEdit.dataset.configEdit, configEdit.dataset.id);
      return;
    }
    const integrationEdit = event.target.closest("[data-integration-edit]");
    if (integrationEdit) {
      fillIntegrationForm(integrationEdit.dataset.integrationEdit, integrationEdit.dataset.id);
      return;
    }
    const testChannel = event.target.closest("[data-test-channel]");
    if (testChannel) {
      await runAction(testChannel, async () => {
        const result = await api(`/api/integrations/channels/${testChannel.dataset.testChannel}/test`, { method: "POST" });
        showToast("success", result.message || "Prueba de canal registrada.");
        await loadPhase8BData();
        renderIntegrations();
      }, "Probando...");
      return;
    }
    const testWebhook = event.target.closest("[data-test-webhook]");
    if (testWebhook) {
      await runAction(testWebhook, async () => {
        const result = await api(`/api/integrations/webhooks/${testWebhook.dataset.testWebhook}/test`, { method: "POST" });
        showToast("success", result.message || "Prueba de webhook registrada.");
        await loadPhase8BData();
        renderIntegrations();
      }, "Probando...");
      return;
    }
    const confirmUploadButton = event.target.closest("[data-confirm-upload]");
    if (confirmUploadButton) {
      await confirmUpload(confirmUploadButton);
      return;
    }
    if (event.target.closest("[data-clear-upload-preview]")) {
      state.ops.uploadPreview = null;
      state.ops.uploadDraft = null;
      renderUploads();
      return;
    }
    const uploadResult = event.target.closest("[data-upload-result]");
    if (uploadResult) {
      await runAction(uploadResult, async () => {
        const result = await api(`/api/uploads/batches/${uploadResult.dataset.uploadResult}/result`);
        showToast("info", result.result_file_path || "Resultado disponible en metadata del lote.");
      }, "Consultando...");
      return;
    }
    const uploadErrors = event.target.closest("[data-upload-errors]");
    if (uploadErrors) {
      await runAction(uploadErrors, async () => {
        const result = await api(`/api/uploads/batches/${uploadErrors.dataset.uploadErrors}/errors`);
        showToast(result.error_file_path ? "warning" : "info", result.error_file_path || "El lote no tiene archivo de errores.");
      }, "Consultando...");
      return;
    }
    const excelSource = event.target.closest("[data-excel-source]");
    if (excelSource) {
      const source = state.ops.excelSources.find((item) => item.code === excelSource.dataset.excelSource);
      state.ops.excelDraft = { source: excelSource.dataset.excelSource, filters: {}, columns: (source?.columns || []).slice(0, 8), page: 1, page_size: 25 };
      state.ops.excelResult = await api("/api/excel-web/query", { method: "POST", body: JSON.stringify(state.ops.excelDraft) });
      renderExcelWeb();
      return;
    }
    const excelView = event.target.closest("[data-excel-view]");
    if (excelView) {
      const view = state.ops.excelViews.find((item) => String(item.id) === String(excelView.dataset.excelView));
      if (view) {
        state.ops.excelDraft = { source: view.source, filters: view.filters || {}, columns: view.columns || [], page: 1, page_size: 25 };
        state.ops.excelResult = await api("/api/excel-web/query", { method: "POST", body: JSON.stringify(state.ops.excelDraft) });
        showToast("success", "Vista cargada correctamente.");
        renderExcelWeb();
      }
      return;
    }
    const excelExport = event.target.closest("[data-excel-export]");
    if (excelExport) {
      await runAction(excelExport, async () => {
        const form = document.querySelector("#excelQueryForm");
        const payload = state.ops.excelDraft || (form ? excelPayloadFromForm(form) : null);
        if (!payload) throw new Error("Ejecuta una consulta antes de exportar.");
        const result = await api("/api/excel-web/export", { method: "POST", body: JSON.stringify(payload) });
        showToast("success", result.message || "Exportacion solicitada correctamente.");
      }, "Exportando...");
      return;
    }
    const refreshRecordings = event.target.closest("[data-refresh-recordings]");
    if (refreshRecordings) {
      await runAction(refreshRecordings, async () => {
        await loadPhase8BData();
        renderRecordings();
        showToast("success", "Grabaciones actualizadas.");
      }, "Actualizando...");
      return;
    }
    const recordingDetail = event.target.closest("[data-recording-detail]");
    if (recordingDetail) {
      await runAction(recordingDetail, async () => {
        state.ops.recordingDetail = await api(`/api/recordings/${recordingDetail.dataset.recordingDetail}`);
        renderRecordings();
      }, "Consultando...");
      return;
    }
    const recordingPlayback = event.target.closest("[data-recording-playback]");
    if (recordingPlayback) {
      await runAction(recordingPlayback, async () => {
        const result = await api(`/api/recordings/${recordingPlayback.dataset.recordingPlayback}/playback`);
        showToast("info", result.message || result.playback_url || "Playback auditado.");
      }, "Solicitando...");
      return;
    }
    const recordingDownload = event.target.closest("[data-recording-download]");
    if (recordingDownload) {
      await runAction(recordingDownload, async () => {
        const result = await api(`/api/recordings/${recordingDownload.dataset.recordingDownload}/download`);
        showToast("info", result.message || result.download_url || "Descarga auditada.");
      }, "Validando permiso...");
      return;
    }
    const sectionJump = event.target.closest("[data-section-jump]");
    if (sectionJump) {
      document.querySelector(`[data-section="${sectionJump.dataset.sectionJump}"]`)?.click();
    }
    const userAccess = event.target.closest("[data-user-access]");
    if (userAccess) {
      state.governance.effectiveAccess = await api(`/api/governance/users/${userAccess.dataset.userAccess}/effective-access`);
      renderGovernanceTables();
    }
    const complete = event.target.closest("[data-complete-promise]");
    if (complete) {
      await runAction(complete, async () => {
        await api(`/api/crm/promises/${complete.dataset.completePromise}/complete`, { method: "PATCH" });
        showToast("success", "Promesa marcada como cumplida.");
        await refreshAll();
      }, "Actualizando...");
    }
    const editTypification = event.target.closest("[data-edit-typification]");
    if (editTypification) fillTypificationForm(editTypification.dataset.editTypification);
    const deleteTypification = event.target.closest("[data-delete-typification]");
    if (deleteTypification && confirm("Seguro que deseas eliminar esta tipificacion?")) {
      await api(`/api/typifications/${deleteTypification.dataset.deleteTypification}`, { method: "DELETE" });
      await loadTypifications();
      renderAll();
    }
    const toggleModule = event.target.closest("[data-toggle-module]");
    if (toggleModule) {
      const tenantId = document.querySelector("#moduleTenantFilter")?.value;
      if (!tenantId) return showToast("warning", "Selecciona una empresa para modificar modulos.");
      const enabled = toggleModule.dataset.enabled === "true";
      await runAction(toggleModule, async () => {
        await api(`/api/governance/modules/${tenantId}`, {
          method: "PUT",
          body: JSON.stringify([{ module_code: toggleModule.dataset.toggleModule, enabled: !enabled }])
        });
        showToast("success", "Modulo actualizado.");
        await loadGovernanceData();
        renderAll();
      }, "Actualizando...");
    }
  });
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") closeManagementDrawer();
  });
  document.addEventListener("change", async (event) => {
    if (event.target.closest("#roleModuleFilter") || event.target.closest("#roleRiskFilter")) {
      renderRoleMatrix();
      return;
    }
    const roleSelect = event.target.closest("[data-user-role]");
    if (roleSelect && roleSelect.value) {
      await api(`/api/governance/users/${roleSelect.dataset.userRole}/role`, {
        method: "PUT",
        body: JSON.stringify({ role_id: Number(roleSelect.value) })
      });
      await loadGovernanceData();
      renderAll();
    }
  });
  document.querySelector("#queueSearch").addEventListener("input", async () => {
    state.queuePage = 1;
    await loadQueue();
    renderQueue();
  });
  document.querySelector("#queueStatus").addEventListener("change", async () => {
    state.queuePage = 1;
    await loadQueue();
    renderQueue();
  });
  document.querySelector("#queueRisk").addEventListener("change", async () => {
    state.queuePage = 1;
    await loadQueue();
    renderQueue();
  });
  document.querySelector("#customerSearch").addEventListener("input", async () => {
    state.customerPage = 1;
    await loadCustomers();
    renderCustomers();
  });
  document.querySelector("#moduleTenantFilter").addEventListener("change", async () => {
    await loadGovernanceData();
    renderAll();
  });
  document.querySelector("#refreshAudit").addEventListener("click", async () => {
    await loadGovernanceData();
    renderAll();
  });
  document.querySelector("#partySearch").addEventListener("input", async (event) => {
    const q = event.target.value.trim();
    state.governance.parties = await apiMaybe(`/api/governance/parties?${queryParams({ q })}`, []);
    renderGovernanceTables();
  });
  document.querySelector("#exportCustomers").addEventListener("click", async () => {
    try {
      await downloadCsv("/api/crm/customers/export", "clientes_icodeup360.csv");
      showToast("success", "Exportacion de clientes iniciada.");
    } catch (error) {
      showToast("error", error.message);
    }
  });
  document.addEventListener("input", (event) => {
    if (event.target.closest("#recordingSearch")) {
      state.ops.recordingFilters = { text: event.target.value };
      renderRecordings();
    }
  });
  document.querySelector("#exportPayments").addEventListener("click", async () => {
    try {
      await downloadCsv("/api/crm/payments/export", "pagos_icodeup360.csv");
      showToast("success", "Exportacion de pagos iniciada.");
    } catch (error) {
      showToast("error", error.message);
    }
  });
  document.querySelector("#queuePrev").addEventListener("click", async () => {
    state.queuePage = Math.max(1, state.queuePage - 1);
    await loadQueue();
    renderQueue();
  });
  document.querySelector("#queueNext").addEventListener("click", async () => {
    state.queuePage += 1;
    await loadQueue();
    renderQueue();
  });
  document.querySelector("#customerPrev").addEventListener("click", async () => {
    state.customerPage = Math.max(1, state.customerPage - 1);
    await loadCustomers();
    renderCustomers();
  });
  document.querySelector("#customerNext").addEventListener("click", async () => {
    state.customerPage += 1;
    await loadCustomers();
    renderCustomers();
  });
  ["#biTenant", "#biProject", "#biHorizon"].forEach((selector) => {
    document.querySelector(selector).addEventListener("change", async () => {
      await loadBi();
      renderBI();
      renderDashboard();
      renderModuleInsights();
    });
  });
  document.querySelector("#refreshBi").addEventListener("click", async () => {
    await loadBi();
    renderBI();
    renderDashboard();
    renderModuleInsights();
  });
}

function resetTypificationForm() {
  const form = document.querySelector("#typificationForm");
  const tenantId = form.elements.tenant_id.value;
  form.reset();
  form.elements.id.value = "";
  if (tenantId) form.elements.tenant_id.value = tenantId;
  fillSelects();
}

function fillTypificationForm(nodeId) {
  const node = state.admin.typifications.find((item) => String(item.id) === String(nodeId));
  if (!node) return;
  const form = document.querySelector("#typificationForm");
  form.elements.id.value = node.id;
  form.elements.tenant_id.value = node.tenant_id;
  form.elements.project_id.value = node.project_id || "";
  form.elements.label.value = node.label;
  form.elements.code.value = node.code;
  form.elements.next_status.value = node.next_status || "";
  form.elements.requires_promise.checked = Boolean(node.requires_promise);
  form.elements.requires_payment.checked = Boolean(node.requires_payment);
  form.elements.channel.value = node.channel || "";
  form.elements.sort_order.value = node.sort_order || 0;
  fillSelects();
  form.elements.parent_id.value = node.parent_id || "";
}

function setFormValues(form, values = {}) {
  Object.entries(values).forEach(([key, value]) => {
    const field = form.elements[key];
    if (!field) return;
    if (field.type === "checkbox") {
      field.checked = Boolean(value);
    } else {
      field.value = value ?? "";
    }
  });
}

function fillConfigurationForm(type, id) {
  const maps = {
    catalog: { form: "#catalogConfigForm", items: state.configuration.catalogs },
    rule: { form: "#businessRuleForm", items: state.configuration.rules },
    alert: { form: "#alertRuleForm", items: state.configuration.alertRules },
    workflow: { form: "#workflowForm", items: state.configuration.workflows }
  };
  const meta = maps[type];
  const form = meta ? document.querySelector(meta.form) : null;
  const item = meta?.items?.find((row) => String(row.id) === String(id));
  if (!form || !item) return;
  setFormValues(form, item);
  form.scrollIntoView({ behavior: "smooth", block: "center" });
}

async function handleConfigurationSubmit(form) {
  const id = form.elements.id?.value;
  const button = form.querySelector("button[type='submit']");
  await runAction(button, async () => {
    if (form.id === "catalogConfigForm") {
      const createPayload = {
        tenant_id: platformTenantValue(form),
        module: form.elements.module.value,
        catalog_type: form.elements.catalog_type.value,
        code: form.elements.code.value,
        label: form.elements.label.value,
        description: form.elements.description.value || null,
        color: form.elements.color.value || null,
        order: Number(form.elements.order.value || 0),
        is_active: form.elements.is_active.checked,
      };
      const patchPayload = {
        label: createPayload.label,
        description: createPayload.description,
        color: createPayload.color,
        order: createPayload.order,
        is_active: createPayload.is_active,
      };
      await api(id ? `/api/configuration/catalogs/${id}` : "/api/configuration/catalogs", { method: id ? "PATCH" : "POST", body: JSON.stringify(id ? patchPayload : createPayload) });
    }
    if (form.id === "businessRuleForm") {
      const createPayload = {
        tenant_id: platformTenantValue(form),
        module: form.elements.module.value,
        rule_type: form.elements.rule_type.value,
        code: form.elements.code.value,
        name: form.elements.name.value,
        description: form.elements.description.value || null,
        condition_json: form.elements.condition_json.value || null,
        action_json: form.elements.action_json.value || null,
        severity: form.elements.severity.value,
        is_active: form.elements.is_active.checked,
      };
      const patchPayload = {
        name: createPayload.name,
        description: createPayload.description,
        condition_json: createPayload.condition_json,
        action_json: createPayload.action_json,
        severity: createPayload.severity,
        is_active: createPayload.is_active,
      };
      await api(id ? `/api/configuration/rules/${id}` : "/api/configuration/rules", { method: id ? "PATCH" : "POST", body: JSON.stringify(id ? patchPayload : createPayload) });
    }
    if (form.id === "alertRuleForm") {
      const createPayload = {
        tenant_id: platformTenantValue(form),
        module: form.elements.module.value,
        code: form.elements.code.value,
        name: form.elements.name.value,
        description: form.elements.description.value || null,
        condition_type: form.elements.condition_type.value,
        threshold_days: Number(form.elements.threshold_days.value || 0),
        severity: form.elements.severity.value,
        target_role: form.elements.target_role.value || null,
        message_template: form.elements.message_template.value || null,
        is_active: form.elements.is_active.checked,
      };
      const patchPayload = {
        name: createPayload.name,
        description: createPayload.description,
        condition_type: createPayload.condition_type,
        threshold_days: createPayload.threshold_days,
        severity: createPayload.severity,
        target_role: createPayload.target_role,
        message_template: createPayload.message_template,
        is_active: createPayload.is_active,
      };
      await api(id ? `/api/configuration/alert-rules/${id}` : "/api/configuration/alert-rules", { method: id ? "PATCH" : "POST", body: JSON.stringify(id ? patchPayload : createPayload) });
    }
    if (form.id === "workflowForm") {
      const createPayload = {
        tenant_id: platformTenantValue(form),
        module: form.elements.module.value,
        code: form.elements.code.value,
        name: form.elements.name.value,
        description: form.elements.description.value || null,
        is_active: form.elements.is_active?.checked ?? true,
      };
      const patchPayload = { name: createPayload.name, description: createPayload.description, is_active: createPayload.is_active };
      await api(id ? `/api/configuration/workflows/${id}` : "/api/configuration/workflows", { method: id ? "PATCH" : "POST", body: JSON.stringify(id ? patchPayload : createPayload) });
    }
    if (form.id === "workflowStageForm") {
      await api(`/api/configuration/workflows/${form.elements.workflow_id.value}/stages`, {
        method: "POST",
        body: JSON.stringify({
          code: form.elements.code.value,
          name: form.elements.name.value,
          order: Number(form.elements.order.value || 0),
          color: form.elements.color.value || null,
          is_final: form.elements.is_final.checked,
          is_active: true,
        })
      });
    }
    showToast("success", "Configuracion guardada correctamente.");
    form.reset();
    await loadPhase8Data();
    renderConfigurationCenter();
  }, "Guardando...");
}

function fillIntegrationForm(type, id) {
  const maps = {
    provider: { form: "#providerForm", items: state.ops.providers },
    channel: { form: "#channelConfigForm", items: state.ops.integrationChannels },
    template: { form: "#templateForm", items: state.ops.templates },
    webhook: { form: "#webhookForm", items: state.ops.webhooks }
  };
  const meta = maps[type];
  const form = meta ? document.querySelector(meta.form) : null;
  const item = meta?.items?.find((row) => String(row.id) === String(id));
  if (!form || !item) return;
  setFormValues(form, { ...item, config: item.config ? JSON.stringify(item.config, null, 2) : "" });
  form.scrollIntoView({ behavior: "smooth", block: "center" });
}

async function handleIntegrationSubmit(form) {
  const id = form.elements.id?.value;
  const button = form.querySelector("button[type='submit']");
  await runAction(button, async () => {
    if (form.id === "providerForm") {
      await api(id ? `/api/integrations/providers/${id}` : "/api/integrations/providers", {
        method: id ? "PATCH" : "POST",
        body: JSON.stringify({
          tenant_id: platformTenantValue(form),
          provider_type: form.elements.provider_type.value,
          code: form.elements.code.value,
          name: form.elements.name.value,
          base_url: form.elements.base_url.value || null,
          status: form.elements.status.value,
          secret: form.elements.secret.value || null,
          config: parseJsonField(form.elements.config.value, {}),
        })
      });
    }
    if (form.id === "channelConfigForm") {
      await api(id ? `/api/integrations/channels/${id}` : "/api/integrations/channels", {
        method: id ? "PATCH" : "POST",
        body: JSON.stringify({
          tenant_id: platformTenantValue(form),
          provider_id: optionalNumber(form.elements.provider_id.value),
          channel_type: form.elements.channel_type.value,
          name: form.elements.name.value,
          status: form.elements.status.value,
          from_value: form.elements.from_value.value || null,
          config: parseJsonField(form.elements.config.value, {}),
        })
      });
    }
    if (form.id === "templateForm") {
      await api(id ? `/api/integrations/templates/${id}` : "/api/integrations/templates", {
        method: id ? "PATCH" : "POST",
        body: JSON.stringify({
          tenant_id: platformTenantValue(form),
          channel_type: form.elements.channel_type.value,
          code: form.elements.code.value,
          name: form.elements.name.value,
          subject: form.elements.subject.value || null,
          body: form.elements.body.value,
          status: form.elements.status.value,
        })
      });
    }
    if (form.id === "webhookForm") {
      await api(id ? `/api/integrations/webhooks/${id}` : "/api/integrations/webhooks", {
        method: id ? "PATCH" : "POST",
        body: JSON.stringify({
          tenant_id: platformTenantValue(form),
          name: form.elements.name.value,
          event_type: form.elements.event_type.value,
          target_url: form.elements.target_url.value,
          status: form.elements.status.value,
          secret: form.elements.secret.value || null,
        })
      });
    }
    showToast("success", "Integracion guardada correctamente.");
    form.reset();
    await loadPhase8BData();
    renderIntegrations();
  }, "Guardando...");
}

async function handleUploadPreview(form) {
  const file = form.elements.csv_file.files[0];
  if (!file) throw new Error("Selecciona un archivo CSV para previsualizar.");
  const csvText = await file.text();
  const payload = {
    project_id: optionalNumber(form.elements.project_id.value),
    upload_type: form.elements.upload_type.value,
    file_name: file.name,
    csv_text: csvText,
    mapping: parseJsonField(form.elements.mapping.value, {}),
    create_records: form.elements.create_records.checked,
  };
  const button = form.querySelector("button[type='submit']");
  await runAction(button, async () => {
    const preview = await api("/api/uploads/preview", { method: "POST", body: JSON.stringify(payload) });
    state.ops.uploadPreview = preview;
    state.ops.uploadDraft = payload;
    showToast("success", "Archivo previsualizado correctamente.");
    renderUploads();
  }, "Previsualizando...");
}

async function confirmUpload(button) {
  if (!state.ops.uploadDraft) {
    showToast("warning", "Primero genera un preview de carga.");
    return;
  }
  await runAction(button, async () => {
    const batch = await api("/api/uploads/confirm", {
      method: "POST",
      body: JSON.stringify({ ...state.ops.uploadDraft, create_records: Boolean(state.ops.uploadDraft.create_records) })
    });
    state.ops.uploadPreview = null;
    state.ops.uploadDraft = null;
    showToast("success", `Carga confirmada. Lote #${batch.id}.`);
    await loadPhase8BData();
    renderUploads();
  }, "Confirmando...");
}

function excelPayloadFromForm(form) {
  const columns = Array.from(form.querySelectorAll('input[name="columns"]:checked'))
    .map((item) => item.value)
    .filter(Boolean);
  const filters = {
    text: form.elements.q.value || "",
    status: form.elements.status.value || "",
    risk: form.elements.risk.value || "",
    project_id: optionalNumber(form.elements.project_id.value),
    assigned_user_id: optionalNumber(form.elements.assigned_user_id.value),
    dpd_min: optionalNumber(form.elements.dpd_min.value),
    dpd_max: optionalNumber(form.elements.dpd_max.value),
  };
  return {
    source: form.elements.source.value,
    filters,
    columns,
    page: Number(form.elements.page.value || 1),
    page_size: Number(form.elements.page_size.value || 25),
  };
}

async function handleExcelQuery(form) {
  const button = form.querySelector("button[type='submit']");
  await runAction(button, async () => {
    const payload = excelPayloadFromForm(form);
    state.ops.excelDraft = payload;
    state.ops.excelResult = await api("/api/excel-web/query", { method: "POST", body: JSON.stringify(payload) });
    showToast("success", "Consulta ejecutada correctamente.");
    renderExcelWeb();
  }, "Consultando...");
}

async function saveExcelView(form) {
  const queryForm = document.querySelector("#excelQueryForm");
  const payload = state.ops.excelDraft || (queryForm ? excelPayloadFromForm(queryForm) : null);
  if (!payload) {
    showToast("warning", "Ejecuta una consulta antes de guardar la vista.");
    return;
  }
  await runAction(form.querySelector("button[type='submit']"), async () => {
    await api("/api/excel-web/views", {
      method: "POST",
      body: JSON.stringify({
        name: form.elements.name.value,
        source: payload.source,
        columns: payload.columns,
        filters: payload.filters,
        sort: {},
        is_public: form.elements.is_public.checked,
        is_favorite: form.elements.is_favorite.checked,
      })
    });
    showToast("success", "Vista guardada correctamente.");
    form.reset();
    await loadPhase8BData();
    renderExcelWeb();
  }, "Guardando...");
}

async function handleTypificationOpsSubmit(form) {
  const button = form.querySelector("button[type='submit']");
  await runAction(button, async () => {
    if (form.id === "typificationTreeForm") {
      await api("/api/typifications/trees", {
        method: "POST",
        body: JSON.stringify({
          project_id: optionalNumber(form.elements.project_id.value),
          module: form.elements.module.value,
          name: form.elements.name.value,
          code: form.elements.code.value,
          description: form.elements.description.value || null,
          status: form.elements.status.value,
        })
      });
    }
    if (form.id === "typificationNodeForm") {
      await api(`/api/typifications/trees/${form.elements.tree_id.value}/nodes`, {
        method: "POST",
        body: JSON.stringify({
          level: Number(form.elements.level.value || 1),
          code: form.elements.code.value,
          label: form.elements.label.value,
          order: Number(form.elements.order.value || 0),
          color: form.elements.color.value || null,
          requires_promise: form.elements.requires_promise.checked,
          requires_next_action: form.elements.requires_next_action.checked,
        })
      });
    }
    if (form.id === "typificationCombinationForm") {
      await api("/api/typifications/combinations", {
        method: "POST",
        body: JSON.stringify({
          tree_id: Number(form.elements.tree_id.value),
          path: form.elements.path.value.split(",").map((item) => item.trim()).filter(Boolean),
          required_fields: parseJsonField(form.elements.required_fields.value, {}),
          effects: parseJsonField(form.elements.effects.value, {}),
          is_active: form.elements.is_active.checked,
        })
      });
    }
    showToast("success", "Tipificacion actualizada correctamente.");
    form.reset();
    await loadPhase8BData();
    renderTypificationTrees();
  }, "Guardando...");
}

document.querySelector("#loginForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  loginResult.textContent = "Validando credenciales...";
  try {
    const payload = await api("/api/auth/login", {
      method: "POST",
      body: JSON.stringify({ email: document.querySelector("#email").value, password: document.querySelector("#password").value })
    });
    token = payload.access_token;
    currentUser = payload.user;
    localStorage.setItem("icodeup_v2_token", token);
    localStorage.setItem("icodeup_v2_user", JSON.stringify(currentUser));
    showApp();
    await refreshAll();
  } catch (error) {
    loginResult.textContent = error.message;
  }
});

document.querySelector("#logoutButton").addEventListener("click", logout);
setupNavigation();
setupForms();
setupEvents();

await loadHealth();
if (token && currentUser) {
  showApp();
  await refreshAll().catch((error) => {
    loginResult.textContent = error.message;
    logout();
  });
} else {
  showLogin();
}
