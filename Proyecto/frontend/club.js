// club.js
// Maneja selección de club, solicitud de edición y creación de eventos (como solicitudes)

const API_BASE = localStorage.getItem('API_BASE') || 'http://localhost:8000/api';
const authToken = localStorage.getItem('authToken') || '';
const currentUser = JSON.parse(localStorage.getItem('currentUser') || 'null');

function headers() {
  const h = { 'Content-Type': 'application/json' };
  if (authToken) h['Authorization'] = `Token ${authToken}`;
  return h;
}

function qs(id){ return document.getElementById(id); }

const select = qs('club-select');
const clubName = qs('club-name');
const clubArea = qs('club-area');
const clubDesc = qs('club-desc');
const clubEmail = qs('club-email');
const clubWhatsapp = qs('club-whatsapp');
const clubMsg = qs('club-msg');
const editBtn = qs('edit-club-btn');
const refreshBtn = qs('refresh-club-btn');
const openCreateBtn = qs('open-create-btn');

const editModal = qs('edit-modal');
const editName = qs('edit-name');
const editDesc = qs('edit-desc');
const editEmail = qs('edit-email');
const editWhatsapp = qs('edit-whatsapp');
const sendEditBtn = qs('send-edit-btn');
const cancelEditBtn = qs('cancel-edit-btn');
const editMsg = qs('edit-msg');

const eName = qs('e-name');
const eStart = qs('e-start');
const eEnd = qs('e-end');
const ePlace = qs('e-place');
const eDesc = qs('e-desc');
const eTipo = qs('e-tipo');
const eCupo = qs('e-cupo');
const createEventBtn = qs('create-event-btn');
const eventMsg = qs('event-msg');
const createEventModal = qs('create-event-modal');
const cancelCreateBtn = qs('cancel-create-btn');
const eventsBody = qs('events-body');
const eventsMsg = qs('events-msg');
const eventEditModal = qs('event-edit-modal');
const evTitle = qs('ev-title');
const evStart = qs('ev-start');
const evEnd = qs('ev-end');
const evType = qs('ev-type');
const evCupo = qs('ev-cupo');
const evPlace = qs('ev-place');
const evDesc = qs('ev-desc');
const saveEventBtn = qs('save-event-btn');
const cancelEventBtn = qs('cancel-event-btn');
const eventEditMsg = qs('event-edit-msg');

let currentGroupId = null;
let eventsCache = [];
let editingEventId = null;

function setControlsEnabled(enabled) {
  const ids = ['edit-club-btn','open-create-btn','e-name','e-start','e-end','e-place','e-desc','e-tipo','e-cupo','create-event-btn'];
  ids.forEach(id => {
    const el = document.getElementById(id);
    if (!el) return;
    el.disabled = !enabled;
    if (!enabled) el.classList.add('disabled'); else el.classList.remove('disabled');
  });
}

async function fetchUserGroups() {
  if (!currentUser) return [];
  const uid = currentUser.id_usuario || currentUser.id;
  try {
    const res = await fetch(`${API_BASE}/usuarios/${uid}/grupos/`, { headers: headers() });
    if (!res.ok) throw new Error(await res.text());
    const data = await res.json();
    const list = Array.isArray(data) ? data : data?.results || [];
    return list;
  } catch (err) {
    console.error('Error al obtener grupos usuario', err);
    return [];
  }
}

async function loadSelect() {
  select.innerHTML = '<option value="">-- Selecciona un club --</option>';
  const grupos = await fetchUserGroups();
  grupos.forEach(g => {
    const gid = g.grupo || g.id_grupo || g.id || g.grupo_id;
    const name = g.grupo_nombre || g.nombre_grupo || g.nombre || g.name || `Grupo ${gid}`;
    const opt = document.createElement('option');
    opt.value = gid;
    opt.textContent = name;
    select.appendChild(opt);
  });
}

async function fetchGroupDetails(id) {
  try {
    const res = await fetch(`${API_BASE}/grupos/${id}/`, { headers: headers() });
    if (!res.ok) throw new Error(await res.text());
    return await res.json();
  } catch (err) {
    console.error('Error fetching group details', err);
    return null;
  }
}

