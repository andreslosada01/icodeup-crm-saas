const STORAGE_KEY = "icodeup-crm-local-v1";
const API_ENABLED = location.protocol !== "file:";

const ROLE_LABELS = {
  platform_admin: "IcodeUp plataforma",
  superadmin: "Super usuario",
  admin: "Administrador",
  coordinator: "Coordinador",
  agent: "Usuario estandar",
  quality: "Supervisor calidad"
};

const DEMO_USERS = {
  platform: { email: "platform@icodeup.com", password: "Platform123!" },
  superadmin: { email: "super@pepeperez.com", password: "Super123!" },
  admin: { email: "admin@pepeperez.com", password: "Admin123!" },
  coordinator: { email: "lider@pepeperez.com", password: "Lider123!" },
  agent: { email: "gestor@pepeperez.com", password: "Gestor123!" },
  quality: { email: "calidad@pepeperez.com", password: "Calidad123!" }
};

const today = new Date();
const isoToday = toIsoDate(today);

const defaultState = {
  settings: {
    monthlyGoal: 85000000,
    promiseAlertDays: 2,
    criticalDpd: 60
  },
  communication: {
    whatsappNumbers: [
      channelAccount("WA-1", "whatsapp", "Linea principal cobranzas", "+57 300 555 0101", "WhatsApp Web / Cloud API pendiente", true),
      channelAccount("WA-2", "whatsapp", "Linea acuerdos de pago", "+57 300 555 0102", "WhatsApp Web / Cloud API pendiente", false)
    ],
    emailAccounts: [
      channelAccount("EMAIL-1", "email", "Correo cobranzas", "cobranzas@icodeupcrm.local", "SMTP/API pendiente", true),
      channelAccount("EMAIL-2", "email", "Correo acuerdos", "acuerdos@icodeupcrm.local", "SMTP/API pendiente", false)
    ],
    telephonyAccounts: [
      channelAccount("TEL-1", "telephony", "Telefonia WebRTC futura", "PBX no configurada", "SIP/WebRTC pendiente", true, {
        mode: "planned",
        sipDomain: "",
        webSocketUrl: ""
      })
    ]
  },
  agents: ["Laura Gomez", "Mateo Ruiz", "Sofia Pardo", "Andres Mora"],
  users: [
    { id: 1, name: "Super Usuario", email: "super@pepeperez.com", role: "superadmin", leaderId: null, active: true },
    { id: 2, name: "Administrador Operativo", email: "admin@pepeperez.com", role: "admin", leaderId: null, active: true },
    { id: 3, name: "Coordinador Cobranzas", email: "lider@pepeperez.com", role: "coordinator", leaderId: null, active: true },
    { id: 4, name: "Gestor Estandar", email: "gestor@pepeperez.com", role: "agent", leaderId: 3, active: true },
    { id: 5, name: "Supervisor Calidad", email: "calidad@pepeperez.com", role: "quality", leaderId: 3, active: true }
  ],
  portfolios: [
    portfolio("CAR-BASE", "Cartera base cobranzas", "BASE", 3)
  ],
  companies: [],
  segments: ["Consumo", "Microcredito", "Hipotecario", "Pyme", "Tarjeta"],
  customers: [
    {
      id: "C-1001",
      name: "Mariana Torres",
      document: "CC 1002457891",
      phone: "+57 300 456 7788",
      email: "mariana.torres@email.com",
      city: "Bogota",
      segment: "Consumo",
      agent: "Laura Gomez",
      balance: 6420000,
      originalBalance: 8400000,
      dpd: 18,
      status: "Contactado",
      risk: "Medio",
      priority: 81,
      nextAction: "Enviar link de pago y confirmar promesa",
      lastContact: addDays(-1),
      nextContact: addDays(1),
      contactability: "Alta",
      accounts: ["Credito libre inversion 8842"],
      tags: ["Mora temprana", "Buen historial"],
      notes: "Solicito recibir alternativas por WhatsApp despues de las 6 p.m.",
      timeline: [
        activity("Llamada contestada", "Acepta revisar plan de pago parcial.", "Laura Gomez", addDays(-1)),
        activity("WhatsApp enviado", "Se comparte estado de cuenta y link de pago.", "Sistema", addDays(-2))
      ]
    },
    {
      id: "C-1002",
      name: "Alimentos La Quinta SAS",
      document: "NIT 901221334",
      phone: "+57 601 772 1188",
      email: "tesoreria@laquinta.co",
      city: "Medellin",
      segment: "Pyme",
      agent: "Andres Mora",
      balance: 28400000,
      originalBalance: 32000000,
      dpd: 74,
      status: "Promesa",
      risk: "Alto",
      priority: 94,
      nextAction: "Confirmar pago prometido y escalar si incumple",
      lastContact: addDays(-3),
      nextContact: isoToday,
      contactability: "Media",
      accounts: ["Credito capital trabajo 1120", "Tarjeta empresarial 0981"],
      tags: ["Cuenta clave", "Promesa critica"],
      notes: "Pagos dependen de recaudo semanal. Validar con representante legal.",
      timeline: [
        activity("Promesa registrada", "Compromiso por $8.000.000 para hoy.", "Andres Mora", addDays(-3)),
        activity("Email enviado", "Se remite certificado de deuda.", "Sistema", addDays(-5))
      ]
    },
    {
      id: "C-1003",
      name: "Julian Herrera",
      document: "CC 80222333",
      phone: "+57 310 889 4400",
      email: "julian.h@correo.com",
      city: "Cali",
      segment: "Tarjeta",
      agent: "Mateo Ruiz",
      balance: 3180000,
      originalBalance: 5100000,
      dpd: 41,
      status: "Sin contacto",
      risk: "Medio",
      priority: 72,
      nextAction: "Intentar llamada antes de SMS preventivo",
      lastContact: addDays(-9),
      nextContact: isoToday,
      contactability: "Baja",
      accounts: ["Tarjeta credito 4412"],
      tags: ["Telefono intermitente"],
      notes: "No responde llamadas en horario laboral.",
      timeline: [
        activity("Llamada sin respuesta", "Tres intentos en franja tarde.", "Mateo Ruiz", addDays(-2)),
        activity("SMS enviado", "Recordatorio de mora y canales de pago.", "Sistema", addDays(-4))
      ]
    },
    {
      id: "C-1004",
      name: "Carolina Benitez",
      document: "CC 52888990",
      phone: "+57 315 920 1100",
      email: "carolina.b@email.com",
      city: "Barranquilla",
      segment: "Hipotecario",
      agent: "Sofia Pardo",
      balance: 18600000,
      originalBalance: 22000000,
      dpd: 96,
      status: "Disputa",
      risk: "Alto",
      priority: 89,
      nextAction: "Solicitar soporte a operaciones y congelar gestion masiva",
      lastContact: addDays(-4),
      nextContact: addDays(2),
      contactability: "Alta",
      accounts: ["Credito hipotecario 7719"],
      tags: ["Disputa abierta", "Requiere soporte"],
      notes: "Cliente afirma pago no aplicado. Pendiente conciliacion.",
      timeline: [
        activity("Disputa creada", "Reporta transferencia pendiente por aplicar.", "Sofia Pardo", addDays(-4)),
        activity("Caso enviado a operaciones", "Se solicita trazabilidad bancaria.", "Sofia Pardo", addDays(-4))
      ]
    },
    {
      id: "C-1005",
      name: "David Rojas",
      document: "CC 1033445522",
      phone: "+57 320 622 1155",
      email: "drojas@email.com",
      city: "Bucaramanga",
      segment: "Microcredito",
      agent: "Laura Gomez",
      balance: 1260000,
      originalBalance: 2400000,
      dpd: 7,
      status: "Contactado",
      risk: "Bajo",
      priority: 54,
      nextAction: "Enviar recordatorio amable por WhatsApp",
      lastContact: isoToday,
      nextContact: addDays(3),
      contactability: "Alta",
      accounts: ["Microcredito productivo 5640"],
      tags: ["Mora temprana"],
      notes: "Tiene intencion de pago al cierre de semana.",
      timeline: [
        activity("Llamada contestada", "Cliente confirma ingreso el viernes.", "Laura Gomez", isoToday)
      ]
    },
    {
      id: "C-1006",
      name: "Inversiones Mistral SAS",
      document: "NIT 900882123",
      phone: "+57 604 552 8801",
      email: "finanzas@mistral.co",
      city: "Pereira",
      segment: "Pyme",
      agent: "Andres Mora",
      balance: 51600000,
      originalBalance: 51600000,
      dpd: 122,
      status: "Escalado",
      risk: "Alto",
      priority: 98,
      nextAction: "Revision juridica y propuesta de normalizacion",
      lastContact: addDays(-8),
      nextContact: addDays(1),
      contactability: "Media",
      accounts: ["Credito rotativo 2319", "Leasing equipo 4480"],
      tags: ["Prejuridico", "Alto valor"],
      notes: "Direccion financiera pide acuerdo formal por escrito.",
      timeline: [
        activity("Escalamiento", "Se activa ruta prejuridica por mora mayor a 120.", "Andres Mora", addDays(-1)),
        activity("Email enviado", "Propuesta de normalizacion enviada.", "Andres Mora", addDays(-2))
      ]
    },
    {
      id: "C-1007",
      name: "Natalia Ospina",
      document: "CC 1100442200",
      phone: "+57 312 876 5520",
      email: "nospina@email.com",
      city: "Manizales",
      segment: "Consumo",
      agent: "Mateo Ruiz",
      balance: 4720000,
      originalBalance: 6000000,
      dpd: 33,
      status: "Promesa",
      risk: "Medio",
      priority: 78,
      nextAction: "Verificar pago parcial prometido",
      lastContact: addDays(-2),
      nextContact: addDays(2),
      contactability: "Alta",
      accounts: ["Credito educacion 2290"],
      tags: ["Promesa vigente"],
      notes: "Prometio pago parcial y refinanciacion del saldo.",
      timeline: [
        activity("Promesa registrada", "Compromiso por $1.400.000.", "Mateo Ruiz", addDays(-2))
      ]
    },
    {
      id: "C-1008",
      name: "Oscar Valencia",
      document: "CC 91222311",
      phone: "+57 301 665 4499",
      email: "ovalencia@email.com",
      city: "Cartagena",
      segment: "Tarjeta",
      agent: "Sofia Pardo",
      balance: 8750000,
      originalBalance: 10100000,
      dpd: 63,
      status: "Sin contacto",
      risk: "Alto",
      priority: 86,
      nextAction: "Validar telefono alterno y enviar email certificado",
      lastContact: addDays(-12),
      nextContact: isoToday,
      contactability: "Baja",
      accounts: ["Tarjeta credito 9930"],
      tags: ["Busqueda de contacto"],
      notes: "Se requiere enriquecimiento de datos.",
      timeline: [
        activity("Llamada sin respuesta", "Numero principal fuera de servicio.", "Sofia Pardo", addDays(-1))
      ]
    }
  ],
  promises: [
    promise("P-2001", "C-1002", 8000000, isoToday, "WhatsApp", "Vigente"),
    promise("P-2002", "C-1007", 1400000, addDays(2), "Telefono", "Vigente"),
    promise("P-2003", "C-1001", 900000, addDays(-2), "WhatsApp", "Vencida"),
    promise("P-2004", "C-1005", 600000, addDays(-4), "Telefono", "Cumplida")
  ],
  payments: [
    payment("PAY-3001", "C-1005", 600000, addDays(-4), "PSE", "PSE-87311"),
    payment("PAY-3002", "C-1001", 1080000, addDays(-10), "Transferencia", "TRF-55380"),
    payment("PAY-3003", "C-1003", 450000, addDays(-13), "Efectivo", "REC-00412"),
    payment("PAY-3004", "C-1007", 700000, addDays(-19), "Transferencia", "TRF-11084")
  ],
  campaigns: [
    {
      id: "CAM-4001",
      name: "Mora temprana WhatsApp",
      segment: "Consumo",
      channel: "WhatsApp",
      template: "Hola {{nombre}}, tienes un saldo vencido de {{saldo}}. Puedes normalizar hoy usando tu link de pago.",
      createdAt: addDays(-6),
      sent: 1120,
      contacted: 534,
      promises: 186,
      payments: 91
    },
    {
      id: "CAM-4002",
      name: "Pyme alto valor",
      segment: "Pyme",
      channel: "Email",
      template: "Estimado equipo {{nombre}}, adjuntamos propuesta de normalizacion para evitar escalamiento.",
      createdAt: addDays(-3),
      sent: 84,
      contacted: 38,
      promises: 14,
      payments: 5
    }
  ],
  typifications: [
    typification("T-CONTACTO", null, "Contacto", "CONTACTO", "", false, false, ""),
    typification("T-NOCONTACTO", null, "No contacto", "NO_CONTACTO", "Sin contacto", false, false, ""),
    typification("T-DISPUTA", null, "Disputa o reclamo", "DISPUTA", "Disputa", false, false, ""),
    typification("T-CON-TITULAR", "T-CONTACTO", "Titular contactado", "TITULAR", "Contactado", false, false, ""),
    typification("T-CON-TERCERO", "T-CONTACTO", "Tercero contactado", "TERCERO", "Contactado", false, false, ""),
    typification("T-PROMESA", "T-CON-TITULAR", "Promesa de pago", "PROMESA", "Promesa", true, false, ""),
    typification("T-PAGO", "T-CON-TITULAR", "Pago realizado", "PAGO", "Contactado", false, true, ""),
    typification("T-RENEGOCIAR", "T-CON-TITULAR", "Solicita refinanciacion", "RENEGOCIAR", "Contactado", false, false, ""),
    typification("T-MENSAJE", "T-CON-TERCERO", "Mensaje dejado", "MENSAJE_TERCERO", "Contactado", false, false, ""),
    typification("T-NO-CONTESTA", "T-NOCONTACTO", "No contesta", "NO_CONTESTA", "Sin contacto", false, false, "Telefono"),
    typification("T-NUMERO-ERRADO", "T-NOCONTACTO", "Numero errado", "NUMERO_ERRADO", "Sin contacto", false, false, "Telefono"),
    typification("T-WA-SIN-RESPUESTA", "T-NOCONTACTO", "WhatsApp sin respuesta", "WA_SIN_RESPUESTA", "Sin contacto", false, false, "WhatsApp"),
    typification("T-SOPORTE-PAGO", "T-DISPUTA", "Pago no aplicado", "PAGO_NO_APLICADO", "Disputa", false, false, "")
  ]
};

let state = structuredClone(defaultState);
let currentUser = null;
let activeView = "dashboard";
let selectedCustomerId = state.customers[0]?.id || null;
let customerPage = 1;
let queuePage = 1;
let activityPage = 1;
const QUEUE_PAGE_SIZE = 10;
const MAX_CUSTOMER_PAGE_SIZE = 10;
const ACTIVITY_PAGE_SIZE = 10;

const elements = {
  viewTitle: document.querySelector("#viewTitle"),
  globalSearch: document.querySelector("#globalSearch"),
  metricGrid: document.querySelector("#metricGrid"),
  dashboardCommandStrip: document.querySelector("#dashboardCommandStrip"),
  portfolioRiskList: document.querySelector("#portfolioRiskList"),
  teamSnapshot: document.querySelector("#teamSnapshot"),
  governanceList: document.querySelector("#governanceList"),
  reportMetricGrid: document.querySelector("#reportMetricGrid"),
  reportRecoveryChart: document.querySelector("#reportRecoveryChart"),
  reportRiskChart: document.querySelector("#reportRiskChart"),
  biMetricGrid: document.querySelector("#biMetricGrid"),
  biRecoveryChart: document.querySelector("#biRecoveryChart"),
  biRiskDonut: document.querySelector("#biRiskDonut"),
  biRiskLegend: document.querySelector("#biRiskLegend"),
  biPortfolioChart: document.querySelector("#biPortfolioChart"),
  biAgentChart: document.querySelector("#biAgentChart"),
  biAgingChart: document.querySelector("#biAgingChart"),
  biDecisionGrid: document.querySelector("#biDecisionGrid"),
  agingBars: document.querySelector("#agingBars"),
  criticalAgenda: document.querySelector("#criticalAgenda"),
  todayCasesTable: document.querySelector("#todayCasesTable"),
  queueTable: document.querySelector("#queueTable"),
  queueResultsBar: document.querySelector("#queueResultsBar"),
  queuePageLabel: document.querySelector("#queuePageLabel"),
  queuePrevPage: document.querySelector("#queuePrevPage"),
  queueNextPage: document.querySelector("#queueNextPage"),
  queueDetailPanel: document.querySelector("#queueDetailPanel"),
  customerTable: document.querySelector("#customerTable"),
  customerResultsBar: document.querySelector("#customerResultsBar"),
  customerPageLabel: document.querySelector("#customerPageLabel"),
  customerPrevPage: document.querySelector("#customerPrevPage"),
  customerNextPage: document.querySelector("#customerNextPage"),
  portfolioList: document.querySelector("#portfolioList"),
  userDirectory: document.querySelector("#userDirectory"),
  portfolioMembers: document.querySelector("#portfolioMembers"),
  tenantGrid: document.querySelector("#tenantGrid"),
  typificationSummary: document.querySelector("#typificationSummary"),
  typificationList: document.querySelector("#typificationList"),
  promiseList: document.querySelector("#promiseList"),
  paymentsTable: document.querySelector("#paymentsTable"),
  campaignList: document.querySelector("#campaignList"),
  agentRecoveryReport: document.querySelector("#agentRecoveryReport"),
  collectionFunnel: document.querySelector("#collectionFunnel"),
  insightList: document.querySelector("#insightList"),
  customerModal: document.querySelector("#customerModal"),
  loginScreen: document.querySelector("#loginScreen"),
  appShell: document.querySelector("#appShell"),
  loginForm: document.querySelector("#loginForm"),
  loginCompany: document.querySelector("#loginCompany"),
  loginEmail: document.querySelector("#loginEmail"),
  loginPassword: document.querySelector("#loginPassword"),
  sessionPill: document.querySelector("#sessionPill"),
  sessionCompany: document.querySelector("#sessionCompany"),
  sessionUser: document.querySelector("#sessionUser"),
  sessionLabel: document.querySelector("#sessionLabel"),
  logoutBtn: document.querySelector("#logoutBtn"),
  whatsappChannelList: document.querySelector("#whatsappChannelList"),
  emailChannelList: document.querySelector("#emailChannelList"),
  telephonyChannelList: document.querySelector("#telephonyChannelList"),
  toast: document.querySelector("#toast")
};

