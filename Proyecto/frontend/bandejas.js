// Bandejas de entrada por rol (RF_13, RF_14 y notificaciones/eventos)
const $ = (q) => document.querySelector(q);

const apiBaseInput = $("#apiBase");
const tokenInput = $("#apiToken");
const userIdInput = $("#userId");
const roleSelect = $("#userRole");
const saveBaseBtn = $("#saveBase");
const saveTokenBtn = $("#saveToken");
const saveUserBtn = $("#saveUser");

const solicitudesDiv = $("#solicitudes");
const notifsDiv = $("#notifs");
const eventosDiv = $("#eventos");
const filterFecha = $("#f-fecha");
const filterArea = $("#f-area");
const filterClub = $("#f-club");
const filterTipo = $("#f-tipo");
const applyFiltersBtn = $("#applyFilters");
const clearFiltersBtn = $("#clearFilters");

const reloadSolicitudesBtn = $("#reloadSolicitudes");
const reloadNotifsBtn = $("#reloadNotifs");
const reloadEventosBtn = $("#reloadEventos");

let API_BASE = localStorage.getItem("API_BASE") || apiBaseInput.value;
let API_TOKEN = localStorage.getItem("API_TOKEN") || "";
let USER_ID = localStorage.getItem("USER_ID") || "";
let USER_ROLE = localStorage.getItem("USER_ROLE") || "ESTUDIANTE";
let eventosCache = [];
let gruposCache = [];

apiBaseInput.value = API_BASE;
tokenInput.value = API_TOKEN;
userIdInput.value = USER_ID;
roleSelect.value = USER_ROLE;

function headers() {
  const h = { "Content-Type": "application/json" };
  if (API_TOKEN) h["Authorization"] = `Token ${API_TOKEN}`;
  return h;
}

async function fetchJSON(url, opts = {}) {
  const res = await fetch(url, {
    ...opts,
    headers: { ...headers(), ...(opts.headers || {}) },
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`HTTP ${res.status}: ${text}`);
  }
  if (res.status === 204 || res.status === 205) return null;
  const text = await res.text();
  if (!text) return null;
  return JSON.parse(text);
}

function saveSettings() {
  API_BASE = apiBaseInput.value.trim().replace(/\/+$/, "");
  API_TOKEN = tokenInput.value.trim();
  USER_ID = userIdInput.value.trim();
  USER_ROLE = roleSelect.value;
  localStorage.setItem("API_BASE", API_BASE);
  localStorage.setItem("API_TOKEN", API_TOKEN);
  localStorage.setItem("USER_ID", USER_ID);
  localStorage.setItem("USER_ROLE", USER_ROLE);
}

saveBaseBtn.onclick = () => {
  saveSettings();
  loadSolicitudes();
  loadNotificaciones();
  loadEventos();
};
saveTokenBtn.onclick = saveBaseBtn.onclick;
saveUserBtn.onclick = saveBaseBtn.onclick;

reloadSolicitudesBtn.onclick = () => loadSolicitudes();
reloadNotifsBtn.onclick = () => loadNotificaciones();
reloadEventosBtn.onclick = () => loadEventos();
applyFiltersBtn.onclick = () => renderEventos(eventosCache);
if (clearFiltersBtn) {
  clearFiltersBtn.onclick = () => {
    if (filterFecha) filterFecha.value = "";
    if (filterArea) filterArea.value = "";
    if (filterClub) filterClub.value = "";
    if (filterTipo) filterTipo.value = "";
    renderEventos(eventosCache);
  };
}
// Cambio de filtros reactivo
[filterFecha, filterArea, filterClub, filterTipo].forEach(el => {
  if (el) el.addEventListener("change", () => renderEventos(eventosCache));
});