async function showGroup(id) {
  if (!id) {
    clubName.textContent = 'Nombre del club';
    clubArea.textContent = '';
    clubDesc.textContent = '';
    clubEmail.textContent = '';
    clubWhatsapp.textContent = '';
    currentGroupId = null;
    eventsBody.innerHTML = '';
    return;
  }
  const g = await fetchGroupDetails(id);
  if (!g) {
    clubMsg.textContent = 'No se pudo cargar la información del club.';
    clubMsg.classList.remove('hidden');
    return;
  }
  clubMsg.classList.add('hidden');
  currentGroupId = g.id_grupo || g.id;
  clubName.textContent = g.nombre_grupo || g.nombre || g.name || `Grupo ${currentGroupId}`;
  clubArea.textContent = g.area_interes ? `Área: ${g.area_interes}` : '';
  clubDesc.textContent = g.descripcion || g.descripcion_grupo || g.descripcion_grupo || '';
  clubEmail.textContent = g.correo_grupo || g.correo || '';
  clubWhatsapp.textContent = g.link_whatsapp || g.whatsapp || '';
  // Prefill edit form
  editName.value = clubName.textContent;
  editDesc.value = clubDesc.textContent;
  editEmail.value = clubEmail.textContent;
  editWhatsapp.value = clubWhatsapp.textContent;
  await loadEventsList(currentGroupId);
}

select.addEventListener('change', (e) => {
  const val = e.target.value;
  if (!val) {
    setControlsEnabled(false);
    showGroup('');
    return;
  }
  setControlsEnabled(true);
  showGroup(val);
});

refreshBtn.addEventListener('click', async () => {
  if (!select.value) {
    await loadSelect();
    clubMsg.textContent = 'Lista actualizada.';
    clubMsg.classList.remove('hidden');
    setTimeout(()=>clubMsg.classList.add('hidden'),2000);
    return;
  }
  await showGroup(select.value);
});

// Abrir/cerrar modal de creación de evento
if (openCreateBtn) {
  openCreateBtn.addEventListener('click', () => {
    if (!currentUser) { alert('Debes iniciar sesión'); return; }
    if (!currentGroupId) { alert('Selecciona primero un club'); return; }
    createEventModal.classList.remove('hidden');
    eventMsg.classList.add('hidden');
  });
}

if (cancelCreateBtn) {
  cancelCreateBtn.addEventListener('click', () => {
    createEventModal.classList.add('hidden');
  });
}

function formatDate(str) {
  if (!str) return '';
  const d = new Date(str);
  if (isNaN(d.getTime())) return str;
  return d.toLocaleString();
}

function toLocalInput(str) {
  if (!str) return '';
  const d = new Date(str);
  if (isNaN(d.getTime())) return '';
  const off = d.getTimezoneOffset();
  const local = new Date(d.getTime() - off * 60000);
  return local.toISOString().slice(0, 16);
}

async function loadEventsList(grupoId) {
  if (!grupoId) return;
  try {
    const res = await fetch(`${API_BASE}/eventos/?grupo=${grupoId}`, { headers: headers() });
    const text = await res.text();
    let data = [];
    try {
      const parsed = text ? JSON.parse(text) : [];
      data = Array.isArray(parsed) ? parsed : (parsed.results || []);
    } catch (err) {
      console.error('Parse eventos', err, text);
    }
    eventsCache = data || [];
    renderEventsTable(eventsCache);
    eventsMsg.classList.add('hidden');
  } catch (err) {
    console.error('Error cargando eventos', err);
    eventsMsg.textContent = 'No se pudieron cargar los eventos.';
    eventsMsg.classList.remove('hidden');
  }
}

function renderEventsTable(list) {
  if (!eventsBody) return;
  eventsBody.innerHTML = '';
  if (!list || list.length === 0) {
    const tr = document.createElement('tr');
    tr.innerHTML = `<td colspan="5" style="padding:.6rem;color:#64748b">Sin eventos para este club.</td>`;
    eventsBody.appendChild(tr);
    return;
  }
  list.forEach(ev => {
    const tr = document.createElement('tr');
    tr.style.borderBottom = '1px solid #e5e7eb';
    tr.innerHTML = `
      <td style="padding:.5rem">${ev.nombre_evento || 'Evento'}</td>
      <td style="padding:.5rem">${formatDate(ev.fecha_inicio)}</td>
      <td style="padding:.5rem">${ev.tipo_evento || ''}</td>
      <td style="padding:.5rem">${ev.cupo ?? ''}</td>
      <td style="padding:.5rem;white-space:nowrap">
        <button class="btn-secondary small edit-event-btn" data-id="${ev.id_evento}">Editar</button>
        <button class="btn-secondary small delete-event-btn" data-id="${ev.id_evento}" style="background:#ef4444">Eliminar</button>
      </td>
    `;
    eventsBody.appendChild(tr);
  });
}