document.addEventListener("DOMContentLoaded", async () => {
  configureDevelopmentAccess();
  wireLogin();
  wireNavigation();
  wireForms();
  await bootstrapData();
  populateStaticOptions();
  applySettingsToForm();
  applyRolePermissions();
  renderAll();
});

function configureDevelopmentAccess() {
  const demoUsers = document.querySelector("#demoUsers");
  if (!demoUsers) return;
  const isLocal = ["127.0.0.1", "localhost", ""].includes(location.hostname) || location.protocol === "file:";
  demoUsers.hidden = !isLocal;
  demoUsers.open = false;
}

async function bootstrapData() {
  if (!API_ENABLED) {
    state = loadState();
    currentUser = {
      name: "Usuario local",
      role: "admin",
      companyName: "Modo demo sin servidor"
    };
    selectedCustomerId = state.customers[0]?.id || null;
    updateSessionUi();
    return;
  }

  elements.appShell.hidden = true;
  try {
    const sessionResponse = await apiFetch("/api/session", { allowUnauthorized: true });
    if (!sessionResponse?.user) {
      await showLogin();
      return;
    }
    currentUser = sessionResponse.user;
    await loadStateFromApi();
    elements.loginScreen.hidden = true;
    elements.appShell.hidden = false;
    updateSessionUi();
  } catch (error) {
    await showLogin("No se pudo validar la sesion. Intenta ingresar de nuevo.");
  }
}

function wireLogin() {
  elements.loginForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    await login({
      companyId: elements.loginCompany.value,
      email: elements.loginEmail.value,
      password: elements.loginPassword.value
    });
  });

  document.body.addEventListener("click", (event) => {
    const demoButton = event.target.closest("[data-demo-login]");
    if (!demoButton) return;
    const demo = DEMO_USERS[demoButton.dataset.demoLogin];
    elements.loginEmail.value = demo.email;
    elements.loginPassword.value = demo.password;
  });

  elements.logoutBtn.addEventListener("click", logout);
}

async function showLogin(message = "") {
  elements.appShell.hidden = true;
  elements.loginScreen.hidden = false;
  await loadCompaniesForLogin();
  if (message) showToast(message);
}

async function loadCompaniesForLogin() {
  elements.loginCompany.innerHTML = `<option value="">Autodetectar empresa</option>`;
}

async function login(credentials) {
  try {
    const payload = await apiFetch("/api/login", {
      method: "POST",
      body: credentials
    });
    currentUser = payload.user;
    await loadStateFromApi();
    elements.loginScreen.hidden = true;
    elements.appShell.hidden = false;
    updateSessionUi();
    applyRolePermissions();
    renderAll();
    showToast("Sesion iniciada.");
  } catch (error) {
    showToast(error.message || "No se pudo iniciar sesion.");
  }
}

async function logout() {
  if (API_ENABLED) {
    await apiFetch("/api/logout", { method: "POST", body: {} }).catch(() => null);
  }
  currentUser = null;
  await showLogin("Sesion cerrada.");
}

async function loadStateFromApi() {
  const payload = await apiFetch("/api/state");
  state = hydrateState(payload.state);
  currentUser = payload.user || currentUser;
  selectedCustomerId = state.customers[0]?.id || null;
}

async function apiFetch(path, options = {}) {
  const fetchOptions = {
    method: options.method || "GET",
    headers: { "Content-Type": "application/json" },
    credentials: "same-origin"
  };
  if (options.body) fetchOptions.body = JSON.stringify(options.body);
  const response = await fetch(path, fetchOptions);
  if (options.allowUnauthorized && response.status === 401) return null;
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(payload.error || "Error de comunicacion con el servidor.");
  }
  return payload;
}

function updateSessionUi() {
  if (!currentUser) return;
  elements.sessionPill.hidden = false;
  elements.sessionCompany.textContent = currentUser.companyName || "Empresa local";
  elements.sessionUser.textContent = `${currentUser.name} - ${ROLE_LABELS[currentUser.role] || currentUser.role}`;
  elements.sessionLabel.textContent = API_ENABLED ? "Base SQLite activa" : "Base local activa";
  elements.logoutBtn.hidden = !API_ENABLED;
}

function applyRolePermissions() {
  const role = currentUser?.role || "admin";
  const isPlatform = role === "platform_admin";
  const isAdmin = ["superadmin", "admin"].includes(role);
  const isOps = ["superadmin", "admin", "coordinator"].includes(role);
  const isReadOnly = role === "quality";

  document.querySelectorAll("[data-admin-only]").forEach((element) => {
    element.hidden = !isAdmin;
  });
  document.querySelectorAll("[data-ops-only]").forEach((element) => {
    element.hidden = !isOps;
  });
  document.querySelectorAll("[data-super-only]").forEach((element) => {
    element.hidden = role !== "superadmin";
  });
  document.querySelectorAll("[data-platform-only]").forEach((element) => {
    element.hidden = !isPlatform;
  });

  if (!isAdmin && ["settings", "bi", "users"].includes(activeView)) setActiveView(isPlatform ? "tenants" : "dashboard");
  if (!isOps && activeView === "assignments") setActiveView("dashboard");
  if (!isPlatform && activeView === "tenants") setActiveView("dashboard");

  document.querySelector("#newCaseBtn").hidden = !isOps || isReadOnly;
  document.querySelector("#openCustomerFormBtn").hidden = !isOps || isReadOnly;
  elements.appShell.querySelectorAll("form button[type='submit'], #seedDataBtn, #clearDataBtn").forEach((button) => {
    button.disabled = isReadOnly || (button.id === "clearDataBtn" && !isAdmin) || (button.id === "seedDataBtn" && !isAdmin);
  });
  document.querySelector("#assignmentUploadForm button[type='submit']").disabled = !isOps || isReadOnly;
}

function isReadOnlyRole() {
  return currentUser?.role === "quality";
}

function wireNavigation() {
  document.querySelector("#mainNav").addEventListener("click", (event) => {
    const button = event.target.closest("[data-view]");
    if (!button) return;
    setActiveView(button.dataset.view);
  });

  document.body.addEventListener("click", (event) => {
    const viewButton = event.target.closest("[data-view-target]");
    if (viewButton) setActiveView(viewButton.dataset.viewTarget);

    const openButton = event.target.closest("[data-open-customer]");
    if (openButton) {
      selectedCustomerId = openButton.dataset.openCustomer;
      queuePage = pageForCustomerInQueue(selectedCustomerId);
      activityPage = 1;
      setActiveView("queue");
      renderQueueDetail();
    }

    const activityPagerButton = event.target.closest("[data-activity-page]");
    if (activityPagerButton) {
      activityPage += activityPagerButton.dataset.activityPage === "next" ? 1 : -1;
      renderQueueDetail();
    }

    const completePromiseButton = event.target.closest("[data-complete-promise]");
    if (completePromiseButton) {
      if (isReadOnlyRole()) {
        showToast("El supervisor de calidad tiene acceso de solo lectura.");
        return;
      }
      markPromiseCompleted(completePromiseButton.dataset.completePromise);
    }

    const quickActionButton = event.target.closest("[data-quick-action]");
    if (quickActionButton) {
      if (isReadOnlyRole()) {
        event.preventDefault();
        showToast("El supervisor de calidad tiene acceso de solo lectura.");
        return;
      }
      const [customerId, action] = quickActionButton.dataset.quickAction.split("|");
      addQuickActivity(customerId, action);
    }

    const channelDefaultButton = event.target.closest("[data-channel-default]");
    if (channelDefaultButton) {
      const [group, channelId] = channelDefaultButton.dataset.channelDefault.split("|");
      setDefaultChannel(group, channelId);
    }

    const channelDeleteButton = event.target.closest("[data-channel-delete]");
    if (channelDeleteButton) {
      const [group, channelId] = channelDeleteButton.dataset.channelDelete.split("|");
      deleteChannel(group, channelId);
    }

    const platformUserToggle = event.target.closest("[data-platform-user-toggle]");
    if (platformUserToggle) {
      const [companyId, userId, active] = platformUserToggle.dataset.platformUserToggle.split("|");
      updatePlatformUserStatus(companyId, userId, active === "1");
    }

    const platformProjectStatus = event.target.closest("[data-platform-project-status]");
    if (platformProjectStatus) {
      const [companyId, portfolioId, status] = platformProjectStatus.dataset.platformProjectStatus.split("|");
      updatePlatformProjectStatus(companyId, portfolioId, status);
    }

    const editTypification = event.target.closest("[data-edit-typification]");
    if (editTypification) {
      const [companyId, nodeId] = editTypification.dataset.editTypification.split("|");
      fillTypificationForm(companyId, nodeId);
    }

    const deleteTypification = event.target.closest("[data-delete-typification]");
    if (deleteTypification) {
      const [companyId, nodeId] = deleteTypification.dataset.deleteTypification.split("|");
      deletePlatformTypification(companyId, nodeId);
    }
  });

  elements.globalSearch.addEventListener("input", () => {
    customerPage = 1;
    queuePage = 1;
    renderAll();
  });
  document.querySelector("#dashboardSegmentFilter").addEventListener("change", renderDashboard);
  document.querySelector("#queueAgentFilter").addEventListener("change", () => {
    queuePage = 1;
    renderQueue();
  });
  document.querySelector("#queueStatusFilter").addEventListener("change", () => {
    queuePage = 1;
    renderQueue();
  });
  document.querySelector("#queueRiskFilter").addEventListener("change", () => {
    queuePage = 1;
    renderQueue();
  });
  document.querySelector("#customerPortfolioFilter").addEventListener("change", () => {
    customerPage = 1;
    renderCustomers();
  });
  document.querySelector("#customerAgentFilter").addEventListener("change", () => {
    customerPage = 1;
    renderCustomers();
  });
  document.querySelector("#customerStatusFilter").addEventListener("change", () => {
    customerPage = 1;
    renderCustomers();
  });
  document.querySelector("#customerPageSize").addEventListener("change", () => {
    customerPage = 1;
    renderCustomers();
  });
  document.querySelector("#tenantUserCompany")?.addEventListener("change", hydrateTenantLeaderOptions);
  document.querySelector("#tenantCustomerCompany")?.addEventListener("change", hydrateTenantCustomerOptions);
  document.querySelector("#typificationCompany")?.addEventListener("change", () => {
    resetTypificationForm(false);
    hydrateTypificationParentOptions();
    renderTypificationAdmin();
  });
  elements.customerPrevPage.addEventListener("click", () => {
    customerPage = Math.max(1, customerPage - 1);
    renderCustomers();
  });
  elements.customerNextPage.addEventListener("click", () => {
    customerPage += 1;
    renderCustomers();
  });
  elements.queuePrevPage.addEventListener("click", () => {
    queuePage = Math.max(1, queuePage - 1);
    renderQueue();
  });
  elements.queueNextPage.addEventListener("click", () => {
    queuePage += 1;
    renderQueue();
  });
  document.querySelector("#promiseFilter").addEventListener("change", renderPromises);
  document.querySelector("#exportCsvBtn").addEventListener("click", exportCustomersCsv);
  document.querySelector("#newCaseBtn").addEventListener("click", openCustomerModal);
  document.querySelector("#openCustomerFormBtn").addEventListener("click", openCustomerModal);
  document.querySelector("#closeCustomerModalBtn").addEventListener("click", closeCustomerModal);
  document.querySelector("#cancelCustomerBtn").addEventListener("click", closeCustomerModal);
}

