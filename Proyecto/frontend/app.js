// Simple MVP para consumir la API DRF de ÁgoraUN
const $ = (q) => document.querySelector(q);
const $$ = (q) => document.querySelectorAll(q);

const apiBaseInput = $("#apiBase");
const tokenInput = $("#apiToken");
const saveBaseBtn = $("#saveBase");
const saveTokBtn = $("#saveToken");
const searchBtn = $("#searchBtn");
const qInput = $("#q");
const areaSel = $("#area");
const groupsDiv = $("#groups");
const cardTpl = $("#cardTpl");

// ⚠️ Por ahora, usuario de prueba para unirse/salir de grupos.
// Debe existir un Usuario con id_usuario = 1 en la BD.
const DEFAULT_USER_ID = 1;

let API_BASE = localStorage.getItem("API_BASE") || apiBaseInput.value;
let API_TOKEN = localStorage.getItem("API_TOKEN") || "";

apiBaseInput.value = API_BASE;
tokenInput.value = API_TOKEN;

saveBaseBtn.onclick = () => {
  API_BASE = apiBaseInput.value.trim().replace(/\/+$/, "");
  localStorage.setItem("API_BASE", API_BASE);
  fetchGroups();
};

saveTokBtn.onclick = () => {
  API_TOKEN = tokenInput.value.trim();
  localStorage.setItem("API_TOKEN", API_TOKEN);
  fetchGroups();
};

searchBtn.onclick = () => fetchGroups();

function headers() {
  const h = { "Content-Type": "application/json" };
  if (API_TOKEN) h["Authorization"] = `Token ${API_TOKEN}`; // DRF TokenAuth
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

  // Algunos endpoints (p.ej. DELETE 204) no devuelven JSON
  if (res.status === 204 || res.status === 205) {
    return null;
  }

  // Si no hay cuerpo, evitar error de JSON vacío
  const text = await res.text();
  if (!text) return null;
  return JSON.parse(text);
}

async function fetchGroups() {
  groupsDiv.innerHTML = "<p>Cargando...</p>";
  try {
    const params = new URLSearchParams();
    const q = qInput.value.trim();
    const area = areaSel.value.trim();

    if (q) params.set("search", q); // DRF SearchFilter
    if (area) params.set("area", area); // filtro por area_interes (iexact)

    const query = params.toString();
    const url = query
      ? `${API_BASE}/grupos/?${query}`
      : `${API_BASE}/grupos/`;

    const data = await fetchJSON(url);
    const items = Array.isArray(data) ? data : data?.results || [];
    renderGroups(items);
  } catch (err) {
    console.error(err);
    groupsDiv.innerHTML = `<p class="error">${err.message}</p>`;
  }
}

function renderGroups(items) {
  groupsDiv.innerHTML = "";
  if (!items.length) {
    groupsDiv.innerHTML = "<p>Sin resultados</p>";
    return;
  }

  items.forEach((g) => {
    // Adaptar nombres de campos a lo que devuelve tu API
    const id = g.id_grupo || g.id;
    const nombre = g.nombre_grupo || g.nombre || g.name || `Grupo #${id}`;
    const area = g.area_interes || g.area || "";

    const frag = cardTpl.content.cloneNode(true);
    const card = frag.querySelector(".card");

    const nameEl = card.querySelector(".g-name");
    const areaEl = card.querySelector(".g-area");
    const detailEl = card.querySelector(".detail");
    const eventsList = card.querySelector(".events");
    const btnView = card.querySelector(".btn-view");
    const btnJoin = card.querySelector(".btn-join");
    const btnLeave = card.querySelector(".btn-leave");

    nameEl.textContent = nombre;
    areaEl.textContent = area ? `Área: ${area}` : "";

    // Ver detalles (eventos del grupo)
    btnView.onclick = async () => {
      detailEl.classList.toggle("hidden");
      if (!detailEl.classList.contains("hidden")) {
        eventsList.innerHTML = "<li>Cargando eventos...</li>";
        try {
          const evs = await fetchJSON(`${API_BASE}/grupos/${id}/eventos/`);
          const lista = Array.isArray(evs) ? evs : evs?.results || [];
          eventsList.innerHTML = "";

          if (!lista.length) {
            eventsList.innerHTML = "<li>Sin eventos registrados</li>";
            return;
          }

          lista.forEach((e) => {
            const li = document.createElement("li");
            const titulo =
              e.nombre_evento || e.titulo || e.nombre || "Evento";
            const fecha = e.fecha_inicio || e.fecha || "";
            const lugar = e.lugar || "";
            const fechaTxt = fecha ? new Date(fecha).toLocaleString() : "";
            li.textContent = `${titulo}${
              fechaTxt ? " — " + fechaTxt : ""
            }${lugar ? " @ " + lugar : ""}`;
            eventsList.appendChild(li);
          });
        } catch (err) {
          console.error(err);
          eventsList.innerHTML = `<li class="error">${err.message}</li>`;
        }
      }
    };

    // Unirme al grupo
    btnJoin.onclick = async () => {
      try {
        await fetchJSON(`${API_BASE}/grupos/${id}/agregar_miembro/`, {
          method: "POST",
          body: JSON.stringify({
            id_usuario: DEFAULT_USER_ID,
            // rol_en_grupo: "MIEMBRO", // opcional
          }),
        });
        alert("¡Te uniste al grupo!");
      } catch (err) {
        console.error(err);
        alert("Error al unirte: " + err.message);
      }
    };

    // Salir del grupo
    btnLeave.onclick = async () => {
      try {
        const url = `${API_BASE}/grupos/${id}/eliminar_miembro/?id_usuario=${DEFAULT_USER_ID}`;
        await fetchJSON(url, { method: "DELETE" });
        alert("Has salido del grupo.");
      } catch (err) {
        console.error(err);
        alert("Error al salir: " + err.message);
      }
    };

    groupsDiv.appendChild(frag);
  });
}

// Cargar lista inicial
fetchGroups();