// Edit flow: abrir modal
editBtn.addEventListener('click', () => {
  if (!currentUser) { alert('Debes iniciar sesión'); return; }
  if (!currentGroupId) { alert('Selecciona primero un club'); return; }
  editModal.classList.remove('hidden');
});

cancelEditBtn.addEventListener('click', () => {
  editModal.classList.add('hidden');
});

sendEditBtn.addEventListener('click', async () => {
  if (!currentGroupId) return;

  const updatePayload = {
    nombre_grupo: editName.value || '',
    descripcion: editDesc.value || '',
    correo_grupo: editEmail.value || '',
    link_whatsapp: editWhatsapp.value || ''
  };

  try {
    // Enviar al endpoint real de grupos para actualizar datos del club (evita 404 de /solicitudes/)
    const res = await fetch(`${API_BASE}/grupos/${currentGroupId}/`, {
      method: 'PATCH',
      headers: headers(),
      body: JSON.stringify(updatePayload)
    });

    const text = await res.text();
    if (!res.ok) throw new Error(text || res.statusText);

    editMsg.textContent = 'Cambios enviados correctamente.';
    editMsg.classList.remove('hidden');
    setTimeout(()=>{ editModal.classList.add('hidden'); editMsg.classList.add('hidden'); },2000);
    await showGroup(currentGroupId); // refresca datos visibles
  } catch (err) {
    console.error(err);
    editMsg.textContent = 'Error enviando la solicitud: ' + err.message;
    editMsg.classList.remove('hidden');
  }
});

// Crear evento (como solicitud / evento pendiente)
createEventBtn.addEventListener('click', async () => {
  if (!currentUser) { alert('Debes iniciar sesión'); return; }
  if (!currentGroupId) { alert('Selecciona primero un club'); return; }
  // Validaciones cliente
  const tipo = eTipo.value || '';
  const cupo = Number(eCupo.value || 0);
  if (!tipo) {
    eventMsg.textContent = 'Seleccione el tipo de evento.';
    eventMsg.classList.remove('hidden');
    return;
  }
  if (!cupo || cupo <= 0) {
    eventMsg.textContent = 'Ingrese un cupo válido (> 0).';
    eventMsg.classList.remove('hidden');
    return;
  }

  const solicitudPayload = {
    tipo_solicitud: 'crear_evento',
    grupo: currentGroupId,
    creador: currentUser ? (currentUser.id_usuario || currentUser.id) : null,
    datos_evento: {
      nombre_evento: eName.value || 'Evento',
      fecha_inicio: eStart.value || null,
      fecha_fin: eEnd.value || null,
      lugar: ePlace.value || '',
      descripcion_evento: eDesc.value || '',
      tipo_evento: tipo,
      cupo: cupo,
      notificar: true
    }
  };

  try {
    // Enviar directamente al endpoint de eventos con los campos obligatorios
    const eventoPayload = {
      grupo: currentGroupId,
      nombre_evento: eName.value || 'Evento',
      descripcion_evento: eDesc.value || '',
      fecha_inicio: eStart.value || null,
      fecha_fin: eEnd.value || null,
      lugar: ePlace.value || '',
      tipo_evento: tipo,
      cupo: cupo,
      // estado_evento: 'PROGRAMADO' // el serializer tiene default
    };

    const res = await fetch(`${API_BASE}/eventos/`, {
      method: 'POST',
      headers: headers(),
      body: JSON.stringify(eventoPayload)
    });

    const text = await res.text();
    let data = null;
    try { data = text ? JSON.parse(text) : null; } catch(e) { data = text; }

    if (!res.ok) {
      // Si backend devuelve HTML o JSON, hacemos un mensaje legible
      let msg = data && data.detail ? data.detail : (data && data.error ? data.error : text || res.statusText);
      throw new Error(msg);
    }

    eventMsg.textContent = 'Evento creado correctamente.';
    eventMsg.classList.remove('hidden');
    setTimeout(()=>{ eventMsg.classList.add('hidden'); },3000);
    // reset
    eName.value=''; eStart.value=''; eEnd.value=''; ePlace.value=''; eDesc.value=''; eTipo.value=''; eCupo.value='';
    await loadEventsList(currentGroupId);
    createEventModal.classList.add('hidden');
  } catch (err) {
    console.error(err);
    let msg = err.message || String(err);
    eventMsg.textContent = 'Error creando el evento: ' + msg;
    eventMsg.classList.remove('hidden');
  }
});