function wireForms() {
  document.querySelector("#promiseForm").addEventListener("submit", (event) => {
    event.preventDefault();
    const customerId = document.querySelector("#promiseCustomer").value;
    const amount = Number(document.querySelector("#promiseAmount").value);
    const date = document.querySelector("#promiseDate").value;
    const channel = document.querySelector("#promiseChannel").value;
    const newPromise = promise(nextId("P", state.promises), customerId, amount, date, channel, "Vigente");
    state.promises.unshift(newPromise);
    updateCustomer(customerId, {
      status: "Promesa",
      nextAction: "Confirmar cumplimiento de promesa",
      nextContact: date
    });
    pushTimeline(customerId, "Promesa registrada", `Compromiso por ${money(amount)} para ${formatDate(date)}.`, currentAgent(customerId));
    saveAndRender("Promesa guardada correctamente.");
    event.target.reset();
    setDefaultDates();
  });

  document.querySelector("#paymentForm").addEventListener("submit", (event) => {
    event.preventDefault();
    const customerId = document.querySelector("#paymentCustomer").value;
    const amount = Number(document.querySelector("#paymentAmount").value);
    const date = document.querySelector("#paymentDate").value;
    const method = document.querySelector("#paymentMethod").value;
    const reference = document.querySelector("#paymentReference").value || `REF-${Date.now().toString().slice(-6)}`;
    state.payments.unshift(payment(nextId("PAY", state.payments), customerId, amount, date, method, reference));

    const customer = findCustomer(customerId);
    const newBalance = Math.max(0, customer.balance - amount);
    updateCustomer(customerId, {
      balance: newBalance,
      status: newBalance === 0 ? "Contactado" : customer.status,
      nextAction: newBalance === 0 ? "Cerrar expediente y enviar paz y salvo" : "Confirmar saldo restante",
      lastContact: date
    });

    state.promises = state.promises.map((item) => {
      if (item.customerId === customerId && item.status === "Vigente" && amount >= item.amount) {
        return { ...item, status: "Cumplida" };
      }
      return item;
    });

    pushTimeline(customerId, "Pago registrado", `${money(amount)} via ${method}. Referencia ${reference}.`, currentAgent(customerId), date);
    saveAndRender("Pago aplicado al expediente.");
    event.target.reset();
    setDefaultDates();
  });

  document.querySelector("#campaignForm").addEventListener("submit", (event) => {
    event.preventDefault();
    const segment = document.querySelector("#campaignSegment").value;
    const matchingCustomers = state.customers.filter((customer) => customer.segment === segment);
    state.campaigns.unshift({
      id: nextId("CAM", state.campaigns),
      name: document.querySelector("#campaignName").value,
      segment,
      channel: document.querySelector("#campaignChannel").value,
      template: document.querySelector("#campaignTemplate").value,
      createdAt: isoToday,
      sent: matchingCustomers.length,
      contacted: 0,
      promises: 0,
      payments: 0
    });
    saveAndRender("Campana creada con segmento calculado.");
    event.target.reset();
    hydrateCampaignDefaults();
  });

  document.querySelector("#assignmentUploadForm").addEventListener("submit", async (event) => {
    event.preventDefault();
    if (!canManageAssignments()) {
      showToast("Tu rol no puede cargar repartos.");
      return;
    }
    const file = document.querySelector("#assignmentCsvFile").files[0];
    if (!file) return;
    const portfolioName = document.querySelector("#assignmentPortfolioName").value.trim();
    const portfolioCode = document.querySelector("#assignmentPortfolioCode").value.trim();
    const leaderUserId = Number(document.querySelector("#assignmentLeader").value) || null;
    const defaultAgent = document.querySelector("#assignmentDefaultAgent").value;
    const csvText = await file.text();
    const imported = importAssignmentCsv(csvText, {
      portfolioName,
      portfolioCode,
      leaderUserId,
      defaultAgent
    });
    if (!imported.count) {
      showToast("No se encontraron clientes validos en el CSV.");
      return;
    }
    await saveAndRender(`Reparto cargado: ${imported.count} clientes.`);
    event.target.reset();
    populateStaticOptions();
  });

  document.querySelector("#userCreateForm").addEventListener("submit", async (event) => {
    event.preventDefault();
    try {
      const payload = await apiFetch("/api/users", {
        method: "POST",
        body: {
          name: document.querySelector("#userName").value,
          email: document.querySelector("#userEmail").value,
          role: document.querySelector("#userRole").value,
          leaderId: document.querySelector("#userLeader").value || null,
          password: document.querySelector("#userPassword").value
        }
      });
      state = hydrateState(payload.state);
      currentUser = payload.user || currentUser;
      populateStaticOptions();
      renderAll();
      event.target.reset();
      showToast("Usuario creado correctamente.");
    } catch (error) {
      showToast(error.message || "No se pudo crear el usuario.");
    }
  });

  document.querySelector("#portfolioUserForm").addEventListener("submit", async (event) => {
    event.preventDefault();
    try {
      const payload = await apiFetch("/api/portfolio-users", {
        method: "POST",
        body: {
          portfolioId: document.querySelector("#portfolioUserPortfolio").value,
          userId: document.querySelector("#portfolioUserUser").value,
          assignmentRole: document.querySelector("#portfolioUserRole").value,
          leaderId: document.querySelector("#portfolioUserLeader").value || null
        }
      });
      state = hydrateState(payload.state);
      currentUser = payload.user || currentUser;
      populateStaticOptions();
      renderAll();
      showToast("Asociacion guardada.");
    } catch (error) {
      showToast(error.message || "No se pudo guardar la asociacion.");
    }
  });

  document.querySelector("#tenantCreateForm").addEventListener("submit", async (event) => {
    event.preventDefault();
    try {
      const payload = await apiFetch("/api/platform/companies", {
        method: "POST",
        body: {
          name: document.querySelector("#tenantName").value,
          slug: document.querySelector("#tenantSlug").value,
          taxId: document.querySelector("#tenantTaxId").value,
          adminName: document.querySelector("#tenantAdminName").value,
          adminEmail: document.querySelector("#tenantAdminEmail").value,
          adminPassword: document.querySelector("#tenantAdminPassword").value,
          projectName: document.querySelector("#tenantProjectName").value,
          projectCode: document.querySelector("#tenantProjectCode").value
        }
      });
      state = hydrateState(payload.state);
      currentUser = payload.user || currentUser;
      populateStaticOptions();
      renderAll();
      event.target.reset();
      document.querySelector("#tenantAdminPassword").value = "Admin123!";
      document.querySelector("#tenantProjectName").value = "Cartera inicial";
      document.querySelector("#tenantProjectCode").value = "BASE";
      showToast("Empresa creada con entorno inicial.");
    } catch (error) {
      showToast(error.message || "No se pudo crear la empresa.");
    }
  });

  document.querySelector("#tenantProjectForm").addEventListener("submit", async (event) => {
    event.preventDefault();
    try {
      const payload = await apiFetch("/api/platform/portfolios", {
        method: "POST",
        body: {
          companyId: document.querySelector("#tenantProjectCompany").value,
          name: document.querySelector("#tenantProjectOnlyName").value,
          code: document.querySelector("#tenantProjectOnlyCode").value
        }
      });
      state = hydrateState(payload.state);
      currentUser = payload.user || currentUser;
      populateStaticOptions();
      renderAll();
      event.target.reset();
      showToast("Proyecto creado para la empresa.");
    } catch (error) {
      showToast(error.message || "No se pudo crear el proyecto.");
    }
  });

  document.querySelector("#tenantUserForm").addEventListener("submit", async (event) => {
    event.preventDefault();
    try {
      const payload = await apiFetch("/api/platform/users", {
        method: "POST",
        body: {
          companyId: document.querySelector("#tenantUserCompany").value,
          name: document.querySelector("#tenantUserName").value,
          email: document.querySelector("#tenantUserEmail").value,
          role: document.querySelector("#tenantUserRole").value,
          leaderId: document.querySelector("#tenantUserLeader").value || null,
          password: document.querySelector("#tenantUserPassword").value
        }
      });
      state = hydrateState(payload.state);
      currentUser = payload.user || currentUser;
      populateStaticOptions();
      renderAll();
      event.target.reset();
      document.querySelector("#tenantUserPassword").value = "Usuario123!";
      hydrateTenantLeaderOptions();
      showToast("Usuario tenant creado por IcodeUp plataforma.");
    } catch (error) {
      showToast(error.message || "No se pudo crear el usuario tenant.");
    }
  });

  document.querySelector("#tenantCustomerForm").addEventListener("submit", async (event) => {
    event.preventDefault();
    try {
      const payload = await apiFetch("/api/platform/customers", {
        method: "POST",
        body: {
          companyId: document.querySelector("#tenantCustomerCompany").value,
          portfolioId: document.querySelector("#tenantCustomerPortfolio").value,
          agent: document.querySelector("#tenantCustomerAgent").value,
          name: document.querySelector("#tenantCustomerName").value,
          document: document.querySelector("#tenantCustomerDocument").value,
          phone: document.querySelector("#tenantCustomerPhone").value,
          email: document.querySelector("#tenantCustomerEmail").value,
          segment: document.querySelector("#tenantCustomerSegment").value,
          city: document.querySelector("#tenantCustomerCity").value,
          balance: Number(document.querySelector("#tenantCustomerBalance").value),
          dpd: Number(document.querySelector("#tenantCustomerDpd").value),
          notes: document.querySelector("#tenantCustomerNotes").value
        }
      });
      state = hydrateState(payload.state);
      currentUser = payload.user || currentUser;
      populateStaticOptions();
      renderAll();
      event.target.reset();
      hydrateTenantCustomerOptions();
      showToast("Cliente tenant creado desde IcodeUp plataforma.");
    } catch (error) {
      showToast(error.message || "No se pudo crear el cliente tenant.");
    }
  });

  document.querySelector("#typificationForm").addEventListener("submit", async (event) => {
    event.preventDefault();
    try {
      const payload = await apiFetch("/api/platform/typifications", {
        method: "POST",
        body: {
          companyId: document.querySelector("#typificationCompany").value,
          typification: {
            id: document.querySelector("#typificationNodeId").value || null,
            parentId: document.querySelector("#typificationParent").value || null,
            label: document.querySelector("#typificationLabel").value,
            code: document.querySelector("#typificationCode").value,
            nextStatus: document.querySelector("#typificationNextStatus").value,
            channel: document.querySelector("#typificationChannel").value,
            sortOrder: Number(document.querySelector("#typificationSortOrder").value) || 0,
            requiresPromise: document.querySelector("#typificationRequiresPromise").checked,
            requiresPayment: document.querySelector("#typificationRequiresPayment").checked
          }
        }
      });
      state = hydrateState(payload.state);
      currentUser = payload.user || currentUser;
      populateStaticOptions();
      resetTypificationForm(false);
      renderAll();
      showToast("Arbol de tipificacion actualizado.");
    } catch (error) {
      showToast(error.message || "No se pudo guardar la tipificacion.");
    }
  });

  document.querySelector("#typificationResetBtn").addEventListener("click", () => resetTypificationForm());

  document.querySelector("#settingsForm").addEventListener("submit", (event) => {
    event.preventDefault();
    state.settings.monthlyGoal = Number(document.querySelector("#monthlyGoal").value);
    state.settings.promiseAlertDays = Number(document.querySelector("#promiseAlertDays").value);
    state.settings.criticalDpd = Number(document.querySelector("#criticalDpd").value);
    saveAndRender("Parametros actualizados.");
  });

  document.querySelector("#whatsappChannelForm").addEventListener("submit", (event) => {
    event.preventDefault();
    addChannel("whatsappNumbers", channelAccount(
      nextChannelId("WA", state.communication.whatsappNumbers),
      "whatsapp",
      document.querySelector("#whatsappChannelLabel").value,
      document.querySelector("#whatsappChannelValue").value,
      document.querySelector("#whatsappChannelProvider").value,
      document.querySelector("#whatsappChannelDefault").checked,
      { mode: "link", businessProfile: currentUser?.companyName || "IcodeUp CRM" }
    ));
    event.target.reset();
    document.querySelector("#whatsappChannelProvider").value = "WhatsApp Web / Cloud API pendiente";
  });

  document.querySelector("#emailChannelForm").addEventListener("submit", (event) => {
    event.preventDefault();
    addChannel("emailAccounts", channelAccount(
      nextChannelId("EMAIL", state.communication.emailAccounts),
      "email",
      document.querySelector("#emailChannelLabel").value,
      document.querySelector("#emailChannelValue").value,
      document.querySelector("#emailChannelProvider").value,
      document.querySelector("#emailChannelDefault").checked,
      { signature: `Equipo de cobranzas ${currentUser?.companyName || "IcodeUp CRM"}` }
    ));
    event.target.reset();
    document.querySelector("#emailChannelProvider").value = "SMTP/API pendiente";
  });

  document.querySelector("#telephonyChannelForm").addEventListener("submit", (event) => {
    event.preventDefault();
    addChannel("telephonyAccounts", channelAccount(
      nextChannelId("TEL", state.communication.telephonyAccounts),
      "telephony",
      document.querySelector("#telephonyChannelLabel").value,
      document.querySelector("#telephonyChannelValue").value,
      document.querySelector("#telephonyChannelProvider").value,
      state.communication.telephonyAccounts.length === 0,
      { mode: "planned", sipDomain: "", webSocketUrl: document.querySelector("#telephonyChannelValue").value }
    ));
    event.target.reset();
    document.querySelector("#telephonyChannelProvider").value = "SIP/WebRTC pendiente";
  });

  document.querySelector("#customerForm").addEventListener("submit", (event) => {
    event.preventDefault();
    const dpd = Number(document.querySelector("#newDpd").value);
    const balance = Number(document.querySelector("#newBalance").value);
    const customer = {
      id: nextId("C", state.customers),
      name: document.querySelector("#newName").value,
      document: document.querySelector("#newDocument").value,
      phone: document.querySelector("#newPhone").value,
      email: document.querySelector("#newEmail").value,
      city: "",
      segment: document.querySelector("#newSegment").value,
      agent: document.querySelector("#newAgent").value,
      balance,
      originalBalance: balance,
      dpd,
      status: "Sin contacto",
      risk: riskFromDpd(dpd, balance),
      priority: scoreCustomer({ dpd, balance, risk: riskFromDpd(dpd, balance), status: "Sin contacto", contactability: "Media" }),
      nextAction: "Primer contacto y validacion de datos",
      lastContact: "",
      nextContact: isoToday,
      contactability: "Media",
      accounts: ["Cuenta principal"],
      tags: ["Nuevo caso"],
      notes: document.querySelector("#newNotes").value,
      timeline: [
        activity("Caso creado", document.querySelector("#newNotes").value || "Ingreso manual a la cartera.", document.querySelector("#newAgent").value, isoToday)
      ]
    };
    state.customers.unshift(customer);
    selectedCustomerId = customer.id;
    saveAndRender("Caso creado y asignado.");
    closeCustomerModal();
    event.target.reset();
  });

  document.querySelector("#seedDataBtn").addEventListener("click", () => {
    state = structuredClone(defaultState);
    saveAndRender("Datos demo restaurados.");
    populateStaticOptions();
    applySettingsToForm();
  });

  document.querySelector("#clearDataBtn").addEventListener("click", () => {
    if (!confirm("Seguro que deseas borrar los datos locales del CRM?")) return;
    localStorage.removeItem(STORAGE_KEY);
    state = structuredClone(defaultState);
    selectedCustomerId = state.customers[0]?.id || null;
    saveAndRender("Datos locales reiniciados.");
  });
}

function populateStaticOptions() {
  fillOptions("#dashboardSegmentFilter", ["all", ...state.segments], ["Todos los segmentos", ...state.segments]);
  fillOptions("#queueAgentFilter", ["all", ...state.agents], ["Todos los agentes", ...state.agents]);
  fillOptions("#customerPortfolioFilter", ["all", ...state.portfolios.map((item) => item.id)], ["Todas las carteras", ...state.portfolios.map((item) => item.name)]);
  fillOptions("#customerAgentFilter", ["all", ...state.agents], ["Todos los gestores", ...state.agents]);
  fillOptions("#promiseCustomer", state.customers.map((customer) => customer.id), state.customers.map((customer) => customer.name));
  fillOptions("#paymentCustomer", state.customers.map((customer) => customer.id), state.customers.map((customer) => customer.name));
  fillOptions("#campaignSegment", state.segments, state.segments);
  fillOptions("#newSegment", state.segments, state.segments);
  fillOptions("#newAgent", state.agents, state.agents);
  const leaders = state.users.filter((user) => ["superadmin", "admin", "coordinator"].includes(user.role));
  fillOptions("#assignmentLeader", leaders.map((user) => user.id), leaders.map((user) => `${user.name} (${ROLE_LABELS[user.role]})`));
  fillOptions("#assignmentDefaultAgent", state.agents, state.agents);
  fillOptions("#userLeader", ["", ...leaders.map((user) => user.id)], ["Sin lider", ...leaders.map((user) => `${user.name} (${ROLE_LABELS[user.role]})`)]);
  fillOptions("#portfolioUserLeader", ["", ...leaders.map((user) => user.id)], ["Sin cambio", ...leaders.map((user) => `${user.name} (${ROLE_LABELS[user.role]})`)]);
  fillOptions("#portfolioUserPortfolio", state.portfolios.map((item) => item.id), state.portfolios.map((item) => `${item.name} (${item.code})`));
  fillOptions("#portfolioUserUser", state.users.map((user) => user.id), state.users.map((user) => `${user.name} (${ROLE_LABELS[user.role]})`));
  const tenantCompanies = state.companies || [];
  const tenantCompanyValues = tenantCompanies.length ? tenantCompanies.map((company) => String(company.id)) : [""];
  const tenantCompanyLabels = tenantCompanies.length ? tenantCompanies.map((company) => company.name) : ["Sin empresas creadas"];
  fillOptions("#tenantProjectCompany", tenantCompanyValues, tenantCompanyLabels);
  fillOptions("#tenantUserCompany", tenantCompanyValues, tenantCompanyLabels);
  fillOptions("#tenantCustomerCompany", tenantCompanyValues, tenantCompanyLabels);
  fillOptions("#typificationCompany", tenantCompanyValues, tenantCompanyLabels);
  document.querySelector("#tenantProjectForm button[type='submit']")?.toggleAttribute("disabled", !tenantCompanies.length);
  document.querySelector("#tenantUserForm button[type='submit']")?.toggleAttribute("disabled", !tenantCompanies.length);
  document.querySelector("#tenantCustomerForm button[type='submit']")?.toggleAttribute("disabled", !tenantCompanies.length);
  document.querySelector("#typificationForm button[type='submit']")?.toggleAttribute("disabled", !tenantCompanies.length);
  hydrateTenantLeaderOptions();
  hydrateTenantCustomerOptions();
  hydrateTypificationParentOptions();
  setDefaultDates();
  hydrateCampaignDefaults();
}

function hydrateTenantLeaderOptions() {
  const companyId = document.querySelector("#tenantUserCompany")?.value;
  const company = (state.companies || []).find((item) => String(item.id) === String(companyId));
  const leaders = (company?.users || []).filter((user) => ["superadmin", "admin", "coordinator"].includes(user.role) && user.active);
  fillOptions(
    "#tenantUserLeader",
    ["", ...leaders.map((user) => user.id)],
    ["Sin lider", ...leaders.map((user) => `${user.name} (${ROLE_LABELS[user.role] || user.role})`)]
  );
}

function hydrateTenantCustomerOptions() {
  const company = selectedTenantCompany("#tenantCustomerCompany");
  const portfolios = company?.portfolios || [];
  const users = (company?.users || []).filter((user) => ["agent", "coordinator", "admin", "superadmin"].includes(user.role) && user.active);
  fillOptions(
    "#tenantCustomerPortfolio",
    portfolios.map((item) => item.id),
    portfolios.map((item) => `${item.name} (${item.code})`)
  );
  fillOptions(
    "#tenantCustomerAgent",
    users.map((user) => user.name),
    users.map((user) => `${user.name} (${ROLE_LABELS[user.role] || user.role})`)
  );
  fillOptions("#tenantCustomerSegment", defaultState.segments, defaultState.segments);
}

function selectedTenantCompany(selector) {
  const companyId = document.querySelector(selector)?.value;
  return (state.companies || []).find((item) => String(item.id) === String(companyId));
}

function applySettingsToForm() {
  document.querySelector("#monthlyGoal").value = state.settings.monthlyGoal;
  document.querySelector("#promiseAlertDays").value = state.settings.promiseAlertDays;
  document.querySelector("#criticalDpd").value = state.settings.criticalDpd;
}

