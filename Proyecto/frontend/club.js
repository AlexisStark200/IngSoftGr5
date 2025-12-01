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

let currentGroupId = null;

function setControlsEnabled(enabled) {
  const ids = ['edit-club-btn','e-name','e-start','e-end','e-place','e-desc','e-tipo','e-cupo','create-event-btn'];
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
  const payload = {
    tipo_solicitud: 'editar_club',
    grupo: currentGroupId,
    creador: currentUser ? (currentUser.id_usuario || currentUser.id) : null,
    cambios: {
      nombre_grupo: editName.value || '',
      descripcion: editDesc.value || '',
      correo_grupo: editEmail.value || '',
      link_whatsapp: editWhatsapp.value || ''
    }
  };
  try {
    const res = await fetch(`${API_BASE}/solicitudes/`, {
      method: 'POST',
      headers: headers(),
      body: JSON.stringify(payload)
    });
    if (!res.ok) throw new Error(await res.text());
    editMsg.textContent = 'Solicitud enviada al administrador.';
    editMsg.classList.remove('hidden');
    setTimeout(()=>{ editModal.classList.add('hidden'); editMsg.classList.add('hidden'); },2000);
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
  } catch (err) {
    console.error(err);
    let msg = err.message || String(err);
    eventMsg.textContent = 'Error creando el evento: ' + msg;
    eventMsg.classList.remove('hidden');
  }
});

// Inicialización
(async function init(){
  if (!currentUser) {
    clubMsg.textContent = 'Debes iniciar sesión para gestionar clubs.';
    clubMsg.classList.remove('hidden');
  }
  setControlsEnabled(false);
  await loadSelect();
})();