async function loadSolicitudes() {
  // Mostrar u ocultar toda la sección de solicitudes según el rol
  const solicitudesPanel = solicitudesDiv.closest('section') || solicitudesDiv.parentElement;
  const twoCols = document.querySelector('.two-cols');
  if (USER_ROLE !== 'ADMIN_GENERAL') {
    // Ocultar la sección completamente para usuarios no-admin
    if (solicitudesPanel) solicitudesPanel.style.display = 'none';
    // Aplicar layout centrado cuando sólo quede la bandeja de notificaciones
    if (twoCols) twoCols.classList.add('single-column');
    return;
  }
  // Si es admin general, asegurarnos de que la sección esté visible
  if (solicitudesPanel) solicitudesPanel.style.display = '';
  if (twoCols) twoCols.classList.remove('single-column');
  solicitudesDiv.innerHTML = "<p>Cargando solicitudes...</p>";
  try {
    const data = await fetchJSON(`${API_BASE}/grupos/?estado=PENDIENTE`);
    const items = Array.isArray(data) ? data : data?.results || [];
    if (!items.length) {
      solicitudesDiv.innerHTML = "<p>No hay solicitudes pendientes</p>";
      return;
    }
    solicitudesDiv.innerHTML = "";
    items.forEach((g) => {
      const card = document.createElement("article");
      card.className = "card";
      card.innerHTML = `
        <h3>${g.nombre_grupo || "Grupo"}</h3>
        <p>Área: ${g.area_interes || "-"}</p>
        <p>Tipo: ${g.tipo_grupo || "-"}</p>
        <p class="tag">Estado: ${g.estado_grupo}</p>
        <div class="actions">
          <button class="btn-approve">Aprobar</button>
          <button class="btn-reject secondary">Rechazar</button>
        </div>
      `;
      card.querySelector(".btn-approve").onclick = () => aprobarGrupo(g.id_grupo);
      card.querySelector(".btn-reject").onclick = () => rechazarGrupo(g.id_grupo);
      solicitudesDiv.appendChild(card);
    });
  } catch (err) {
    console.error(err);
    solicitudesDiv.innerHTML = `<p class="error">${err.message}</p>`;
  }
}

async function aprobarGrupo(id) {
  if (!confirm("¿Aprobar este grupo?")) return;
  try {
    await fetchJSON(`${API_BASE}/grupos/${id}/aprobar/`, { method: "POST" });
    alert("Grupo aprobado");
    loadSolicitudes();
    loadNotificaciones();
  } catch (err) {
    alert("Error: " + err.message);
  }
}

async function rechazarGrupo(id) {
  const motivo = prompt("Motivo del rechazo:");
  if (!motivo) return;
  try {
    await fetchJSON(`${API_BASE}/grupos/${id}/rechazar/`, {
      method: "POST",
      body: JSON.stringify({ motivo }),
    });
    alert("Grupo rechazado");
    loadSolicitudes();
    loadNotificaciones();
  } catch (err) {
    alert("Error: " + err.message);
  }
}

async function loadNotificaciones() {
  if (!USER_ID) {
    notifsDiv.innerHTML = "<p>Configura un Usuario ID para ver notificaciones.</p>";
    return;
  }
  notifsDiv.innerHTML = "<p>Cargando notificaciones...</p>";
  try {
    const data = await fetchJSON(`${API_BASE}/notificaciones/?usuario=${USER_ID}`);
    const items = Array.isArray(data) ? data : data?.results || [];
    if (!items.length) {
      notifsDiv.innerHTML = "<p>Sin notificaciones</p>";
      return;
    }
    notifsDiv.innerHTML = "";
    items.forEach((n) => {
      const row = document.createElement("div");
      row.className = "card";
      row.innerHTML = `
        <h4>${n.tipo_notificacion}</h4>
        <p>${n.mensaje}</p>
        <small>${new Date(n.fecha_envio).toLocaleString()}</small>
      `;
      notifsDiv.appendChild(row);
    });
  } catch (err) {
    notifsDiv.innerHTML = `<p class="error">${err.message}</p>`;
  }
}