function setDefaultDates() {
  document.querySelector("#promiseDate").value = addDays(3);
  document.querySelector("#paymentDate").value = isoToday;
}

function hydrateCampaignDefaults() {
  document.querySelector("#campaignTemplate").value = "Hola {{nombre}}, tu saldo vencido es {{saldo}}. Responde este mensaje para acordar una fecha de pago o solicita alternativas de normalizacion.";
}

function setActiveView(view) {
  activeView = view;
  document.querySelectorAll(".nav-item").forEach((button) => {
    button.classList.toggle("active", button.dataset.view === view);
  });
  document.querySelectorAll(".view").forEach((section) => {
    section.classList.toggle("active", section.id === `view-${view}`);
  });
  elements.viewTitle.textContent = titleForView(view);
  renderAll();
}

function renderAll() {
  renderDashboard();
  renderQueue();
  renderCustomers();
  renderPromises();
  renderPayments();
  renderCampaigns();
  renderReports();
  renderBI();
  renderChannelSettings();
  renderPortfolios();
  renderUsers();
  renderTenants();
  renderTypificationAdmin();
  applyRolePermissions();
}

function renderDashboard() {
  const customers = filteredCustomers();
  const totalBalance = sum(customers, "balance");
  const recovered = sum(state.payments, "amount");
  const activePromises = state.promises.filter((item) => item.status === "Vigente");
  const highRisk = customers.filter((customer) => customer.risk === "Alto");
  const promiseValue = sum(activePromises, "amount");
  const goalProgress = Math.min(100, Math.round((recovered / state.settings.monthlyGoal) * 100));
  const contactRate = Math.round((customers.filter((customer) => customer.status !== "Sin contacto").length / Math.max(customers.length, 1)) * 100);
  const overduePromises = state.promises.filter((item) => item.status === "Vencida").length;
  const criticalCases = customers.filter((customer) => customer.dpd >= state.settings.criticalDpd).length;

  elements.metricGrid.innerHTML = [
    metric("Saldo vencido", money(totalBalance), `${customers.length} expedientes activos`, "warning"),
    metric("Recuperado mes", money(recovered), `${goalProgress}% de la meta mensual`, "success"),
    metric("Promesas vigentes", money(promiseValue), `${activePromises.length} compromisos abiertos`, "accent"),
    metric("Riesgo alto", highRisk.length, `${money(sum(highRisk, "balance"))} concentrados`, "danger"),
    metric("Contacto efectivo", `${contactRate}%`, "Clientes con alguna gestion", "violet"),
    metric("Alertas criticas", overduePromises + criticalCases, `${overduePromises} promesas vencidas`, "warning")
  ].join("");

  renderDashboardCommand(customers, recovered, goalProgress, contactRate);
  renderAgingBars(customers);
  renderAgenda();
  renderPortfolioRisk(customers);
  renderTeamSnapshot(customers);
  renderGovernance();
  renderTodayCases();
}

function renderDashboardCommand(customers, recovered, goalProgress, contactRate) {
  const pendingBalance = sum(customers, "balance");
  const todayFollowUps = customers.filter((customer) => customer.nextContact && customer.nextContact <= isoToday).length;
  const portfolioCount = new Set(customers.map((customer) => customer.portfolioId || "sin-cartera")).size;
  const riskExposure = Math.round((sum(customers.filter((customer) => customer.risk === "Alto"), "balance") / Math.max(pendingBalance, 1)) * 100);
  const operationalHealth = Math.max(0, Math.min(100, Math.round((goalProgress * 0.35) + (contactRate * 0.35) + ((100 - riskExposure) * 0.3))));

  elements.dashboardCommandStrip.innerHTML = [
    commandCard("Salud operacional", `${operationalHealth}%`, `Meta ${goalProgress}% | Contacto ${contactRate}%`, "primary"),
    commandCard("Carteras", portfolioCount, "Proyectos activos", ""),
    commandCard("Seguimientos hoy", todayFollowUps, "Vencidos o programados", ""),
    commandCard("Exposicion alto riesgo", `${riskExposure}%`, money(sum(customers.filter((customer) => customer.risk === "Alto"), "balance")), ""),
    commandCard("Recuperado", money(recovered), "Pagos registrados", "")
  ].join("");
}

function renderAgingBars(customers) {
  const groups = [
    { label: "0-30 dias", min: 0, max: 30, className: "" },
    { label: "31-60 dias", min: 31, max: 60, className: "warning" },
    { label: "61-90 dias", min: 61, max: 90, className: "danger" },
    { label: "91+ dias", min: 91, max: Infinity, className: "danger" }
  ].map((group) => {
    const value = sum(customers.filter((customer) => customer.dpd >= group.min && customer.dpd <= group.max), "balance");
    return { ...group, value };
  });
  const max = Math.max(...groups.map((group) => group.value), 1);
  elements.agingBars.innerHTML = groups.map((group) => `
    <div class="aging-row">
      <strong>${group.label}</strong>
      <div class="track"><div class="fill ${group.className}" style="width:${Math.max(5, (group.value / max) * 100)}%"></div></div>
      <span>${money(group.value)}</span>
    </div>
  `).join("");
}

function renderPortfolioRisk(customers) {
  const rows = state.portfolios.map((portfolioItem) => {
    const assigned = customers.filter((customer) => customer.portfolioId === portfolioItem.id);
    const highRisk = assigned.filter((customer) => customer.risk === "Alto");
    return {
      ...portfolioItem,
      count: assigned.length,
      balance: sum(assigned, "balance"),
      highRiskBalance: sum(highRisk, "balance"),
      highRiskCount: highRisk.length
    };
  }).filter((item) => item.count > 0).sort((a, b) => b.balance - a.balance).slice(0, 5);

  elements.portfolioRiskList.innerHTML = rows.map((item) => {
    const riskShare = Math.round((item.highRiskBalance / Math.max(item.balance, 1)) * 100);
    return `
      <article class="portfolio-risk-item">
        <header>
          <div>
            <strong>${escapeHtml(item.name)}</strong>
            <p>${escapeHtml(item.code)} - ${item.count} clientes</p>
          </div>
          ${riskBadge(riskShare >= 45 ? "Alto" : riskShare >= 18 ? "Medio" : "Bajo")}
        </header>
        <div class="track"><div class="fill ${riskShare >= 45 ? "danger" : riskShare >= 18 ? "warning" : ""}" style="width:${Math.max(6, riskShare)}%"></div></div>
        <div class="mini-stat-row">
          ${miniStat("Saldo", money(item.balance))}
          ${miniStat("Alto riesgo", money(item.highRiskBalance))}
          ${miniStat("Concentracion", `${riskShare}%`)}
        </div>
      </article>
    `;
  }).join("") || emptyState("Sin carteras activas en el filtro actual.");
}

function renderTeamSnapshot(customers) {
  const rows = state.agents.map((agent) => {
    const assigned = customers.filter((customer) => customer.agent === agent);
    const assignedIds = assigned.map((customer) => customer.id);
    const recovered = sum(state.payments.filter((item) => assignedIds.includes(item.customerId)), "amount");
    const contactRate = Math.round((assigned.filter((customer) => customer.status !== "Sin contacto").length / Math.max(assigned.length, 1)) * 100);
    const overdue = assigned.filter((customer) => customer.nextContact && customer.nextContact < isoToday).length;
    return { agent, assigned: assigned.length, recovered, contactRate, overdue };
  }).filter((row) => row.assigned > 0).sort((a, b) => b.recovered - a.recovered || b.assigned - a.assigned).slice(0, 6);

  elements.teamSnapshot.innerHTML = rows.map((row) => `
    <article class="team-row">
      <header>
        <strong>${escapeHtml(row.agent)}</strong>
        <span class="badge ${row.overdue ? "medium" : "low"}">${row.overdue} alertas</span>
      </header>
      <div class="mini-stat-row">
        ${miniStat("Asignados", row.assigned)}
        ${miniStat("Contacto", `${row.contactRate}%`)}
        ${miniStat("Recuperado", money(row.recovered))}
      </div>
    </article>
  `).join("") || emptyState("No hay gestores con clientes asignados.");
}

function renderGovernance() {
  const checks = [
    {
      title: "Multiempresa",
      status: currentUser?.companyId ? "Activo" : "Pendiente",
      body: "Datos separados por empresa y sesion."
    },
    {
      title: "Roles y alcance",
      status: ROLE_LABELS[currentUser?.role] || "Local",
      body: "Super usuario, administrador, coordinador, gestor y calidad."
    },
    {
      title: "Trazabilidad",
      status: "Base",
      body: "Gestiones, pagos, promesas y clicks de canal quedan en bitacora."
    },
    {
      title: "Omnicanalidad",
      status: "Preparada",
      body: "Canales configurables antes de conectar APIs reales."
    }
  ];

  elements.governanceList.innerHTML = checks.map((item) => `
    <article class="governance-item">
      <header>
        <strong>${escapeHtml(item.title)}</strong>
        <span class="badge info">${escapeHtml(item.status)}</span>
      </header>
      <p>${escapeHtml(item.body)}</p>
    </article>
  `).join("");
}

function renderAgenda() {
  const upcomingPromises = state.promises
    .filter((item) => item.status === "Vigente" || item.status === "Vencida")
    .sort((a, b) => a.date.localeCompare(b.date))
    .slice(0, 5);

  const followUps = state.customers
    .filter((customer) => customer.nextContact && daysBetween(isoToday, customer.nextContact) <= state.settings.promiseAlertDays)
    .sort((a, b) => a.nextContact.localeCompare(b.nextContact))
    .slice(0, 4);

  const items = [
    ...upcomingPromises.map((item) => {
      const customer = findCustomer(item.customerId);
      return taskItem("Promesa", customer?.name || "Cliente", `${money(item.amount)} para ${formatDate(item.date)} (${item.status})`, item.customerId);
    }),
    ...followUps.map((customer) => taskItem("Seguimiento", customer.name, `${customer.nextAction} - ${formatDate(customer.nextContact)}`, customer.id))
  ].slice(0, 7);

  elements.criticalAgenda.innerHTML = items.length ? items.join("") : emptyState("Sin alertas criticas para la agenda.");
}

function renderTodayCases() {
  const rows = filteredCustomers()
    .sort((a, b) => scoreCustomer(b) - scoreCustomer(a))
    .slice(0, 7)
    .map((customer) => `
      <tr>
        <td>${nameStack(customer)}</td>
        <td>${customer.segment}</td>
        <td>${money(customer.balance)}</td>
        <td>${customer.dpd} dias</td>
        <td>${riskBadge(customer.risk)}</td>
        <td>${customer.nextAction}</td>
        <td><button class="ghost-button compact" data-open-customer="${customer.id}" type="button">Abrir</button></td>
      </tr>
    `);

  elements.todayCasesTable.innerHTML = rows.join("") || tableEmptyRow(7, "No hay casos con los filtros actuales.");
}

function queueCustomers() {
  const agent = document.querySelector("#queueAgentFilter").value;
  const status = document.querySelector("#queueStatusFilter").value;
  const risk = document.querySelector("#queueRiskFilter").value;
  return filteredCustomers()
    .filter((customer) => agent === "all" || customer.agent === agent)
    .filter((customer) => status === "all" || customer.status === status)
    .filter((customer) => risk === "all" || customer.risk === risk)
    .sort((a, b) => scoreCustomer(b) - scoreCustomer(a));
}

function pageForCustomerInQueue(customerId) {
  const index = queueCustomers().findIndex((customer) => customer.id === customerId);
  return index >= 0 ? Math.floor(index / QUEUE_PAGE_SIZE) + 1 : 1;
}

function sortedTimeline(timeline = []) {
  return [...timeline]
    .map((entry, index) => ({ ...entry, originalIndex: index }))
    .sort((a, b) => String(b.date || "").localeCompare(String(a.date || "")) || a.originalIndex - b.originalIndex);
}

function renderQueue() {
  const customers = queueCustomers();
  const totalPages = Math.max(1, Math.ceil(customers.length / QUEUE_PAGE_SIZE));
  queuePage = Math.min(Math.max(1, queuePage), totalPages);
  const start = (queuePage - 1) * QUEUE_PAGE_SIZE;
  const visible = customers.slice(start, start + QUEUE_PAGE_SIZE);

  elements.queueResultsBar.textContent = `${customers.length} casos encontrados. Mostrando ${visible.length} de maximo ${QUEUE_PAGE_SIZE} por pagina.`;
  elements.queuePageLabel.textContent = `Pagina ${queuePage} de ${totalPages}`;
  elements.queuePrevPage.disabled = queuePage <= 1;
  elements.queueNextPage.disabled = queuePage >= totalPages;
  elements.queueTable.innerHTML = visible.map((customer) => `
    <tr>
      <td><strong>${scoreCustomer(customer)}</strong></td>
      <td>${nameStack(customer)}</td>
      <td>${customer.document}</td>
      <td>${money(customer.balance)}</td>
      <td>${customer.dpd}</td>
      <td>${statusBadge(customer.status)}</td>
      <td>${customer.agent}</td>
      <td><button class="ghost-button compact" data-open-customer="${customer.id}" type="button">Gestionar</button></td>
    </tr>
  `).join("") || tableEmptyRow(8, "La cola no tiene resultados.");

  if (!customers.find((customer) => customer.id === selectedCustomerId)) {
    selectedCustomerId = customers[0]?.id || null;
    activityPage = 1;
  } else if (!visible.find((customer) => customer.id === selectedCustomerId)) {
    selectedCustomerId = visible[0]?.id || customers[0]?.id || null;
    activityPage = 1;
  }
  renderQueueDetail();
}

