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

const reloadSolicitudesBtn = $("#reloadSolicitudes");
const reloadNotifsBtn = $("#reloadNotifs");
const reloadEventosBtn = $("#reloadEventos");

let API_BASE = localStorage.getItem("API_BASE") || apiBaseInput.value;
let API_TOKEN = localStorage.getItem("API_TOKEN") || "";
let USER_ID = localStorage.getItem("USER_ID") || "";
let USER_ROLE = localStorage.getItem("USER_ROLE") || "ESTUDIANTE";

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

async function loadEventos() {
  eventosDiv.innerHTML = "<p>Cargando eventos...</p>";
  try {
    const today = new Date().toISOString().slice(0, 10);
    const data = await fetchJSON(`${API_BASE}/eventos/?desde=${today}`);
    const items = Array.isArray(data) ? data : data?.results || [];
    if (!items.length) {
      eventosDiv.innerHTML = "<p>No hay eventos futuros</p>";
      return;
    }
    eventosDiv.innerHTML = "";
    items.slice(0, 10).forEach((ev) => {
      const row = document.createElement("div");
      row.className = "card";
      const fecha = ev.fecha_inicio ? new Date(ev.fecha_inicio).toLocaleString() : "";
      row.innerHTML = `
        <h4>${ev.nombre_evento || "Evento"}</h4>
        <p>${ev.grupo_nombre || ""}</p>
        <p>${fecha} @ ${ev.lugar || ""}</p>
        <span class="tag">${ev.estado_evento || ""}</span>
      `;
      eventosDiv.appendChild(row);
    });
  } catch (err) {
    eventosDiv.innerHTML = `<p class="error">${err.message}</p>`;
  }
}

// Inicial
loadSolicitudes();
loadNotificaciones();
loadEventos();