async function loadClubOptions(force=false) {
  if (!filterClub) return;
  if (!force && gruposCache.length) return;
  filterClub.innerHTML = `<option value="">Todos</option>`;
  try {
    let grupos = [];
    if (USER_ID) {
      const membership = await fetchJSON(`${API_BASE}/usuarios/${USER_ID}/grupos/`);
      const memList = Array.isArray(membership) ? membership : membership?.results || [];
      const ids = new Set(memList.map(g => String(g.grupo || g.id_grupo || g.grupo_id || g.id)));
      const all = await fetchJSON(`${API_BASE}/grupos/?ordering=nombre_grupo`);
      const allList = Array.isArray(all) ? all : all?.results || [];
      grupos = allList.filter(g => ids.has(String(g.id_grupo || g.id)));
    } else {
      const all = await fetchJSON(`${API_BASE}/grupos/?ordering=nombre_grupo`);
      grupos = Array.isArray(all) ? all : all?.results || [];
    }
    gruposCache = grupos;
    fillClubFilter(gruposCache);
  } catch (err) {
    console.error("No se pudo cargar clubes para filtro", err);
  }
}

async function loadEventos() {
  eventosDiv.innerHTML = "<p>Cargando eventos...</p>";
  try {
    await loadClubOptions();
    const today = new Date().toISOString().slice(0, 10);
    const data = await fetchJSON(`${API_BASE}/eventos/?desde=${today}`);
    const items = Array.isArray(data) ? data : data?.results || [];
    // Ordenar por fecha inicio ascendente
    eventosCache = items
      .filter(ev => ev.fecha_inicio)
      .sort((a,b) => new Date(a.fecha_inicio) - new Date(b.fecha_inicio));
    renderEventos(eventosCache);
  } catch (err) {
    eventosDiv.innerHTML = `<p class="error">${err.message}</p>`;
  }
}

function fillClubFilter(lista) {
  if (!filterClub) return;
  filterClub.innerHTML = `<option value="">Todos</option>`;
  lista.forEach(g => {
    const opt = document.createElement("option");
    opt.value = g.id_grupo || g.id;
    opt.textContent = g.nombre_grupo || g.nombre || `Grupo ${opt.value}`;
    filterClub.appendChild(opt);
  });
}

function renderEventos(list) {
  if (!eventosDiv) return;
  let filtered = Array.isArray(list) ? [...list] : [];
  const fDesde = filterFecha?.value;
  const fArea = (filterArea?.value || "").toLowerCase();
  const fClub = filterClub?.value;
  const fTipo = filterTipo?.value;

  if (fDesde) {
    const date = new Date(fDesde);
    filtered = filtered.filter(ev => ev.fecha_inicio && new Date(ev.fecha_inicio) >= date);
  }
  if (fClub) {
    filtered = filtered.filter(ev => String(ev.grupo) === String(fClub));
  }
  if (fTipo) {
    filtered = filtered.filter(ev => (ev.tipo_evento || '').toUpperCase() === fTipo);
  }
  if (fArea) {
    const areaMap = new Map();
    gruposCache.forEach(g => {
      const id = g.id_grupo || g.id;
      const area = (g.area_interes || "").toLowerCase();
      areaMap.set(String(id), area);
    });
    filtered = filtered.filter(ev => {
      const area = areaMap.get(String(ev.grupo)) || "";
      return area === fArea;
    });
  }
  // ordenar por fecha cercana ascendente
  filtered.sort((a,b) => {
    const da = a.fecha_inicio ? new Date(a.fecha_inicio).getTime() : Infinity;
    const db = b.fecha_inicio ? new Date(b.fecha_inicio).getTime() : Infinity;
    return da - db;
  });

  if (!filtered.length) {
    eventosDiv.innerHTML = "<p>No hay eventos que cumplan el filtro.</p>";
    return;
  }

  eventosDiv.innerHTML = "";
  filtered.slice(0, 20).forEach((ev) => {
    const row = document.createElement("div");
    row.className = "card";
    const fecha = ev.fecha_inicio ? new Date(ev.fecha_inicio).toLocaleString() : "";
    const club = ev.grupo_nombre || (gruposCache.find(g => String(g.id_grupo || g.id) === String(ev.grupo))?.nombre_grupo) || "";
    row.innerHTML = `
      <h4>${ev.nombre_evento || "Evento"}</h4>
      <p>${club}</p>
      <p>${fecha} @ ${ev.lugar || ""}</p>
      <span class="tag">${ev.tipo_evento || ""}</span>
    `;
    eventosDiv.appendChild(row);
  });
}

// Inicial
loadSolicitudes();
loadNotificaciones();
loadEventos();