function renderQueueDetail() {
  const customer = findCustomer(selectedCustomerId);
  if (!customer) {
    elements.queueDetailPanel.innerHTML = `<div class="empty-detail">Selecciona un caso para ver el expediente.</div>`;
    return;
  }
  const phoneHref = `tel:${cleanPhone(customer.phone)}`;
  const whatsappChannel = defaultChannel("whatsappNumbers");
  const emailChannel = defaultChannel("emailAccounts");
  const telephonyChannel = defaultChannel("telephonyAccounts");
  const whatsAppMessage = `Hola ${customer.name}, te contactamos desde ${currentUser?.companyName || "IcodeUp CRM"} para revisar alternativas de normalizacion de tu obligacion.`;
  const emailBody = `Hola ${customer.name},\n\nTe contactamos desde ${currentUser?.companyName || "IcodeUp CRM"} para revisar el estado de tu obligacion y acordar una alternativa de pago.\n\nRemitente configurado: ${emailChannel?.label || "Sin cuenta configurada"} (${emailChannel?.value || "pendiente"}).`;
  const whatsAppHref = `https://wa.me/${phoneDigits(customer.phone)}?text=${encodeURIComponent(whatsAppMessage)}`;
  const emailHref = `mailto:${customer.email || ""}?subject=${encodeURIComponent("Alternativas de normalizacion")}&body=${encodeURIComponent(emailBody)}`;
  const timelineEntries = sortedTimeline(customer.timeline);
  const activityTotalPages = Math.max(1, Math.ceil(timelineEntries.length / ACTIVITY_PAGE_SIZE));
  activityPage = Math.min(Math.max(1, activityPage), activityTotalPages);
  const activityStart = (activityPage - 1) * ACTIVITY_PAGE_SIZE;
  const activityVisible = timelineEntries.slice(activityStart, activityStart + ACTIVITY_PAGE_SIZE);

  elements.queueDetailPanel.innerHTML = `
    <div class="profile-header">
      <div class="item-head">
        <div>
          <h2>${escapeHtml(customer.name)}</h2>
          <p>${escapeHtml(customer.document)} - ${escapeHtml(customer.segment)}</p>
        </div>
        ${riskBadge(customer.risk)}
      </div>
      <div class="badge info">${customer.status}</div>
    </div>

    <div class="profile-grid">
      ${profileStat("Saldo", money(customer.balance))}
      ${profileStat("Mora", `${customer.dpd} dias`)}
      ${profileStat("Agente", customer.agent)}
      ${profileStat("Contactabilidad", customer.contactability)}
      ${profileStat("Cartera", portfolioName(customer.portfolioId))}
      ${profileStat("Ciudad", customer.city || customer.demographic?.ciudad || "Sin dato")}
    </div>

    <div class="case-workspace">
      <section class="case-card case-channel-panel">
        <div class="communication-context">
          <strong>Canales configurados</strong>
          <span>WhatsApp: ${escapeHtml(whatsappChannel?.label || "Sin linea")} ${whatsappChannel?.value ? `(${escapeHtml(whatsappChannel.value)})` : ""}</span>
          <span>Email: ${escapeHtml(emailChannel?.label || "Sin correo")} ${emailChannel?.value ? `(${escapeHtml(emailChannel.value)})` : ""}</span>
          <span>Telefonia: ${escapeHtml(telephonyChannel?.label || "Click to call externo")} ${telephonyChannel?.provider ? `- ${escapeHtml(telephonyChannel.provider)}` : ""}</span>
        </div>

        <div class="action-stack">
          <a class="primary-button" href="${phoneHref}" data-quick-action="${customer.id}|Click to call iniciado desde ${escapeHtml(telephonyChannel?.label || "telefonia externa")}">Click to call</a>
          <a class="ghost-button" href="${whatsAppHref}" target="_blank" rel="noopener" data-quick-action="${customer.id}|WhatsApp abierto desde ${escapeHtml(whatsappChannel?.label || "linea no configurada")}">WhatsApp</a>
          <a class="ghost-button" href="${emailHref}" data-quick-action="${customer.id}|Email abierto desde ${escapeHtml(emailChannel?.label || "correo no configurado")}">Email</a>
          <button class="danger-button" data-quick-action="${customer.id}|Escalado a supervisor" type="button">Escalar caso</button>
        </div>
      </section>

      <form class="management-form case-card" data-management-form="${customer.id}">
        <label>
          Tipificacion
          <select name="typification1" data-typification-level="1">
            ${typificationOptions(null)}
          </select>
        </label>
        <label>
          Subtipificacion
          <select name="typification2" data-typification-level="2">
            <option value="">Selecciona primero una tipificacion</option>
          </select>
        </label>
        <label>
          Calificacion final
          <select name="typification3" data-typification-level="3">
            <option value="">Opcional</option>
          </select>
        </label>
        <label>
          Resultado de gestion
          <select name="result">
            <option>Contactado</option>
            <option>Promesa</option>
            <option>Sin contacto</option>
            <option>Disputa</option>
            <option>Escalado</option>
          </select>
        </label>
        <label>
          Siguiente fecha
          <input name="nextContact" type="date" value="${customer.nextContact || isoToday}" />
        </label>
        <label class="wide-field">
          Nota
          <textarea name="note" rows="3" placeholder="Resumen de conversacion, objecion o acuerdo."></textarea>
        </label>
        <button class="primary-button wide-field" type="submit">Guardar gestion</button>
      </form>

      <section class="activity-panel case-card">
        <div class="section-mini-head">
          <div>
            <h3>Actividad reciente</h3>
            <span>${timelineEntries.length} gestiones registradas</span>
          </div>
          <div class="activity-pager">
            <button class="ghost-button compact" data-activity-page="prev" type="button" ${activityPage <= 1 ? "disabled" : ""}>Anterior</button>
            <span>Pagina ${activityPage} de ${activityTotalPages}</span>
            <button class="ghost-button compact" data-activity-page="next" type="button" ${activityPage >= activityTotalPages ? "disabled" : ""}>Siguiente</button>
          </div>
        </div>
        <div class="table-wrap activity-table-wrap">
          <table class="activity-table">
            <thead>
              <tr>
                <th>Fecha</th>
                <th>Gestion</th>
                <th>Agente</th>
                <th>Detalle</th>
              </tr>
            </thead>
            <tbody>
              ${activityVisible.map((entry) => `
                <tr>
                  <td>${formatDate(entry.date)}</td>
                  <td><strong>${escapeHtml(entry.type)}</strong></td>
                  <td>${escapeHtml(entry.agent)}</td>
                  <td class="activity-note">${escapeHtml(entry.note)}</td>
                </tr>
              `).join("") || tableEmptyRow(4, "Este expediente aun no tiene gestiones.")}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  `;

  const managementForm = elements.queueDetailPanel.querySelector("[data-management-form]");
  wireTypificationForm(managementForm);
  managementForm.addEventListener("submit", (event) => {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const typificationId = form.get("typification3") || form.get("typification2") || form.get("typification1");
    const typificationNode = findTypification(typificationId);
    const result = typificationNode?.nextStatus || form.get("result");
    const typedNote = typificationNode ? `Tipificacion: ${typificationNode.label}. ` : "";
    const note = `${typedNote}${form.get("note") || "Gestion registrada."}`;
    const nextContact = form.get("nextContact");
    updateCustomer(customer.id, {
      status: result,
      nextContact,
      lastContact: isoToday,
      nextAction: typificationNode?.requiresPromise
        ? "Crear promesa de pago y programar confirmacion"
        : typificationNode?.requiresPayment
          ? "Registrar pago y conciliar saldo"
          : actionFromStatus(result)
    });
    pushTimeline(customer.id, result, note, customer.agent);
    activityPage = 1;
    saveAndRender("Gestion guardada en la bitacora.");
  });
}

function renderCustomers() {
  const portfolioFilter = document.querySelector("#customerPortfolioFilter").value;
  const agentFilter = document.querySelector("#customerAgentFilter").value;
  const statusFilter = document.querySelector("#customerStatusFilter").value;
  const pageSize = Math.min(MAX_CUSTOMER_PAGE_SIZE, Number(document.querySelector("#customerPageSize").value) || MAX_CUSTOMER_PAGE_SIZE);
  const customers = filteredCustomers()
    .filter((customer) => portfolioFilter === "all" || customer.portfolioId === portfolioFilter)
    .filter((customer) => agentFilter === "all" || customer.agent === agentFilter)
    .filter((customer) => statusFilter === "all" || customer.status === statusFilter)
    .sort((a, b) => scoreCustomer(b) - scoreCustomer(a));
  const totalPages = Math.max(1, Math.ceil(customers.length / pageSize));
  customerPage = Math.min(customerPage, totalPages);
  const start = (customerPage - 1) * pageSize;
  const visible = customers.slice(start, start + pageSize);

  elements.customerResultsBar.textContent = `${customers.length} clientes encontrados. Mostrando ${visible.length} de maximo ${MAX_CUSTOMER_PAGE_SIZE} por pagina.`;
  elements.customerPageLabel.textContent = `Pagina ${customerPage} de ${totalPages}`;
  elements.customerPrevPage.disabled = customerPage <= 1;
  elements.customerNextPage.disabled = customerPage >= totalPages;
  elements.customerTable.innerHTML = visible.map((customer) => `
    <tr>
      <td>${nameStack(customer)}</td>
      <td>${escapeHtml(portfolioName(customer.portfolioId))}</td>
      <td>${escapeHtml(customer.agent)}</td>
      <td>${money(customer.balance)}</td>
      <td>${customer.dpd} dias</td>
      <td>${statusBadge(customer.status)}</td>
      <td>${riskBadge(customer.risk)}</td>
      <td><button class="ghost-button compact" data-open-customer="${customer.id}" type="button">Gestionar</button></td>
    </tr>
  `).join("") || tableEmptyRow(8, "No hay clientes con los filtros actuales.");
}

function renderPromises() {
  refreshPromiseStatuses();
  const filter = document.querySelector("#promiseFilter").value;
  const promises = state.promises
    .filter((item) => filter === "all" || item.status === filter)
    .sort((a, b) => a.date.localeCompare(b.date));

  elements.promiseList.innerHTML = promises.map((item) => {
    const customer = findCustomer(item.customerId);
    return `
      <article class="promise-item">
        <div class="item-head">
          <div>
            <h3>${escapeHtml(customer?.name || "Cliente no encontrado")}</h3>
            <p>${money(item.amount)} - ${item.channel} - ${formatDate(item.date)}</p>
          </div>
          ${statusBadge(item.status)}
        </div>
        <div class="topbar-actions">
          <button class="ghost-button compact" data-open-customer="${item.customerId}" type="button">Expediente</button>
          ${item.status !== "Cumplida" ? `<button class="primary-button compact" data-complete-promise="${item.id}" type="button">Marcar cumplida</button>` : ""}
        </div>
      </article>
    `;
  }).join("") || emptyState("No hay promesas en este estado.");
}

function renderPayments() {
  elements.paymentsTable.innerHTML = state.payments
    .sort((a, b) => b.date.localeCompare(a.date))
    .map((item) => {
      const customer = findCustomer(item.customerId);
      return `
        <tr>
          <td>${formatDate(item.date)}</td>
          <td>${escapeHtml(customer?.name || "Cliente no encontrado")}</td>
          <td>${money(item.amount)}</td>
          <td>${item.method}</td>
          <td>${escapeHtml(item.reference)}</td>
        </tr>
      `;
    }).join("") || tableEmptyRow(5, "No hay pagos registrados.");
}

function renderCampaigns() {
  elements.campaignList.innerHTML = state.campaigns.map((campaign) => {
    const conversion = campaign.sent ? Math.round((campaign.payments / campaign.sent) * 100) : 0;
    return `
      <article class="campaign-item">
        <div class="item-head">
          <div>
            <h3>${escapeHtml(campaign.name)}</h3>
            <p>${campaign.channel} - ${campaign.segment} - ${formatDate(campaign.createdAt)}</p>
          </div>
          <span class="badge info">${conversion}% pago</span>
        </div>
        <div class="customer-meta">
          <div><span>Enviados</span><strong>${campaign.sent}</strong></div>
          <div><span>Contactados</span><strong>${campaign.contacted}</strong></div>
          <div><span>Promesas</span><strong>${campaign.promises}</strong></div>
          <div><span>Pagos</span><strong>${campaign.payments}</strong></div>
        </div>
        <p>${escapeHtml(campaign.template)}</p>
      </article>
    `;
  }).join("") || emptyState("No hay campanas creadas.");
}

function renderReports() {
  const customers = state.customers;
  const recovered = sum(state.payments, "amount");
  const totalOriginal = sum(customers, "originalBalance");
  const totalBalance = sum(customers, "balance");
  const contactRate = Math.round((customers.filter((customer) => customer.status !== "Sin contacto").length / Math.max(customers.length, 1)) * 100);
  const promiseRate = Math.round((state.promises.filter((item) => item.status === "Cumplida").length / Math.max(state.promises.length, 1)) * 100);

  elements.reportMetricGrid.innerHTML = [
    metric("Efectividad", `${Math.round((recovered / Math.max(totalOriginal, 1)) * 100)}%`, "Pagos sobre saldo original", "good"),
    metric("Saldo pendiente", money(totalBalance), "Cartera por recuperar", "warn"),
    metric("Contacto", `${contactRate}%`, "Clientes con alguna gestion", "good"),
    metric("Cumplimiento promesas", `${promiseRate}%`, "Promesas cumplidas vs totales", "")
  ].join("");

  renderAgentRecovery();
  renderFunnel(contactRate);
  renderInsights();
  drawBarChart(elements.reportRecoveryChart, monthlyRecoverySeries(), {
    color: "#0f766e",
    title: "Pagos"
  });
  drawDoughnutChart(elements.reportRiskChart, riskDistribution(customers), {
    colors: ["#c2412d", "#b7791f", "#188038"]
  });
}

function renderBI() {
  if (!elements.biMetricGrid) return;
  const customers = state.customers;
  const recovered = sum(state.payments, "amount");
  const totalBalance = sum(customers, "balance");
  const totalOriginal = sum(customers, "originalBalance");
  const activePromises = state.promises.filter((item) => item.status === "Vigente");
  const overduePromises = state.promises.filter((item) => item.status === "Vencida");
  const highRiskBalance = sum(customers.filter((customer) => customer.risk === "Alto"), "balance");
  const recoveryRate = Math.round((recovered / Math.max(totalOriginal, 1)) * 100);
  const promiseCoverage = Math.round((sum(activePromises, "amount") / Math.max(totalBalance, 1)) * 100);
  const contactRate = Math.round((customers.filter((customer) => customer.status !== "Sin contacto").length / Math.max(customers.length, 1)) * 100);
  const riskShare = Math.round((highRiskBalance / Math.max(totalBalance, 1)) * 100);

  elements.biMetricGrid.innerHTML = [
    metric("Recuperacion global", `${recoveryRate}%`, `${money(recovered)} recuperados`, "success"),
    metric("Cartera pendiente", money(totalBalance), `${customers.length} clientes visibles`, "warning"),
    metric("Cobertura promesas", `${promiseCoverage}%`, `${activePromises.length} promesas vigentes`, "accent"),
    metric("Contacto operativo", `${contactRate}%`, "Clientes con gestion registrada", "violet"),
    metric("Exposicion alto riesgo", `${riskShare}%`, money(highRiskBalance), "danger"),
    metric("Promesas vencidas", overduePromises.length, "Requieren accion inmediata", "warning")
  ].join("");

  drawLineChart(elements.biRecoveryChart, executiveRecoverySeries(), {
    color: "#2f67d8",
    fill: "rgba(47,103,216,0.12)"
  });
  const riskData = riskDistribution(customers);
  drawDoughnutChart(elements.biRiskDonut, riskData, {
    colors: ["#c2412d", "#b7791f", "#188038"]
  });
  elements.biRiskLegend.innerHTML = riskData.map((item, index) => `
    <span><i style="background:${["#c2412d", "#b7791f", "#188038"][index]}"></i>${item.label}: ${money(item.value)}</span>
  `).join("");
  drawHorizontalBarChart(elements.biPortfolioChart, portfolioExposureSeries(customers), {
    color: "#0f766e"
  });
  drawGroupedBarChart(elements.biAgentChart, agentProductivitySeries(customers), {
    colors: ["#2f67d8", "#0f766e"]
  });
  drawBarChart(elements.biAgingChart, agingSeries(customers), {
    color: "#6d5bd0"
  });
  renderBIDecisions({ customers, recovered, totalBalance, highRiskBalance, contactRate, overduePromises, riskShare });
}

function monthlyRecoverySeries() {
  return executiveRecoverySeries().map((item) => ({
    label: item.label,
    value: item.recovered
  }));
}

