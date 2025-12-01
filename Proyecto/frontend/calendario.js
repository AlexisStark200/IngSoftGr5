
// FullCalendar integración
const calMessage = document.getElementById('cal-message');
const calendarDiv = document.getElementById('calendar');
const API_BASE = localStorage.getItem('API_BASE') || 'http://localhost:8000/api';
const API_TOKEN = localStorage.getItem('API_TOKEN') || '';
const USER_ID = localStorage.getItem('USER_ID') || '';
function headers() {
  const h = { 'Content-Type': 'application/json' };
  if (API_TOKEN) h['Authorization'] = `Token ${API_TOKEN}`;
  return h;
}
async function fetchJSON(url, opts = {}) {
  const res = await fetch(url, {
    ...opts,
    headers: { ...headers(), ...(opts.headers || {}) },
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}: ${await res.text()}`);
  const text = await res.text();
  if (!text) return null;
  return JSON.parse(text);
}
async function getEventosUsuario() {
  if (!USER_ID) return [];
  // 1. Obtener los grupos del usuario
  const grupos = await fetchJSON(`${API_BASE}/usuarios/${USER_ID}/grupos/`);
  const grupoIds = Array.isArray(grupos) ? grupos.map(g => g.grupo) : [];
  if (!grupoIds.length) return [];
  // 2. Obtener eventos de cada grupo
  let eventos = [];
  for (const gid of grupoIds) {
    try {
      const evs = await fetchJSON(`${API_BASE}/grupos/${gid}/eventos/`);
      if (Array.isArray(evs)) eventos = eventos.concat(evs);
    } catch {}
  }
  return eventos;
}
function mapEventosToCalendar(evList) {
  // FullCalendar espera: { title, start, end, description, ... }
  return evList.map(ev => ({
    title: `${ev.nombre_evento || 'Evento'}${ev.grupo_nombre ? ' - ' + ev.grupo_nombre : ''}`,
    start: ev.fecha_inicio,
    end: ev.fecha_fin,
    description: ev.descripcion_evento || '',
    location: ev.lugar || '',
    estado: ev.estado_evento || '',
  }));
}
async function renderCalendar() {
  if (!USER_ID) {
    calMessage.textContent = 'Debes iniciar sesión para ver tu calendario.';
    calMessage.classList.remove('hidden');
    calendarDiv.innerHTML = '';
    return;
  }
  calMessage.classList.add('hidden');
  calendarDiv.innerHTML = '';
  try {
    const eventos = await getEventosUsuario();
    const calendarEvents = mapEventosToCalendar(eventos);
    // Inicializar FullCalendar
    const calendar = new FullCalendar.Calendar(calendarDiv, {
      initialView: 'dayGridMonth',
      headerToolbar: {
        left: 'prev,next today',
        center: 'title',
        right: 'dayGridMonth,timeGridWeek',
      },
      locale: 'es',
      buttonText: {
        today: 'Hoy',
        month: 'Mes',
        week: 'Semana',
        day: 'Día',
        list: 'Lista'
      },
      events: calendarEvents,
      eventClick: function(info) {
        // Mostrar detalles en un alert o modal
        const ev = info.event;
        alert(
          `${ev.title}\n\n` +
          `Inicio: ${ev.start ? ev.start.toLocaleString('es-CO') : ''}\n` +
          (ev.end ? `Fin: ${ev.end.toLocaleString('es-CO')}\n` : '') +
          (ev.extendedProps.location ? `Lugar: ${ev.extendedProps.location}\n` : '') +
          (ev.extendedProps.description ? `Descripción: ${ev.extendedProps.description}\n` : '') +
          (ev.extendedProps.estado ? `Estado: ${ev.extendedProps.estado}` : '')
        );
      },
      height: 650,
    });
    calendar.render();
    if (!eventos.length) {
      calMessage.textContent = 'No hay eventos próximos en tus grupos.';
      calMessage.classList.remove('hidden');
    } else {
      calMessage.classList.add('hidden');
    }
  } catch (err) {
    calendarDiv.innerHTML = '';
    calMessage.textContent = 'Error al cargar eventos: ' + err.message;
    calMessage.classList.remove('hidden');
  }
}
renderCalendar();