// Tabla de eventos: delegación para editar/eliminar
eventsBody.addEventListener('click', (ev) => {
  const target = ev.target;
  if (target.classList.contains('edit-event-btn')) {
    const id = target.getAttribute('data-id');
    openEditEvent(id);
  }
  if (target.classList.contains('delete-event-btn')) {
    const id = target.getAttribute('data-id');
    deleteEvent(id);
  }
});

function openEditEvent(id) {
  const evData = eventsCache.find(e => String(e.id_evento) === String(id));
  if (!evData) return;
  editingEventId = evData.id_evento;
  evTitle.value = evData.nombre_evento || '';
  evDesc.value = evData.descripcion_evento || '';
  evPlace.value = evData.lugar || '';
  evType.value = evData.tipo_evento || '';
  evCupo.value = evData.cupo || '';
  evStart.value = toLocalInput(evData.fecha_inicio);
  evEnd.value = toLocalInput(evData.fecha_fin);
  eventEditMsg.classList.add('hidden');
  eventEditModal.classList.remove('hidden');
}

cancelEventBtn.addEventListener('click', () => {
  eventEditModal.classList.add('hidden');
  editingEventId = null;
});

saveEventBtn.addEventListener('click', async () => {
  if (!editingEventId) return;
  const payload = {
    nombre_evento: evTitle.value || 'Evento',
    descripcion_evento: evDesc.value || '',
    lugar: evPlace.value || '',
    tipo_evento: evType.value || '',
    cupo: Number(evCupo.value || 0),
    fecha_inicio: evStart.value || null,
    fecha_fin: evEnd.value || null,
    grupo: currentGroupId
  };
  if (!payload.tipo_evento) {
    eventEditMsg.textContent = 'Selecciona un tipo de evento.';
    eventEditMsg.classList.remove('hidden');
    return;
  }
  if (!payload.cupo || payload.cupo <= 0) {
    eventEditMsg.textContent = 'Cupo debe ser mayor que 0.';
    eventEditMsg.classList.remove('hidden');
    return;
  }
  try {
    const res = await fetch(`${API_BASE}/eventos/${editingEventId}/`, {
      method: 'PATCH',
      headers: headers(),
      body: JSON.stringify(payload)
    });
    const text = await res.text();
    if (!res.ok) throw new Error(text || res.statusText);
    eventEditMsg.textContent = 'Evento actualizado.';
    eventEditMsg.classList.remove('hidden');
    setTimeout(()=>{ eventEditModal.classList.add('hidden'); eventEditMsg.classList.add('hidden'); },1500);
    await loadEventsList(currentGroupId);
  } catch (err) {
    console.error(err);
    eventEditMsg.textContent = 'Error actualizando: ' + err.message;
    eventEditMsg.classList.remove('hidden');
  }
});

async function deleteEvent(id) {
  if (!id) return;
  const confirmDelete = confirm('¿Eliminar este evento?');
  if (!confirmDelete) return;
  try {
    const res = await fetch(`${API_BASE}/eventos/${id}/`, {
      method: 'DELETE',
      headers: headers()
    });
    if (!res.ok) throw new Error(await res.text());
    await loadEventsList(currentGroupId);
    eventsMsg.textContent = 'Evento eliminado.';
    eventsMsg.classList.remove('hidden');
    setTimeout(()=>eventsMsg.classList.add('hidden'), 2000);
  } catch (err) {
    console.error(err);
    eventsMsg.textContent = 'No se pudo eliminar: ' + err.message;
    eventsMsg.classList.remove('hidden');
  }
}

// Inicialización
(async function init(){
  if (!currentUser) {
    clubMsg.textContent = 'Debes iniciar sesión para gestionar clubs.';
    clubMsg.classList.remove('hidden');
  }
  setControlsEnabled(false);
  await loadSelect();
})();