function executiveRecoverySeries() {
  const months = [];
  for (let offset = 5; offset >= 0; offset -= 1) {
    const date = new Date(today.getFullYear(), today.getMonth() - offset, 1);
    const key = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}`;
    months.push({
      key,
      label: new Intl.DateTimeFormat("es-CO", { month: "short" }).format(date),
      recovered: 0,
      target: Math.round(state.settings.monthlyGoal / 6)
    });
  }
  state.payments.forEach((item) => {
    const key = String(item.date || "").slice(0, 7);
    const month = months.find((entry) => entry.key === key);
    if (month) month.recovered += Number(item.amount || 0);
  });
  return months;
}

function riskDistribution(customers) {
  return [
    { label: "Alto", value: sum(customers.filter((customer) => customer.risk === "Alto"), "balance") },
    { label: "Medio", value: sum(customers.filter((customer) => customer.risk === "Medio"), "balance") },
    { label: "Bajo", value: sum(customers.filter((customer) => customer.risk === "Bajo"), "balance") }
  ];
}

function portfolioExposureSeries(customers) {
  return state.portfolios.map((item) => {
    const assigned = customers.filter((customer) => customer.portfolioId === item.id);
    return {
      label: item.code || item.name,
      value: sum(assigned, "balance")
    };
  }).filter((item) => item.value > 0).sort((a, b) => b.value - a.value).slice(0, 6);
}

function agentProductivitySeries(customers) {
  return state.agents.map((agent) => {
    const assigned = customers.filter((customer) => customer.agent === agent);
    const assignedIds = assigned.map((customer) => customer.id);
    const recovered = sum(state.payments.filter((item) => assignedIds.includes(item.customerId)), "amount");
    return {
      label: agent,
      assigned: assigned.length,
      recovered
    };
  }).filter((item) => item.assigned > 0).slice(0, 6);
}

function agingSeries(customers) {
  const buckets = [
    { label: "0-30", min: 0, max: 30, value: 0 },
    { label: "31-60", min: 31, max: 60, value: 0 },
    { label: "61-90", min: 61, max: 90, value: 0 },
    { label: "91+", min: 91, max: Infinity, value: 0 }
  ];
  customers.forEach((customer) => {
    const bucket = buckets.find((item) => customer.dpd >= item.min && customer.dpd <= item.max);
    if (bucket) bucket.value += customer.balance;
  });
  return buckets;
}

function renderBIDecisions({ customers, totalBalance, highRiskBalance, contactRate, overduePromises, riskShare }) {
  const staleCases = customers.filter((customer) => customer.lastContact && daysBetween(customer.lastContact, isoToday) > 7);
  const noContactBalance = sum(customers.filter((customer) => customer.status === "Sin contacto"), "balance");
  const decisions = [
    {
      title: "Priorizar riesgo alto",
      impact: riskShare >= 35 ? "Alto" : "Medio",
      body: `El ${riskShare}% del saldo visible esta en riesgo alto (${money(highRiskBalance)}). Asignar gestores senior y ruta de normalizacion.`
    },
    {
      title: "Recuperar contacto",
      impact: contactRate < 70 ? "Alto" : "Controlado",
      body: `${money(noContactBalance)} esta en clientes sin contacto. Activar enriquecimiento de datos y canales alternos.`
    },
    {
      title: "Cerrar promesas vencidas",
      impact: overduePromises.length ? "Alto" : "Bajo",
      body: `${overduePromises.length} promesas vencidas deben pasar a seguimiento humano antes de automatizar mensajes.`
    },
    {
      title: "Higiene operacional",
      impact: staleCases.length ? "Medio" : "Controlado",
      body: `${staleCases.length} clientes tienen mas de 7 dias sin gestion reciente. Rebalancear cola por prioridad.`
    },
    {
      title: "Exposicion total",
      impact: "Referencia",
      body: `La cartera pendiente visible es ${money(totalBalance)}. Mantener seguimiento por cartera, lider y segmento.`
    }
  ];

  elements.biDecisionGrid.innerHTML = decisions.map((item) => `
    <article class="decision-card">
      <header>
        <strong>${escapeHtml(item.title)}</strong>
        <span class="badge ${item.impact === "Alto" ? "high" : item.impact === "Medio" ? "medium" : "info"}">${escapeHtml(item.impact)}</span>
      </header>
      <p>${escapeHtml(item.body)}</p>
    </article>
  `).join("");
}

function prepareCanvas(canvas, fallbackHeight = 260) {
  if (!canvas) return null;
  const parent = canvas.parentElement;
  const width = Math.max(parent?.clientWidth || 540, 320);
  const height = Math.max(parent?.clientHeight || fallbackHeight, fallbackHeight);
  const ratio = window.devicePixelRatio || 1;
  canvas.width = Math.floor(width * ratio);
  canvas.height = Math.floor(height * ratio);
  canvas.style.width = `${width}px`;
  canvas.style.height = `${height}px`;
  const ctx = canvas.getContext("2d");
  ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
  ctx.clearRect(0, 0, width, height);
  const gradient = ctx.createLinearGradient(0, 0, width, height);
  gradient.addColorStop(0, "rgba(255,255,255,0.98)");
  gradient.addColorStop(1, "rgba(246,249,251,0.98)");
  ctx.fillStyle = gradient;
  ctx.fillRect(0, 0, width, height);
  ctx.font = "12px Segoe UI, Arial, sans-serif";
  ctx.lineWidth = 2;
  return { ctx, width, height };
}

function drawBarChart(canvas, data, options = {}) {
  const prepared = prepareCanvas(canvas);
  if (!prepared) return;
  const { ctx, width, height } = prepared;
  const padding = { top: 20, right: 16, bottom: 42, left: 44 };
  const chartWidth = width - padding.left - padding.right;
  const chartHeight = height - padding.top - padding.bottom;
  const max = Math.max(...data.map((item) => item.value), 1);
  drawChartGrid(ctx, padding, chartWidth, chartHeight, max);
  const barWidth = chartWidth / Math.max(data.length, 1) * 0.58;
  data.forEach((item, index) => {
    const x = padding.left + (chartWidth / data.length) * index + (chartWidth / data.length - barWidth) / 2;
    const barHeight = (item.value / max) * chartHeight;
    const y = padding.top + chartHeight - barHeight;
    const gradient = ctx.createLinearGradient(0, y, 0, y + barHeight);
    gradient.addColorStop(0, lightenColor(options.color || "#0f766e", 18));
    gradient.addColorStop(1, options.color || "#0f766e");
    roundedRect(ctx, x, y, barWidth, barHeight, 5, gradient);
    drawAxisLabel(ctx, item.label, x + barWidth / 2, height - 17);
  });
}

function drawHorizontalBarChart(canvas, data, options = {}) {
  const prepared = prepareCanvas(canvas);
  if (!prepared) return;
  const { ctx, width, height } = prepared;
  const padding = { top: 18, right: 28, bottom: 18, left: 84 };
  const chartWidth = width - padding.left - padding.right;
  const rowHeight = (height - padding.top - padding.bottom) / Math.max(data.length, 1);
  const max = Math.max(...data.map((item) => item.value), 1);
  data.forEach((item, index) => {
    const y = padding.top + index * rowHeight + rowHeight * 0.24;
    const barHeight = rowHeight * 0.46;
    const barWidth = Math.max(4, (item.value / max) * chartWidth);
    ctx.fillStyle = "#64717a";
    ctx.textAlign = "right";
    ctx.fillText(truncateLabel(item.label, 10), padding.left - 10, y + barHeight * 0.72);
    const gradient = ctx.createLinearGradient(padding.left, 0, padding.left + barWidth, 0);
    gradient.addColorStop(0, options.color || "#2f67d8");
    gradient.addColorStop(1, lightenColor(options.color || "#2f67d8", 22));
    roundedRect(ctx, padding.left, y, barWidth, barHeight, 5, gradient);
    ctx.fillStyle = "#65727a";
    ctx.textAlign = "left";
    ctx.fillText(compactMoney(item.value), padding.left + barWidth + 8, y + barHeight * 0.72);
  });
}

function drawGroupedBarChart(canvas, data, options = {}) {
  const prepared = prepareCanvas(canvas);
  if (!prepared) return;
  const { ctx, width, height } = prepared;
  const padding = { top: 20, right: 16, bottom: 48, left: 44 };
  const chartWidth = width - padding.left - padding.right;
  const chartHeight = height - padding.top - padding.bottom;
  const maxAssigned = Math.max(...data.map((item) => item.assigned), 1);
  const maxRecovered = Math.max(...data.map((item) => item.recovered), 1);
  const groupWidth = chartWidth / Math.max(data.length, 1);
  const barWidth = groupWidth * 0.22;
  drawChartGrid(ctx, padding, chartWidth, chartHeight, maxAssigned);
  data.forEach((item, index) => {
    const center = padding.left + groupWidth * index + groupWidth / 2;
    const assignedHeight = (item.assigned / maxAssigned) * chartHeight;
    const recoveredHeight = (item.recovered / maxRecovered) * chartHeight;
    roundedRect(ctx, center - barWidth - 2, padding.top + chartHeight - assignedHeight, barWidth, assignedHeight, 4, options.colors?.[0] || "#2f67d8");
    roundedRect(ctx, center + 2, padding.top + chartHeight - recoveredHeight, barWidth, recoveredHeight, 4, options.colors?.[1] || "#0f766e");
    drawAxisLabel(ctx, firstName(item.label), center, height - 17);
  });
}

function drawLineChart(canvas, data, options = {}) {
  const prepared = prepareCanvas(canvas, 300);
  if (!prepared) return;
  const { ctx, width, height } = prepared;
  const padding = { top: 20, right: 22, bottom: 42, left: 54 };
  const chartWidth = width - padding.left - padding.right;
  const chartHeight = height - padding.top - padding.bottom;
  const max = Math.max(...data.map((item) => Math.max(item.recovered, item.target || 0)), 1);
  drawChartGrid(ctx, padding, chartWidth, chartHeight, max);
  const points = data.map((item, index) => ({
    x: padding.left + (chartWidth / Math.max(data.length - 1, 1)) * index,
    y: padding.top + chartHeight - (item.recovered / max) * chartHeight,
    label: item.label
  }));
  ctx.beginPath();
  points.forEach((point, index) => index ? ctx.lineTo(point.x, point.y) : ctx.moveTo(point.x, point.y));
  ctx.shadowColor = "rgba(47, 103, 216, 0.28)";
  ctx.shadowBlur = 12;
  ctx.strokeStyle = options.color || "#2f67d8";
  ctx.lineWidth = 3;
  ctx.stroke();
  ctx.shadowBlur = 0;
  ctx.lineTo(points.at(-1).x, padding.top + chartHeight);
  ctx.lineTo(points[0].x, padding.top + chartHeight);
  ctx.closePath();
  ctx.fillStyle = options.fill || "rgba(47,103,216,0.1)";
  ctx.fill();
  points.forEach((point) => {
    ctx.beginPath();
    ctx.arc(point.x, point.y, 4, 0, Math.PI * 2);
    ctx.fillStyle = "#ffffff";
    ctx.fill();
    ctx.strokeStyle = options.color || "#2f67d8";
    ctx.stroke();
    drawAxisLabel(ctx, point.label, point.x, height - 17);
  });
}

function drawDoughnutChart(canvas, data, options = {}) {
  const prepared = prepareCanvas(canvas);
  if (!prepared) return;
  const { ctx, width, height } = prepared;
  const total = Math.max(sum(data, "value"), 1);
  const colors = options.colors || ["#c2412d", "#b7791f", "#188038"];
  const radius = Math.min(width, height) * 0.32;
  const centerX = width / 2;
  const centerY = height / 2;
  let start = -Math.PI / 2;
  data.forEach((item, index) => {
    const angle = (item.value / total) * Math.PI * 2;
    ctx.beginPath();
    ctx.arc(centerX, centerY, radius, start, start + angle);
    ctx.arc(centerX, centerY, radius * 0.58, start + angle, start, true);
    ctx.closePath();
    ctx.shadowColor = "rgba(18, 31, 38, 0.12)";
    ctx.shadowBlur = 8;
    ctx.fillStyle = colors[index % colors.length];
    ctx.fill();
    ctx.shadowBlur = 0;
    start += angle;
  });
  ctx.fillStyle = "#172026";
  ctx.textAlign = "center";
  ctx.font = "700 20px Segoe UI, Arial, sans-serif";
  ctx.fillText("100%", centerX, centerY - 2);
  ctx.font = "12px Segoe UI, Arial, sans-serif";
  ctx.fillStyle = "#65727a";
  ctx.fillText("cartera", centerX, centerY + 17);
}

function drawChartGrid(ctx, padding, chartWidth, chartHeight, max) {
  ctx.strokeStyle = "#e8eef2";
  ctx.fillStyle = "#65727a";
  ctx.textAlign = "right";
  for (let index = 0; index <= 3; index += 1) {
    const y = padding.top + (chartHeight / 3) * index;
    ctx.beginPath();
    ctx.moveTo(padding.left, y);
    ctx.lineTo(padding.left + chartWidth, y);
    ctx.stroke();
    const value = max - (max / 3) * index;
    ctx.fillText(compactMoney(value), padding.left - 8, y + 4);
  }
}

function roundedRect(ctx, x, y, width, height, radius, color) {
  const safeHeight = Math.max(height, 2);
  ctx.beginPath();
  ctx.moveTo(x + radius, y);
  ctx.lineTo(x + width - radius, y);
  ctx.quadraticCurveTo(x + width, y, x + width, y + radius);
  ctx.lineTo(x + width, y + safeHeight - radius);
  ctx.quadraticCurveTo(x + width, y + safeHeight, x + width - radius, y + safeHeight);
  ctx.lineTo(x + radius, y + safeHeight);
  ctx.quadraticCurveTo(x, y + safeHeight, x, y + safeHeight - radius);
  ctx.lineTo(x, y + radius);
  ctx.quadraticCurveTo(x, y, x + radius, y);
  ctx.closePath();
  ctx.fillStyle = color;
  ctx.fill();
}

function lightenColor(hex, amount) {
  const value = String(hex || "#0f766e").replace("#", "");
  const number = parseInt(value.length === 3 ? value.split("").map((char) => char + char).join("") : value, 16);
  const red = Math.min(255, ((number >> 16) & 255) + amount);
  const green = Math.min(255, ((number >> 8) & 255) + amount);
  const blue = Math.min(255, (number & 255) + amount);
  return `rgb(${red}, ${green}, ${blue})`;
}

function drawAxisLabel(ctx, label, x, y) {
  ctx.fillStyle = "#65727a";
  ctx.textAlign = "center";
  ctx.font = "12px Segoe UI, Arial, sans-serif";
  ctx.fillText(truncateLabel(label, 10), x, y);
}

function compactMoney(value) {
  const absolute = Math.abs(Number(value) || 0);
  if (absolute >= 1000000000) return `$${Math.round(absolute / 1000000000)}B`;
  if (absolute >= 1000000) return `$${Math.round(absolute / 1000000)}M`;
  if (absolute >= 1000) return `$${Math.round(absolute / 1000)}K`;
  return `$${Math.round(absolute)}`;
}

function truncateLabel(label, maxLength) {
  const text = String(label || "");
  return text.length > maxLength ? `${text.slice(0, maxLength - 1)}.` : text;
}

function firstName(label) {
  return String(label || "").split(" ")[0] || label;
}

function renderAgentRecovery() {
  const rows = state.agents.map((agent) => {
    const assigned = state.customers.filter((customer) => customer.agent === agent);
    const assignedIds = assigned.map((customer) => customer.id);
    const recovered = state.payments
      .filter((paymentItem) => assignedIds.includes(paymentItem.customerId))
      .reduce((total, item) => total + item.amount, 0);
    const original = sum(assigned, "originalBalance");
    return {
      agent,
      recovered,
      rate: Math.round((recovered / Math.max(original, 1)) * 100)
    };
  });
  const max = Math.max(...rows.map((row) => row.recovered), 1);
  elements.agentRecoveryReport.innerHTML = rows.map((row) => `
    <div class="bar-row">
      <strong>${row.agent}</strong>
      <div class="track"><div class="fill" style="width:${Math.max(5, (row.recovered / max) * 100)}%"></div></div>
      <span>${money(row.recovered)} (${row.rate}%)</span>
    </div>
  `).join("");
}

function renderFunnel(contactRate) {
  const total = state.customers.length;
  const contacted = state.customers.filter((customer) => customer.status !== "Sin contacto").length;
  const promised = new Set(state.promises.map((item) => item.customerId)).size;
  const paid = new Set(state.payments.map((item) => item.customerId)).size;
  const max = Math.max(total, 1);
  const steps = [
    ["Cartera", total],
    ["Contactados", contacted],
    ["Promesas", promised],
    ["Pagos", paid]
  ];
  elements.collectionFunnel.innerHTML = steps.map(([label, value]) => `
    <div class="funnel-step">
      <strong>${label}</strong>
      <div class="funnel-block" style="width:${Math.max(12, (value / max) * 100)}%; background:${label === "Pagos" ? "var(--success)" : label === "Promesas" ? "var(--primary)" : "var(--accent)"}"></div>
      <span>${value}</span>
    </div>
  `).join("") + `<p class="note-box">Tasa de contacto actual: ${contactRate}%.</p>`;
}

function renderInsights() {
  const highRiskBalance = sum(state.customers.filter((customer) => customer.risk === "Alto"), "balance");
  const overduePromises = state.promises.filter((item) => item.status === "Vencida");
  const staleCases = state.customers.filter((customer) => customer.lastContact && daysBetween(customer.lastContact, isoToday) > 7);

  const insights = [
    {
      title: "Concentracion de riesgo",
      body: `La cartera de riesgo alto suma ${money(highRiskBalance)}. Conviene separar alto valor con ruta prejuridica y gestores senior.`
    },
    {
      title: "Promesas vencidas",
      body: `${overduePromises.length} promesas requieren accion inmediata. Prioriza contacto humano antes de campanas masivas.`
    },
    {
      title: "Casos sin contacto reciente",
      body: `${staleCases.length} expedientes superan 7 dias sin interaccion efectiva. Revisa contactabilidad y datos alternos.`
    }
  ];

  elements.insightList.innerHTML = insights.map((insight) => `
    <article class="insight-item">
      <strong>${insight.title}</strong>
      <p>${insight.body}</p>
    </article>
  `).join("");
}

function renderChannelSettings() {
  if (!elements.whatsappChannelList) return;
  elements.whatsappChannelList.innerHTML = renderChannelList("whatsappNumbers", "WhatsApp");
  elements.emailChannelList.innerHTML = renderChannelList("emailAccounts", "Correo");
  elements.telephonyChannelList.innerHTML = renderChannelList("telephonyAccounts", "Telefonia");
}

function renderPortfolios() {
  if (!elements.portfolioList) return;
  elements.portfolioList.innerHTML = state.portfolios.map((item) => {
    const assigned = state.customers.filter((customer) => customer.portfolioId === item.id);
    const leader = state.users.find((user) => Number(user.id) === Number(item.leaderUserId));
    const agents = Array.from(new Set(assigned.map((customer) => customer.agent))).filter(Boolean);
    return `
      <article class="channel-item">
        <header>
          <div>
            <strong>${escapeHtml(item.name)}</strong>
            <p>${escapeHtml(item.code)} - ${assigned.length} clientes</p>
          </div>
          <span class="badge info">${escapeHtml(item.status || "active")}</span>
        </header>
        <p>Lider: ${escapeHtml(leader?.name || "Sin lider asignado")}</p>
        <p>Gestores: ${escapeHtml(agents.join(", ") || "Sin asignacion")}</p>
        <p>Saldo: ${money(sum(assigned, "balance"))}</p>
      </article>
    `;
  }).join("") || emptyState("No hay carteras configuradas.");
}

function renderUsers() {
  if (!elements.userDirectory) return;
  elements.userDirectory.innerHTML = state.users.map((user) => {
    const leader = state.users.find((item) => Number(item.id) === Number(user.leaderId));
    const assignedPortfolios = state.portfolios.filter((portfolioItem) =>
      (portfolioItem.members || []).some((member) => Number(member.userId) === Number(user.id))
    );
    return `
      <article class="user-card">
        <header>
          <div>
            <strong>${escapeHtml(user.name)}</strong>
            <p>${escapeHtml(user.email)}</p>
          </div>
          <span class="badge info">${ROLE_LABELS[user.role] || user.role}</span>
        </header>
        <div class="mini-stat-row">
          ${miniStat("Lider", leader?.name || "Sin lider")}
          ${miniStat("Carteras", assignedPortfolios.length)}
          ${miniStat("Estado", user.active ? "Activo" : "Inactivo")}
        </div>
      </article>
    `;
  }).join("") || emptyState("No hay usuarios visibles.");

  elements.portfolioMembers.innerHTML = state.portfolios.map((portfolioItem) => `
    <article class="user-card">
      <header>
        <div>
          <strong>${escapeHtml(portfolioItem.name)}</strong>
          <p>${escapeHtml(portfolioItem.code)}</p>
        </div>
        <span class="badge info">${(portfolioItem.members || []).length} miembros</span>
      </header>
      <div class="member-list">
        ${(portfolioItem.members || []).map((member) => `
          <span>${escapeHtml(member.name)} <strong>${escapeHtml(member.role)}</strong></span>
        `).join("") || "<span>Sin miembros asociados</span>"}
      </div>
    </article>
  `).join("") || emptyState("No hay carteras para asociar.");
}

function renderTenants() {
  if (!elements.tenantGrid) return;
  elements.tenantGrid.innerHTML = (state.companies || []).map((company) => {
    const users = company.users || [];
    const projects = company.portfolios || [];
    return `
      <article class="tenant-card">
        <header class="tenant-card-header">
          <div>
            <span class="tenant-kicker">Tenant ${escapeHtml(company.slug)}</span>
            <strong>${escapeHtml(company.name)}</strong>
            <p>${company.taxId ? escapeHtml(company.taxId) : "Sin NIT registrado"}</p>
          </div>
          <span class="badge low">${escapeHtml(company.status || "active")}</span>
        </header>

        <div class="mini-stat-row">
          ${miniStat("Usuarios", company.counts?.users || 0)}
          ${miniStat("Proyectos", company.counts?.portfolios || 0)}
          ${miniStat("Clientes", company.counts?.customers || 0)}
        </div>

        <div class="tenant-sections">
          <section class="tenant-section">
            <h3>Proyectos / carteras</h3>
            <div class="inventory-list">
              ${projects.map((project) => {
                const nextStatus = project.status === "active" ? "paused" : "active";
                const actionLabel = project.status === "active" ? "Pausar" : "Activar";
                return `
                  <article class="inventory-row">
                    <div>
                      <strong>${escapeHtml(project.name)}</strong>
                      <p>${escapeHtml(project.code)} · ${project.customers || 0} clientes · ${project.members || 0} miembros</p>
                      <p>Lider: ${escapeHtml(project.leaderName || "Sin lider asignado")}</p>
                    </div>
                    <div class="tenant-actions">
                      <span class="badge info">${escapeHtml(project.status || "active")}</span>
                      <button class="ghost-button compact" data-platform-project-status="${company.id}|${escapeHtml(project.id)}|${nextStatus}" type="button">${actionLabel}</button>
                    </div>
                  </article>
                `;
              }).join("") || emptyState("Sin proyectos creados.")}
            </div>
          </section>

          <section class="tenant-section">
            <h3>Usuarios tenant</h3>
            <div class="inventory-list">
              ${users.map((tenantUser) => {
                const leader = users.find((item) => Number(item.id) === Number(tenantUser.leaderId));
                const targetActive = tenantUser.active ? "0" : "1";
                const actionLabel = tenantUser.active ? "Inactivar" : "Activar";
                return `
                  <article class="inventory-row">
                    <div>
                      <strong>${escapeHtml(tenantUser.name)}</strong>
                      <p>${escapeHtml(tenantUser.email)}</p>
                      <p>${escapeHtml(ROLE_LABELS[tenantUser.role] || tenantUser.role)} · Lider: ${escapeHtml(leader?.name || "Sin lider")}</p>
                    </div>
                    <div class="tenant-actions">
                      <span class="badge ${tenantUser.active ? "low" : "danger"}">${tenantUser.active ? "Activo" : "Inactivo"}</span>
                      <button class="ghost-button compact" data-platform-user-toggle="${company.id}|${tenantUser.id}|${targetActive}" type="button">${actionLabel}</button>
                    </div>
                  </article>
                `;
              }).join("") || emptyState("Sin usuarios creados.")}
            </div>
          </section>
        </div>
      </article>
    `;
  }).join("") || emptyState("No hay empresas cliente creadas.");
}

function renderTypificationAdmin() {
  if (!elements.typificationList) return;
  const company = selectedTenantCompany("#typificationCompany");
  if (!company) {
    elements.typificationSummary.textContent = "No hay empresas cliente para parametrizar.";
    elements.typificationList.innerHTML = tableEmptyRow(6, "Crea primero una empresa cliente.");
    return;
  }
  const nodes = sortedTypifications(company.typifications || []);
  elements.typificationSummary.textContent = `${nodes.length} nodos configurados para ${company.name}.`;
  elements.typificationList.innerHTML = nodes.map((node) => {
    const parent = nodes.find((item) => item.id === node.parentId);
    const level = typificationLevel(node, nodes);
    const rules = [
      node.requiresPromise ? "Promesa" : "",
      node.requiresPayment ? "Pago" : "",
      node.channel ? `Canal ${node.channel}` : ""
    ].filter(Boolean).join(" / ") || "Sin regla adicional";
    return `
      <tr>
        <td><span class="badge info">Nivel ${level}</span></td>
        <td>
          <div class="name-stack">
            <strong>${"&nbsp;".repeat(Math.max(0, level - 1) * 3)}${escapeHtml(node.label)}</strong>
            <span>${escapeHtml(node.code)} - ${escapeHtml(node.id)}</span>
          </div>
        </td>
        <td>${escapeHtml(parent?.label || "Raiz")}</td>
        <td>${node.nextStatus ? statusBadge(node.nextStatus) : "<span class=\"badge info\">Sin cambio</span>"}</td>
        <td>${escapeHtml(rules)}</td>
        <td>
          <div class="table-actions">
            <button class="ghost-button compact" data-edit-typification="${company.id}|${escapeHtml(node.id)}" type="button">Editar</button>
            <button class="danger-button compact" data-delete-typification="${company.id}|${escapeHtml(node.id)}" type="button">Eliminar</button>
          </div>
        </td>
      </tr>
    `;
  }).join("") || tableEmptyRow(6, "Esta empresa no tiene tipificaciones.");
}

function sortedTypifications(nodes = []) {
  return [...nodes].sort((a, b) => {
    const levelDiff = typificationLevel(a, nodes) - typificationLevel(b, nodes);
    return levelDiff || Number(a.sortOrder || 0) - Number(b.sortOrder || 0) || String(a.label || "").localeCompare(String(b.label || ""));
  });
}

function typificationLevel(node, nodes) {
  let level = 1;
  let parentId = node?.parentId;
  const seen = new Set([node?.id]);
  while (parentId && !seen.has(parentId)) {
    seen.add(parentId);
    const parent = nodes.find((item) => item.id === parentId);
    if (!parent) break;
    level += 1;
    parentId = parent.parentId;
  }
  return level;
}

function hydrateTypificationParentOptions(excludeId = "") {
  const company = selectedTenantCompany("#typificationCompany");
  const nodes = sortedTypifications(company?.typifications || []).filter((node) => node.id !== excludeId);
  fillOptions(
    "#typificationParent",
    ["", ...nodes.map((node) => node.id)],
    ["Raiz / primera tipificacion", ...nodes.map((node) => `${"-- ".repeat(Math.max(0, typificationLevel(node, nodes) - 1))}${node.label}`)]
  );
}

function resetTypificationForm(clearCompany = true) {
  const companyValue = document.querySelector("#typificationCompany")?.value || "";
  document.querySelector("#typificationForm")?.reset();
  document.querySelector("#typificationNodeId").value = "";
  document.querySelector("#typificationSortOrder").value = "0";
  if (!clearCompany) document.querySelector("#typificationCompany").value = companyValue;
  hydrateTypificationParentOptions();
}

function fillTypificationForm(companyId, nodeId) {
  const company = (state.companies || []).find((item) => String(item.id) === String(companyId));
  const node = (company?.typifications || []).find((item) => item.id === nodeId);
  if (!company || !node) return;
  document.querySelector("#typificationCompany").value = String(company.id);
  hydrateTypificationParentOptions(node.id);
  document.querySelector("#typificationNodeId").value = node.id;
  document.querySelector("#typificationParent").value = node.parentId || "";
  document.querySelector("#typificationLabel").value = node.label || "";
  document.querySelector("#typificationCode").value = node.code || "";
  document.querySelector("#typificationNextStatus").value = node.nextStatus || "";
  document.querySelector("#typificationChannel").value = node.channel || "";
  document.querySelector("#typificationSortOrder").value = node.sortOrder || 0;
  document.querySelector("#typificationRequiresPromise").checked = Boolean(node.requiresPromise);
  document.querySelector("#typificationRequiresPayment").checked = Boolean(node.requiresPayment);
}

async function deletePlatformTypification(companyId, nodeId) {
  if (!confirm("Seguro que deseas eliminar esta tipificacion? Si tiene hijos, el sistema no permitira borrarla.")) return;
  try {
    const payload = await apiFetch("/api/platform/typifications/delete", {
      method: "POST",
      body: { companyId, id: nodeId }
    });
    state = hydrateState(payload.state);
    currentUser = payload.user || currentUser;
    populateStaticOptions();
    renderAll();
    showToast("Tipificacion eliminada.");
  } catch (error) {
    showToast(error.message || "No se pudo eliminar la tipificacion.");
  }
}

async function updatePlatformUserStatus(companyId, userId, active) {
  try {
    const payload = await apiFetch("/api/platform/users/status", {
      method: "POST",
      body: { companyId, userId, active }
    });
    state = hydrateState(payload.state);
    currentUser = payload.user || currentUser;
    populateStaticOptions();
    renderAll();
    showToast(active ? "Usuario tenant activado." : "Usuario tenant inactivado.");
  } catch (error) {
    showToast(error.message || "No se pudo modificar el usuario tenant.");
  }
}

async function updatePlatformProjectStatus(companyId, portfolioId, status) {
  try {
    const payload = await apiFetch("/api/platform/portfolios/status", {
      method: "POST",
      body: { companyId, portfolioId, status }
    });
    state = hydrateState(payload.state);
    currentUser = payload.user || currentUser;
    populateStaticOptions();
    renderAll();
    showToast(status === "active" ? "Proyecto activado." : "Proyecto pausado.");
  } catch (error) {
    showToast(error.message || "No se pudo modificar el proyecto.");
  }
}

function renderChannelList(group, label) {
  const channels = state.communication?.[group] || [];
  if (!channels.length) return emptyState(`No hay canales de ${label.toLowerCase()} configurados.`);
  return channels.map((channel) => `
    <article class="channel-item">
      <header>
        <div>
          <strong>${escapeHtml(channel.label)}</strong>
          <p>${escapeHtml(channel.value)}</p>
        </div>
        ${channel.isDefault ? `<span class="badge low">Default</span>` : `<span class="badge info">${escapeHtml(channel.status || "active")}</span>`}
      </header>
      <p>${escapeHtml(channel.provider || "Proveedor pendiente")}</p>
      <div class="channel-actions">
        ${channel.isDefault ? "" : `<button class="ghost-button compact" data-channel-default="${group}|${channel.id}" type="button">Predeterminar</button>`}
        <button class="danger-button compact" data-channel-delete="${group}|${channel.id}" type="button">Quitar</button>
      </div>
    </article>
  `).join("");
}

function addChannel(group, channel) {
  if (!ensureAdminAction()) return;
  if (channel.isDefault) setDefaultFlag(group, channel.id, false);
  const channels = state.communication[group];
  if (!channel.isDefault && channels.length === 0) channel.isDefault = true;
  state.communication[group] = [channel, ...channels];
  saveAndRender("Canal guardado para la empresa.");
}

function setDefaultChannel(group, channelId) {
  if (!ensureAdminAction()) return;
  setDefaultFlag(group, channelId, true);
  saveAndRender("Canal predeterminado actualizado.");
}

function setDefaultFlag(group, channelId, shouldMatchId) {
  state.communication[group] = (state.communication[group] || []).map((channel) => ({
    ...channel,
    isDefault: shouldMatchId ? channel.id === channelId : false
  }));
}

function deleteChannel(group, channelId) {
  if (!ensureAdminAction()) return;
  const channels = state.communication[group] || [];
  const removedWasDefault = channels.find((channel) => channel.id === channelId)?.isDefault;
  state.communication[group] = channels.filter((channel) => channel.id !== channelId);
  if (removedWasDefault && state.communication[group][0]) {
    state.communication[group][0].isDefault = true;
  }
  saveAndRender("Canal eliminado.");
}

function ensureAdminAction() {
  if (!["superadmin", "admin"].includes(currentUser?.role || "admin")) {
    showToast("Solo el administrador puede configurar canales.");
    return false;
  }
  return true;
}

function canManageAssignments() {
  return ["superadmin", "admin", "coordinator"].includes(currentUser?.role || "admin");
}

function canManageSettings() {
  return ["superadmin"].includes(currentUser?.role || "admin");
}

function importAssignmentCsv(csvText, options) {
  const rows = parseCsv(csvText);
  if (rows.length < 2) return { count: 0 };
  const headers = rows[0].map((header) => normalizeHeader(header));
  const portfolioId = nextPortfolioId(options.portfolioCode || options.portfolioName);
  const newPortfolio = portfolio(portfolioId, options.portfolioName, options.portfolioCode, options.leaderUserId);
  state.portfolios = [newPortfolio, ...state.portfolios.filter((item) => item.id !== portfolioId)];

  let count = 0;
  const importedCustomers = [];
  for (const row of rows.slice(1)) {
    if (!row.some((cell) => String(cell || "").trim())) continue;
    const record = Object.fromEntries(headers.map((header, index) => [header, row[index] || ""]));
    const name = pick(record, ["nombre", "cliente", "name"]);
    const documentId = pick(record, ["documento", "cedula", "nit", "identificacion", "id"]);
    const phone = pick(record, ["telefono", "celular", "movil", "phone"]);
    if (!name || !documentId || !phone) continue;
    const balance = parseMoney(pick(record, ["saldo", "saldo_vencido", "balance", "valor"]));
    const originalBalance = parseMoney(pick(record, ["saldo_original", "obligacion_total", "capital", "originalbalance"])) || balance;
    const dpd = parseInt(pick(record, ["mora", "dpd", "dias_mora", "diasdemora"]), 10) || 0;
    const agent = pick(record, ["gestor", "agente", "asesor"]) || options.defaultAgent;
    const segment = pick(record, ["segmento", "producto", "tipo_producto"]) || "Consumo";
    const city = pick(record, ["ciudad", "municipio"]) || "";
    const email = pick(record, ["email", "correo"]) || "";
    const obligation = pick(record, ["obligacion", "cuenta", "credito", "account"]) || "Obligacion principal";
    const customer = {
      id: nextId("C", [...state.customers, ...importedCustomers]),
      name,
      document: documentId,
      phone,
      email,
      city,
      segment,
      agent,
      portfolioId,
      balance,
      originalBalance,
      dpd,
      status: "Sin contacto",
      risk: riskFromDpd(dpd, balance),
      priority: scoreCustomer({ dpd, balance, risk: riskFromDpd(dpd, balance), status: "Sin contacto", contactability: "Media" }),
      nextAction: "Primer contacto del reparto",
      lastContact: "",
      nextContact: isoToday,
      contactability: "Media",
      accounts: [obligation],
      tags: [options.portfolioCode],
      demographic: {
        direccion: pick(record, ["direccion", "address"]),
        ciudad: city,
        departamento: pick(record, ["departamento", "region"]),
        ingreso: pick(record, ["ingreso", "salario"])
      },
      financial: {
        producto: segment,
        score: pick(record, ["score", "puntaje"]),
        cuota: pick(record, ["cuota", "valor_cuota"]),
        fechaVencimiento: pick(record, ["fecha_vencimiento", "vencimiento"])
      },
      notes: pick(record, ["observacion", "nota", "notes"]) || `Cliente cargado en reparto ${options.portfolioCode}.`,
      timeline: [
        activity("Reparto cargado", `Asignado a ${agent} en cartera ${options.portfolioName}.`, currentUser?.name || "Sistema", isoToday)
      ]
    };
    importedCustomers.push(customer);
    count += 1;
  }

  const importedDocuments = new Set(importedCustomers.map((customer) => normalize(customer.document)));
  state.customers = [
    ...importedCustomers,
    ...state.customers.filter((customer) => !importedDocuments.has(normalize(customer.document)))
  ];
  state.segments = Array.from(new Set([...state.segments, ...importedCustomers.map((customer) => customer.segment)])).sort();
  return { count };
}

function parseCsv(text) {
  const firstLine = text.split(/\r?\n/, 1)[0] || "";
  const delimiter = (firstLine.match(/;/g) || []).length > (firstLine.match(/,/g) || []).length ? ";" : ",";
  const rows = [];
  let row = [];
  let cell = "";
  let inQuotes = false;
  for (let index = 0; index < text.length; index += 1) {
    const char = text[index];
    const next = text[index + 1];
    if (char === '"' && inQuotes && next === '"') {
      cell += '"';
      index += 1;
    } else if (char === '"') {
      inQuotes = !inQuotes;
    } else if (char === delimiter && !inQuotes) {
      row.push(cell.trim());
      cell = "";
    } else if ((char === "\n" || char === "\r") && !inQuotes) {
      if (char === "\r" && next === "\n") index += 1;
      row.push(cell.trim());
      rows.push(row);
      row = [];
      cell = "";
    } else {
      cell += char;
    }
  }
  if (cell || row.length) {
    row.push(cell.trim());
    rows.push(row);
  }
  return rows.filter((item) => item.length && item.some(Boolean));
}

function normalizeHeader(value) {
  return normalize(value).replace(/[^a-z0-9]+/g, "_").replace(/^_|_$/g, "");
}

function pick(record, keys) {
  for (const key of keys) {
    const normalizedKey = normalizeHeader(key);
    if (record[normalizedKey]) return String(record[normalizedKey]).trim();
  }
  return "";
}

function parseMoney(value) {
  const cleaned = String(value || "").replace(/[^\d.-]/g, "");
  return Math.max(0, Math.round(Number(cleaned) || 0));
}

function nextPortfolioId(seed) {
  const base = normalizeHeader(seed || "cartera").toUpperCase().slice(0, 18) || "CARTERA";
  let candidate = `CAR-${base}`;
  let suffix = 1;
  const existing = new Set(state.portfolios.map((item) => item.id));
  while (existing.has(candidate)) {
    suffix += 1;
    candidate = `CAR-${base}-${suffix}`;
  }
  return candidate;
}

function filteredCustomers() {
  const search = normalize(elements.globalSearch.value);
  const dashboardSegment = document.querySelector("#dashboardSegmentFilter")?.value || "all";
  return state.customers.filter((customer) => {
    const matchesSearch = !search || normalize([
      customer.name,
      customer.document,
      customer.phone,
      customer.email,
      customer.segment,
      customer.agent
    ].join(" ")).includes(search);
    const matchesSegment = activeView === "dashboard" && dashboardSegment !== "all"
      ? customer.segment === dashboardSegment
      : true;
    return matchesSearch && matchesSegment;
  });
}

function markPromiseCompleted(promiseId) {
  const promiseItem = state.promises.find((item) => item.id === promiseId);
  if (!promiseItem) return;
  promiseItem.status = "Cumplida";
  pushTimeline(promiseItem.customerId, "Promesa cumplida", `Se confirma promesa por ${money(promiseItem.amount)}.`, currentAgent(promiseItem.customerId));
  saveAndRender("Promesa marcada como cumplida.");
}

function addQuickActivity(customerId, action) {
  const customer = findCustomer(customerId);
  if (!customer) return;
  const nextStatus = action.includes("Escalado") ? "Escalado" : action.includes("Llamada") ? "Contactado" : customer.status;
  updateCustomer(customerId, {
    status: nextStatus,
    lastContact: isoToday,
    nextContact: addDays(2),
    nextAction: actionFromStatus(nextStatus)
  });
  pushTimeline(customerId, action, `Accion rapida registrada desde cola.`, customer.agent);
  activityPage = 1;
  saveAndRender(`${action} registrado.`);
}

function refreshPromiseStatuses() {
  let changed = false;
  state.promises = state.promises.map((item) => {
    if (item.status === "Vigente" && item.date < isoToday) {
      changed = true;
      return { ...item, status: "Vencida" };
    }
    return item;
  });
  if (changed && !API_ENABLED) saveState();
}

async function saveAndRender(message) {
  recalculateCustomers();
  try {
    if (API_ENABLED) {
      const payload = await apiFetch("/api/state", {
        method: "PUT",
        body: { state }
      });
      state = hydrateState(payload.state);
      currentUser = payload.user || currentUser;
    } else {
      saveState();
    }
    populateStaticOptions();
    renderAll();
    showToast(message);
  } catch (error) {
    showToast(error.message || "No se pudo guardar en la base de datos.");
  }
}

function recalculateCustomers() {
  state.customers = state.customers.map((customer) => ({
    ...customer,
    risk: riskFromDpd(customer.dpd, customer.balance),
    priority: scoreCustomer(customer)
  }));
}

function scoreCustomer(customer) {
  const riskScore = customer.risk === "Alto" ? 28 : customer.risk === "Medio" ? 16 : 7;
  const dpdScore = Math.min(35, Math.round(customer.dpd / 3));
  const balanceScore = Math.min(25, Math.round(customer.balance / 2000000));
  const statusScore = customer.status === "Promesa" ? 10 : customer.status === "Sin contacto" ? 7 : customer.status === "Escalado" ? 9 : 3;
  const contactScore = customer.contactability === "Alta" ? 5 : customer.contactability === "Media" ? 3 : 1;
  return Math.min(99, riskScore + dpdScore + balanceScore + statusScore + contactScore);
}

function riskFromDpd(dpd, balance) {
  if (dpd >= 61 || balance >= 20000000) return "Alto";
  if (dpd >= 16 || balance >= 4000000) return "Medio";
  return "Bajo";
}

function actionFromStatus(status) {
  const actions = {
    "Contactado": "Enviar propuesta y solicitar fecha de pago",
    "Promesa": "Confirmar cumplimiento de promesa",
    "Sin contacto": "Intentar contacto alterno y validar datos",
    "Disputa": "Recolectar soportes y pausar automatizaciones",
    "Escalado": "Seguimiento supervisor o prejuridico"
  };
  return actions[status] || "Programar nueva gestion";
}

function updateCustomer(customerId, patch) {
  state.customers = state.customers.map((customer) => customer.id === customerId ? { ...customer, ...patch } : customer);
}

function pushTimeline(customerId, type, note, agent, date = isoToday) {
  if (customerId === selectedCustomerId) activityPage = 1;
  state.customers = state.customers.map((customer) => {
    if (customer.id !== customerId) return customer;
    return {
      ...customer,
      timeline: [activity(type, note, agent, date), ...customer.timeline]
    };
  });
}

function openCustomerModal() {
  elements.customerModal.showModal();
}

function closeCustomerModal() {
  elements.customerModal.close();
}

function exportCustomersCsv() {
  const headers = ["id", "name", "document", "phone", "email", "segment", "agent", "balance", "dpd", "status", "risk", "nextAction"];
  const rows = state.customers.map((customer) => headers.map((header) => csvCell(customer[header])).join(","));
  const csv = [headers.join(","), ...rows].join("\n");
  const blob = new Blob([csv], { type: "text/csv;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = `cartera-cobranzas-${isoToday}.csv`;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
  showToast("CSV generado.");
}

function fillOptions(selector, values, labels) {
  const select = document.querySelector(selector);
  if (!select) return;
  const current = select.value;
  const options = values.map((value, index) => ({
    value: String(value ?? ""),
    label: String(labels[index] ?? value ?? "")
  }));
  select.innerHTML = options.map((option) => `<option value="${escapeHtml(option.value)}">${escapeHtml(option.label)}</option>`).join("");
  if (options.some((option) => option.value === current)) {
    select.value = current;
  } else if (options.length) {
    select.value = options[0].value;
  }
}

function metric(label, value, trend, trendClass) {
  return `
    <article class="metric-card ${trendClass || ""}">
      <span class="metric-label">${label}</span>
      <strong class="metric-value">${value}</strong>
      <span class="metric-trend ${trendClass}">${trend}</span>
    </article>
  `;
}

function commandCard(label, value, detail, className) {
  return `
    <article class="command-card ${className || ""}">
      <span>${label}</span>
      <strong>${value}</strong>
      <span>${detail}</span>
    </article>
  `;
}

function miniStat(label, value) {
  return `<div class="mini-stat"><span>${label}</span><strong>${value}</strong></div>`;
}

function taskItem(type, title, body, customerId) {
  return `
    <article class="task-item">
      <div class="item-head">
        <div>
          <h3>${type}: ${escapeHtml(title)}</h3>
          <p>${escapeHtml(body)}</p>
        </div>
        <button class="ghost-button compact" data-open-customer="${customerId}" type="button">Abrir</button>
      </div>
    </article>
  `;
}

function nameStack(customer) {
  return `<div class="name-stack"><strong>${escapeHtml(customer.name)}</strong><span>${escapeHtml(customer.phone)}</span></div>`;
}

function typificationOptions(parentId) {
  const children = state.typifications
    .filter((node) => (node.parentId || null) === (parentId || null))
    .sort((a, b) => (a.sortOrder || 0) - (b.sortOrder || 0) || a.label.localeCompare(b.label));
  const placeholder = parentId ? "Selecciona una opcion" : "Selecciona tipificacion";
  return [`<option value="">${placeholder}</option>`, ...children.map((node) => `<option value="${node.id}">${escapeHtml(node.label)}</option>`)].join("");
}

function wireTypificationForm(form) {
  const level1 = form.querySelector("[data-typification-level='1']");
  const level2 = form.querySelector("[data-typification-level='2']");
  const level3 = form.querySelector("[data-typification-level='3']");
  const result = form.querySelector("[name='result']");

  level1.addEventListener("change", () => {
    if (!level1.value) {
      level2.innerHTML = `<option value="">Selecciona primero una tipificacion</option>`;
      level3.innerHTML = `<option value="">Opcional</option>`;
      return;
    }
    level2.innerHTML = typificationOptions(level1.value);
    level3.innerHTML = `<option value="">Opcional</option>`;
    applyTypificationResult(level1.value, result);
  });

  level2.addEventListener("change", () => {
    if (!level2.value) {
      level3.innerHTML = `<option value="">Opcional</option>`;
      applyTypificationResult(level1.value, result);
      return;
    }
    level3.innerHTML = typificationOptions(level2.value);
    applyTypificationResult(level2.value, result);
  });

  level3.addEventListener("change", () => {
    applyTypificationResult(level3.value || level2.value || level1.value, result);
  });
}

function applyTypificationResult(typificationId, resultSelect) {
  const node = findTypification(typificationId);
  if (node?.nextStatus) resultSelect.value = node.nextStatus;
}

function findTypification(typificationId) {
  return state.typifications.find((node) => node.id === typificationId);
}

function riskBadge(risk) {
  const className = risk === "Alto" ? "high" : risk === "Medio" ? "medium" : "low";
  return `<span class="badge ${className}">${risk}</span>`;
}

function statusBadge(status) {
  const className = status === "Vencida" || status === "Escalado" || status === "Disputa"
    ? "high"
    : status === "Vigente" || status === "Promesa"
      ? "medium"
      : status === "Cumplida" || status === "Contactado"
        ? "low"
        : "info";
  return `<span class="badge ${className}">${status}</span>`;
}

function profileStat(label, value) {
  return `<div class="profile-stat"><span>${label}</span><strong>${value}</strong></div>`;
}

function emptyState(message) {
  return `<div class="note-box">${message}</div>`;
}

function tableEmptyRow(cols, message) {
  return `<tr><td colspan="${cols}">${message}</td></tr>`;
}

function findCustomer(customerId) {
  return state.customers.find((customer) => customer.id === customerId);
}

function currentAgent(customerId) {
  return findCustomer(customerId)?.agent || "Sistema";
}

function defaultChannel(group) {
  const channels = state.communication?.[group] || [];
  return channels.find((channel) => channel.isDefault) || channels[0] || null;
}

function portfolioName(portfolioId) {
  return state.portfolios.find((item) => item.id === portfolioId)?.name || "Sin cartera";
}

function sum(items, key) {
  return items.reduce((total, item) => total + Number(item[key] || 0), 0);
}

function money(value) {
  return new Intl.NumberFormat("es-CO", {
    style: "currency",
    currency: "COP",
    maximumFractionDigits: 0
  }).format(value || 0);
}

function formatDate(value) {
  if (!value) return "Sin fecha";
  const [year, month, day] = value.split("-").map(Number);
  return new Intl.DateTimeFormat("es-CO", { day: "2-digit", month: "short", year: "numeric" }).format(new Date(year, month - 1, day));
}

function addDays(days) {
  const date = new Date(today);
  date.setDate(date.getDate() + days);
  return toIsoDate(date);
}

function toIsoDate(date) {
  return date.toISOString().slice(0, 10);
}

function daysBetween(start, end) {
  const startDate = new Date(`${start}T00:00:00`);
  const endDate = new Date(`${end}T00:00:00`);
  return Math.round((endDate - startDate) / 86400000);
}

function normalize(value) {
  return String(value || "")
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "");
}

function escapeHtml(value) {
  return String(value ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function csvCell(value) {
  const text = String(value ?? "");
  return `"${text.replace(/"/g, '""')}"`;
}

