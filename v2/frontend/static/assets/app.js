let token = localStorage.getItem("icodeup_v2_token") || "";
let currentUser = JSON.parse(localStorage.getItem("icodeup_v2_user") || "null");

const state = {
  admin: { overview: null, tenants: [], projects: [], users: [], roles: [], typifications: [] },
  crm: { options: { tenants: [], projects: [], users: [], channels: [] }, dashboard: null, bi: null, customers: null, queue: null, promises: [], payments: [], channels: [], typifications: [] },
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
  reports: "Reportes BI",
  channels: "Canales",
  tenants: "Empresas",
  projects: "Proyectos",
  users: "Usuarios",
  typifications: "Tipificaciones"
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
    throw new Error(payload.detail || "Error de comunicacion.");
  }
  return payload;
}

function isPlatform() {
  return currentUser?.role === "platform_admin";
}

function canManageCrm() {
  return ["platform_admin", "tenant_admin", "coordinator"].includes(currentUser?.role);
}

function showApp() {
  loginView.classList.add("hidden");
  appView.classList.remove("hidden");
  document.querySelector("#sessionUser").textContent = currentUser ? `${currentUser.name} - ${currentUser.role}` : "Sesion activa";
  document.querySelectorAll(".platform-only").forEach((item) => item.classList.toggle("hidden", !isPlatform()));
  document.querySelectorAll(".manager-only").forEach((item) => item.classList.toggle("hidden", !canManageCrm()));
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
  try {
    const data = await api("/api/health");
    dot.className = data.database?.ok ? "status-ok" : "status-bad";
    text.textContent = data.database?.ok ? "PostgreSQL conectado" : "Base no conectada";
  } catch (error) {
    dot.className = "status-bad";
    text.textContent = error.message;
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
  const [options, dashboard, promises, payments, channels, typifications] = await Promise.all([
    api("/api/crm/options"),
    api("/api/crm/dashboard"),
    api("/api/crm/promises"),
    api("/api/crm/payments"),
    api("/api/crm/channels"),
    api("/api/crm/typifications")
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

async function refreshAll() {
  await loadAdminData();
  await loadTypifications();
  await loadCrmData();
  await loadBi();
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
    { label: "Motor predictivo", detail: `Modelo ${escapeHtml(bi.prediction?.model || "scoring_operativo_v1")} con scoring, semaforos y valor esperado.`, tone: "blue" },
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
    <form id="activityForm" class="form-grid management-grid">
      <label>Tipificacion<select name="typification_id">${typificationOptionsForCustomer(customer)}</select></label>
      <label>Canal<select name="channel"><option value="phone">Llamada</option><option value="whatsapp">WhatsApp</option><option value="email">Email</option><option value="manual">Manual</option></select></label>
      <label>Resultado<select name="result"><option>Contactado</option><option>Sin contacto</option><option>Promesa</option><option>Escalado</option><option>Disputa</option></select></label>
      <label>Siguiente fecha<input name="next_contact_at" type="date" /></label>
      <label>Promesa monto<input name="promise_amount" type="number" min="0" /></label>
      <label>Promesa fecha<input name="promise_due_date" type="date" /></label>
      <label class="wide">Nota<textarea name="note" placeholder="Resumen de conversacion, objecion o acuerdo."></textarea></label>
      <button type="submit">Guardar gestion</button>
    </form>
    <div class="activity-head"><strong>Actividad reciente</strong><span>Ultimas 10 gestiones</span></div>
    <div class="activity-matrix">${activityCards || `<p class="empty">Sin gestiones registradas.</p>`}</div>
  `;
  panel.querySelector("#activityForm").addEventListener("submit", submitActivity);
}

async function submitActivity(event) {
  event.preventDefault();
  const form = event.currentTarget;
  const body = {
    typification_id: form.elements.typification_id.value ? Number(form.elements.typification_id.value) : null,
    channel: form.elements.channel.value,
    result: form.elements.result.value,
    note: form.elements.note.value,
    next_contact_at: toDateTime(form.elements.next_contact_at.value),
    promise_amount: form.elements.promise_amount.value ? Number(form.elements.promise_amount.value) : null,
    promise_due_date: toDateTime(form.elements.promise_due_date.value)
  };
  await api(`/api/crm/customers/${state.selectedCustomer.id}/activities`, { method: "POST", body: JSON.stringify(body) });
  await loadCrmData();
  await loadBi();
  await selectCustomer(state.selectedCustomer.id);
  renderAll();
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

function renderAll() {
  fillSelects();
  renderDashboard();
  renderBI();
  renderQueue();
  renderCustomers();
  renderPromises();
  renderPayments();
  renderChannels();
  renderAdminTables();
  renderModuleInsights();
}

function formPayload(form) {
  return Object.fromEntries(new FormData(form).entries());
}

async function submitJson(form, endpoint, buildPayload) {
  const button = form.querySelector("button[type='submit']");
  const text = button.textContent;
  button.disabled = true;
  button.textContent = "Guardando...";
  try {
    await api(endpoint, { method: "POST", body: JSON.stringify(buildPayload(form)) });
    form.reset();
    await refreshAll();
  } catch (error) {
    alert(error.message);
  } finally {
    button.disabled = false;
    button.textContent = text;
  }
}

function setupNavigation() {
  document.querySelectorAll(".nav-item").forEach((button) => {
    button.addEventListener("click", () => {
      if (button.classList.contains("hidden")) return;
      document.querySelectorAll(".nav-item").forEach((item) => item.classList.remove("active"));
      document.querySelectorAll(".section").forEach((section) => section.classList.remove("active-section"));
      button.classList.add("active");
      document.querySelector(`#${button.dataset.section}`).classList.add("active-section");
      document.querySelector("#sectionTitle").textContent = titles[button.dataset.section] || "IcodeUp CRM";
    });
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
}

function setupEvents() {
  document.addEventListener("click", async (event) => {
    const open = event.target.closest("[data-open-customer]");
    if (open) {
      document.querySelector('[data-section="queue"]').click();
      await selectCustomer(open.dataset.openCustomer);
    }
    const sectionJump = event.target.closest("[data-section-jump]");
    if (sectionJump) {
      document.querySelector(`[data-section="${sectionJump.dataset.sectionJump}"]`)?.click();
    }
    const complete = event.target.closest("[data-complete-promise]");
    if (complete) {
      await api(`/api/crm/promises/${complete.dataset.completePromise}/complete`, { method: "PATCH" });
      await refreshAll();
    }
    const editTypification = event.target.closest("[data-edit-typification]");
    if (editTypification) fillTypificationForm(editTypification.dataset.editTypification);
    const deleteTypification = event.target.closest("[data-delete-typification]");
    if (deleteTypification && confirm("Seguro que deseas eliminar esta tipificacion?")) {
      await api(`/api/typifications/${deleteTypification.dataset.deleteTypification}`, { method: "DELETE" });
      await loadTypifications();
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
