let token = localStorage.getItem("icodeup_v2_token") || "";
let currentUser = JSON.parse(localStorage.getItem("icodeup_v2_user") || "null");
const SUPPORT_TENANT_STORAGE_KEY = "icodeup_support_tenant_id";
const SUPPORT_AUDIENCE_STORAGE_KEY = "icodeup_support_audience";
const recentToasts = new Map();
const pendingClickToCallCustomers = new Set();
const DEFAULT_TABLE_PAGE_SIZE = 10;
const MAX_TABLE_PAGE_SIZE = 10;

const state = {
  core: { menu: null, roleDashboard: null },
  admin: { overview: null, tenants: [], projects: [], users: [], roles: [], typifications: [] },
  governance: { permissions: [], roles: [], users: [], modules: [], settings: null, audit: [], parties: [], plans: [], subscriptions: [], health: null, securityInsights: [], effectiveAccess: null },
  crm: { options: { tenants: [], projects: [], users: [], channels: [] }, dashboard: null, bi: null, customers: null, queue: null, promises: [], payments: [], agreements: [], paymentObligations: [], channels: [], typifications: [] },
  configuration: { catalogs: [], rules: [], alertRules: [], workflows: [] },
  alerts: { items: [], summary: null },
  legal: { dashboard: null, kanban: null, cases: [] },
  sales: { dashboard: null, pipeline: null, kanban: null, leads: [], opportunities: [] },
  teams: { projects: [], leaders: [], agents: [], projectUsers: [], leaderAgents: [], leaderSummary: null, selectedProjectId: null, selectedLeaderId: null },
  ops: { trees: [], combinations: [], recordings: [], telephonyProviders: [], telephonyExtensions: [], telephonyCallLogs: [], myExtension: null, uploads: [], demographics: [], excelSources: [], excelViews: [], excelResult: null, excelDraft: null, excelSheetRows: null, excelSheetFilters: {}, excelSheetEditingId: null, excelSheetChanges: {}, excelSheetNewRow: {}, excelSheetActiveCell: null, uploadPreview: null, uploadDraft: null, providers: [], integrationChannels: [], templates: [], webhooks: [], events: [] },
  ui: { tablePages: {}, selectedAgreementId: null },
  selectedCustomer: null,
  selectedActivities: [],
  selectedObligations: [],
  selectedAgreements: [],
  selectedDemographics: [],
  queuePage: 1,
  customerPage: 1
};

const titles = {
  dashboard: "Tablero ejecutivo",
  queue: "Cola de gestion",
  customers: "Clientes y repartos",
  promises: "Promesas de pago",
  payments: "PayControl 360",
  agreements: "Acuerdos de pago",
  legal: "Gestion juridica",
  documents: "Gestion documental",
  sales: "Pipeline comercial",
  reports: "Analytics 360",
  channels: "ChatBOX 360",
  tenants: "Empresas",
  projects: "Proyectos",
  users: "Usuarios",
  typifications: "Tipificaciones",
  governance: "Gobierno SaaS IEP",
  plans: "Planes",
  subscriptions: "Suscripciones",
  modules: "Modulos",
  configuration: "Centro de configuracion",
  alerts: "Alertas",
  "typification-trees": "Arboles de gestion",
  recordings: "Grabaciones",
  telephony: "Telefonia",
  uploads: "Cargas y repartos",
  "excel-web": "Mi Excel Web",
  integrations: "Integraciones",
  "tenant-settings": "Mi empresa",
  "company-users": "Usuarios de empresa",
  "roles-permissions": "Roles y permisos",
  "tenant-modules": "Modulos contratados",
  teams: "Equipos y carteras",
  branding: "Branding",
  audit: "Auditoria",
  "system-health": "Salud del sistema",
  parties: "Tercero maestro",
  tasks: "Mis tareas"
};

const roleLabels = {
  platform_admin: "SuperAdmin",
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
  platform_admin: "Gobierno SaaS",
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
  teams: "Administracion",
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
  telephony: "Operacion",
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
  teams: "administration",
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
  telephony: "telephony",
  uploads: "collections",
  integrations: "integrations",
  parties: "crm",
  reports: "bi",
  "excel-web": "bi",
  alerts: "bi"
};

const moduleCopy = {
  crm: { name: "Collects 360", category: "Operacion", description: "CRM de cobranzas, recuperacion de cartera, promesas, pagos y acuerdos." },
  core: { name: "Core SaaS", category: "Core", description: "Identidad, tenants, permisos, auditoria y base de operacion segura." },
  administration: { name: "Administracion", category: "Administracion", description: "Usuarios, roles, configuracion, branding y gobierno de empresa." },
  collections: { name: "Collects 360 · Cobranzas", category: "Operacion", description: "CRM de cobranzas, recuperacion de cartera, promesas, pagos y acuerdos." },
  legal: { name: "Juridico", category: "Operacion", description: "Casos, actuaciones, audiencias, vencimientos y riesgo legal." },
  documents: { name: "Documentos", category: "Operacion", description: "Metadatos documentales asociados a terceros, pagos, acuerdos y casos." },
  sales: { name: "Pipeline comercial", category: "Expansion", description: "Leads, oportunidades, valor ponderado y forecast comercial." },
  bi: { name: "Analytics 360", category: "Analitica", description: "Dashboards, reportes, analitica operacional y ejecutiva." },
  telephony: { name: "Telefonia", category: "Integraciones", description: "Click-to-call, extensiones, historial de llamadas y base para softphone WebRTC." },
  integrations: { name: "ChatBOX 360", category: "Integraciones", description: "Canales, chatbot, WhatsApp y automatizacion conversacional." },
  hr: { name: "FoodFlow 360", category: "Operacion", description: "Produccion de alimentos, inventarios, pedidos, costos y trazabilidad." },
  finance: { name: "PayControl 360", category: "Operacion", description: "Control, validacion, soporte y reporteria de pagos." },
  industrial: { name: "ProdLine 360", category: "Operacion", description: "Produccion industrial, ordenes, costos, maquinas y operaciones." }
};