function cleanPhone(value) {
  return String(value || "").replace(/[^\d+]/g, "");
}

function phoneDigits(value) {
  return String(value || "").replace(/\D/g, "");
}

function nextId(prefix, items) {
  const numbers = items
    .map((item) => Number(String(item.id).replace(/\D/g, "")))
    .filter(Boolean);
  return `${prefix}-${Math.max(1000, ...numbers) + 1}`;
}

function nextChannelId(prefix, items) {
  const numbers = items
    .map((item) => Number(String(item.id).replace(/\D/g, "")))
    .filter(Boolean);
  return `${prefix}-${Math.max(0, ...numbers) + 1}`;
}

function activity(type, note, agent, date) {
  return { type, note, agent, date };
}

function promise(id, customerId, amount, date, channel, status) {
  return { id, customerId, amount, date, channel, status, createdAt: isoToday };
}

function payment(id, customerId, amount, date, method, reference) {
  return { id, customerId, amount, date, method, reference };
}

function typification(id, parentId, label, code, nextStatus, requiresPromise, requiresPayment, channel) {
  return { id, parentId, label, code, nextStatus, requiresPromise, requiresPayment, channel, sortOrder: 0 };
}

function channelAccount(id, type, label, value, provider, isDefault = false, config = {}) {
  return {
    id,
    type,
    label,
    value,
    provider,
    status: "active",
    isDefault,
    config,
    createdAt: isoToday
  };
}

function portfolio(id, name, code, leaderUserId = null) {
  return { id, name, code, leaderUserId, status: "active", createdAt: isoToday };
}

function titleForView(view) {
  const titles = {
    dashboard: "Tablero ejecutivo",
    queue: "Cola de gestion",
    customers: "Clientes y expedientes",
    assignments: "Repartos y equipos",
    users: "Usuarios y equipos",
    tenants: "Empresas cliente",
    promises: "Promesas de pago",
    payments: "Pagos y conciliacion",
    campaigns: "Campanas multicanal",
    reports: "Reportes gerenciales",
    bi: "BI ejecutivo",
    settings: "Configuracion operativa"
  };
  return titles[view] || "IcodeUp CRM";
}

function loadState() {
  const raw = localStorage.getItem(STORAGE_KEY);
  if (!raw) return structuredClone(defaultState);
  try {
    const parsed = JSON.parse(raw);
    return hydrateState(parsed);
  } catch {
    return structuredClone(defaultState);
  }
}

function hydrateState(source = {}) {
  const base = structuredClone(defaultState);
  const hydrated = {
    ...base,
    ...source,
    settings: { ...base.settings, ...(source.settings || {}) },
    communication: {
      whatsappNumbers: source.communication?.whatsappNumbers || base.communication.whatsappNumbers,
      emailAccounts: source.communication?.emailAccounts || base.communication.emailAccounts,
      telephonyAccounts: source.communication?.telephonyAccounts || base.communication.telephonyAccounts
    }
  };
  hydrated.users = source.users || base.users;
  hydrated.portfolios = source.portfolios?.length ? source.portfolios : base.portfolios;
  hydrated.companies = source.companies || [];
  hydrated.customers = (hydrated.customers || []).map((customer) => ({
    portfolioId: hydrated.portfolios[0]?.id || "CAR-BASE",
    demographic: {},
    financial: {},
    ...customer
  }));
  return hydrated;
}

function saveState() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
}

function showToast(message) {
  elements.toast.textContent = message;
  elements.toast.classList.add("show");
  window.clearTimeout(showToast.timeout);
  showToast.timeout = window.setTimeout(() => {
    elements.toast.classList.remove("show");
  }, 2400);
}