const IPCOM_PROVIDER_PRESET = {
  name: "IpCom",
  provider_type: "sip_trunk",
  host: "35.192.135.117",
  port: 5060,
  trunk_name: "IpCom",
  dtmf_mode: "rfc2833",
  nat: "force_rport,comedia",
  codecs: "ulaw,alaw,g729",
  external_prefix: "0218739#",
  mobile_prepend: "000157",
  mobile_match_pattern: "3XXXXXXXXX",
  country_context: "Colombia",
  outbound_enabled: true,
  priority: 1,
  is_primary: true
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
    const detail = payload.detail;
    const message = typeof detail === "string"
      ? detail
      : detail?.message || payload.message || "No fue posible completar la solicitud. Intenta nuevamente o contacta al administrador.";
    const error = new Error(message);
    error.code = detail?.code || payload.code || null;
    error.payload = payload;
    throw error;
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
  const key = `${type}:${message}`;
  const now = Date.now();
  if (recentToasts.has(key) && now - recentToasts.get(key) < 1800) return;
  recentToasts.set(key, now);
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

async function downloadCsvPost(path, fileName, body) {
  const response = await fetch(path, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {})
    },
    body: JSON.stringify(body)
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

function downloadCsvText(filename, csvText) {
  const blob = new Blob([csvText || ""], { type: "text/csv;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename || "iep.csv";
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

function isPlatform() {
  return currentUser?.role === "platform_admin";
}

function canManageCrm() {
  if (isOperationalSupportMode()) return ["company_admin", "operational_leader"].includes(menuUser().audience);
  return ["platform_admin", "tenant_admin", "coordinator"].includes(currentUser?.role);
}

function menuUser() {
  return state.core.menu?.user || currentUser || {};
}

function canExportCrmData() {
  const audience = state.core.menu?.user?.audience;
  if (audience) return ["platform_admin", "company_admin", "operational_leader"].includes(audience);
  return ["platform_admin", "tenant_admin", "coordinator"].includes(currentUser?.role);
}

function canExportExcelWeb() {
  const audience = menuUser().audience;
  return ["platform_admin", "company_admin", "operational_leader"].includes(audience);
}

function activeTenant() {
  return state.core.menu?.tenant || currentUser || {};
}

function supportContext() {
  return state.core.menu?.support_context || {};
}

function isOperationalSupportMode() {
  return Boolean(supportContext().enabled);
}

function storedOperationalSupport() {
  if (!isPlatform()) return null;
  const tenantId = localStorage.getItem(SUPPORT_TENANT_STORAGE_KEY);
  if (!tenantId) return null;
  return {
    tenant_id: tenantId,
    audience: localStorage.getItem(SUPPORT_AUDIENCE_STORAGE_KEY) || "company_admin"
  };
}

function operationalTenantId() {
  return isOperationalSupportMode() ? supportContext().tenant_id : "";
}

function scopedTenantParams(params = {}) {
  const tenantId = operationalTenantId();
  return tenantId ? { ...params, tenant_id: tenantId } : params;
}

function roleLabel(role = menuUser().profile_role || menuUser().role) {
  return roleLabels[role] || role || "Usuario";
}

function audienceLabel(audience = menuUser().audience) {
  return audienceLabels[audience] || audience || "Workspace";
}

function activePlanLabel() {
  if (isOperationalSupportMode()) return "Soporte operativo";
  const tenant = activeTenant();
  if (tenant.is_platform || menuUser().is_platform_admin || isPlatform()) return "IEP";
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
  const copy = moduleCopy[key] || {};
  return {
    code: key,
    name: copy.name || fallback.name || fallback.label || key,
    category: copy.category || fallback.category || "Modulo",
    description: copy.description || fallback.description || "Capacidad modular disponible bajo permisos y plan contratado.",
  };
}

function menuItemLabel(item) {
  return titles[item.section] || item.label;
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
    telephony: '<path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.8 19.8 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.12 4.18 2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72c.12.9.33 1.77.62 2.6a2 2 0 0 1-.45 2.11L8 9.71a16 16 0 0 0 6.29 6.29l1.28-1.28a2 2 0 0 1 2.11-.45c.83.29 1.7.5 2.6.62A2 2 0 0 1 22 16.92z"/>',
    uploads: '<path d="M12 3v12"/><path d="m7 8 5-5 5 5"/><path d="M5 21h14"/>',
    integrations: '<path d="M8 7V3"/><path d="M16 7V3"/><path d="M7 7h10v5a5 5 0 0 1-10 0z"/><path d="M12 17v4"/>',
    configuration: '<circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.7 1.7 0 0 0 .34 1.88l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06A1.7 1.7 0 0 0 15 19.4a1.7 1.7 0 0 0-1 .6 1.7 1.7 0 0 0-.4 1V21a2 2 0 1 1-4 0v-.08a1.7 1.7 0 0 0-.4-1 1.7 1.7 0 0 0-1-.6 1.7 1.7 0 0 0-1.88.34l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06A1.7 1.7 0 0 0 4.6 15a1.7 1.7 0 0 0-.6-1 1.7 1.7 0 0 0-1-.4H3a2 2 0 1 1 0-4h.08a1.7 1.7 0 0 0 1-.4 1.7 1.7 0 0 0 .6-1 1.7 1.7 0 0 0-.34-1.88l-.06-.06A2 2 0 1 1 7.11 3.4l.06.06A1.7 1.7 0 0 0 9 4.6a1.7 1.7 0 0 0 1-.6 1.7 1.7 0 0 0 .4-1V3a2 2 0 1 1 4 0v.08a1.7 1.7 0 0 0 .4 1 1.7 1.7 0 0 0 1 .6 1.7 1.7 0 0 0 1.88-.34l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06A1.7 1.7 0 0 0 19.4 9c.2.35.4.65.6 1 .3.2.62.35 1 .4H21a2 2 0 1 1 0 4h-.08a1.7 1.7 0 0 0-1 .4 1.7 1.7 0 0 0-.52.6z"/>',
    alerts: '<path d="M18 8a6 6 0 0 0-12 0c0 7-3 7-3 7h18s-3 0-3-7"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/>',
    "excel-web": '<rect x="3" y="4" width="18" height="16" rx="2"/><path d="M3 10h18"/><path d="M9 4v16"/><path d="M15 4v16"/>',
    governance: '<path d="M12 3 4 6v6c0 5 3.5 8 8 9 4.5-1 8-4 8-9V6z"/><path d="m9 12 2 2 4-4"/>',
    tenants: '<path d="M3 21h18"/><path d="M5 21V7l7-4 7 4v14"/><path d="M9 21v-7h6v7"/>',
    users: '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M19 8v6"/><path d="M16 11h6"/>',
    teams: '<path d="M7 17v-1a3 3 0 0 1 3-3h4a3 3 0 0 1 3 3v1"/><circle cx="12" cy="8" r="3"/><path d="M4 20h16"/><path d="M5 11h2"/><path d="M17 11h2"/>',
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
  const supportMode = isOperationalSupportMode();
  const isPlatformContext = !supportMode && Boolean(tenant.is_platform || user.is_platform_admin || currentUser?.role === "platform_admin");
  const tenantName = tenant.name || currentUser?.tenant_name || "Workspace activo";
  const profile = roleLabel(user.profile_role || user.role || currentUser?.role);
  const audience = audienceLabel(user.audience);
  const plan = activePlanLabel();
  const displayName = isPlatformContext ? "Icodeup Enterprise Platform" : user.name || currentUser?.name;
  const sessionText = supportMode
    ? `${currentUser?.name || "SuperAdmin"} - Soporte operativo`
    : displayName ? `${displayName} - ${profile}` : "Sesion activa";
  document.querySelector("#sessionUser") && (document.querySelector("#sessionUser").textContent = sessionText);
  document.querySelector("#sidebarTenant") && (document.querySelector("#sidebarTenant").textContent = isPlatformContext ? "Icodeup Enterprise Platform" : tenantName);
  document.querySelector("#sidebarRole") && (document.querySelector("#sidebarRole").textContent = supportMode ? `Soporte - ${audience}` : profile);
  document.querySelector("#sidebarPlanBadge") && (document.querySelector("#sidebarPlanBadge").textContent = plan);
  document.querySelector("#topbarTenant") && (document.querySelector("#topbarTenant").textContent = isPlatformContext ? "IEP - Gobierno SaaS" : `${tenantName} - ${supportMode ? "Soporte operativo" : audience}`);
  document.querySelector("#systemStatusPill") && (document.querySelector("#systemStatusPill").textContent = "Sistema operativo");
  const demoBadge = document.querySelector("#demoModeBadge");
  if (demoBadge) demoBadge.classList.toggle("hidden", !isDemoContext());
  document.querySelectorAll(".platform-only").forEach((item) => item.classList.toggle("hidden", !isPlatform() || isOperationalSupportMode()));
  document.querySelectorAll(".manager-only").forEach((item) => item.classList.toggle("hidden", !canManageCrm()));
  document.querySelectorAll("#exportCustomers, #exportPayments").forEach((item) => item.classList.toggle("hidden", !canExportCrmData()));
  renderOperationalSupportControls();
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
              <p>${escapeHtml(plan.description || "Plan comercial para licenciar capacidades de IEP.")}</p>
              <div class="plan-limits">
                <small>Usuarios: ${escapeHtml(limitText(plan.max_users))}</small>
                <small>Proyectos: ${escapeHtml(limitText(plan.max_projects))}</small>
                <small>Registros: ${escapeHtml(limitText(plan.max_records || plan.max_customers))}</small>
              </div>
            </article>
          `
        )
        .join("")
    : `<article class="empty-state"><strong>Planes por configurar</strong><p>Los planes comerciales apareceran aqui cuando IEP los active para venta.</p></article>`;
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
            .map((item, index) => `<button class="nav-item ${items.indexOf(item) === 0 && index === 0 ? "active" : ""}" data-section="${escapeHtml(item.section)}">${iconForSection(item.section)}<span class="nav-label">${escapeHtml(menuItemLabel(item))}</span></button>`)
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
  document.querySelector("#sectionTitle").textContent = titles[firstSection] || items[0]?.label || "IEP";
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
  document.querySelectorAll(".platform-only").forEach((item) => item.classList.toggle("hidden", !isPlatform() || isOperationalSupportMode()));
  document.querySelectorAll(".manager-only").forEach((item) => item.classList.toggle("hidden", !canManageCrm()));
  document.querySelectorAll("#exportCustomers, #exportPayments").forEach((item) => item.classList.toggle("hidden", !canExportCrmData()));
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
  localStorage.removeItem(SUPPORT_TENANT_STORAGE_KEY);
  localStorage.removeItem(SUPPORT_AUDIENCE_STORAGE_KEY);
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
  const selectedModuleTenant = isPlatform() ? (operationalTenantId() || document.querySelector("#moduleTenantFilter")?.value || state.admin.tenants[0]?.id || "") : "";
  const moduleTenant = selectedModuleTenant ? `?tenant_id=${selectedModuleTenant}` : "";
  const auditParams = queryParams({
    tenant_id: isPlatform() ? operationalTenantId() || document.querySelector("#auditTenantFilter")?.value || "" : "",
    module: document.querySelector("#auditModuleFilter")?.value || ""
  });
  const scope = scopedQuery();
  const [permissions, roles, users, modules, settings, audit, parties, plans, subscriptions, health, securityInsights] = await Promise.all([
    allowed("roles-permissions") ? apiMaybe("/api/governance/permissions", []) : [],
    allowed("roles-permissions") ? apiMaybe(`/api/governance/roles${scope}`, []) : [],
    allowed("company-users", "roles-permissions") ? apiMaybe(`/api/governance/users${scope}`, []) : [],
    allowed("modules", "tenant-modules") ? apiMaybe(`/api/governance/modules${moduleTenant}`, []) : [],
    allowed("tenant-settings", "branding") ? apiMaybe(`/api/governance/settings${scope}`, null) : null,
    allowed("audit", "governance") ? apiMaybe(`/api/governance/audit-logs?${auditParams}`, []) : [],
    allowed("parties") ? apiMaybe(`/api/governance/parties${scope}`, []) : [],
    allowed("plans") ? apiMaybe("/api/subscriptions/plans", []) : [],
    allowed("subscriptions", "governance") ? apiMaybe("/api/governance/subscriptions", []) : [],
    allowed("system-health", "governance") ? apiMaybe("/api/health", null) : null,
    allowed("company-users", "roles-permissions", "tenant-modules") ? apiMaybe(`/api/governance/security-insights${scope}`, []) : []
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
  const support = storedOperationalSupport();
  const menuParams = support ? queryParams({ operational_tenant_id: support.tenant_id, operational_audience: support.audience }) : "";
  let menu;
  try {
    menu = await api(`/api/menu/me${menuParams ? `?${menuParams}` : ""}`);
  } catch (error) {
    if (!support) throw error;
    localStorage.removeItem(SUPPORT_TENANT_STORAGE_KEY);
    localStorage.removeItem(SUPPORT_AUDIENCE_STORAGE_KEY);
    showToast("warning", error.message || "No fue posible entrar a operacion tenant.");
    menu = await api("/api/menu/me");
  }
  const roleDashboard = menu.support_context?.enabled ? null : await api("/api/dashboard/me");
  state.core.menu = menu;
  state.core.roleDashboard = roleDashboard;
  applyBranding(menu.tenant || {});
  renderShellContext();
}

async function loadTeamsData() {
  if (!menuHasSection("teams")) return;
  const scope = scopedQuery();
  const [projects, leaders, agents] = await Promise.all([
    apiMaybe(`/api/teams/projects${scope}`, []),
    apiMaybe(`/api/teams/leaders${scope}`, []),
    apiMaybe(`/api/teams/agents${scope}`, [])
  ]);
  const selectedProjectId = state.teams.selectedProjectId || projects[0]?.id || null;
  const selectedLeaderId = state.teams.selectedLeaderId || leaders[0]?.id || null;
  const [projectUsers, leaderAgents, leaderSummary] = await Promise.all([
    selectedProjectId ? apiMaybe(`/api/teams/projects/${selectedProjectId}/users`, []) : [],
    selectedLeaderId ? apiMaybe(`/api/teams/leaders/${selectedLeaderId}/agents`, []) : [],
    selectedLeaderId ? apiMaybe(`/api/teams/leaders/${selectedLeaderId}/summary`, null) : null
  ]);
  state.teams = { projects, leaders, agents, projectUsers, leaderAgents, leaderSummary, selectedProjectId, selectedLeaderId };
}

async function loadTypifications() {
  if (!isPlatform()) return;
  const tenantId = operationalTenantId() || document.querySelector('#typificationForm select[name="tenant_id"]')?.value || state.admin.tenants[0]?.id;
  state.admin.typifications = tenantId ? await api(`/api/typifications?tenant_id=${tenantId}`) : [];
}

function queryParams(params) {
  const search = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "") search.set(key, value);
  });
  return search.toString();
}

function scopedQuery(params = {}) {
  const text = queryParams(scopedTenantParams(params));
  return text ? `?${text}` : "";
}

function scopedExcelFilters(filters = {}) {
  const tenantId = operationalTenantId();
  return tenantId ? { ...filters, tenant_id: Number(tenantId) } : filters;
}

async function loadCrmData() {
  const allowed = (...sections) => menuHasSection(...sections);
  const [options, dashboard, promises, payments, agreements, channels, typifications] = await Promise.all([
    apiMaybe(`/api/crm/options${scopedQuery()}`, { tenants: [], projects: [], users: [], channels: [] }),
    allowed("dashboard", "queue", "customers", "reports") ? apiMaybe(`/api/crm/dashboard${scopedQuery()}`, null) : null,
    allowed("promises") ? apiMaybe(`/api/crm/promises${scopedQuery()}`, []) : [],
    allowed("payments") ? apiMaybe(`/api/crm/payments${scopedQuery()}`, []) : [],
    allowed("agreements") ? apiMaybe(`/api/crm/agreements${scopedQuery()}`, []) : [],
    allowed("channels") ? apiMaybe("/api/crm/channels", []) : [],
    canManageCrm() || allowed("queue", "customers") ? apiMaybe(`/api/crm/typifications${scopedQuery()}`, []) : []
  ]);
  state.crm.options = options;
  state.crm.dashboard = dashboard;
  state.crm.promises = promises;
  state.crm.payments = payments;
  state.crm.agreements = agreements;
  state.crm.channels = channels;
  state.crm.typifications = typifications;
  await Promise.all([loadQueue(), loadCustomers()]);
}

async function loadQueue() {
  const params = queryParams(scopedTenantParams({
    page: state.queuePage,
    page_size: 10,
    q: document.querySelector("#queueSearch")?.value || "",
    status: document.querySelector("#queueStatus")?.value || "",
    risk: document.querySelector("#queueRisk")?.value || ""
  }));
  state.crm.queue = await api(`/api/crm/customers?${params}`);
}

async function loadCustomers() {
  const params = queryParams(scopedTenantParams({
    page: state.customerPage,
    page_size: 10,
    q: document.querySelector("#customerSearch")?.value || ""
  }));
  state.crm.customers = await api(`/api/crm/customers?${params}`);
}

async function loadBi() {
  const params = queryParams(scopedTenantParams({
    tenant_id: operationalTenantId() || document.querySelector("#biTenant")?.value || "",
    project_id: document.querySelector("#biProject")?.value || "",
    horizon_days: document.querySelector("#biHorizon")?.value || 30
  }));
  state.crm.bi = await api(`/api/crm/bi?${params}`);
}

async function loadPhase8Data() {
  const allowed = (...sections) => menuHasSection(...sections);
  const scope = scopedQuery();
  const [catalogs, rules, alertRules, workflows, alertItems, alertSummary, legalDashboard, legalKanban, legalCases, salesDashboard, salesPipeline, salesKanban, leads, opportunities] = await Promise.all([
    allowed("configuration") ? apiMaybe(`/api/configuration/catalogs${scope}`, []) : [],
    allowed("configuration") ? apiMaybe(`/api/configuration/rules${scope}`, []) : [],
    allowed("configuration") ? apiMaybe(`/api/configuration/alert-rules${scope}`, []) : [],
    allowed("configuration") ? apiMaybe(`/api/configuration/workflows${scope}`, []) : [],
    allowed("alerts", "dashboard", "reports") ? apiMaybe(`/api/alerts${scopedQuery({ limit: DEFAULT_TABLE_PAGE_SIZE })}`, []) : [],
    allowed("alerts", "dashboard", "reports") ? apiMaybe(`/api/alerts/summary${scope}`, null) : null,
    allowed("legal") ? apiMaybe(`/api/legal/dashboard${scope}`, null) : null,
    allowed("legal") ? apiMaybe(`/api/legal/kanban${scope}`, null) : null,
    allowed("legal") ? apiMaybe(`/api/legal/cases${scope}`, []) : [],
    allowed("sales") ? apiMaybe(`/api/sales/dashboard${scope}`, null) : null,
    allowed("sales") ? apiMaybe(`/api/sales/pipeline${scope}`, null) : null,
    allowed("sales") ? apiMaybe(`/api/sales/kanban${scope}`, null) : null,
    allowed("sales") ? apiMaybe(`/api/sales/leads${scope}`, []) : [],
    allowed("sales") ? apiMaybe(`/api/sales/opportunities${scope}`, []) : []
  ]);
  state.configuration = { catalogs, rules, alertRules, workflows };
  state.alerts = { items: alertItems, summary: alertSummary };
  state.legal = { dashboard: legalDashboard, kanban: legalKanban, cases: legalCases };
  state.sales = { dashboard: salesDashboard, pipeline: salesPipeline, kanban: salesKanban, leads, opportunities };
}

async function loadPhase8BData() {
  const allowed = (...sections) => menuHasSection(...sections);
  const scope = scopedQuery();
  const [trees, combinations, recordings, telephonyProviders, telephonyExtensions, telephonyCallLogs, myExtension, uploads, demographics, excelSources, excelViews, excelResult, excelSheetRows, providers, integrationChannels, templates, webhooks, events, telephonyTenants] = await Promise.all([
    allowed("typification-trees", "typifications") ? apiMaybe(`/api/typifications/trees${scope}`, []) : [],
    allowed("typification-trees", "typifications") ? apiMaybe(`/api/typifications/combinations${scope}`, []) : [],
    allowed("recordings") ? apiMaybe(`/api/recordings${scope}`, []) : [],
    allowed("telephony") ? apiMaybe(`/api/telephony/providers${scope}`, []) : [],
    allowed("telephony") ? apiMaybe(`/api/telephony/extensions${scope}`, []) : [],
    allowed("telephony") ? apiMaybe(`/api/telephony/call-logs${scope}`, []) : [],
    allowed("telephony") ? apiMaybe("/api/telephony/my-extension", null) : null,
    allowed("uploads") ? apiMaybe(`/api/uploads/batches${scopedQuery({ page_size: DEFAULT_TABLE_PAGE_SIZE })}`, []) : [],
    allowed("uploads", "queue", "customers") ? apiMaybe(`/api/uploads/demographics${scopedQuery({ page_size: DEFAULT_TABLE_PAGE_SIZE })}`, []) : [],
    allowed("excel-web") ? apiMaybe("/api/excel-web/sources", []) : [],
    allowed("excel-web") ? apiMaybe(`/api/excel-web/views${scope}`, []) : [],
    allowed("excel-web") ? apiMaybe("/api/excel-web/query", null, { method: "POST", body: JSON.stringify({ source: "customers", page: 1, page_size: DEFAULT_TABLE_PAGE_SIZE, filters: scopedExcelFilters({}), columns: [] }) }) : null,
    allowed("excel-web") ? apiMaybe(`/api/excel-web/sheet-rows${scopedQuery({ page_size: DEFAULT_TABLE_PAGE_SIZE })}`, { items: [], page: 1, total_pages: 0, total: 0 }) : null,
    allowed("integrations", "channels") ? apiMaybe(`/api/integrations/providers${scope}`, []) : [],
    allowed("integrations", "channels") ? apiMaybe(`/api/integrations/channels${scope}`, []) : [],
    allowed("integrations") ? apiMaybe(`/api/integrations/templates${scope}`, []) : [],
    allowed("integrations") ? apiMaybe(`/api/integrations/webhooks${scope}`, []) : [],
    allowed("integrations") ? apiMaybe(`/api/integrations/events${scope}`, []) : [],
    allowed("telephony") && isPlatform() && !state.admin.tenants.length ? apiMaybe("/api/admin/tenants", []) : []
  ]);
  if (telephonyTenants.length && !state.admin.tenants.length) {
    state.admin = { ...state.admin, tenants: telephonyTenants };
  }
  state.ops = { ...state.ops, trees, combinations, recordings, telephonyProviders, telephonyExtensions, telephonyCallLogs, myExtension, uploads, demographics, excelSources, excelViews, excelResult: state.ops.excelResult || excelResult, excelSheetRows, providers, integrationChannels, templates, webhooks, events };
}

async function refreshAll() {
  await loadCoreData();
  renderDynamicMenu();
  await loadAdminData();
  await loadGovernanceData();
  if (menuHasSection("teams")) {
    await optionalLoad("Equipos y carteras", loadTeamsData);
  }
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
  if (menuHasSection("typification-trees", "recordings", "telephony", "uploads", "excel-web", "integrations")) {
    await optionalLoad("Fase 8B", loadPhase8BData);
  }
  renderAll();
}

function optionList(items, valueKey = "id", labelKey = "name", selected = "") {
  return items
    .map((item) => {
      const value = item[valueKey];
      const label = item[labelKey] || item.name || item.label || item.display_name || item.slug || value;
      return `<option value="${escapeHtml(value)}" ${String(value) === String(selected) ? "selected" : ""}>${escapeHtml(label)}</option>`;
    })
    .join("");
}

function tenantOptionValue(item) {
  return item?.id ?? item?.tenant_id ?? item?.value ?? "";
}

function tenantOptionLabel(item) {
  return item?.label || item?.name || item?.display_name || item?.company_name || item?.slug || `Empresa ${tenantOptionValue(item)}`;
}

function telephonyTenantSource() {
  const tenants = [];
  const currentTenant = activeTenant();
  if (currentTenant?.id) tenants.push(currentTenant);
  tenants.push(...(state.admin.tenants || []), ...(state.crm.options.tenants || []));

  const byId = new Map();
  tenants.forEach((item) => {
    const value = tenantOptionValue(item);
    if (!value) return;
    const key = String(value);
    const existing = byId.get(key) || {};
    byId.set(key, { ...existing, ...item, id: value, name: tenantOptionLabel({ ...existing, ...item }) });
  });
  return Array.from(byId.values()).sort((a, b) => tenantOptionLabel(a).localeCompare(tenantOptionLabel(b), "es"));
}

function defaultTelephonyTenantId(tenants, currentValue = "") {
  const values = new Set((tenants || []).map((item) => String(tenantOptionValue(item))));
  if (currentValue && values.has(String(currentValue))) return String(currentValue);
  const activeId = tenantOptionValue(activeTenant()) || currentUser?.tenant_id;
  if (activeId && values.has(String(activeId))) return String(activeId);
  if ((tenants || []).length === 1) return String(tenantOptionValue(tenants[0]));
  return "";
}

function telephonyTenantOptions(tenants, selected = "") {
  return (tenants || [])
    .map((item) => {
      const value = tenantOptionValue(item);
      const label = tenantOptionLabel(item);
      return `<option value="${escapeHtml(value)}" ${String(value) === String(selected) ? "selected" : ""}>${escapeHtml(label)}</option>`;
    })
    .join("");
}

function businessTenantSource() {
  const source = [...(state.admin.tenants || []), ...(state.crm.options.tenants || [])];
  const byId = new Map();
  source.forEach((item) => {
    const value = tenantOptionValue(item);
    if (!value || item?.is_platform || item?.slug === "icodeup-platform") return;
    byId.set(String(value), { ...item, id: value, name: tenantOptionLabel(item) });
  });
  return Array.from(byId.values()).sort((a, b) => tenantOptionLabel(a).localeCompare(tenantOptionLabel(b), "es"));
}

function supportAudienceOptions(selected = "company_admin") {
  const options = [
    ["company_admin", "Admin empresa"],
    ["operational_leader", "Lider cobranzas"],
    ["operational_user", "Gestor"]
  ];
  return options.map(([value, label]) => `<option value="${value}" ${value === selected ? "selected" : ""}>${label}</option>`).join("");
}

function renderOperationalSupportControls() {
  const topbarMeta = document.querySelector(".topbar-meta");
  if (!topbarMeta) return;
  let container = document.querySelector("#supportModeControls");
  if (!isPlatform()) {
    if (container) container.remove();
    return;
  }
  if (!container) {
    container = document.createElement("div");
    container.id = "supportModeControls";
    container.className = "support-mode-controls";
    topbarMeta.prepend(container);
  }
  const tenants = businessTenantSource();
  const stored = storedOperationalSupport();
  const context = supportContext();
  const selectedTenantId = operationalTenantId() || stored?.tenant_id || (tenants.length === 1 ? tenantOptionValue(tenants[0]) : "");
  const selectedAudience = context.audience || stored?.audience || "company_admin";
  const tenantOptions = tenants.map((item) => `<option value="${escapeHtml(tenantOptionValue(item))}" ${String(tenantOptionValue(item)) === String(selectedTenantId) ? "selected" : ""}>${escapeHtml(tenantOptionLabel(item))}</option>`).join("");
  container.innerHTML = `
    <span>${isOperationalSupportMode() ? "Operacion tenant" : "Gobierno SaaS"}</span>
    <select id="supportTenantSelect" aria-label="Empresa operativa" ${tenants.length ? "" : "disabled"}>
      <option value="">Empresa operativa</option>${tenantOptions}
    </select>
    <select id="supportAudienceSelect" aria-label="Vista operativa">
      ${supportAudienceOptions(selectedAudience)}
    </select>
    <button type="button" data-enter-support-mode>${isOperationalSupportMode() ? "Aplicar" : "Entrar a operacion"}</button>
    ${isOperationalSupportMode() ? `<button type="button" data-exit-support-mode>Gobierno SaaS</button>` : ""}
  `;
}

async function enterOperationalSupportMode(button) {
  const tenantSelect = document.querySelector("#supportTenantSelect");
  const audienceSelect = document.querySelector("#supportAudienceSelect");
  const tenantId = tenantSelect?.value;
  if (!tenantId) {
    showToast("warning", "Selecciona una empresa operativa para entrar a soporte.");
    tenantSelect?.focus();
    return;
  }
  await runAction(button, async () => {
    localStorage.setItem(SUPPORT_TENANT_STORAGE_KEY, tenantId);
    localStorage.setItem(SUPPORT_AUDIENCE_STORAGE_KEY, audienceSelect?.value || "company_admin");
    state.queuePage = 1;
    state.customerPage = 1;
    state.selectedCustomer = null;
    await refreshAll();
    showToast("success", "Modo soporte operativo activado.");
  }, "Entrando...");
}

async function exitOperationalSupportMode(button) {
  await runAction(button, async () => {
    localStorage.removeItem(SUPPORT_TENANT_STORAGE_KEY);
    localStorage.removeItem(SUPPORT_AUDIENCE_STORAGE_KEY);
    state.queuePage = 1;
    state.customerPage = 1;
    state.selectedCustomer = null;
    closeManagementDrawer();
    await refreshAll();
    showToast("success", "Volviste a Gobierno SaaS.");
  }, "Saliendo...");
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
    if (isOperationalSupportMode() && operationalTenantId()) select.value = String(operationalTenantId());
    else if (current) select.value = current;
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
    { label: "Aislamiento por empresa", detail: isPlatform() ? "IEP permite gobierno global; cada empresa solo ve su operacion." : "Tu sesion esta limitada a la empresa autenticada.", tone: "green" },
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
      { label: "Decision", title: "Analytics 360", detail: "Consulta semaforos y oportunidades.", section: "reports" },
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
    document.querySelector("#experienceActions") && (document.querySelector("#experienceActions").innerHTML = "");
    document.querySelector("#experienceModules") && (document.querySelector("#experienceModules").innerHTML = "");
    return;
  }
  const user = menuUser();
  const tenant = activeTenant();
  const audience = user.audience || data.audience || "operational_user";
  container.innerHTML = `
    <article class="role-dashboard-head">
      <div>
        <p class="eyebrow">${escapeHtml(audienceLabel(audience))}</p>
        <h2>${escapeHtml(data.title || "IEP")}</h2>
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

function tableKey(headers, emptyMessage) {
  const raw = `${headers.join("|")}::${emptyMessage}`;
  let hash = 0;
  for (let index = 0; index < raw.length; index += 1) hash = ((hash << 5) - hash + raw.charCodeAt(index)) | 0;
  return `table-${Math.abs(hash)}`;
}

function rowsToArray(rows) {
  if (Array.isArray(rows)) return rows.filter(Boolean);
  if (!rows) return [];
  return String(rows).match(/<tr[\s\S]*?<\/tr>/g) || [];
}

function table(headers, rows, emptyMessage, options = {}) {
  const allRows = rowsToArray(rows);
  if (!allRows.length) return `<p class="empty">${escapeHtml(emptyMessage)}</p>`;
  const key = options.key || tableKey(headers, emptyMessage);
  if (options.noClientPager) {
    return `<div class="data-table-shell"><table><thead><tr>${headers.map((item) => `<th>${escapeHtml(item)}</th>`).join("")}</tr></thead><tbody>${allRows.join("")}</tbody></table><div class="table-pager muted"><span>${allRows.length} filas visibles</span></div></div>`;
  }
  const requestedPageSize = Number(options.pageSize || DEFAULT_TABLE_PAGE_SIZE);
  const pageSize = Math.min(Math.max(requestedPageSize || DEFAULT_TABLE_PAGE_SIZE, 1), MAX_TABLE_PAGE_SIZE);
  const totalPages = Math.max(1, Math.ceil(allRows.length / pageSize));
  const requestedPage = Number(state.ui.tablePages[key] || 1);
  const page = Math.min(Math.max(requestedPage, 1), totalPages);
  state.ui.tablePages[key] = page;
  const visibleRows = allRows.slice((page - 1) * pageSize, page * pageSize).join("");
  const pager = allRows.length > pageSize || options.forcePager
    ? `<div class="table-pager">
        <button data-table-page="${escapeHtml(key)}" data-page="${page - 1}" type="button" ${page <= 1 ? "disabled" : ""}>Anterior</button>
        <span>Pagina ${page} de ${totalPages} · ${allRows.length} registros</span>
        <button data-table-page="${escapeHtml(key)}" data-page="${page + 1}" type="button" ${page >= totalPages ? "disabled" : ""}>Siguiente</button>
      </div>`
    : `<div class="table-pager muted"><span>${allRows.length} registros</span></div>`;
  return `<div class="data-table-shell"><table><thead><tr>${headers.map((item) => `<th>${escapeHtml(item)}</th>`).join("")}</tr></thead><tbody>${visibleRows}</tbody></table>${pager}</div>`;
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
  if (customer) {
    const [activities, obligations, demographics, agreements] = await Promise.all([
      api(`/api/crm/customers/${customer.id}/activities`),
      apiMaybe(`/api/crm/customers/${customer.id}/obligations`, []),
      apiMaybe(`/api/uploads/demographics?${queryParams(scopedTenantParams({ customer_id: customer.id, page_size: DEFAULT_TABLE_PAGE_SIZE }))}`, []),
      apiMaybe(`/api/crm/agreements?${queryParams(scopedTenantParams({ customer_id: customer.id }))}`, [])
    ]);
    state.selectedActivities = activities;
    state.selectedObligations = obligations;
    state.selectedDemographics = demographics;
    state.selectedAgreements = agreements;
  } else {
    state.selectedActivities = [];
    state.selectedObligations = [];
    state.selectedDemographics = [];
    state.selectedAgreements = [];
  }
  renderQueueDetail();
}

function obligationLabel(item) {
  const product = item.product_type || item.portfolio_name || "Obligacion";
  return `${product} - ${item.obligation_number}`;
}

function obligationOptions(selected = "") {
  const options = [`<option value="">Cliente completo</option>`];
  (state.selectedObligations || []).forEach((item) => {
    const label = `${obligationLabel(item)} - ${money(item.current_balance || 0)} - ${item.days_past_due || 0} dias`;
    options.push(`<option value="${item.id}" ${String(selected) === String(item.id) ? "selected" : ""}>${escapeHtml(label)}</option>`);
  });
  return options.join("");
}

function formObligationOptions(obligations = [], selected = "") {
  const options = [`<option value="">Cliente completo</option>`];
  (obligations || []).forEach((item) => {
    const label = `${obligationLabel(item)} - ${money(item.current_balance || 0)} - ${item.days_past_due || 0} dias`;
    options.push(`<option value="${item.id}" ${String(selected) === String(item.id) ? "selected" : ""}>${escapeHtml(label)}</option>`);
  });
  return options.join("");
}

function setFormObligationOptions(form, obligations = [], selected = "") {
  const select = form?.elements?.obligation_id;
  if (!select) return;
  select.innerHTML = formObligationOptions(obligations, selected);
}

async function loadObligationsForForm(form) {
  const customerId = form?.elements?.customer_id?.value;
  setFormObligationOptions(form, []);
  if (!customerId) return;
  const obligations = await apiMaybe(`/api/crm/customers/${customerId}/obligations`, []);
  setFormObligationOptions(form, obligations);
  if (form?.id === "paymentForm") state.crm.paymentObligations = obligations;
}

function selectedObligationSummary(obligationId) {
  const item = (state.selectedObligations || []).find((obligation) => String(obligation.id) === String(obligationId));
  return item ? `Obligacion: ${item.obligation_number}` : "";
}

function renderObligationMatrix(obligations = state.selectedObligations) {
  return relatedRows(
    obligations,
    (item) => `
      <article class="activity-card">
        <strong>${escapeHtml(obligationLabel(item))}</strong>
        <span>${money(item.current_balance || 0)} - ${item.days_past_due || 0} dias mora - ${escapeHtml(item.risk || "-")} - prioridad ${item.priority || 0}</span>
        <p>${escapeHtml(item.status || "Activa")} - vence ${escapeHtml(item.due_date ? dateOnly(item.due_date) : "-")} - ${escapeHtml(item.assigned_user_name || "Sin gestor")}</p>
      </article>
    `,
    "Este cliente aun no tiene obligaciones detalladas."
  );
}

function agreementSummary(item) {
  const paid = (item.installments || []).filter((installment) => installment.status === "paid").length;
  const total = item.installment_count || (item.installments || []).length || 0;
  return `${paid}/${total} cuotas pagadas`;
}

function renderAgreementMiniList(agreements = state.selectedAgreements) {
  return relatedRows(
    agreements,
    (item) => `
      <article class="activity-card">
        <strong>${money(item.total_amount)} - ${escapeHtml(item.status || "active")}</strong>
        <span>${escapeHtml(item.obligation_number || "Cliente completo")} - ${agreementSummary(item)}</span>
        <p>${escapeHtml(item.notes || "Acuerdo registrado con trazabilidad de cuotas.")}</p>
      </article>
    `,
    "Sin acuerdos registrados para este cliente."
  );
}

function renderDemographicMiniList(demographics = state.selectedDemographics) {
  return relatedRows(
    demographics,
    (item) => `
      <p>
        <strong>${escapeHtml(item.source)}</strong>
        <span>${escapeHtml([item.phone, item.email, item.address, item.city].filter(Boolean).join(" - ") || "-")}</span>
        <small>${escapeHtml(item.contactability || "Media")} - prioridad ${item.priority || 0}</small>
      </p>
    `,
    "Sin demograficos asociados."
  );
}

function channelHref(kind, customer) {
  if (kind === "whatsapp") {
    return `https://wa.me/${phoneDigits(customer.phone)}?text=${encodeURIComponent(`Hola ${customer.name}, te contactamos desde Collects 360 para revisar alternativas de normalizacion de tu obligacion.`)}`;
  }
  if (kind === "email") {
    return `mailto:${customer.email || ""}?subject=${encodeURIComponent("Alternativas de normalizacion")}`;
  }
  return "#";
}

function callActionButton(customer) {
  return `<button type="button" data-click-to-call="${customer.id}">Llamar</button>`;
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
          ${item.obligation_number ? `<span>${escapeHtml(item.obligation_number)}</span>` : ""}
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
      ${callActionButton(customer)}
      <a href="${channelHref("whatsapp", customer)}" target="_blank" rel="noreferrer">WhatsApp</a>
      <a href="${channelHref("email", customer)}">Email</a>
    </div>
    <div class="activity-head"><strong>Obligaciones</strong><span>Gestiona por deuda o cliente completo</span></div>
    <div class="activity-matrix">${renderObligationMatrix()}</div>
    <form id="activityForm" class="form-grid management-grid" data-customer-id="${customer.id}">
      <label class="wide">Gestionar sobre<select name="obligation_id">${obligationOptions()}</select></label>
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
  const agreements = state.selectedAgreements || [];
  const demographics = state.selectedDemographics || [];
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
        ${callActionButton(customer)}
        <a href="${channelHref("whatsapp", customer)}" target="_blank" rel="noreferrer">WhatsApp</a>
        <a href="${channelHref("email", customer)}">Email</a>
        <button type="button" data-prefill-result="Contactado">Registrar llamada</button>
        <button type="button" data-prefill-result="Promesa">Crear promesa</button>
        <button type="button" data-section-jump="agreements">Crear acuerdo</button>
        <button type="button" data-prefill-result="Escalado">Escalar juridico</button>
      </div>
      <article class="drawer-card">
        <h3>Obligaciones del cliente</h3>
        <div class="activity-matrix">${renderObligationMatrix()}</div>
      </article>
      <div class="drawer-content-grid">
        <article class="drawer-card">
          <h3>Registrar gestion</h3>
          <form id="drawerActivityForm" class="form-grid management-grid" data-customer-id="${customer.id}">
            <label class="wide">Gestionar sobre<select name="obligation_id">${obligationOptions()}</select></label>
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
          <div class="activity-matrix compact">${relatedRows(activities, (item) => `<article class="activity-card"><strong>${escapeHtml(item.result)}</strong><span>${dateOnly(item.created_at)} - ${escapeHtml(item.user_name || "")}</span>${item.obligation_number ? `<span>${escapeHtml(item.obligation_number)}</span>` : ""}<p>${escapeHtml(item.note || "Gestion registrada.")}</p></article>`, "Sin gestiones registradas.")}</div>
        </article>
        <article class="drawer-card">
          <h3>Promesas y pagos</h3>
          <div class="mini-list">${relatedRows(promises, (item) => `<p><strong>${money(item.amount)}</strong><span>${dateOnly(item.due_date)} - ${escapeHtml(item.status)}</span>${item.obligation_number ? `<span>${escapeHtml(item.obligation_number)}</span>` : ""}</p>`, "Sin promesas para este cliente.")}</div>
          <div class="mini-list">${relatedRows(payments, (item) => `<p><strong>${money(item.amount)}</strong><span>${dateOnly(item.paid_at)} - ${escapeHtml(item.method || "-")}</span>${item.obligation_number ? `<span>${escapeHtml(item.obligation_number)}</span>` : ""}</p>`, "Sin pagos para este cliente.")}</div>
        </article>
        <article class="drawer-card">
          <h3>Acuerdos y cuotas</h3>
          <div class="activity-matrix compact">${renderAgreementMiniList(agreements)}</div>
        </article>
        ${menuHasSection("agreements") ? `
        <article class="drawer-card">
          <h3>Crear acuerdo</h3>
          <form id="drawerAgreementForm" class="form-grid management-grid" data-customer-id="${customer.id}">
            <label class="wide">Obligacion<select name="obligation_id">${obligationOptions()}</select></label>
            <label>Monto total<input name="total_amount" type="number" min="1" required /></label>
            <label>Cuotas<input name="installment_count" type="number" min="1" value="3" required /></label>
            <label>Inicio<input name="start_date" type="date" required /></label>
            <label class="wide">Notas<textarea name="notes" placeholder="Condiciones acordadas, periodicidad o soporte pendiente."></textarea></label>
            <button type="submit">Guardar acuerdo</button>
            <p class="form-message wide" data-form-message></p>
          </form>
        </article>` : ""}
        ${menuHasSection("documents") ? `
        <article class="drawer-card">
          <h3>Registrar soporte</h3>
          <form id="drawerDocumentForm" class="form-grid management-grid" data-customer-id="${customer.id}" data-project-id="${customer.project_id || ""}">
            <label>Tipo<select name="document_type"><option value="Soporte de gestion">Soporte de gestion</option><option value="Acuerdo de pago">Acuerdo de pago</option><option value="Comprobante">Comprobante</option><option value="Contrato">Contrato</option></select></label>
            <label>Nombre<input name="original_name" placeholder="soporte_demo.pdf" required /></label>
            <label class="wide">Obligacion relacionada<select name="obligation_id">${obligationOptions()}</select></label>
            <label class="wide">Nota<textarea name="notes" placeholder="Detalle del soporte registrado como metadata."></textarea></label>
            <button type="submit">Registrar soporte</button>
            <p class="form-message wide" data-form-message></p>
          </form>
        </article>` : ""}
        <article class="drawer-card">
          <h3>Datos complementarios</h3>
          <div class="mini-list">${renderDemographicMiniList(demographics)}</div>
          ${menuHasSection("recordings") ? `<h3>Grabaciones</h3><div class="mini-list">${relatedRows(recordings, (item) => `<p><strong>${escapeHtml(item.call_id)}</strong><span>${Math.round((item.duration_seconds || 0) / 60)} min - ${escapeHtml(item.status)}</span></p>`, "Sin grabaciones asociadas.")}</div>` : ""}
        </article>
      </div>
    </section>
  `;
  drawer.querySelector("#drawerActivityForm")?.addEventListener("submit", submitActivity);
  drawer.querySelector("#drawerAgreementForm")?.addEventListener("submit", saveDrawerAgreement);
  drawer.querySelector("#drawerDocumentForm")?.addEventListener("submit", saveDrawerDocument);
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
    obligation_id: form.elements.obligation_id?.value ? Number(form.elements.obligation_id.value) : null,
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

async function saveDrawerAgreement(event) {
  event.preventDefault();
  const form = event.currentTarget;
  const button = form.querySelector("button[type='submit']");
  const message = form.querySelector("[data-form-message]");
  const customerId = form.dataset.customerId || state.selectedCustomer?.id;
  if (!customerId) return showToast("error", "No hay cliente seleccionado para crear el acuerdo.");
  const body = {
    customer_id: Number(customerId),
    obligation_id: form.elements.obligation_id?.value ? Number(form.elements.obligation_id.value) : null,
    total_amount: Number(form.elements.total_amount.value || 0),
    installment_count: Number(form.elements.installment_count.value || 0),
    start_date: toDateTime(form.elements.start_date.value),
    notes: form.elements.notes.value || null
  };
  if (!body.total_amount || !body.installment_count || !body.start_date) {
    showToast("warning", "Completa monto, cuotas y fecha de inicio del acuerdo.");
    return;
  }
  setButtonLoading(button, true, "Guardando...");
  try {
    await api("/api/crm/agreements", { method: "POST", body: JSON.stringify(body) });
    form.reset();
    if (message) message.textContent = "Acuerdo registrado correctamente.";
    showToast("success", "Acuerdo registrado correctamente.");
    await refreshCustomerAfterActivity(customerId);
  } catch (error) {
    console.warn(error);
    showToast("error", error.message || "No fue posible crear el acuerdo.");
  } finally {
    setButtonLoading(button, false);
  }
}

async function saveDrawerDocument(event) {
  event.preventDefault();
  const form = event.currentTarget;
  const button = form.querySelector("button[type='submit']");
  const message = form.querySelector("[data-form-message]");
  const customerId = form.dataset.customerId || state.selectedCustomer?.id;
  if (!customerId) return showToast("error", "No hay cliente seleccionado para registrar el soporte.");
  const obligationNote = selectedObligationSummary(form.elements.obligation_id?.value);
  const rawNotes = form.elements.notes.value || "";
  const body = {
    project_id: form.dataset.projectId ? Number(form.dataset.projectId) : null,
    customer_id: Number(customerId),
    document_type: form.elements.document_type.value,
    original_name: form.elements.original_name.value,
    mime_type: "application/pdf",
    size_bytes: 0,
    status: "registered",
    notes: [obligationNote, rawNotes].filter(Boolean).join(" | ") || null
  };
  if (!body.original_name) {
    showToast("warning", "Indica un nombre de soporte.");
    return;
  }
  setButtonLoading(button, true, "Registrando...");
  try {
    await api("/api/documents", { method: "POST", body: JSON.stringify(body) });
    form.reset();
    if (message) message.textContent = "Soporte registrado como metadata.";
    showToast("success", "Soporte registrado como metadata documental.");
  } catch (error) {
    console.warn(error);
    showToast("error", error.message || "No fue posible registrar el soporte.");
  } finally {
    setButtonLoading(button, false);
  }
}

async function refreshCustomerAfterActivity(customerId) {
  const activityRequest = api(`/api/crm/customers/${customerId}/activities`);
  const obligationsRequest = apiMaybe(`/api/crm/customers/${customerId}/obligations`, []);
  const demographicsRequest = apiMaybe(`/api/uploads/demographics?${queryParams(scopedTenantParams({ customer_id: customerId, page_size: DEFAULT_TABLE_PAGE_SIZE }))}`, []);
  const agreementsRequest = apiMaybe(`/api/crm/agreements?${queryParams(scopedTenantParams({ customer_id: customerId }))}`, []);
  const [queueResult, customersResult, activitiesResult, obligationsResult, demographicsResult, agreementsResult, promisesResult, paymentsResult, globalAgreementsResult] = await Promise.allSettled([
    loadQueue(),
    loadCustomers(),
    activityRequest,
    obligationsRequest,
    demographicsRequest,
    agreementsRequest,
    menuHasSection("promises") ? api(`/api/crm/promises${scopedQuery()}`) : Promise.resolve(state.crm.promises || []),
    menuHasSection("payments") ? api(`/api/crm/payments${scopedQuery()}`) : Promise.resolve(state.crm.payments || []),
    menuHasSection("agreements") ? api(`/api/crm/agreements${scopedQuery()}`) : Promise.resolve(state.crm.agreements || []),
  ]);
  [queueResult, customersResult, activitiesResult, obligationsResult, demographicsResult, agreementsResult, promisesResult, paymentsResult, globalAgreementsResult].forEach((result) => {
    if (result.status === "rejected") console.warn("Refresh posterior a gestion omitido:", result.reason);
  });
  if (activitiesResult.status === "fulfilled") state.selectedActivities = activitiesResult.value;
  if (obligationsResult.status === "fulfilled") state.selectedObligations = obligationsResult.value;
  if (demographicsResult.status === "fulfilled") state.selectedDemographics = demographicsResult.value;
  if (agreementsResult.status === "fulfilled") state.selectedAgreements = agreementsResult.value;
  if (promisesResult.status === "fulfilled") state.crm.promises = promisesResult.value;
  if (paymentsResult.status === "fulfilled") state.crm.payments = paymentsResult.value;
  if (globalAgreementsResult.status === "fulfilled") state.crm.agreements = globalAgreementsResult.value;
  const refreshedCustomer = [...(state.crm.queue?.items || []), ...(state.crm.customers?.items || [])].find((item) => Number(item.id) === Number(customerId));
  if (refreshedCustomer) state.selectedCustomer = refreshedCustomer;
  renderQueue();
  renderCustomers();
  renderPromises();
  renderPayments();
  renderAgreements();
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
          <td>${escapeHtml(item.obligation_number || "-")}</td>
          <td>${money(item.amount)}</td>
          <td>${dateOnly(item.due_date)}</td>
          <td>${escapeHtml(item.channel || "-")}</td>
          <td><span class="badge">${escapeHtml(item.status)}</span></td>
          <td>${item.status === "Vigente" ? `<button class="table-button" data-complete-promise="${item.id}" type="button">Cumplir</button>` : ""}</td>
        </tr>
      `
    )
    .join("");
  document.querySelector("#promiseTable").innerHTML = table(["Cliente", "Obligacion", "Monto", "Fecha", "Canal", "Estado", ""], rows, "No hay promesas.");
}

function renderPayments() {
  const rows = state.crm.payments
    .map(
      (item) => `
        <tr>
          <td>${escapeHtml(item.customer_name || "-")}</td>
          <td>${escapeHtml(item.obligation_number || "Cliente completo")}</td>
          <td>${money(item.amount)}</td>
          <td>${dateOnly(item.paid_at)}</td>
          <td>${escapeHtml(item.method)}</td>
          <td>${escapeHtml(item.reference || "-")}</td>
        </tr>
      `
    )
    .join("");
  document.querySelector("#paymentTable").innerHTML = table(["Cliente", "Obligacion", "Monto", "Fecha", "Metodo", "Referencia"], rows, "No hay pagos.");
}

function selectedAgreement() {
  const selectedId = state.ui.selectedAgreementId;
  return (state.crm.agreements || []).find((item) => String(item.id) === String(selectedId)) || (state.crm.agreements || [])[0] || null;
}

function renderAgreementInstallments(agreement) {
  if (!agreement) return `<p class="empty">Selecciona un acuerdo para ver cuotas.</p>`;
  const rows = (agreement.installments || [])
    .map(
      (item) => `
        <tr>
          <td>${dateOnly(item.due_date)}</td>
          <td>${money(item.amount)}</td>
          <td>${money(item.paid_amount || 0)}</td>
          <td><span class="badge">${escapeHtml(item.status)}</span></td>
        </tr>
      `
    )
    .join("");
  return table(["Vence", "Cuota", "Pagado", "Estado"], rows, "Este acuerdo aun no tiene cuotas.", { key: `agreement-installments-${agreement.id}` });
}

function renderAgreements() {
  const container = document.querySelector("#agreementTable");
  if (!container) return;
  const agreements = state.crm.agreements || [];
  const active = agreements.filter((item) => ["active", "vigente", "al dia", "Acuerdo"].includes(item.status)).length;
  const totalAmount = agreements.reduce((sum, item) => sum + Number(item.total_amount || 0), 0);
  const installments = agreements.reduce((sum, item) => sum + Number(item.installment_count || 0), 0);
  document.querySelector("#agreementInsightCards") && (document.querySelector("#agreementInsightCards").innerHTML = [
    { label: "Acuerdos", value: agreements.length, detail: "Registros visibles por alcance.", tone: agreements.length ? "green" : "yellow" },
    { label: "Vigentes", value: active, detail: "Planes activos o en seguimiento.", tone: active ? "blue" : "neutral" },
    { label: "Monto acordado", value: money(totalAmount), detail: "Suma de acuerdos cargados.", tone: "purple" },
    { label: "Cuotas", value: installments, detail: "Plan de pagos comprometido.", tone: "green" },
  ].map(kpiCard).join(""));
  const rows = (state.crm.agreements || [])
    .map(
      (item) => `
        <tr>
          <td><strong>${escapeHtml(item.customer_name || "-")}</strong><small>${escapeHtml(item.obligation_number || "Cliente completo")}</small></td>
          <td>${money(item.total_amount)}</td>
          <td>${item.installment_count}</td>
          <td>${dateOnly(item.start_date)}</td>
          <td><span class="badge">${escapeHtml(item.status)}</span></td>
          <td>${agreementSummary(item)}</td>
          <td><button class="table-button" data-open-agreement="${item.id}" type="button">Cuotas</button></td>
        </tr>
      `
    )
    .join("");
  container.innerHTML = table(["Cliente", "Monto", "Cuotas", "Inicio", "Estado", "Avance", ""], rows, "No hay acuerdos registrados.");
  const detail = document.querySelector("#agreementInstallments");
  if (detail) detail.innerHTML = renderAgreementInstallments(selectedAgreement());
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
    { label: "Empresas", value: tenants.length, detail: "Clientes SaaS registrados por IEP.", tone: tenants.length ? "green" : "yellow", action: "Cada empresa conserva datos, usuarios y proyectos separados." },
    { label: "Activas", value: countBy(tenants, (tenant) => tenant.status === "active"), detail: "Empresas habilitadas para operar.", tone: "green", action: "Monitorear crecimiento y capacidad." },
    { label: "Proyectos", value: projects.length, detail: "Carteras operativas entre empresas.", tone: projects.length ? "green" : "yellow", action: "Crear proyectos antes de cargar repartos." },
    { label: "Clientes", value: sumBy(tenants, (tenant) => tenant.customer_count), detail: "Inventario de clientes cargados en tenants.", tone: "blue", action: "IEP permite auditar todo el ecosistema." },
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
    { label: "Usuarios tenant", value: users.length, detail: "Usuarios de empresas administrados por IEP.", tone: "blue", action: "El superusuario conserva control total." },
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
      ? [{ title: "Motor configurable", body: "Los superusuarios de IEP pueden parametrizar arboles sin tocar base de datos.", value: "Autogestion", action: "Siguiente paso: versionamiento y aprobacion de cambios.", tone: "green" }]
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
    { label: "Suscripciones", value: governance.subscriptions.length, detail: "Contratos visibles para IEP SuperAdmin.", tone: "blue" },
    { label: "Modulos activos", value: activeModules, detail: "Capacidades habilitadas en la empresa seleccionada.", tone: "yellow" },
    { label: "Eventos auditoria", value: governance.audit.length, detail: "Acciones recientes trazadas.", tone: "neutral" },
  ]);
  renderAlertSet("#governanceAlerts", [
    { title: "Gobierno separado", body: "El menu dinamico separa IEP, administracion de empresa y operacion final.", tone: "green" },
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
  const tenantField = isPlatform() && !isOperationalSupportMode() ? `<label>Tenant ID<input name="tenant_id" type="number" placeholder="Opcional para alcance global" /></label>` : "";
  const catalogRows = catalogs.slice(0, 20).map((item) => `<tr><td><strong>${escapeHtml(item.label)}</strong><small>${escapeHtml(item.code)}</small></td><td>${escapeHtml(item.module)}</td><td>${escapeHtml(item.catalog_type)}</td><td><span class="workflow-dot" style="background:${escapeHtml(item.color || "#94a3b8")}"></span>${item.is_active ? "Activo" : "Inactivo"}</td><td>${item.tenant_id ? "Tenant" : "Global"}</td><td><button class="table-button" data-config-edit="catalog" data-id="${item.id}" type="button">Editar</button></td></tr>`).join("");
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
  const ruleRows = rules.slice(0, 20).map((item) => `<tr><td><strong>${escapeHtml(item.name)}</strong><small>${escapeHtml(item.code)}</small></td><td>${escapeHtml(item.module)}</td><td>${escapeHtml(item.rule_type)}</td><td><span class="badge ${severityClass(item.severity)}">${escapeHtml(item.severity)}</span></td><td>${item.is_active ? "Activa" : "Inactiva"}</td><td><button class="table-button" data-config-edit="rule" data-id="${item.id}" type="button">Editar</button></td></tr>`).join("");
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
  const alertRows = alertRules.slice(0, 20).map((item) => `<tr><td><strong>${escapeHtml(item.name)}</strong><small>${escapeHtml(item.code)}</small></td><td>${escapeHtml(item.module)}</td><td>${escapeHtml(item.condition_type)}</td><td>${item.threshold_days} dias</td><td><span class="badge ${severityClass(item.severity)}">${escapeHtml(item.severity)}</span></td><td>${escapeHtml(item.target_role || "-")}</td><td><button class="table-button" data-config-edit="alert" data-id="${item.id}" type="button">Editar</button></td></tr>`).join("");
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
    { label: "Modulos", value: Object.keys(summary.by_module || {}).length, detail: "Cobertura transversal del motor.", tone: "blue", action: "Collects 360, juridico, ventas y administracion." },
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
    { label: "Collects 360", value: trees.filter((item) => item.module === "collections").length, detail: "Producto principal Collects 360.", tone: "green", action: "Estandarizar resultados por cartera." },
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
  const rows = recordings.slice(0, 20).map((item) => `<tr><td><strong>${escapeHtml(item.call_id)}</strong><small>${escapeHtml(item.phone_number || "-")}</small></td><td>${escapeHtml(item.direction)}</td><td>${Math.round((item.duration_seconds || 0) / 60)} min</td><td>${escapeHtml(item.provider_code || "-")}</td><td>${escapeHtml(item.status)}</td><td><button class="table-button" data-recording-detail="${item.id}" type="button">Detalle</button><button class="table-button" data-recording-playback="${item.id}" type="button">Playback</button><button class="table-button" data-recording-download="${item.id}" type="button">Descargar</button></td></tr>`).join("");
  document.querySelector("#recordingTable") && (document.querySelector("#recordingTable").innerHTML = `
    <div class="inline-filters">
      <label>Buscar<input id="recordingSearch" value="${escapeHtml(filters.text || "")}" placeholder="cliente, telefono, proveedor, estado" /></label>
      <button class="secondary-button" data-refresh-recordings type="button">Actualizar</button>
    </div>
    ${state.ops.recordingDetail ? `<article class="preview-panel"><header><strong>${escapeHtml(state.ops.recordingDetail.call_id)}</strong><span>${escapeHtml(state.ops.recordingDetail.status)}</span></header><p>${escapeHtml(state.ops.recordingDetail.phone_number || "-")} - ${Math.round((state.ops.recordingDetail.duration_seconds || 0) / 60)} min - ${escapeHtml(state.ops.recordingDetail.provider_code || "-")}</p></article>` : ""}
    ${table(["Llamada", "Direccion", "Duracion", "Proveedor", "Estado", ""], rows, "Sin grabaciones registradas para los filtros actuales.")}
  `);
}

function canManageTelephony() {
  return ["platform_admin", "company_admin"].includes(menuUser().audience) || ["platform_admin", "tenant_admin"].includes(currentUser?.role);
}

function renderTelephony() {
  const providers = state.ops.telephonyProviders || [];
  const extensions = state.ops.telephonyExtensions || [];
  const logs = state.ops.telephonyCallLogs || [];
  const myExtension = state.ops.myExtension;
  const activeProviders = providers.filter((item) => item.is_active);
  const activeExtensions = extensions.filter((item) => item.is_active);
  const primaryProvider = activeProviders.find((item) => item.is_primary || item.config?.is_primary);
  renderCardSet("#telephonyKpis", [
    { label: "Proveedores", value: providers.length, detail: "PBX, WebRTC SIP, API externa, troncal SIP o modo manual.", tone: providers.length ? "green" : "yellow", action: providers.length ? "Listos para parametrizacion." : "Configura un proveedor manual para comenzar." },
    { label: "Principal", value: primaryProvider?.name || "Pendiente", detail: primaryProvider ? "Proveedor activo para llamadas salientes." : "Define un proveedor principal por tenant.", tone: primaryProvider ? "green" : "yellow", action: primaryProvider ? `${primaryProvider.provider_type} · prioridad ${primaryProvider.priority || primaryProvider.config?.priority || "-"}` : "Marcar proveedor principal." },
    { label: "Extensiones", value: activeExtensions.length, detail: "Usuarios con extension activa.", tone: activeExtensions.length ? "green" : "yellow", action: "Asignar extension por usuario y tenant." },
    { label: "Llamadas", value: logs.length, detail: "Historial visible segun rol.", tone: logs.length ? "blue" : "yellow", action: "Click-to-call registra llamadas simuladas." },
    { label: "Modo", value: "Seguro", detail: "No se hacen llamadas reales sin TELEPHONY_REAL_CALLS_ENABLED=true.", tone: "blue", action: "Base lista para PBX/AMI/WebRTC." },
  ]);
  const mineHtml = myExtension
    ? `<article class="workspace-profile-card"><span>Extension</span><strong>${escapeHtml(myExtension.extension_number)}</strong><p>${escapeHtml(myExtension.display_name || myExtension.user_name || "Extension asignada")}</p><small>${escapeHtml(myExtension.status)} - ${escapeHtml(myExtension.provider_name || "Sin proveedor")}</small></article>`
    : `<article class="empty-state"><strong>Extension no configurada</strong><p>Solicita al administrador de tu empresa una extension activa para usar click-to-call desde la ficha del cliente.</p></article>`;
  document.querySelector("#myTelephonyPanel") && (document.querySelector("#myTelephonyPanel").innerHTML = mineHtml);

  const logRows = logs.slice(0, 30).map((item) => `<tr><td><strong>${escapeHtml(item.customer_name || "Cliente")}</strong><small>${escapeHtml(item.phone_number)}</small></td><td>${escapeHtml(item.user_name || "-")}</td><td>${escapeHtml(item.call_status)}</td><td>${escapeHtml(item.metadata?.mode || item.direction)}</td><td>${Math.round((item.duration_seconds || 0) / 60)} min</td><td>${dateOnly(item.started_at)}</td></tr>`).join("");
  document.querySelector("#telephonyCallLogTable") && (document.querySelector("#telephonyCallLogTable").innerHTML = table(["Cliente", "Usuario", "Estado", "Modo", "Duracion", "Inicio"], logRows, "Sin llamadas registradas para tu alcance."));

  const tenantSource = telephonyTenantSource();
  const userSource = state.crm.options.users?.length ? state.crm.options.users : (state.admin.users || []);
  const currentTenantSelection = document.querySelector('#telephonyProviderForm select[name="tenant_id"]')?.value
    || document.querySelector('#telephonyExtensionForm select[name="tenant_id"]')?.value
    || "";
  const selectedTenantId = defaultTelephonyTenantId(tenantSource, currentTenantSelection);
  const tenantOptions = telephonyTenantOptions(tenantSource, selectedTenantId);
  const tenantSelector = isPlatform()
    ? `<label>Empresa<select name="tenant_id" required ${tenantSource.length ? "" : "disabled"}><option value="">Selecciona empresa</option>${tenantOptions}</select><small class="field-hint">Tenant donde quedara configurado el proveedor.</small></label>`
    : "";
  const tenantEmptyMessage = isPlatform() && !tenantSource.length
    ? `<article class="empty-state compact"><strong>No hay empresas disponibles</strong><p>No hay empresas disponibles para configurar proveedores. Crea una empresa primero o valida el tenant actual.</p></article>`
    : "";
  const providerOptions = providers.map((item) => `<option value="${item.id}">${escapeHtml(item.name)} (${escapeHtml(item.provider_type)})</option>`).join("");
  const userOptions = userSource.map((item) => `<option value="${item.id}">${escapeHtml(item.name)} - ${escapeHtml(item.email || "")}</option>`).join("");
  const providerRows = providers.map((item) => {
    const config = item.config || {};
    const isPrimary = Boolean(item.is_primary || config.is_primary);
    const outboundEnabled = item.outbound_enabled !== false && config.outbound_enabled !== false;
    const priority = item.priority || config.priority || "-";
    const connection = [item.host, item.port].filter(Boolean).join(":") || item.websocket_url || item.api_url || "Manual/simulado";
    const dialing = [config.external_prefix, config.mobile_prepend, config.mobile_match_pattern].filter(Boolean).join(" + ") || "Sin regla";
    const warnings = [
      !item.is_active ? "Inactivo" : "",
      !outboundEnabled ? "Salida off" : "",
      item.provider_type !== "manual" && !item.host && !item.websocket_url && !item.api_url ? "Falta conexion" : "",
    ].filter(Boolean);
    return `<tr>
      <td><strong>${escapeHtml(item.name)}</strong><small>${isPrimary ? "Principal" : "Secundario"}</small></td>
      <td>${item.is_active ? '<span class="status-pill status-pill-ok">Activo</span>' : '<span class="status-pill status-pill-warn">Inactivo</span>'}</td>
      <td>${escapeHtml(item.provider_type)}</td>
      <td><strong>${escapeHtml(connection)}</strong><small>${escapeHtml(config.country_context || "Sin contexto")}</small></td>
      <td>${escapeHtml(priority)}</td>
      <td><strong>${escapeHtml(dialing)}</strong><small>${warnings.length ? escapeHtml(warnings.join(" - ")) : "Listo para simulacion segura"}</small></td>
      <td class="row-actions">
        ${canManageTelephony() ? `<button type="button" data-edit-telephony-provider="${item.id}">Editar</button><button type="button" data-toggle-telephony-provider="${item.id}">${item.is_active ? "Desactivar" : "Activar"}</button><button type="button" data-primary-telephony-provider="${item.id}" ${isPrimary && item.is_active ? "disabled" : ""}>Principal</button><button type="button" data-test-telephony-provider="${item.id}">Probar</button>` : ""}
      </td>
    </tr>`;
  }).join("");
  const extensionByUser = new Map(extensions.map((item) => [Number(item.user_id), item]));
  const extensionRows = (userSource.length ? userSource : extensions).map((item) => {
    const user = item.email ? item : null;
    const extension = user ? extensionByUser.get(Number(user.id)) : item;
    const userName = user ? user.name : extension.user_name;
    const userEmail = user ? user.email : "";
    return `<tr>
      <td><strong>${escapeHtml(userName || "-")}</strong><small>${escapeHtml(userEmail || "Usuario con extension")}</small></td>
      <td>${extension ? `<strong>${escapeHtml(extension.extension_number)}</strong><small>${escapeHtml(extension.display_name || "")}</small>` : `<span class="status-pill status-pill-warn">Sin extension</span>`}</td>
      <td>${escapeHtml(extension?.provider_name || "Manual/simulado")}</td>
      <td>${extension ? escapeHtml(extension.status) : "-"}</td>
      <td>${extension ? (extension.is_active ? "Activa" : "Inactiva") : "Pendiente"}</td>
      <td class="row-actions">
        ${canManageTelephony() && extension ? `<button type="button" data-edit-telephony-extension="${extension.id}">Editar</button><button type="button" data-toggle-telephony-extension="${extension.id}">${extension.is_active ? "Desactivar" : "Activar"}</button>` : ""}
        ${canManageTelephony() && !extension && user ? `<button type="button" data-new-telephony-extension="${user.id}">Crear</button>` : ""}
      </td>
    </tr>`;
  }).join("");
  document.querySelector("#telephonyProviderPanel") && (document.querySelector("#telephonyProviderPanel").innerHTML = `
    ${tenantEmptyMessage}
    ${canManageTelephony() ? `<form id="telephonyProviderForm" class="ops-form form-grid">
      <input type="hidden" name="provider_id" />
      ${tenantSelector}
      <label>Nombre<input name="name" required placeholder="IpCom" /></label>
      <label>Tipo<select name="provider_type"><option value="manual">Manual/simulado</option><option value="sip_trunk">SIP trunk</option><option value="asterisk_ami">Asterisk AMI</option><option value="pbx_ami">PBX AMI legacy</option><option value="pbx_ari">Asterisk ARI</option><option value="webrtc_sip">WebRTC SIP</option><option value="external_api">API externa</option></select></label>
      <label>Host<input name="host" placeholder="35.192.135.117" /></label>
      <label>Puerto<input name="port" type="number" min="1" max="65535" /></label>
      <label class="wide">WebSocket URL<input name="websocket_url" placeholder="wss://pbx.empresa/ws" /></label>
      <label class="wide">API URL<input name="api_url" placeholder="https://proveedor/api" /></label>
      <label>Troncal<input name="trunk_name" placeholder="IpCom" /></label>
      <label>DTMF<input name="dtmf_mode" placeholder="rfc2833" /></label>
      <label>NAT<input name="nat" placeholder="force_rport,comedia" /></label>
      <label>Codecs<input name="codecs" placeholder="ulaw,alaw,g729" /></label>
      <label>Prefijo externo<input name="external_prefix" placeholder="0218739#" /></label>
      <label>Prefijo movil<input name="mobile_prepend" placeholder="000157" /></label>
      <label>Patron movil<input name="mobile_match_pattern" placeholder="3XXXXXXXXX" /></label>
      <label>Contexto pais<input name="country_context" placeholder="Colombia" /></label>
      <label>Prioridad<input name="priority" type="number" min="1" max="100" value="1" /></label>
      <label class="checkbox-row"><input name="is_active" type="checkbox" checked /> Activo</label>
      <label class="checkbox-row"><input name="is_primary" type="checkbox" /> Principal saliente</label>
      <label class="checkbox-row"><input name="outbound_enabled" type="checkbox" checked /> Habilitar llamadas salientes</label>
      <label class="wide">Config JSON sin secretos<textarea name="config" placeholder='{"mode":"simulated"}'></textarea></label>
      <button type="submit" ${isPlatform() && !tenantSource.length ? "disabled" : ""}>Crear proveedor</button>
      <button class="secondary-button" data-ipcom-preset type="button">Preset IpCom</button>
      <button class="secondary-button" data-clear-telephony-provider type="button">Limpiar</button>
    </form>` : `<p class="empty">Solo administradores pueden configurar proveedores.</p>`}
    ${table(["Proveedor", "Estado", "Tipo", "Conexion", "Prioridad", "Marcado", "Acciones"], providerRows, "Sin proveedores configurados. Click-to-call puede operar en modo manual si existe extension.")}
  `);
  document.querySelector("#telephonyExtensionPanel") && (document.querySelector("#telephonyExtensionPanel").innerHTML = `
    ${canManageTelephony() ? `<form id="telephonyExtensionForm" class="ops-form form-grid">
      <input type="hidden" name="extension_id" />
      ${tenantSelector}
      <label>Usuario<select name="user_id" required>${userOptions}</select></label>
      <label>Proveedor<select name="provider_id"><option value="">Manual/sin proveedor</option>${providerOptions}</select></label>
      <label>Extension<input name="extension_number" required placeholder="1001" /></label>
      <label>Nombre visible<input name="display_name" placeholder="Gestor 1001" /></label>
      <label>SIP username<input name="sip_username" placeholder="1001" /></label>
      <label>Dominio SIP<input name="sip_domain" placeholder="pbx.empresa.local" /></label>
      <label>Estado<select name="status"><option value="not_connected">No conectado</option><option value="available">Disponible</option><option value="busy">Ocupado</option></select></label>
      <button type="submit">Asignar extension</button>
      <button type="button" data-clear-telephony-extension>Limpiar</button>
    </form>` : `<p class="empty">Tu administrador asigna las extensiones.</p>`}
    ${table(["Usuario", "Extension", "Proveedor", "Estado", "Activa", "Acciones"], extensionRows, "Sin usuarios disponibles para configurar extensiones.")}
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
  const uploadTypes = [
    ["clientes", "Clientes"],
    ["obligaciones", "Obligaciones"],
    ["reparto_cartera", "Reparto / cartera"],
    ["demograficos", "Demograficos"],
    ["telefonos_emails_direcciones", "Telefonos, emails y direcciones"],
    ["pagos", "PayControl 360"],
    ["novedades_operativas", "Novedades operativas"],
  ];
  const mappingRows = preview
    ? Object.entries(preview.suggested_mapping || {})
        .filter(([field]) => (preview.required_fields || []).includes(field) || (preview.optional_fields || []).includes(field))
        .slice(0, 20)
        .map(([field, source]) => `<tr><td>${escapeHtml(field)}</td><td>${escapeHtml(source)}</td><td>${(preview.required_fields || []).includes(field) ? '<span class="status-pill status-pill-warn">Requerido</span>' : '<span class="status-pill">Opcional</span>'}</td></tr>`)
        .join("")
    : "";
  const errorRows = preview
    ? (preview.errors || [])
        .slice(0, 20)
        .map((item) => `<tr><td>${item.row}</td><td>${escapeHtml(item.document || "-")}</td><td>${escapeHtml(item.message || (item.errors || []).join(", "))}</td></tr>`)
        .join("")
    : "";
  const previewPanel = preview ? `
    <article class="preview-panel">
      <header><strong>2. Preview y validaciones</strong><span>${preview.valid_rows}/${preview.total_rows} validas</span></header>
      <p>${escapeHtml(preview.summary?.message || (preview.error_rows ? `${preview.error_rows} filas requieren revision antes de confirmar.` : "Archivo validado sin errores criticos."))}</p>
      <div class="dashboard-grid">
        <article class="compact-card">
          <h3>Mapeo sugerido</h3>
          ${table(["Campo destino", "Columna archivo", "Tipo"], mappingRows, "No se detecto mapeo automatico. Ajusta el JSON de mapeo y vuelve a previsualizar.")}
        </article>
        <article class="compact-card">
          <h3>Errores detectados</h3>
          ${table(["Fila", "Documento", "Detalle"], errorRows, "Sin errores criticos en las primeras validaciones.")}
        </article>
      </div>
      <div class="inline-controls upload-actions">
        <button data-confirm-upload type="button">Confirmar carga</button>
        <button class="secondary-button" data-clear-upload-preview type="button">Descartar preview</button>
      </div>
      ${table(preview.columns || [], (preview.sample || []).map((row) => `<tr>${(preview.columns || []).map((column) => `<td>${escapeHtml(row[column] || "-")}</td>`).join("")}</tr>`).join(""), "Sin filas de muestra.")}
    </article>
  ` : `<article class="empty-state compact"><strong>2. Sin preview activo</strong><p>Selecciona un CSV y previsualiza antes de confirmar. El sistema valida columnas, tenant, proyecto, lider, gestor y errores por fila.</p></article>`;
  const batchRows = batches.map((item) => `<tr><td><strong>${escapeHtml(item.original_filename || `Lote ${item.id}`)}</strong><small>${escapeHtml(item.upload_type)}</small></td><td>${escapeHtml(item.status)}</td><td>${item.total_rows}</td><td>${item.valid_rows}</td><td>${item.error_rows}</td><td>${dateOnly(item.created_at)}</td><td><button class="table-button" data-upload-result="${item.id}" type="button">Resultado</button><button class="table-button" data-upload-errors="${item.id}" type="button">Errores</button></td></tr>`).join("");
  document.querySelector("#uploadBatchTable") && (document.querySelector("#uploadBatchTable").innerHTML = `
    <div class="upload-flow">
      <article><strong>1. Preparar archivo</strong><span>CSV con datos ficticios o reales del tenant.</span></article>
      <article><strong>2. Mapear columnas</strong><span>El sistema sugiere campos destino.</span></article>
      <article><strong>3. Validar y confirmar</strong><span>Solo roles autorizados procesan filas.</span></article>
      <article><strong>4. Auditar lote</strong><span>Descarga errores/resultados por lote.</span></article>
    </div>
    <form id="uploadPreviewForm" class="ops-form form-grid">
      <label>Tipo de carga<select name="upload_type">${uploadTypes.map(([value, label]) => `<option value="${value}">${label}</option>`).join("")}</select></label>
      <label>Proyecto<select name="project_id"><option value="">Sin proyecto</option>${projectOptions}</select></label>
      <label class="wide">Archivo CSV<input name="csv_file" type="file" accept=".csv,text/csv" required /></label>
      <label class="wide">Mapeo JSON opcional<textarea name="mapping" placeholder='{"document":"documento","name":"cliente","current_balance":"saldo_actual","assigned_user_email":"gestor_email"}'></textarea></label>
      <label class="checkbox-row"><input name="create_records" type="checkbox" checked /> Crear/actualizar registros al confirmar</label>
      <button type="submit">Previsualizar</button>
      <button class="secondary-button" data-upload-template type="button">Descargar plantilla</button>
    </form>
    ${previewPanel}
    <article class="preview-panel">
      <header><strong>4. Lotes auditables</strong><span>${batches.length} visibles</span></header>
      ${table(["Lote", "Estado", "Total", "Validas", "Errores", "Fecha", ""], batchRows, "Sin lotes de carga. Previsualiza y confirma el primer reparto.")}
    </article>
  `);
  const demographicRows = demographics.map((item) => `<tr><td><strong>Cliente #${item.customer_id}</strong><small>${escapeHtml(item.source)}</small></td><td>${escapeHtml(item.phone || "-")}</td><td>${escapeHtml(item.email || "-")}</td><td>${escapeHtml(item.city || "-")}</td><td>${escapeHtml(item.contactability || "Media")}</td><td>${item.priority || 0}</td><td>${item.score}</td><td>${escapeHtml(item.valid_until || "-")}</td></tr>`).join("");
  document.querySelector("#demographicTable") && (document.querySelector("#demographicTable").innerHTML = table(["Cliente", "Telefono", "Email", "Ciudad", "Contactabilidad", "Prioridad", "Score", "Vigente hasta"], demographicRows, "Sin demograficos cargados."));
}

const excelColumnLabels = {
  id: "ID",
  name: "Cliente",
  customer_name: "Cliente",
  document: "Documento",
  phone: "Telefono",
  email: "Email",
  city: "Ciudad",
  segment: "Cartera",
  portfolio_name: "Cartera",
  portfolio: "Cartera",
  obligation: "Obligacion",
  obligation_number: "Obligacion",
  product_type: "Producto",
  balance: "Saldo",
  original_amount: "Valor original",
  current_balance: "Saldo actual",
  amount: "Valor",
  total_amount: "Valor acuerdo",
  dpd: "Mora",
  days_past_due: "Mora",
  status: "Estado",
  risk: "Riesgo",
  assigned_user_id: "Gestor",
  assigned_leader_id: "Lider",
  user_id: "Usuario",
  channel: "Canal",
  result: "Resultado",
  note: "Nota",
  management_note: "Gestion",
  commitment: "Compromiso",
  created_at: "Creado",
  updated_at: "Actualizado",
  due_date: "Vence",
  paid_at: "Pago",
  date: "Fecha",
  next_action_at: "Proxima accion",
  method: "Metodo",
  reference: "Referencia"
};

function excelScopeText() {
  const audience = menuUser().audience;
  const profile = menuUser().profile_role || menuUser().role;
  if (audience === "platform_admin") return "Vista plataforma/tenant";
  if (audience === "company_admin") return "Vista empresa";
  if (audience === "operational_leader") return "Vista del equipo asignado";
  if (["collections_agent", "agent"].includes(profile)) return "Vista limitada a tu operacion";
  if (profile === "lawyer") return "Vista legal limitada a tus casos";
  if (profile === "sales_advisor") return "Vista comercial limitada a tus registros";
  return "Datos limitados segun tu rol y cartera asignada";
}

function excelColumnLabel(column) {
  return excelColumnLabels[column] || column.replaceAll("_", " ");
}

function excelMoneyColumn(column) {
  return ["balance", "original_amount", "current_balance", "amount", "total_amount", "paid_amount"].includes(column);
}

function excelDateColumn(column) {
  return column.endsWith("_at") || column.includes("date") || column === "date";
}

function excelCell(column, value) {
  if (value === null || value === undefined || value === "") return "-";
  if (excelMoneyColumn(column)) return money(value);
  if (excelDateColumn(column)) return dateOnly(value);
  return escapeHtml(value);
}

function excelRowClass(row) {
  const status = String(row.status || row.result || row.risk || "").toLowerCase();
  if (status.includes("cerr") || status.includes("cumpl") || status.includes("pago")) return "excel-row-ok";
  if (status.includes("venc") || status.includes("alto") || status.includes("escal")) return "excel-row-risk";
  if (status.includes("segu") || status.includes("prom")) return "excel-row-watch";
  return "";
}

function excelStatusSummaryHtml(rows) {
  const counts = {};
  (rows || []).forEach((row) => {
    const label = row.status || row.result || row.risk || "Sin estado";
    counts[label] = (counts[label] || 0) + 1;
  });
  const entries = Object.entries(counts).sort((a, b) => b[1] - a[1]).slice(0, 8);
  if (!entries.length) return `<p class="empty">Cuando consultes informacion o registres seguimiento, aqui veras el resumen por estado.</p>`;
  const max = Math.max(...entries.map(([, count]) => count), 1);
  return `<div class="excel-status-bars">${entries.map(([label, count]) => `
    <div class="excel-status-row">
      <span>${escapeHtml(label)}</span>
      <div><i style="width:${Math.max(8, Math.round((count / max) * 100))}%"></i></div>
      <strong>${count}</strong>
    </div>
  `).join("")}</div>`;
}

function sheetStatusOptionsHtml(selected = "Pendiente") {
  return ["Pendiente", "Seguimiento", "Gestionado", "Pagos", "Cerrado"]
    .map((item) => `<option value="${item}" ${String(selected) === item ? "selected" : ""}>${item}</option>`)
    .join("");
}

function sheetStatusStats(rows) {
  const statuses = ["Pendiente", "Seguimiento", "Gestionado", "Pagos", "Cerrado"];
  return statuses.map((status) => ({
    status,
    count: countBy(rows, (row) => String(row.status || "").toLowerCase() === status.toLowerCase()),
    value: sumBy(rows.filter((row) => String(row.status || "").toLowerCase() === status.toLowerCase()), (row) => row.amount || 0),
  }));
}

function excelSheetFilterPayloadFromForm(form) {
  return {
    q: form.elements.q.value || "",
    project_id: optionalNumber(form.elements.project_id.value),
    status: form.elements.status.value || "",
    user_id: optionalNumber(form.elements.user_id?.value || ""),
    date_from: form.elements.date_from.value || "",
    date_to: form.elements.date_to.value || "",
  };
}

const SHEET_STATUSES = ["Pendiente", "Seguimiento", "Gestionado", "Pagos", "Cerrado"];
const SHEET_EDITABLE_FIELDS = ["date", "project_id", "customer_name", "document", "obligation_number", "management_note", "commitment", "amount", "status", "next_action_at"];

function sheetFieldValue(row, field) {
  const changes = state.ops.excelSheetChanges?.[row.id] || {};
  if (Object.prototype.hasOwnProperty.call(changes, field)) return changes[field];
  if (field === "date" || field === "next_action_at") return dateOnly(row[field]);
  return row[field] ?? "";
}

function sheetNewValue(field) {
  return state.ops.excelSheetNewRow?.[field] ?? (field === "status" ? "Pendiente" : "");
}

function sheetCellClass(rowId, field, extra = "") {
  const isNew = rowId === "new";
  const changed = isNew
    ? Object.prototype.hasOwnProperty.call(state.ops.excelSheetNewRow || {}, field)
    : Object.prototype.hasOwnProperty.call(state.ops.excelSheetChanges?.[rowId] || {}, field);
  const active = state.ops.excelSheetActiveCell === `${rowId}:${field}`;
  return ["sheet-cell", "sheet-editable-cell", changed ? "sheet-cell-dirty" : "", active ? "sheet-cell-active" : "", extra].filter(Boolean).join(" ");
}

function sheetProjectOptionsHtml(selected = "") {
  const projects = state.crm.options.projects || [];
  if (!projects.length) return "";
  return `<option value="">Sin proyecto</option>${projects.map((item) => `<option value="${item.id}" ${String(selected || "") === String(item.id) ? "selected" : ""}>${escapeHtml(item.label || item.name || `Proyecto ${item.id}`)}</option>`).join("")}`;
}

function renderSheetEditor(rowId, field, value, options = {}) {
  const attr = rowId === "new" ? "data-new-sheet-cell" : "data-sheet-cell";
  const rowAttr = rowId === "new" ? "" : ` data-row-id="${rowId}"`;
  const common = `${attr}="${field}"${rowAttr} data-field="${field}" aria-label="${escapeHtml(options.label || field)}"`;
  if (field === "status") {
    return `<select ${common}>${sheetStatusOptionsHtml(value || "Pendiente")}</select>`;
  }
  if (field === "project_id") {
    const projectOptions = sheetProjectOptionsHtml(value);
    if (projectOptions) return `<select ${common}>${projectOptions}</select>`;
    return `<input ${common} type="text" value="${escapeHtml(options.portfolio || "")}" placeholder="Cartera/proyecto" />`;
  }
  if (["management_note", "commitment"].includes(field)) {
    return `<textarea ${common} placeholder="${escapeHtml(options.placeholder || "")}">${escapeHtml(value || "")}</textarea>`;
  }
  const type = field === "amount" ? "number" : ["date", "next_action_at"].includes(field) ? "date" : "text";
  return `<input ${common} type="${type}" value="${escapeHtml(value || "")}" placeholder="${escapeHtml(options.placeholder || "")}" />`;
}

function renderSheetCell(row, field, options = {}) {
  const value = sheetFieldValue(row, field);
  const displayValue = field === "project_id" ? value || row.project_id || "" : value;
  return `<td class="${sheetCellClass(row.id, field, options.className || "")}">${renderSheetEditor(row.id, field, displayValue, { ...options, portfolio: row.portfolio })}</td>`;
}

function renderNewSheetCell(field, options = {}) {
  return `<td class="${sheetCellClass("new", field, options.className || "")}">${renderSheetEditor("new", field, sheetNewValue(field), options)}</td>`;
}

function hasSheetRowChanges(rowId) {
  return Object.keys(state.ops.excelSheetChanges?.[rowId] || {}).length > 0;
}

function hasSheetNewRowData() {
  return Object.entries(state.ops.excelSheetNewRow || {}).some(([key, value]) => key !== "status" && String(value ?? "").trim() !== "");
}

function hasExcelSheetUnsavedChanges() {
  return Object.keys(state.ops.excelSheetChanges || {}).length > 0 || hasSheetNewRowData();
}

function renderSheetNewRow() {
  const dirty = hasSheetNewRowData();
  return `
    <tr class="sheet-new-row ${dirty ? "sheet-row-dirty" : ""}" data-excel-sheet-new-row>
      <td><strong>Nueva fila</strong><small>Escribe directo</small></td>
      <td><span class="muted">Tu usuario</span></td>
      ${renderNewSheetCell("date", { label: "Fecha" })}
      ${renderNewSheetCell("project_id", { label: "Cartera / proyecto" })}
      ${renderNewSheetCell("customer_name", { label: "Cliente", placeholder: "Cliente" })}
      ${renderNewSheetCell("document", { label: "Documento", placeholder: "Documento" })}
      ${renderNewSheetCell("obligation_number", { label: "Obligacion", placeholder: "Obligacion" })}
      ${renderNewSheetCell("management_note", { label: "Gestion / Nota", placeholder: "Gestion realizada o pendiente" })}
      ${renderNewSheetCell("commitment", { label: "Compromiso", placeholder: "Compromiso o siguiente paso" })}
      ${renderNewSheetCell("amount", { label: "Valor" })}
      ${renderNewSheetCell("status", { label: "Estado" })}
      ${renderNewSheetCell("next_action_at", { label: "Proxima accion" })}
      <td><span class="sheet-state ${dirty ? "sheet-state-pending" : ""}">${dirty ? "Sin guardar" : "Lista"}</span></td>
    </tr>
  `;
}

function renderSheetRow(row) {
  const dirty = hasSheetRowChanges(row.id);
  return `
    <tr class="${excelRowClass(row)} ${dirty ? "sheet-row-dirty" : ""}" data-excel-sheet-row="${row.id}">
      <td><strong>${row.id}</strong><small>${dirty ? "Sin guardar" : "Guardado"}</small></td>
      <td>${escapeHtml(row.user_name || `Usuario ${row.user_id}`)}</td>
      ${renderSheetCell(row, "date", { label: "Fecha" })}
      ${renderSheetCell(row, "project_id", { label: "Cartera / proyecto" })}
      ${renderSheetCell(row, "customer_name", { label: "Cliente" })}
      ${renderSheetCell(row, "document", { label: "Documento" })}
      ${renderSheetCell(row, "obligation_number", { label: "Obligacion" })}
      ${renderSheetCell(row, "management_note", { label: "Gestion / Nota" })}
      ${renderSheetCell(row, "commitment", { label: "Compromiso" })}
      ${renderSheetCell(row, "amount", { label: "Valor" })}
      ${renderSheetCell(row, "status", { label: "Estado" })}
      ${renderSheetCell(row, "next_action_at", { label: "Proxima accion" })}
      <td><span class="sheet-state ${dirty ? "sheet-state-pending" : ""}">${dirty ? "Sin guardar" : "Guardado"}</span></td>
    </tr>
  `;
}

function renderExcelWeb() {
  const sources = state.ops.excelSources || [];
  const views = state.ops.excelViews || [];
  const result = state.ops.excelResult;
  const sheetResponse = state.ops.excelSheetRows || { items: [], page: 1, total_pages: 0, total: 0, statuses: [] };
  const sheetRows = sheetResponse.items || [];
  const sheetFilters = state.ops.excelSheetFilters || {};
  const selectedSource = state.ops.excelDraft?.source || result?.source || sources[0]?.code || "customers";
  const source = sources.find((item) => item.code === selectedSource) || sources[0] || { code: selectedSource, columns: [] };
  const selectedColumns = state.ops.excelDraft?.columns?.length ? state.ops.excelDraft.columns : (result?.columns || source.columns || []).slice(0, 8);
  const activeFilters = state.ops.excelDraft?.filters || {};
  const projectOptions = optionList(state.crm.options.projects || [], "id", "label", activeFilters.project_id || "");
  const userOptions = optionList(state.crm.options.users || [], "id", "label", activeFilters.assigned_user_id || activeFilters.user_id || "");
  const canChooseUser = ["platform_admin", "company_admin", "operational_leader"].includes(menuUser().audience);
  const sourceOptions = sources.length
    ? sources.map((item) => `<option value="${escapeHtml(item.code)}" ${item.code === selectedSource ? "selected" : ""}>${escapeHtml(item.label)}</option>`).join("")
    : `<option value="customers">Clientes</option>`;
  const columnChecks = (source.columns || []).map((column) => `
    <label class="checkbox-chip">
      <input name="columns" type="checkbox" value="${escapeHtml(column)}" ${selectedColumns.includes(column) ? "checked" : ""} />
      <span>${escapeHtml(excelColumnLabel(column))}</span>
    </label>
  `).join("");
  const resultRows = (result?.rows || []).map((row) => `<tr class="${excelRowClass(row)}">${(result.columns || selectedColumns).map((column) => `<td>${excelCell(column, row[column])}</td>`).join("")}</tr>`).join("");
  const sheetTableRows = `${renderSheetNewRow()}${sheetRows.map(renderSheetRow).join("")}`;
  const statusRows = [...(result?.rows || []), ...sheetRows];
  const valueTotal = sumBy(result?.rows || [], (row) => row.current_balance || row.balance || row.amount || row.total_amount || 0);
  const sheetValueTotal = sumBy(sheetRows, (row) => row.amount || 0);
  const pendingCount = countBy(sheetRows, (row) => String(row.status).toLowerCase().includes("pend"));
  const followCount = countBy(sheetRows, (row) => String(row.status).toLowerCase().includes("segu"));
  const doneCount = countBy(sheetRows, (row) => ["gestionado", "pagos", "cerrado"].includes(String(row.status).toLowerCase()));
  const sheetFilterProjectOptions = optionList(state.crm.options.projects || [], "id", "label", sheetFilters.project_id || "");
  const sheetFilterUserOptions = optionList(state.crm.options.users || [], "id", "label", sheetFilters.user_id || "");
  const changedRowsCount = Object.keys(state.ops.excelSheetChanges || {}).length;
  const hasNewRow = hasSheetNewRowData();
  const unsavedCount = changedRowsCount + (hasNewRow ? 1 : 0);
  const sheetStatusCards = sheetStatusStats(sheetRows).map((item) => `
    <article class="excel-status-card">
      <span>${escapeHtml(item.status)}</span>
      <strong>${item.count}</strong>
      <small>${money(item.value)}</small>
    </article>
  `).join("");
  document.querySelector("#excelScopeNote") && (document.querySelector("#excelScopeNote").innerHTML = `
    <strong>${escapeHtml(excelScopeText())}</strong>
    <span>Datos limitados segun tu rol, tenant, modulos activos y permisos.</span>
  `);
  renderCardSet("#excelWebKpis", [
    { label: "Registros consulta", value: result?.total || 0, detail: source.label || "Fuente operativa", tone: result?.total ? "green" : "yellow", action: "Maximo 20 visibles por pagina." },
    { label: "Valor pagina", value: money(valueTotal), detail: "Suma de saldos o valores visibles.", tone: valueTotal ? "blue" : "yellow", action: "Filtro seguro por alcance." },
    { label: "Seguimientos", value: sheetResponse.total || 0, detail: `${pendingCount} pendientes · ${followCount} en seguimiento`, tone: sheetResponse.total ? "green" : "yellow", action: "Filas guardadas en base de datos." },
    { label: "Valor hoja", value: money(sheetValueTotal), detail: `${doneCount} filas gestionadas.`, tone: sheetValueTotal ? "blue" : "yellow", action: "Seguimiento financiero visible." },
  ]);
  document.querySelector("#excelStatusSummary") && (document.querySelector("#excelStatusSummary").innerHTML = excelStatusSummaryHtml(statusRows));
  const sourceRows = sources.map((item) => `<tr><td><strong>${escapeHtml(item.label)}</strong><small>${escapeHtml(item.code)}</small></td><td>${(item.columns || []).length}</td><td>${escapeHtml((item.columns || []).slice(0, 6).join(", "))}</td><td><button class="table-button" data-excel-source="${escapeHtml(item.code)}" type="button">Usar</button></td></tr>`).join("");
  document.querySelector("#excelSourceTable") && (document.querySelector("#excelSourceTable").innerHTML = table(["Fuente", "Columnas", "Ejemplo", ""], sourceRows, "Sin fuentes configuradas.", { key: "excel-sources" }));
  const viewRows = views.map((item) => `<tr><td><strong>${escapeHtml(item.name)}</strong><small>${escapeHtml(item.source)}</small></td><td>${item.is_public ? "Publica" : "Privada"}</td><td>${item.is_favorite ? "Favorita" : "-"}</td><td>${dateOnly(item.updated_at)}</td><td><button class="table-button" data-excel-view="${item.id}" type="button">Cargar</button></td></tr>`).join("");
  document.querySelector("#excelViewTable") && (document.querySelector("#excelViewTable").innerHTML = `
    <form id="excelViewForm" class="ops-form form-grid">
      <label>Nombre vista<input name="name" placeholder="Mi vista de cartera" required /></label>
      <label class="checkbox-row"><input name="is_public" type="checkbox" /> Publica para tenant</label>
      <label class="checkbox-row"><input name="is_favorite" type="checkbox" checked /> Favorita</label>
      <button type="submit">Guardar vista</button>
    </form>
    ${table(["Vista", "Alcance", "Favorita", "Actualizada", ""], viewRows, "Sin vistas guardadas. Filtra tu cartera y guarda la vista para reutilizarla.", { key: "excel-views" })}
  `);
  document.querySelector("#excelResultTable") && (document.querySelector("#excelResultTable").innerHTML = `
    <form id="excelQueryForm" class="ops-form form-grid excel-filter-form">
      <label>Selecciona una fuente de informacion<select name="source">${sourceOptions}</select></label>
      <label>Buscar<input name="q" placeholder="cliente, cedula, obligacion, nota, estado" value="${escapeHtml(activeFilters.text || activeFilters.q || "")}" /></label>
      <label>Cartera / proyecto<select name="project_id"><option value="">Todos</option>${projectOptions}</select></label>
      <label>Estado<input name="status" placeholder="Pendiente, Promesa, Activo..." value="${escapeHtml(activeFilters.status || "")}" /></label>
      <label>Riesgo<select name="risk"><option value="">Todos</option><option value="Alto" ${activeFilters.risk === "Alto" ? "selected" : ""}>Alto</option><option value="Medio" ${activeFilters.risk === "Medio" ? "selected" : ""}>Medio</option><option value="Bajo" ${activeFilters.risk === "Bajo" ? "selected" : ""}>Bajo</option></select></label>
      ${canChooseUser ? `<label>Usuario / gestor<select name="assigned_user_id"><option value="">Todos</option>${userOptions}</select></label>` : `<input name="assigned_user_id" type="hidden" value="" />`}
      <label>Mora minima<input name="dpd_min" type="number" min="0" value="${escapeHtml(activeFilters.dpd_min ?? "")}" /></label>
      <label>Mora maxima<input name="dpd_max" type="number" min="0" value="${escapeHtml(activeFilters.dpd_max ?? "")}" /></label>
      <label>Fecha desde<input name="date_from" type="date" value="${escapeHtml(activeFilters.date_from || "")}" /></label>
      <label>Fecha hasta<input name="date_to" type="date" value="${escapeHtml(activeFilters.date_to || "")}" /></label>
      <input name="page" type="hidden" value="${result?.page || 1}" />
      <input name="page_size" type="hidden" value="${DEFAULT_TABLE_PAGE_SIZE}" />
      <label class="wide">Elige las columnas que quieres ver<div class="checkbox-grid">${columnChecks || "<p class='empty'>Selecciona una fuente para ver columnas.</p>"}</div></label>
      <button type="submit">Filtrar</button>
      <button class="secondary-button" data-excel-clear type="button">Limpiar</button>
      ${canExportExcelWeb() ? `<button class="secondary-button" data-excel-export type="button">Exportar</button>` : `<p class="form-note">Exportacion no disponible para gestores. La consulta queda limitada a tu operacion.</p>`}
    </form>
    <div class="excel-query-head">
      <p class="form-note">${result ? `${result.total} registros · pagina ${result.page} de ${Math.max(result.total_pages || 1, 1)} · ${DEFAULT_TABLE_PAGE_SIZE} por pagina` : "Selecciona una fuente de informacion y filtra tu cartera."}</p>
      <div class="pager">
        <button data-excel-page="${(result?.page || 1) - 1}" type="button" ${!result || result.page <= 1 ? "disabled" : ""}>Anterior</button>
        <button data-excel-page="${(result?.page || 1) + 1}" type="button" ${!result || result.page >= (result.total_pages || 1) ? "disabled" : ""}>Siguiente</button>
      </div>
    </div>
    <div class="table-wrap excel-table-wrap">${table((result?.columns || selectedColumns).map(excelColumnLabel), resultRows, "Aun no hay informacion disponible para esta consulta operativa.", { key: "excel-result", pageSize: DEFAULT_TABLE_PAGE_SIZE })}</div>
  `);
  document.querySelector("#excelSheetPanel") && (document.querySelector("#excelSheetPanel").innerHTML = `
    <form id="excelSheetFilterForm" class="ops-form form-grid excel-filter-form">
      <label>Buscar<input name="q" placeholder="cliente, cedula, obligacion, nota o estado" value="${escapeHtml(sheetFilters.q || "")}" /></label>
      <label>Cartera / proyecto<select name="project_id"><option value="">Todos</option>${sheetFilterProjectOptions}</select></label>
      <label>Estado<select name="status"><option value="">Todos</option>${sheetStatusOptionsHtml(sheetFilters.status || "")}</select></label>
      ${canChooseUser ? `<label>Usuario / gestor<select name="user_id"><option value="">Todos</option>${sheetFilterUserOptions}</select></label>` : `<input name="user_id" type="hidden" value="" />`}
      <label>Fecha desde<input name="date_from" type="date" value="${escapeHtml(sheetFilters.date_from || "")}" /></label>
      <label>Fecha hasta<input name="date_to" type="date" value="${escapeHtml(sheetFilters.date_to || "")}" /></label>
      <button type="submit">Filtrar hoja</button>
      <button class="secondary-button" data-excel-sheet-clear type="button">Limpiar</button>
    </form>
    <div class="excel-status-card-grid">${sheetStatusCards}</div>
    <div class="sheet-edit-toolbar">
      <div>
        <strong>Hoja editable</strong>
        <span>${unsavedCount ? `${unsavedCount} fila(s) con cambios sin guardar` : "Sin cambios pendientes"}</span>
      </div>
      <div class="sheet-edit-actions">
        <button data-excel-sheet-save-all type="button" ${!unsavedCount ? "disabled" : ""}>Guardar cambios</button>
        <button class="secondary-button" data-excel-sheet-cancel-all type="button" ${!unsavedCount ? "disabled" : ""}>Cancelar cambios</button>
      </div>
    </div>
    <div class="excel-query-head">
      <p class="form-note">Mi hoja de seguimiento · ${sheetResponse.total || 0} filas guardadas · pagina ${sheetResponse.page || 1} de ${Math.max(sheetResponse.total_pages || 1, 1)}</p>
      <div class="pager">
        <button data-excel-sheet-page="${(sheetResponse.page || 1) - 1}" type="button" ${!sheetResponse.total || sheetResponse.page <= 1 ? "disabled" : ""}>Anterior</button>
        <button data-excel-sheet-page="${(sheetResponse.page || 1) + 1}" type="button" ${!sheetResponse.total || sheetResponse.page >= (sheetResponse.total_pages || 1) ? "disabled" : ""}>Siguiente</button>
      </div>
    </div>
    <div class="table-wrap excel-table-wrap excel-operational-table">${table(["ID", "Usuario", "Fecha", "Cartera", "Cliente", "Documento", "Obligacion", "Gestion", "Compromiso", "Valor", "Estado", "Proxima accion", "Estado fila"], sheetTableRows, "Agrega tu primera fila de seguimiento para trabajar tu cartera como una hoja operativa.", { key: "excel-sheet", noClientPager: true })}</div>
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
  const tenantField = isPlatform() && !isOperationalSupportMode() ? `<label>Tenant ID<input name="tenant_id" type="number" placeholder="Tenant destino" /></label>` : "";
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
  const eventRows = events.slice(0, 20).map((item) => `<tr><td><strong>${escapeHtml(item.event_type)}</strong><small>${escapeHtml(item.channel_type)}</small></td><td>${escapeHtml(item.status)}</td><td>${escapeHtml(item.entity_type || "-")}</td><td>${dateOnly(item.created_at)}</td></tr>`).join("");
  document.querySelector("#integrationEventTable") && (document.querySelector("#integrationEventTable").innerHTML = table(["Evento", "Estado", "Entidad", "Fecha"], eventRows, "Sin eventos de canal."));
}

function teamRoleLabel(value) {
  const labels = {
    leader: "Lider",
    agent: "Agente",
    quality: "Calidad",
    lawyer: "Abogado",
    sales: "Comercial",
    auditor: "Auditor"
  };
  return labels[value] || value || "-";
}

function uniqueUsersForTeams() {
  const map = new Map();
  [...(state.teams.leaders || []), ...(state.teams.agents || [])].forEach((item) => {
    if (!map.has(item.id)) map.set(item.id, item);
  });
  return Array.from(map.values()).sort((a, b) => String(a.name).localeCompare(String(b.name)));
}

function renderTeams() {
  if (!document.querySelector("#teams")) return;
  const projects = state.teams.projects || [];
  const leaders = state.teams.leaders || [];
  const agents = state.teams.agents || [];
  const selectedProjectId = state.teams.selectedProjectId || projects[0]?.id || "";
  const selectedLeaderId = state.teams.selectedLeaderId || leaders[0]?.id || "";
  const userOptions = optionList(uniqueUsersForTeams());
  const leaderOptions = optionList(leaders);
  const agentOptions = optionList(agents);
  const projectOptions = optionList(projects);
  const projectRows = projects
    .map(
      (project) => `
        <tr class="${String(project.id) === String(selectedProjectId) ? "selected-row" : ""}">
          <td><strong>${escapeHtml(project.name)}</strong><small>${escapeHtml(project.code)}</small></td>
          <td>${escapeHtml(project.status)}</td>
          <td>${project.leader_count}</td>
          <td>${project.agent_count}</td>
          <td>${project.customer_count}</td>
          <td>${project.obligation_count}</td>
          <td>${money(project.balance_total)}</td>
          <td><button class="table-button" data-team-project="${project.id}" type="button">Ver usuarios</button></td>
        </tr>
      `
    )
    .join("");
  document.querySelector("#teamProjectTable").innerHTML = table(["Cartera", "Estado", "Lideres", "Agentes", "Clientes", "Obligaciones", "Saldo", ""], projectRows, "No hay carteras disponibles para tu alcance.", { key: "teams-projects", pageSize: DEFAULT_TABLE_PAGE_SIZE });

  const assignmentRows = (state.teams.projectUsers || [])
    .map(
      (assignment) => `
        <tr>
          <td><strong>${escapeHtml(assignment.user_name || "-")}</strong><small>${escapeHtml(assignment.user_email || "")}</small></td>
          <td>${escapeHtml(teamRoleLabel(assignment.role_in_project))}</td>
          <td>${escapeHtml(roleLabel(assignment.profile_role || assignment.user_role))}</td>
          <td><span class="status-pill ${assignment.is_active ? "status-pill-ok" : "status-pill-warn"}">${assignment.is_active ? "Activo" : "Inactivo"}</span></td>
          <td>${dateOnly(assignment.created_at)}</td>
          <td>
            <button class="table-button" data-toggle-project-user="${assignment.id}" data-active="${assignment.is_active}" type="button">${assignment.is_active ? "Desactivar" : "Activar"}</button>
          </td>
        </tr>
      `
    )
    .join("");
  document.querySelector("#teamProjectUsers").innerHTML = table(["Usuario", "Rol cartera", "Perfil", "Estado", "Asignado", ""], assignmentRows, "Selecciona una cartera o asigna usuarios para ver el equipo.", { key: "teams-project-users", pageSize: DEFAULT_TABLE_PAGE_SIZE });

  const summary = state.teams.leaderSummary;
  document.querySelector("#teamLeaderSummary").innerHTML = summary
    ? `
      <div class="metrics-grid compact-metrics">
        <article class="metric-card"><span>Agentes</span><strong>${summary.total_agents}</strong></article>
        <article class="metric-card"><span>Clientes equipo</span><strong>${summary.customers}</strong></article>
        <article class="metric-card"><span>Obligaciones</span><strong>${summary.obligations}</strong></article>
        <article class="metric-card"><span>Saldo equipo</span><strong>${money(summary.balance_total)}</strong></article>
        <article class="metric-card"><span>Gestiones hoy</span><strong>${summary.activities_today}</strong></article>
        <article class="metric-card"><span>Promesas vigentes</span><strong>${summary.active_promises}</strong></article>
        <article class="metric-card"><span>Promesas vencidas</span><strong>${summary.overdue_promises}</strong></article>
        <article class="metric-card"><span>Pagos mes</span><strong>${money(summary.payments_month)}</strong></article>
      </div>
    `
    : `<p class="empty">Selecciona un lider para ver indicadores del equipo.</p>`;
  const leaderAgentRows = (state.teams.leaderAgents || [])
    .map((agent) => `<tr><td><strong>${escapeHtml(agent.name)}</strong><small>${escapeHtml(agent.email)}</small></td><td>${escapeHtml(roleLabel(agent.profile_role || agent.role))}</td><td>${escapeHtml(agent.project_names?.join(", ") || "-")}</td><td>${escapeHtml(agent.status)}</td></tr>`)
    .join("");
  document.querySelector("#teamLeaderAgents").innerHTML = table(["Agente", "Perfil", "Carteras", "Estado"], leaderAgentRows, "Este lider no tiene agentes activos asignados.", { key: "teams-leader-agents", pageSize: DEFAULT_TABLE_PAGE_SIZE });
  const rankingRows = (summary?.ranking || [])
    .map((row) => `<tr><td><strong>${escapeHtml(row.name)}</strong></td><td>${row.customers}</td><td>${row.activities_today}</td><td>${money(row.payments_month)}</td></tr>`)
    .join("");
  document.querySelector("#teamRanking").innerHTML = table(["Agente", "Clientes", "Gestiones hoy", "Pagos mes"], rankingRows, "Sin ranking disponible para este equipo.", { key: "teams-ranking", pageSize: DEFAULT_TABLE_PAGE_SIZE });

  const projectForm = document.querySelector("#projectUserAssignForm");
  if (projectForm) {
    projectForm.elements.project_id.innerHTML = `<option value="">Selecciona cartera</option>${projectOptions}`;
    projectForm.elements.user_id.innerHTML = `<option value="">Selecciona usuario</option>${userOptions}`;
    if (selectedProjectId) projectForm.elements.project_id.value = selectedProjectId;
  }
  const leaderForm = document.querySelector("#leaderAgentAssignForm");
  if (leaderForm) {
    leaderForm.elements.leader_id.innerHTML = `<option value="">Selecciona lider</option>${leaderOptions}`;
    leaderForm.elements.agent_user_id.innerHTML = `<option value="">Selecciona agente</option>${agentOptions}`;
    leaderForm.elements.project_id.innerHTML = `<option value="">Sin cartera especifica</option>${projectOptions}`;
    if (selectedLeaderId) leaderForm.elements.leader_id.value = selectedLeaderId;
  }
}

async function handleProjectUserAssignment(form) {
  const projectId = Number(form.elements.project_id.value);
  if (!projectId || !form.elements.user_id.value) {
    showToast("warning", "Selecciona cartera y usuario para asignar.");
    return;
  }
  await runAction(form.querySelector("button[type='submit']"), async () => {
    await api(`/api/teams/projects/${projectId}/users`, {
      method: "POST",
      body: JSON.stringify({
        user_id: Number(form.elements.user_id.value),
        role_in_project: form.elements.role_in_project.value,
        is_active: true
      })
    });
    state.teams.selectedProjectId = projectId;
    await loadTeamsData();
    renderTeams();
    showToast("success", "Usuario asignado a la cartera.");
  }, "Asignando...");
}

async function handleLeaderAgentAssignment(form) {
  const leaderId = Number(form.elements.leader_id.value);
  if (!leaderId || !form.elements.agent_user_id.value) {
    showToast("warning", "Selecciona lider y agente.");
    return;
  }
  await runAction(form.querySelector("button[type='submit']"), async () => {
    await api(`/api/teams/leaders/${leaderId}/agents`, {
      method: "POST",
      body: JSON.stringify({
        agent_user_id: Number(form.elements.agent_user_id.value),
        project_id: optionalNumber(form.elements.project_id.value)
      })
    });
    state.teams.selectedLeaderId = leaderId;
    await loadTeamsData();
    renderTeams();
    showToast("success", "Agente asociado al lider.");
  }, "Asociando...");
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
  renderAgreements();
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
  renderTelephony();
  renderUploads();
  renderExcelWeb();
  renderIntegrations();
  renderTeams();
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

function telephonyProviderConfigFromForm(form) {
  const config = parseJsonField(form.elements.config.value, {});
  const fieldNames = ["trunk_name", "dtmf_mode", "nat", "codecs", "external_prefix", "mobile_prepend", "mobile_match_pattern", "country_context"];
  fieldNames.forEach((field) => {
    const value = form.elements[field]?.value;
    if (value) config[field] = value;
  });
  config.outbound_enabled = Boolean(form.elements.outbound_enabled?.checked);
  config.is_primary = Boolean(form.elements.is_primary?.checked);
  if (form.elements.priority?.value) config.priority = Number(form.elements.priority.value);
  return config;
}

async function handleTelephonyProviderSubmit(form) {
  const providerId = form.elements.provider_id?.value;
  if (isPlatform() && !form.elements.tenant_id?.value) {
    showToast("warning", "Selecciona una empresa para configurar el proveedor.");
    form.elements.tenant_id?.focus();
    return;
  }
  await submitJson(form, providerId ? `/api/telephony/providers/${providerId}` : "/api/telephony/providers", (currentForm) => ({
    tenant_id: currentForm.elements.tenant_id?.value ? Number(currentForm.elements.tenant_id.value) : null,
    name: currentForm.elements.name.value,
    provider_type: currentForm.elements.provider_type.value,
    host: currentForm.elements.host.value || null,
    port: currentForm.elements.port.value ? Number(currentForm.elements.port.value) : null,
    websocket_url: currentForm.elements.websocket_url.value || null,
    api_url: currentForm.elements.api_url.value || null,
    is_active: Boolean(currentForm.elements.is_active?.checked),
    is_primary: Boolean(currentForm.elements.is_primary?.checked),
    outbound_enabled: Boolean(currentForm.elements.outbound_enabled?.checked),
    priority: currentForm.elements.priority?.value ? Number(currentForm.elements.priority.value) : null,
    config: telephonyProviderConfigFromForm(currentForm)
  }), { method: providerId ? "PATCH" : "POST" });
}

function clearTelephonyProviderForm() {
  const form = document.querySelector("#telephonyProviderForm");
  if (!form) return;
  form.reset();
  form.elements.provider_id.value = "";
  if (form.elements.is_active) form.elements.is_active.checked = true;
  if (form.elements.outbound_enabled) form.elements.outbound_enabled.checked = true;
  if (form.elements.priority) form.elements.priority.value = "1";
  const button = form.querySelector("button[type='submit']");
  if (button) button.textContent = "Crear proveedor";
}

function fillTelephonyProviderForm(providerId) {
  const form = document.querySelector("#telephonyProviderForm");
  const provider = (state.ops.telephonyProviders || []).find((item) => Number(item.id) === Number(providerId));
  if (!form || !provider) return;
  const config = provider.config || {};
  form.elements.provider_id.value = provider.id;
  if (form.elements.tenant_id) form.elements.tenant_id.value = String(provider.tenant_id);
  form.elements.name.value = provider.name || "";
  form.elements.provider_type.value = provider.provider_type || "manual";
  form.elements.host.value = provider.host || "";
  form.elements.port.value = provider.port || "";
  form.elements.websocket_url.value = provider.websocket_url || "";
  form.elements.api_url.value = provider.api_url || "";
  ["trunk_name", "dtmf_mode", "nat", "codecs", "external_prefix", "mobile_prepend", "mobile_match_pattern", "country_context"].forEach((field) => {
    if (form.elements[field]) form.elements[field].value = config[field] || "";
  });
  form.elements.priority.value = provider.priority || config.priority || 1;
  form.elements.is_active.checked = Boolean(provider.is_active);
  form.elements.is_primary.checked = Boolean(provider.is_primary || config.is_primary);
  form.elements.outbound_enabled.checked = provider.outbound_enabled !== false && config.outbound_enabled !== false;
  const visibleConfig = { ...config };
  ["trunk_name", "dtmf_mode", "nat", "codecs", "external_prefix", "mobile_prepend", "mobile_match_pattern", "country_context", "priority", "is_primary", "outbound_enabled"].forEach((field) => delete visibleConfig[field]);
  form.elements.config.value = Object.keys(visibleConfig).length ? JSON.stringify(visibleConfig, null, 2) : "";
  const button = form.querySelector("button[type='submit']");
  if (button) button.textContent = "Guardar proveedor";
  form.scrollIntoView({ behavior: "smooth", block: "start" });
}

function applyIpComProviderPreset() {
  const form = document.querySelector("#telephonyProviderForm");
  if (!form) return;
  Object.entries(IPCOM_PROVIDER_PRESET).forEach(([field, value]) => {
    if (!form.elements[field]) return;
    if (form.elements[field].type === "checkbox") {
      form.elements[field].checked = Boolean(value);
    } else {
      form.elements[field].value = value;
    }
  });
  form.elements.config.value = JSON.stringify({ mode: "safe_simulation" }, null, 2);
  showToast("info", "Preset IpCom cargado sin secretos. Revisa y guarda el proveedor.");
}

async function toggleTelephonyProvider(providerId, button) {
  const provider = (state.ops.telephonyProviders || []).find((item) => Number(item.id) === Number(providerId));
  if (!provider) return;
  await runAction(button, async () => {
    await api(`/api/telephony/providers/${provider.id}`, {
      method: "PATCH",
      body: JSON.stringify({ is_active: !provider.is_active })
    });
    await loadPhase8BData();
    renderTelephony();
    showToast("success", !provider.is_active ? "Proveedor activado." : "Proveedor desactivado.");
  }, "Actualizando...");
}

async function setPrimaryTelephonyProvider(providerId, button) {
  await runAction(button, async () => {
    await api(`/api/telephony/providers/${providerId}`, {
      method: "PATCH",
      body: JSON.stringify({ is_active: true, is_primary: true, outbound_enabled: true })
    });
    await loadPhase8BData();
    renderTelephony();
    showToast("success", "Proveedor principal actualizado.");
  }, "Actualizando...");
}

async function testTelephonyProvider(providerId, button) {
  await runAction(button, async () => {
    const result = await api(`/api/telephony/providers/${providerId}/test`, { method: "POST" });
    const warnings = (result.warnings || []).length ? ` Alertas: ${(result.warnings || []).join(", ")}` : "";
    showToast("success", `${result.message || "Prueba segura generada."} Marcado: ${result.dial_string || "-"}${warnings}`);
  }, "Probando...");
}

async function handleTelephonyExtensionSubmit(form) {
  const extensionId = form.elements.extension_id?.value;
  if (isPlatform() && !form.elements.tenant_id?.value) {
    showToast("warning", "Selecciona una empresa para configurar la extension.");
    form.elements.tenant_id?.focus();
    return;
  }
  await submitJson(form, extensionId ? `/api/telephony/extensions/${extensionId}` : "/api/telephony/extensions", (currentForm) => ({
    tenant_id: currentForm.elements.tenant_id?.value ? Number(currentForm.elements.tenant_id.value) : null,
    user_id: Number(currentForm.elements.user_id.value),
    provider_id: currentForm.elements.provider_id.value ? Number(currentForm.elements.provider_id.value) : null,
    extension_number: currentForm.elements.extension_number.value,
    display_name: currentForm.elements.display_name.value || null,
    sip_username: currentForm.elements.sip_username.value || null,
    sip_domain: currentForm.elements.sip_domain.value || null,
    status: currentForm.elements.status.value,
    metadata: {}
  }), { method: extensionId ? "PATCH" : "POST" });
}

function telephonyExtensionMessage(error) {
  const rawMessage = String(error?.message || "");
  if (rawMessage.toLowerCase().includes("extension")) {
    if (canManageTelephony()) {
      return "Configura una extension en Telefonia > Extensiones antes de iniciar la llamada.";
    }
    return "No tienes una extension telefonica configurada. Solicita al administrador configurarla en Telefonia > Extensiones.";
  }
  return rawMessage || "No fue posible registrar la llamada.";
}

function clickToCallPayload(customerId) {
  const customer = state.selectedCustomer && Number(state.selectedCustomer.id) === Number(customerId)
    ? state.selectedCustomer
    : (state.crm.customers?.items || []).find((item) => Number(item.id) === Number(customerId));
  const activityForm = document.querySelector(`#activityForm[data-customer-id="${customerId}"]`);
  const drawerForm = document.querySelector(`#drawerActivityForm[data-customer-id="${customerId}"]`);
  const obligationId = optionalNumber(drawerForm?.elements.obligation_id?.value || activityForm?.elements.obligation_id?.value || "");
  const payload = {
    customer_id: Number(customerId),
    source: "crm_customer_drawer"
  };
  if (customer?.phone) payload.phone_number = customer.phone;
  if (obligationId) payload.obligation_id = obligationId;
  return payload;
}

function clearTelephonyExtensionForm(userId = "") {
  const form = document.querySelector("#telephonyExtensionForm");
  if (!form) return;
  form.reset();
  form.elements.extension_id.value = "";
  if (userId && form.elements.user_id) form.elements.user_id.value = String(userId);
  const button = form.querySelector("button[type='submit']");
  if (button) button.textContent = "Asignar extension";
}

function editTelephonyExtension(extensionId) {
  const form = document.querySelector("#telephonyExtensionForm");
  const extension = (state.ops.telephonyExtensions || []).find((item) => Number(item.id) === Number(extensionId));
  if (!form || !extension) return;
  form.elements.extension_id.value = extension.id;
  if (form.elements.tenant_id) form.elements.tenant_id.value = String(extension.tenant_id);
  form.elements.user_id.value = String(extension.user_id);
  form.elements.provider_id.value = extension.provider_id ? String(extension.provider_id) : "";
  form.elements.extension_number.value = extension.extension_number || "";
  form.elements.display_name.value = extension.display_name || "";
  form.elements.sip_username.value = extension.sip_username || "";
  form.elements.sip_domain.value = extension.sip_domain || "";
  form.elements.status.value = extension.status || "not_connected";
  const button = form.querySelector("button[type='submit']");
  if (button) button.textContent = "Guardar extension";
  form.scrollIntoView({ behavior: "smooth", block: "start" });
}

async function toggleTelephonyExtension(extensionId, button) {
  const extension = (state.ops.telephonyExtensions || []).find((item) => Number(item.id) === Number(extensionId));
  if (!extension) return;
  await runAction(button, async () => {
    await api(`/api/telephony/extensions/${extension.id}`, {
      method: "PATCH",
      body: JSON.stringify({ is_active: !extension.is_active })
    });
    showToast("success", !extension.is_active ? "Extension activada." : "Extension desactivada.");
    await loadPhase8BData();
    renderTelephony();
  }, "Actualizando...");
}

async function startClickToCall(customerId, button) {
  const key = String(customerId || "");
  if (pendingClickToCallCustomers.has(key)) {
    showToast("info", "La llamada ya se esta procesando.");
    return;
  }
  pendingClickToCallCustomers.add(key);
  const relatedButtons = Array.from(document.querySelectorAll("[data-click-to-call]")).filter((item) => item.dataset.clickToCall === key);
  relatedButtons.forEach((item) => setButtonLoading(item, true, "Llamando..."));
  try {
    const result = await api("/api/telephony/click-to-call", {
      method: "POST",
      body: JSON.stringify(clickToCallPayload(customerId))
    });
    showToast("success", result.message || "Llamada registrada.");
    await loadPhase8BData();
    await refreshCustomerAfterActivity(customerId);
    renderTelephony();
  } catch (error) {
    console.warn(error);
    showToast("warning", telephonyExtensionMessage(error));
  } finally {
    pendingClickToCallCustomers.delete(key);
    relatedButtons.forEach((item) => setButtonLoading(item, false));
  }
}

function optionalNumber(value) {
  return value === undefined || value === null || value === "" ? null : Number(value);
}

function platformTenantValue(form) {
  if (!isPlatform()) return null;
  const supportTenant = operationalTenantId();
  if (supportTenant) return Number(supportTenant);
  return form.elements.tenant_id?.value ? Number(form.elements.tenant_id.value) : null;
}

async function submitJson(form, endpoint, buildPayload, options = {}) {
  const button = form.querySelector("button[type='submit']");
  await runAction(button, async () => {
    await api(endpoint, { method: options.method || "POST", body: JSON.stringify(buildPayload(form)) });
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
    document.querySelector("#sectionTitle").textContent = titles[button.dataset.section] || button.textContent || "IEP";
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
      obligation_id: form.elements.obligation_id.value ? Number(form.elements.obligation_id.value) : null,
      amount: Number(form.elements.amount.value),
      paid_at: toDateTime(form.elements.paid_at.value),
      method: form.elements.method.value || "No especificado",
      reference: form.elements.reference.value
    }));
  });
  document.querySelector("#paymentForm select[name='customer_id']")?.addEventListener("change", async (event) => {
    await loadObligationsForForm(event.currentTarget.form);
  });
  document.querySelector("#agreementForm")?.addEventListener("submit", async (event) => {
    event.preventDefault();
    await submitJson(event.currentTarget, "/api/crm/agreements", (form) => ({
      customer_id: Number(form.elements.customer_id.value),
      obligation_id: form.elements.obligation_id.value ? Number(form.elements.obligation_id.value) : null,
      total_amount: Number(form.elements.total_amount.value || 0),
      installment_count: Number(form.elements.installment_count.value || 0),
      start_date: toDateTime(form.elements.start_date.value),
      notes: form.elements.notes.value || null
    }));
  });
  document.querySelector("#agreementForm select[name='customer_id']")?.addEventListener("change", async (event) => {
    await loadObligationsForForm(event.currentTarget.form);
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
    if (form.id === "telephonyProviderForm") {
      event.preventDefault();
      await handleTelephonyProviderSubmit(form);
    }
    if (form.id === "telephonyExtensionForm") {
      event.preventDefault();
      await handleTelephonyExtensionSubmit(form);
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
    if (form.id === "excelSheetRowForm") {
      event.preventDefault();
      await saveExcelSheetRow(form);
    }
    if (form.id === "excelSheetFilterForm") {
      event.preventDefault();
      if (guardExcelSheetNavigation()) return;
      state.ops.excelSheetFilters = excelSheetFilterPayloadFromForm(form);
      await loadExcelSheetRows(1);
      renderExcelWeb();
    }
    if (["typificationTreeForm", "typificationNodeForm", "typificationCombinationForm"].includes(form.id)) {
      event.preventDefault();
      await handleTypificationOpsSubmit(form);
    }
    if (form.id === "projectUserAssignForm") {
      event.preventDefault();
      await handleProjectUserAssignment(form);
    }
    if (form.id === "leaderAgentAssignForm") {
      event.preventDefault();
      await handleLeaderAgentAssignment(form);
    }
  });
  document.addEventListener("click", async (event) => {
    const enterSupportMode = event.target.closest("[data-enter-support-mode]");
    if (enterSupportMode) {
      await enterOperationalSupportMode(enterSupportMode);
      return;
    }
    const exitSupportMode = event.target.closest("[data-exit-support-mode]");
    if (exitSupportMode) {
      await exitOperationalSupportMode(exitSupportMode);
      return;
    }
    const tablePage = event.target.closest("[data-table-page]");
    if (tablePage) {
      state.ui.tablePages[tablePage.dataset.tablePage] = Number(tablePage.dataset.page || 1);
      renderAll();
      return;
    }
    const open = event.target.closest("[data-open-customer]");
    if (open) {
      await openCustomerDrawer(open.dataset.openCustomer);
      return;
    }
    const agreement = event.target.closest("[data-open-agreement]");
    if (agreement) {
      state.ui.selectedAgreementId = Number(agreement.dataset.openAgreement);
      renderAgreements();
      return;
    }
    const clickToCall = event.target.closest("[data-click-to-call]");
    if (clickToCall) {
      await startClickToCall(clickToCall.dataset.clickToCall, clickToCall);
      return;
    }
    const editProvider = event.target.closest("[data-edit-telephony-provider]");
    if (editProvider) {
      fillTelephonyProviderForm(editProvider.dataset.editTelephonyProvider);
      return;
    }
    const toggleProvider = event.target.closest("[data-toggle-telephony-provider]");
    if (toggleProvider) {
      await toggleTelephonyProvider(toggleProvider.dataset.toggleTelephonyProvider, toggleProvider);
      return;
    }
    const primaryProvider = event.target.closest("[data-primary-telephony-provider]");
    if (primaryProvider) {
      await setPrimaryTelephonyProvider(primaryProvider.dataset.primaryTelephonyProvider, primaryProvider);
      return;
    }
    const testProvider = event.target.closest("[data-test-telephony-provider]");
    if (testProvider) {
      await testTelephonyProvider(testProvider.dataset.testTelephonyProvider, testProvider);
      return;
    }
    const ipcomPreset = event.target.closest("[data-ipcom-preset]");
    if (ipcomPreset) {
      applyIpComProviderPreset();
      return;
    }
    const clearProvider = event.target.closest("[data-clear-telephony-provider]");
    if (clearProvider) {
      clearTelephonyProviderForm();
      return;
    }
    const editTelephony = event.target.closest("[data-edit-telephony-extension]");
    if (editTelephony) {
      editTelephonyExtension(editTelephony.dataset.editTelephonyExtension);
      return;
    }
    const toggleTelephony = event.target.closest("[data-toggle-telephony-extension]");
    if (toggleTelephony) {
      await toggleTelephonyExtension(toggleTelephony.dataset.toggleTelephonyExtension, toggleTelephony);
      return;
    }
    const newTelephony = event.target.closest("[data-new-telephony-extension]");
    if (newTelephony) {
      clearTelephonyExtensionForm(newTelephony.dataset.newTelephonyExtension);
      return;
    }
    const clearTelephony = event.target.closest("[data-clear-telephony-extension]");
    if (clearTelephony) {
      clearTelephonyExtensionForm();
      return;
    }
    const teamProject = event.target.closest("[data-team-project]");
    if (teamProject) {
      state.teams.selectedProjectId = Number(teamProject.dataset.teamProject);
      state.teams.projectUsers = await apiMaybe(`/api/teams/projects/${state.teams.selectedProjectId}/users`, []);
      renderTeams();
      return;
    }
    const toggleProjectUser = event.target.closest("[data-toggle-project-user]");
    if (toggleProjectUser) {
      await runAction(toggleProjectUser, async () => {
        const isActive = toggleProjectUser.dataset.active === "true";
        await api(`/api/teams/project-users/${toggleProjectUser.dataset.toggleProjectUser}`, {
          method: "PATCH",
          body: JSON.stringify({ is_active: !isActive })
        });
        await loadTeamsData();
        renderTeams();
        showToast("success", isActive ? "Asignacion desactivada." : "Asignacion activada.");
      }, "Actualizando...");
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
    const uploadTemplate = event.target.closest("[data-upload-template]");
    if (uploadTemplate) {
      const form = document.querySelector("#uploadPreviewForm");
      const uploadType = form?.elements.upload_type?.value || "reparto_cartera";
      await runAction(uploadTemplate, async () => {
        const template = await api(`/api/uploads/templates/${uploadType}`);
        downloadCsvText(template.filename || `plantilla_${uploadType}.csv`, template.csv_text || "");
        showToast("success", "Plantilla descargada.");
      }, "Preparando...");
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
        downloadCsvText(result.filename || `resultado_lote_${uploadResult.dataset.uploadResult}.csv`, result.csv_text || "");
        showToast("success", "Resultado descargado.");
      }, "Consultando...");
      return;
    }
    const uploadErrors = event.target.closest("[data-upload-errors]");
    if (uploadErrors) {
      await runAction(uploadErrors, async () => {
        const result = await api(`/api/uploads/batches/${uploadErrors.dataset.uploadErrors}/errors`);
        downloadCsvText(result.filename || `errores_lote_${uploadErrors.dataset.uploadErrors}.csv`, result.csv_text || "");
        showToast("success", "Archivo de errores descargado.");
      }, "Consultando...");
      return;
    }
    const excelSource = event.target.closest("[data-excel-source]");
    if (excelSource) {
      const source = state.ops.excelSources.find((item) => item.code === excelSource.dataset.excelSource);
      state.ops.excelDraft = { source: excelSource.dataset.excelSource, filters: scopedExcelFilters({}), columns: (source?.columns || []).slice(0, 8), page: 1, page_size: DEFAULT_TABLE_PAGE_SIZE };
      state.ops.excelResult = await api("/api/excel-web/query", { method: "POST", body: JSON.stringify(state.ops.excelDraft) });
      renderExcelWeb();
      return;
    }
    const excelView = event.target.closest("[data-excel-view]");
    if (excelView) {
      const view = state.ops.excelViews.find((item) => String(item.id) === String(excelView.dataset.excelView));
      if (view) {
        state.ops.excelDraft = { source: view.source, filters: scopedExcelFilters(view.filters || {}), columns: view.columns || [], page: 1, page_size: DEFAULT_TABLE_PAGE_SIZE };
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
        if (!payload) throw new Error("Filtra una fuente de informacion antes de exportar.");
        await downloadCsvPost("/api/excel-web/export", `excel_web_${payload.source}.csv`, payload);
        showToast("success", "Exportacion CSV generada correctamente.");
      }, "Exportando...");
      return;
    }
    const excelPage = event.target.closest("[data-excel-page]");
    if (excelPage) {
      const payload = state.ops.excelDraft || { source: state.ops.excelSources[0]?.code || "customers", filters: scopedExcelFilters({}), columns: [], page: 1, page_size: DEFAULT_TABLE_PAGE_SIZE };
      state.ops.excelDraft = { ...payload, filters: scopedExcelFilters(payload.filters || {}), page: Math.max(1, Number(excelPage.dataset.excelPage || 1)), page_size: DEFAULT_TABLE_PAGE_SIZE };
      state.ops.excelResult = await api("/api/excel-web/query", { method: "POST", body: JSON.stringify(state.ops.excelDraft) });
      renderExcelWeb();
      return;
    }
    const excelClear = event.target.closest("[data-excel-clear]");
    if (excelClear) {
      const source = state.ops.excelSources.find((item) => item.code === (state.ops.excelDraft?.source || state.ops.excelResult?.source)) || state.ops.excelSources[0];
      state.ops.excelDraft = { source: source?.code || "customers", filters: scopedExcelFilters({}), columns: (source?.columns || []).slice(0, 8), page: 1, page_size: DEFAULT_TABLE_PAGE_SIZE };
      state.ops.excelResult = await api("/api/excel-web/query", { method: "POST", body: JSON.stringify(state.ops.excelDraft) });
      renderExcelWeb();
      return;
    }
    const excelSheetPage = event.target.closest("[data-excel-sheet-page]");
    if (excelSheetPage) {
      if (guardExcelSheetNavigation()) return;
      await loadExcelSheetRows(Math.max(1, Number(excelSheetPage.dataset.excelSheetPage || 1)));
      renderExcelWeb();
      return;
    }
    if (event.target.closest("[data-excel-sheet-clear]")) {
      if (guardExcelSheetNavigation()) return;
      state.ops.excelSheetFilters = {};
      state.ops.excelSheetEditingId = null;
      await loadExcelSheetRows(1);
      renderExcelWeb();
      return;
    }
    const excelSheetSaveAll = event.target.closest("[data-excel-sheet-save-all]");
    if (excelSheetSaveAll) {
      await saveExcelSheetChanges(excelSheetSaveAll);
      return;
    }
    if (event.target.closest("[data-excel-sheet-cancel-all]")) {
      cancelExcelSheetChanges();
      return;
    }
    const excelSheetEdit = event.target.closest("[data-excel-sheet-edit]");
    if (excelSheetEdit) {
      state.ops.excelSheetEditingId = Number(excelSheetEdit.dataset.excelSheetEdit);
      renderExcelWeb();
      return;
    }
    if (event.target.closest("[data-excel-sheet-cancel]")) {
      state.ops.excelSheetEditingId = null;
      renderExcelWeb();
      return;
    }
    const excelSheetSave = event.target.closest("[data-excel-sheet-save]");
    if (excelSheetSave) {
      await saveExcelSheetEdit(Number(excelSheetSave.dataset.excelSheetSave), excelSheetSave);
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
    const sheetCell = event.target.closest?.("[data-new-sheet-cell], [data-sheet-cell]");
    if (sheetCell) {
      if (event.key === "Enter") {
        event.preventDefault();
        setExcelSheetCellChange(sheetCell);
        focusRelativeSheetCell(sheetCell, "down");
        return;
      }
      if (event.key === "Escape") {
        event.preventDefault();
        cancelExcelSheetChanges();
        return;
      }
    }
    if (event.key === "Escape") closeManagementDrawer();
  });
  document.addEventListener("change", async (event) => {
    const sheetCell = event.target.closest("[data-new-sheet-cell], [data-sheet-cell]");
    if (sheetCell) {
      setExcelSheetCellChange(sheetCell);
      return;
    }
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
    const leaderSelect = event.target.closest('#leaderAgentAssignForm select[name="leader_id"]');
    if (leaderSelect && leaderSelect.value) {
      state.teams.selectedLeaderId = Number(leaderSelect.value);
      state.teams.leaderAgents = await apiMaybe(`/api/teams/leaders/${state.teams.selectedLeaderId}/agents`, []);
      state.teams.leaderSummary = await apiMaybe(`/api/teams/leaders/${state.teams.selectedLeaderId}/summary`, null);
      renderTeams();
    }
    const teamProjectSelect = event.target.closest('#projectUserAssignForm select[name="project_id"]');
    if (teamProjectSelect && teamProjectSelect.value) {
      state.teams.selectedProjectId = Number(teamProjectSelect.value);
      state.teams.projectUsers = await apiMaybe(`/api/teams/projects/${state.teams.selectedProjectId}/users`, []);
      renderTeams();
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
      await downloadCsv(`/api/crm/customers/export${scopedQuery()}`, "clientes_iep.csv");
      showToast("success", "Exportacion de clientes iniciada.");
    } catch (error) {
      showToast("error", error.message);
    }
  });
  document.addEventListener("input", (event) => {
    const sheetCell = event.target.closest("[data-new-sheet-cell], [data-sheet-cell]");
    if (sheetCell) {
      setExcelSheetCellChange(sheetCell);
      return;
    }
    if (event.target.closest("#recordingSearch")) {
      state.ops.recordingFilters = { text: event.target.value };
      renderRecordings();
    }
  });
  document.addEventListener("focusin", (event) => {
    const sheetCell = event.target.closest("[data-new-sheet-cell], [data-sheet-cell]");
    document.querySelectorAll(".sheet-cell-active").forEach((cell) => cell.classList.remove("sheet-cell-active"));
    if (!sheetCell) return;
    const rowId = sheetCell.dataset.rowId || "new";
    const field = sheetCell.dataset.field || sheetCell.dataset.sheetCell || sheetCell.dataset.newSheetCell;
    state.ops.excelSheetActiveCell = `${rowId}:${field}`;
    sheetCell.closest("td")?.classList.add("sheet-cell-active");
  });
  document.querySelector("#exportPayments").addEventListener("click", async () => {
    try {
      await downloadCsv(`/api/crm/payments/export${scopedQuery()}`, "pagos_iep.csv");
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
    date_from: form.elements.date_from?.value || "",
    date_to: form.elements.date_to?.value || "",
  };
  return {
    source: form.elements.source.value,
    filters: scopedExcelFilters(filters),
    columns,
    page: Number(form.elements.page.value || 1),
    page_size: DEFAULT_TABLE_PAGE_SIZE,
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
    showToast("warning", "Filtra una fuente de informacion antes de guardar la vista.");
    return;
  }
  await runAction(form.querySelector("button[type='submit']"), async () => {
    await api("/api/excel-web/views", {
      method: "POST",
      body: JSON.stringify({
        tenant_id: platformTenantValue(form),
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

async function loadExcelSheetRows(page = 1) {
  const filters = state.ops.excelSheetFilters || {};
  state.ops.excelSheetRows = await api(`/api/excel-web/sheet-rows?${queryParams({
    ...scopedTenantParams({ page }),
    page_size: DEFAULT_TABLE_PAGE_SIZE,
    q: filters.q || "",
    status: filters.status || "",
    project_id: filters.project_id || "",
    user_id: filters.user_id || "",
    date_from: filters.date_from || "",
    date_to: filters.date_to || "",
  })}`);
}

function sheetRowsById() {
  const rows = state.ops.excelSheetRows?.items || [];
  return new Map(rows.map((row) => [String(row.id), row]));
}

function sheetProjectLabel(projectId) {
  const project = (state.crm.options.projects || []).find((item) => String(item.id) === String(projectId));
  return project?.label || project?.name || "";
}

function normalizeSheetCellValue(field, value) {
  if (field === "amount") return Number(value || 0);
  if (field === "project_id") return optionalNumber(value);
  if (["date", "next_action_at"].includes(field)) return value || null;
  return value === "" ? null : value;
}

function originalSheetValue(row, field) {
  if (!row) return "";
  if (field === "date" || field === "next_action_at") return dateOnly(row[field]) || null;
  if (field === "amount") return Number(row[field] || 0);
  if (field === "project_id") return row.project_id || null;
  return row[field] ?? null;
}

function refreshSheetEditToolbar() {
  const unsavedCount = Object.keys(state.ops.excelSheetChanges || {}).length + (hasSheetNewRowData() ? 1 : 0);
  const toolbar = document.querySelector(".sheet-edit-toolbar");
  if (!toolbar) return;
  const status = toolbar.querySelector("span");
  const buttons = toolbar.querySelectorAll("[data-excel-sheet-save-all], [data-excel-sheet-cancel-all]");
  if (status) status.textContent = unsavedCount ? `${unsavedCount} fila(s) con cambios sin guardar` : "Sin cambios pendientes";
  buttons.forEach((button) => { button.disabled = !unsavedCount; });
}

function markSheetCell(target, dirty) {
  const cell = target.closest("td");
  const row = target.closest("tr");
  cell?.classList.toggle("sheet-cell-dirty", dirty);
  row?.classList.toggle("sheet-row-dirty", Boolean(row?.querySelector(".sheet-cell-dirty")) || row?.matches(".sheet-new-row") && hasSheetNewRowData());
  const stateLabel = row?.querySelector(".sheet-state");
  if (stateLabel) {
    const pending = row.classList.contains("sheet-row-dirty");
    stateLabel.textContent = pending ? "Sin guardar" : row?.matches(".sheet-new-row") ? "Lista" : "Guardado";
    stateLabel.classList.toggle("sheet-state-pending", pending);
  }
}

function setExcelSheetCellChange(target) {
  const field = target.dataset.field || target.dataset.sheetCell || target.dataset.newSheetCell;
  const rawValue = target.value;
  if (target.dataset.newSheetCell) {
    const value = normalizeSheetCellValue(field, rawValue);
    if (value === null || value === "") delete state.ops.excelSheetNewRow[field];
    else state.ops.excelSheetNewRow[field] = value;
    if (field === "project_id") {
      const label = sheetProjectLabel(value);
      if (label) state.ops.excelSheetNewRow.portfolio = label;
      else delete state.ops.excelSheetNewRow.portfolio;
    }
    markSheetCell(target, Object.prototype.hasOwnProperty.call(state.ops.excelSheetNewRow, field));
    refreshSheetEditToolbar();
    return;
  }
  const rowId = String(target.dataset.rowId || "");
  const row = sheetRowsById().get(rowId);
  if (!row) return;
  const value = normalizeSheetCellValue(field, rawValue);
  const original = originalSheetValue(row, field);
  state.ops.excelSheetChanges[rowId] = state.ops.excelSheetChanges[rowId] || {};
  if (String(value ?? "") === String(original ?? "")) {
    delete state.ops.excelSheetChanges[rowId][field];
  } else {
    state.ops.excelSheetChanges[rowId][field] = value;
  }
  if (field === "project_id") {
    const label = sheetProjectLabel(value);
    const originalPortfolio = row.portfolio || null;
    if (String(label || "") === String(originalPortfolio || "")) delete state.ops.excelSheetChanges[rowId].portfolio;
    else state.ops.excelSheetChanges[rowId].portfolio = label || null;
  }
  if (!Object.keys(state.ops.excelSheetChanges[rowId]).length) delete state.ops.excelSheetChanges[rowId];
  markSheetCell(target, Boolean(state.ops.excelSheetChanges[rowId]?.[field]));
  refreshSheetEditToolbar();
}

function workingSheetRow(row, changes = {}) {
  return { ...(row || {}), ...(changes || {}) };
}

function validateSheetData(data, isNew = false) {
  const errors = [];
  const customer = String(data.customer_name || "").trim();
  const documentValue = String(data.document || "").trim();
  const note = String(data.management_note || "").trim();
  const commitment = String(data.commitment || "").trim();
  if (!customer && !documentValue) errors.push("Cliente o documento es obligatorio.");
  if (isNew && !note && !commitment) errors.push("Gestion o compromiso es obligatorio para crear una fila.");
  if (data.status && !SHEET_STATUSES.includes(data.status)) errors.push("Estado no permitido.");
  if (data.amount !== null && data.amount !== undefined && (Number.isNaN(Number(data.amount)) || Number(data.amount) < 0)) errors.push("Valor debe ser numerico y mayor o igual a cero.");
  if (data.date && Number.isNaN(Date.parse(data.date))) errors.push("Fecha no valida.");
  if (data.next_action_at && Number.isNaN(Date.parse(data.next_action_at))) errors.push("Proxima accion no valida.");
  return errors;
}

function sheetApiPayload(data) {
  const payload = { ...data };
  const supportTenant = operationalTenantId();
  if (supportTenant && !payload.tenant_id) payload.tenant_id = Number(supportTenant);
  if (Object.prototype.hasOwnProperty.call(payload, "amount")) payload.amount = Number(payload.amount || 0);
  if (Object.prototype.hasOwnProperty.call(payload, "project_id")) payload.project_id = optionalNumber(payload.project_id);
  if (Object.prototype.hasOwnProperty.call(payload, "next_action_at")) payload.next_action_at = toDateTime(payload.next_action_at);
  if (!payload.status) payload.status = "Pendiente";
  return payload;
}

async function saveExcelSheetChanges(button) {
  await runAction(button, async () => {
    const rows = sheetRowsById();
    const updates = Object.entries(state.ops.excelSheetChanges || {});
    const newRow = state.ops.excelSheetNewRow || {};
    const shouldCreate = hasSheetNewRowData();
    if (shouldCreate) {
      const createData = workingSheetRow({}, newRow);
      const errors = validateSheetData(createData, true);
      if (errors.length) throw new Error(errors.join(" "));
    }
    for (const [rowId, changes] of updates) {
      const row = rows.get(String(rowId));
      const errors = validateSheetData(workingSheetRow(row, changes), false);
      if (errors.length) throw new Error(`Fila ${rowId}: ${errors.join(" ")}`);
    }
    let created = 0;
    let updated = 0;
    if (shouldCreate) {
      await api("/api/excel-web/sheet-rows", { method: "POST", body: JSON.stringify({ ...sheetApiPayload(newRow), metadata: { source: "frontend_excel_grid" } }) });
      created += 1;
    }
    for (const [rowId, changes] of updates) {
      await api(`/api/excel-web/sheet-rows/${rowId}`, { method: "PATCH", body: JSON.stringify(sheetApiPayload(changes)) });
      updated += 1;
    }
    state.ops.excelSheetChanges = {};
    state.ops.excelSheetNewRow = {};
    state.ops.excelSheetActiveCell = null;
    await loadExcelSheetRows(state.ops.excelSheetRows?.page || 1);
    showToast("success", `${created ? `${created} fila creada. ` : ""}${updated ? `${updated} fila(s) actualizada(s).` : ""}`.trim() || "Cambios guardados.");
    renderExcelWeb();
  }, "Guardando...");
}

function cancelExcelSheetChanges() {
  state.ops.excelSheetChanges = {};
  state.ops.excelSheetNewRow = {};
  state.ops.excelSheetActiveCell = null;
  renderExcelWeb();
  showToast("info", "Cambios locales cancelados.");
}

function guardExcelSheetNavigation() {
  if (!hasExcelSheetUnsavedChanges()) return false;
  showToast("warning", "Tienes cambios sin guardar. Guarda o cancela antes de cambiar de pagina.");
  return true;
}

function focusRelativeSheetCell(target, direction = "down") {
  const cells = Array.from(document.querySelectorAll("[data-new-sheet-cell], [data-sheet-cell]"));
  const index = cells.indexOf(target);
  if (index < 0) return;
  const columns = SHEET_EDITABLE_FIELDS.length;
  const nextIndex = direction === "down" ? index + columns : index + 1;
  cells[nextIndex]?.focus();
}

function excelSheetPayloadFromForm(form) {
  return {
    tenant_id: operationalTenantId() ? Number(operationalTenantId()) : null,
    project_id: optionalNumber(form.elements.project_id.value),
    date: form.elements.date.value || null,
    portfolio: form.elements.project_id.selectedOptions[0]?.text || "",
    customer_name: form.elements.customer_name.value,
    document: form.elements.document.value || null,
    obligation_number: form.elements.obligation_number.value || null,
    management_note: form.elements.management_note.value || null,
    commitment: form.elements.commitment.value || null,
    amount: Number(form.elements.amount.value || 0),
    status: form.elements.status.value || "Pendiente",
    next_action_at: toDateTime(form.elements.next_action_at.value),
    metadata: { source: "frontend_excel_web" }
  };
}

async function saveExcelSheetRow(form) {
  const button = form.querySelector("button[type='submit']");
  await runAction(button, async () => {
    await api("/api/excel-web/sheet-rows", { method: "POST", body: JSON.stringify(excelSheetPayloadFromForm(form)) });
    form.reset();
    await loadExcelSheetRows(1);
    showToast("success", "Fila de seguimiento guardada correctamente.");
    renderExcelWeb();
  }, "Guardando fila...");
}

function excelSheetPatchFromRow(rowId) {
  const row = document.querySelector(`[data-excel-sheet-row="${rowId}"]`);
  if (!row) throw new Error("No se encontro la fila para actualizar.");
  const data = {};
  row.querySelectorAll("[data-sheet-field]").forEach((field) => {
    const key = field.dataset.sheetField;
    let value = field.value;
    if (key === "amount") value = Number(value || 0);
    if (key === "next_action_at") value = toDateTime(value);
    if (key === "date") value = value || null;
    data[key] = value === "" ? null : value;
  });
  return data;
}

async function saveExcelSheetEdit(rowId, button) {
  await runAction(button, async () => {
    await api(`/api/excel-web/sheet-rows/${rowId}`, { method: "PATCH", body: JSON.stringify(excelSheetPatchFromRow(rowId)) });
    state.ops.excelSheetEditingId = null;
    await loadExcelSheetRows(state.ops.excelSheetRows?.page || 1);
    showToast("success", "Fila actualizada correctamente.");
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
