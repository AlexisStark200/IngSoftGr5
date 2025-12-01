// AgoraUN - Panel principal con vistas por rol
console.log("=== AGORAUN FRONTEND INICIADO ===");

document.addEventListener('DOMContentLoaded', () => {
  const $ = (q) => document.querySelector(q);
  const $$ = (q) => document.querySelectorAll(q);

  // DOM principal
  const landing = $('#landing');
  const dashboard = $('#dashboard');

  // Configuracion API
  const apiBaseInput = $('#apiBase');
  const saveBaseBtn = $('#saveBase');
  const apiTokenInput = $('#apiToken');
  const saveTokenBtn = $('#saveToken');

  // Busqueda catalogo
  const searchBtn = $('#searchBtn');
  const qInput = $('#q');
  const areaSel = $('#area');
  const groupsDiv = $('#groups');
  const cardTpl = $('#cardTpl');

  // Auth
  const authLoggedOut = $('#auth-logged-out');
  const authLoggedIn = $('#auth-logged-in');
  const loginForm = $('#login-form');
  const registerForm = $('#register-form');
  const authMessage = $('#auth-message');
  const userName = $('#user-name');
  const rolePill = $('#role-pill');
  const logoutBtn = $('#logout-btn');
  const authTabs = $$('.auth-tab');
  const toggleLoginPass = $('#login-pass-toggle');
  const toggleRegPass = $('#register-pass-toggle');
  const toggleRegPass2 = $('#register-pass2-toggle');

  // Acciones de usuario
  const createGroupBtn = $('#create-group-btn');
  const createGroupModal = $('#create-group-modal');
  const createGroupForm = $('#create-group-form');
  const createGroupCancel = $('#g-cancel');
  const createGroupMessage = $('#g-message');
  const calendarBtn = $('#calendar-btn');
  const clubBtn = $('#club-btn');

  // Secciones de contenido
  const myGroupsStack = $('#my-groups');
  const calendarList = $('#calendar-list');
  const requestsSection = $('#admin-requests');
  const requestsList = $('#requests-list');
  const reloadRequestsBtn = $('#reloadRequests');

  // Estado
  let API_BASE = localStorage.getItem('API_BASE') || 'http://localhost:8000/api';
  let currentUser = JSON.parse(localStorage.getItem('currentUser') || 'null');
  let authToken = localStorage.getItem('authToken') || '';
  let currentRoles = [];
  let _userGroupIdsCache = null;

  apiBaseInput.value = API_BASE;
  if (apiTokenInput) apiTokenInput.value = authToken;

  // ==================== UTILS ====================
  function headers() {
    const h = { 'Content-Type': 'application/json' };
    if (authToken) h['Authorization'] = `Token ${authToken}`;
    return h;
  }

  async function fetchJSON(url, opts = {}) {
    const res = await fetch(url, { ...opts, headers: { ...headers(), ...(opts.headers || {}) } });
    if (!res.ok) {
      const text = await res.text();
      throw new Error(`HTTP ${res.status}: ${text}`);
    }
    if (res.status === 204 || res.status === 205) return null;
    const text = await res.text();
    if (!text) return null;
    return JSON.parse(text);
  }

  const isValidUNALEmail = (email) => email.toLowerCase().endsWith('@unal.edu.co');

  function showAuthMessage(text, type = 'error') {
    if (!authMessage) return;
    authMessage.textContent = text;
    authMessage.className = `message ${type}`;
    authMessage.classList.remove('hidden');
  }

  function hideAuthMessage() {
    if (!authMessage) return;
    authMessage.classList.add('hidden');
  }

  function toggleLanding(loggedIn) {
    if (loggedIn) {
      landing?.classList.add('hidden');
      dashboard?.classList.remove('hidden');
    } else {
      landing?.classList.remove('hidden');
      dashboard?.classList.add('hidden');
    }
  }

  function updateAuthUI() {
    const loggedIn = Boolean(currentUser && authToken);
    toggleLanding(loggedIn);

    if (loggedIn) {
      authLoggedOut?.classList.add('hidden');
      authLoggedIn?.classList.remove('hidden');
      const nombre = currentUser.nombre_usuario || currentUser.nombre || currentUser.firstName || '';
      const apellido = currentUser.apellido || currentUser.lastName || '';
      userName.textContent = `${nombre} ${apellido}`.trim();
      [createGroupBtn, calendarBtn, clubBtn].forEach((btn) => {
        if (btn) {
          btn.classList.remove('hidden');
          btn.style.display = 'inline-flex';
        }
      });
    } else {
      authLoggedOut?.classList.remove('hidden');
      authLoggedIn?.classList.add('hidden');
      [createGroupBtn, calendarBtn, clubBtn].forEach((btn) => {
        if (btn) {
          btn.classList.add('hidden');
          btn.style.display = 'none';
        }
      });
    }
  }

  function updateRoleUI() {
    if (!rolePill) return;
    if (!currentRoles.length) {
      rolePill.textContent = 'Rol: estudiante';
    } else {
      rolePill.textContent = `Rol: ${currentRoles.join(', ').toLowerCase()}`;
    }
    const isAdminGeneral = currentRoles.includes('ADMIN_GENERAL');
    if (isAdminGeneral) {
      requestsSection?.classList.remove('hidden');
    } else {
      requestsSection?.classList.add('hidden');
    }
  }

  // ==================== AUTH HANDLERS ====================
  authTabs.forEach((tab) => {
    tab.addEventListener('click', (e) => {
      e.preventDefault();
      const tabName = tab.dataset.tab;
      authTabs.forEach((t) => t.classList.remove('active'));
      tab.classList.add('active');
      $$('.auth-form').forEach((form) => form.classList.remove('active'));
      const form = document.getElementById(`${tabName}-form`);
      form?.classList.add('active');
      hideAuthMessage();
    });
  });

  // Mostrar/ocultar contrasenas
  function setupPassToggle(inputId, btn) {
    if (!btn) return;
    const input = document.getElementById(inputId);
    if (!input) return;
    btn.setAttribute('aria-label', 'Mostrar contraseña');
    btn.addEventListener('click', () => {
      const isHidden = input.type === 'password';
      input.type = isHidden ? 'text' : 'password';
      btn.classList.toggle('is-on', !isHidden);
      btn.setAttribute('aria-label', isHidden ? 'Ocultar contraseña' : 'Mostrar contraseña');
    });
  }
  setupPassToggle('login-password', toggleLoginPass);
  setupPassToggle('register-password', toggleRegPass);
  setupPassToggle('register-password-confirm', toggleRegPass2);

  loginForm?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const email = $('#login-email').value;
    const password = $('#login-password').value;
    if (!isValidUNALEmail(email)) {
      showAuthMessage('Usa tu correo @unal.edu.co', 'error');
      return;
    }
    try {
      showAuthMessage('Iniciando sesion...', 'success');
      const response = await fetch(`${API_BASE}/auth/login/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ correo: email, password })
      });
      const data = await response.json();
      if (response.ok) {
        authToken = data.token;
        currentUser = data.usuario;
        localStorage.setItem('authToken', authToken);
        localStorage.setItem('currentUser', JSON.stringify(currentUser));
        showAuthMessage('Login exitoso', 'success');
        await bootstrapAfterAuth();
        loginForm.reset();
      } else {
        showAuthMessage(data.error || 'Error en el login', 'error');
      }
    } catch (error) {
      console.error(error);
      showAuthMessage(`Error de conexion: ${error.message}`, 'error');
    }
  });

  registerForm?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const nombre = $('#register-nombre').value;
    const apellido = $('#register-apellido').value;
    const email = $('#register-email').value;
    const password = $('#register-password').value;
    const passwordConfirm = $('#register-password-confirm').value;

    if (!isValidUNALEmail(email)) {
      showAuthMessage('Usa tu correo @unal.edu.co', 'error');
      return;
    }
    if (password !== passwordConfirm) {
      showAuthMessage('Las contrasenas no coinciden', 'error');
      return;
    }
    if (password.length < 8) {
      showAuthMessage('Minimo 8 caracteres', 'error');
      return;
    }

    try {
      showAuthMessage('Creando cuenta...', 'success');
      const response = await fetch(`${API_BASE}/auth/register/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ nombre_usuario: nombre, apellido, correo: email, password })
      });
      const data = await response.json();
      if (response.ok) {
        authToken = data.token;
        currentUser = data.usuario;
        localStorage.setItem('authToken', authToken);
        localStorage.setItem('currentUser', JSON.stringify(currentUser));
        showAuthMessage('Registro exitoso', 'success');
        authTabs[0]?.click();
        await bootstrapAfterAuth();
        registerForm.reset();
      } else {
        showAuthMessage(data.error || 'Error en el registro', 'error');
      }
    } catch (error) {
      console.error(error);
      showAuthMessage(`Error de conexion: ${error.message}`, 'error');
    }
  });

  logoutBtn?.addEventListener('click', () => {
    authToken = '';
    currentUser = null;
    currentRoles = [];
    _userGroupIdsCache = null;
    localStorage.removeItem('authToken');
    localStorage.removeItem('currentUser');
    updateAuthUI();
    groupsDiv.innerHTML = '';
    myGroupsStack.innerHTML = '';
    calendarList.innerHTML = '';
    showAuthMessage('Sesion cerrada', 'success');
  });

  saveBaseBtn?.addEventListener('click', () => {
    API_BASE = apiBaseInput.value.trim().replace(/\/+$/, '');
    localStorage.setItem('API_BASE', API_BASE);
    if (currentUser) fetchGroups();
  });

  saveTokenBtn?.addEventListener('click', () => {
    authToken = apiTokenInput.value.trim();
    localStorage.setItem('authToken', authToken);
    showAuthMessage('Token guardado', 'success');
  });

  // ==================== DATA LOADERS ====================
  async function loadRoles() {
    if (!currentUser) { currentRoles = []; return; }
    const uid = currentUser.id_usuario || currentUser.id;
    try {
      const data = await fetchJSON(`${API_BASE}/usuarios/${uid}/roles/`);
      const list = Array.isArray(data) ? data : data?.results || [];
      currentRoles = list.map((r) => r.rol?.nombre_rol || r.nombre_rol || r.rol).filter(Boolean);
    } catch (err) {
      console.warn('No se pudieron cargar roles:', err.message);
      currentRoles = [];
    }
  }

  async function getUserGroupIds() {
    if (!currentUser) return [];
    if (_userGroupIdsCache) return _userGroupIdsCache;
    try {
      const uid = currentUser.id_usuario || currentUser.id;
      const res = await fetchJSON(`${API_BASE}/usuarios/${uid}/grupos/`);
      const list = Array.isArray(res) ? res : res?.results || [];
      _userGroupIdsCache = list.map((g) => g.grupo || g.id_grupo || g.id || g.grupo_id).filter((x) => x != null);
      return _userGroupIdsCache;
    } catch (err) {
      console.warn('No se pudo obtener grupos del usuario:', err.message);
      _userGroupIdsCache = [];
      return _userGroupIdsCache;
    }
  }

  async function loadMyGroups() {
    if (!myGroupsStack) return;
    myGroupsStack.innerHTML = '<p>Cargando mis grupos...</p>';
    if (!currentUser) {
      myGroupsStack.innerHTML = '<p>Inicia sesion para ver tus grupos.</p>';
      return;
    }
    try {
      const uid = currentUser.id_usuario || currentUser.id;
      const res = await fetchJSON(`${API_BASE}/usuarios/${uid}/grupos/`);
      const list = Array.isArray(res) ? res : res?.results || [];
      if (!list.length) {
        myGroupsStack.innerHTML = '<p>No tienes grupos aun. Explora el catalogo y unete.</p>';
        return;
      }
      myGroupsStack.innerHTML = '';
      list.forEach((g) => {
        const card = document.createElement('article');
        card.className = 'card horizontal';
        const nombre = g.nombre_grupo || g.nombre || g.grupo_nombre || 'Grupo';
        const area = g.area_interes || g.area || '';
        const estado = g.estado_grupo || g.estado || '';
        card.innerHTML = `
          <div>
            <p class="eyebrow">${area || 'Area sin definir'}</p>
            <h3>${nombre}</h3>
            <p class="tag">${estado || 'Activo'}</p>
          </div>
          <div class="actions">
            <button class="secondary" data-action="leave">Salir</button>
          </div>
        `;
        card.querySelector('[data-action="leave"]').onclick = () => leaveGroup(g.grupo || g.id_grupo || g.id);
        myGroupsStack.appendChild(card);
      });
    } catch (err) {
      myGroupsStack.innerHTML = `<p class="error">${err.message}</p>`;
    }
  }

  async function loadCalendar() {
    if (!calendarList) return;
    calendarList.innerHTML = '<p>Cargando eventos...</p>';
    try {
      const res = await fetchJSON(`${API_BASE}/eventos/`);
      const items = Array.isArray(res) ? res : res?.results || [];
      if (!items.length) {
        calendarList.innerHTML = '<p>Sin eventos publicados.</p>';
        return;
      }
      calendarList.innerHTML = '';
      items.slice(0, 10).forEach((ev) => {
        const row = document.createElement('div');
        row.className = 'card horizontal';
        const titulo = ev.nombre_evento || ev.titulo || 'Evento';
        const fecha = ev.fecha_inicio || ev.fecha || '';
        const lugar = ev.lugar || '';
        const fechaTxt = fecha ? new Date(fecha).toLocaleString() : '';
        row.innerHTML = `
          <div>
            <p class="eyebrow">${ev.grupo_nombre || 'Actividad'}</p>
            <h3>${titulo}</h3>
            <p>${fechaTxt}${lugar ? ' @ ' + lugar : ''}</p>
          </div>
          <div class="tag">${ev.estado_evento || 'Programado'}</div>
        `;
        calendarList.appendChild(row);
      });
    } catch (err) {
      calendarList.innerHTML = `<p class="error">${err.message}</p>`;
    }
  }

  async function loadRequests() {
    const isAdmin = currentRoles.includes('ADMIN_GENERAL');
    if (!isAdmin) {
      requestsSection?.classList.add('hidden');
      return;
    }
    requestsSection?.classList.remove('hidden');
    requestsList.innerHTML = '<p>Cargando solicitudes...</p>';
    try {
      const data = await fetchJSON(`${API_BASE}/grupos/?estado=PENDIENTE`);
      const items = Array.isArray(data) ? data : data?.results || [];
      if (!items.length) {
        requestsList.innerHTML = '<p>No hay solicitudes pendientes.</p>';
        return;
      }
      requestsList.innerHTML = '';
      items.forEach((g) => {
        const card = document.createElement('article');
        card.className = 'card horizontal';
        card.innerHTML = `
          <div>
            <p class="eyebrow">${g.area_interes || 'Area'}</p>
            <h3>${g.nombre_grupo || 'Grupo'}</h3>
            <p>${g.tipo_grupo || ''}</p>
            <p class="tag">${g.estado_grupo || 'PENDIENTE'}</p>
          </div>
          <div class="actions">
            <button class="btn-approve">Aprobar</button>
            <button class="btn-reject secondary">Rechazar</button>
          </div>
        `;
        card.querySelector('.btn-approve').onclick = () => aprobarGrupo(g.id_grupo || g.id);
        card.querySelector('.btn-reject').onclick = () => rechazarGrupo(g.id_grupo || g.id);
        requestsList.appendChild(card);
      });
    } catch (err) {
      requestsList.innerHTML = `<p class="error">${err.message}</p>`;
    }
  }

  // ==================== CATALOGO ====================
  searchBtn?.addEventListener('click', () => fetchGroups());

  async function fetchGroups() {
    if (!groupsDiv) return;
    groupsDiv.innerHTML = '<p>Cargando catalogo...</p>';
    try {
      const params = new URLSearchParams();
      const q = qInput?.value.trim();
      const area = areaSel?.value.trim();
      if (q) params.set('search', q);
      if (area) params.set('area', area);
      const query = params.toString();
      const url = query ? `${API_BASE}/grupos/?${query}` : `${API_BASE}/grupos/`;
      const data = await fetchJSON(url);
      const items = Array.isArray(data) ? data : data?.results || [];
      await renderGroups(items);
    } catch (err) {
      groupsDiv.innerHTML = `<p class="error">${err.message}</p>`;
    }
  }

  async function renderGroups(items) {
    groupsDiv.innerHTML = '';
    if (!items.length) {
      groupsDiv.innerHTML = '<div class="no-results"><h3>Sin resultados</h3><p>No se encontraron grupos.</p></div>';
      return;
    }
    const userGroupIds = currentUser ? await getUserGroupIds() : [];
    items.forEach((g) => {
      const id = g.id_grupo || g.id;
      const nombre = g.nombre_grupo || g.nombre || `Grupo #${id}`;
      const area = g.area_interes || g.area || '';
      const desc = g.descripcion || g.descripcion_grupo || g.description || '';
      const miembrosCount = g.miembros?.length || g.total_miembros || g.num_miembros || '';
      const eventosCount = g.eventos?.length || g.total_eventos || g.num_eventos || '';
      const frag = cardTpl.content.cloneNode(true);
      const card = frag.querySelector('.card');
      const heroEl = card.querySelector('.card-hero-img');
      const heroLetter = card.querySelector('.card-hero-letter');
      const nameEl = card.querySelector('.g-name');
      const areaEl = card.querySelector('.g-area');
      const descEl = card.querySelector('.g-desc');
      const metaMembers = card.querySelector('.meta-members');
      const metaEvents = card.querySelector('.meta-events');
      const detailEl = card.querySelector('.detail');
      const eventsList = card.querySelector('.events');
      const btnView = card.querySelector('.btn-view');
      const btnJoin = card.querySelector('.btn-join');
      const btnLeave = card.querySelector('.btn-leave');
      nameEl.textContent = nombre;
      areaEl.textContent = area || 'General';
      descEl.textContent = desc ? desc.slice(0, 140) + (desc.length > 140 ? '…' : '') : 'Explora las actividades y proyectos de este club.';
      if (metaMembers) metaMembers.textContent = miembrosCount ? `${miembrosCount} miembros` : '';
      if (metaEvents) metaEvents.textContent = eventosCount ? `${eventosCount} eventos` : '';

      // Logo del club
      const logoUrl = resolveLogoUrl(g);
      const initial = (nombre || 'A').trim().charAt(0).toUpperCase();
      if (heroLetter) heroLetter.textContent = initial;
      if (heroEl) {
        if (logoUrl) {
          heroEl.style.backgroundImage = `url("${logoUrl}")`;
          heroEl.classList.remove('placeholder');
        } else {
          heroEl.style.backgroundImage = '';
          heroEl.classList.add('placeholder');
        }
      }

      const possibleFlags = [g.usuario_inscrito, g.esta_inscrito, g.is_member, g.en_miembros, g.miembro, g.user_is_member];
      let isMember = possibleFlags.some(Boolean);
      const uid = currentUser?.id_usuario || currentUser?.id;
      if (!isMember && Array.isArray(g.miembros)) {
        isMember = g.miembros.some((m) => m === uid || m?.id === uid || m?.id_usuario === uid);
      }
      if (!isMember && userGroupIds?.length) {
        isMember = userGroupIds.includes(id);
      }

      if (!currentUser) {
        btnJoin.style.display = 'none';
        btnLeave.style.display = 'none';
      } else if (isMember) {
        btnJoin.style.display = 'none';
        btnLeave.style.display = 'inline-block';
      } else {
        btnJoin.style.display = 'inline-block';
        btnLeave.style.display = 'none';
      }

      btnView.onclick = async () => {
        detailEl.classList.toggle('hidden');
        if (!detailEl.classList.contains('hidden')) {
          eventsList.innerHTML = '<li>Cargando eventos...</li>';
          try {
            const evs = await fetchJSON(`${API_BASE}/grupos/${id}/eventos/`);
            const lista = Array.isArray(evs) ? evs : evs?.results || [];
            eventsList.innerHTML = '';
            if (!lista.length) {
              eventsList.innerHTML = '<li>Sin eventos registrados</li>';
              return;
            }
            lista.forEach((e) => {
              const li = document.createElement('li');
              const titulo = e.nombre_evento || e.titulo || 'Evento';
              const fecha = e.fecha_inicio || e.fecha || '';
              const lugar = e.lugar || '';
              const fechaTxt = fecha ? new Date(fecha).toLocaleString() : '';
              li.textContent = `${titulo}${fechaTxt ? ' · ' + fechaTxt : ''}${lugar ? ' @ ' + lugar : ''}`;
              eventsList.appendChild(li);
            });
          } catch (err) {
            eventsList.innerHTML = `<li class="error">${err.message}</li>`;
          }
        }
      };

      btnJoin.onclick = async () => {
        if (!currentUser) { alert('Debes iniciar sesion para unirte.'); return; }
        try {
          await fetchJSON(`${API_BASE}/grupos/${id}/agregar_miembro/`, {
            method: 'POST',
            body: JSON.stringify({ id_usuario: currentUser.id_usuario || currentUser.id })
          });
          _userGroupIdsCache = null;
          alert('Te uniste al grupo');
          fetchGroups();
          loadMyGroups();
        } catch (err) {
          alert('Error al unirte: ' + err.message);
        }
      };

      btnLeave.onclick = () => leaveGroup(id);

      groupsDiv.appendChild(frag);
    });
  }

  function resolveLogoUrl(g) {
    const logo = g.logo || g.logo_url || g.logo_grupo || g.imagen || g.foto || g.image;
    if (!logo) return '';
    if (/^https?:\/\//i.test(logo)) return logo;
    try {
      const base = API_BASE.replace(/\/api\/?$/, '/');
      return new URL(logo, base).toString();
    } catch (e) {
      return '';
    }
  }

  async function leaveGroup(id) {
    if (!currentUser) { alert('Debes iniciar sesion.'); return; }
    try {
      const userId = currentUser.id_usuario || currentUser.id;
      await fetchJSON(`${API_BASE}/grupos/${id}/eliminar_miembro/?id_usuario=${userId}`, { method: 'DELETE' });
      _userGroupIdsCache = null;
      alert('Saliste del grupo');
      fetchGroups();
      loadMyGroups();
    } catch (err) {
      alert('Error al salir: ' + err.message);
    }
  }

  // ==================== ADMIN ACTIONS ====================
  reloadRequestsBtn?.addEventListener('click', () => loadRequests());

  async function aprobarGrupo(id) {
    const adminId = currentUser?.id_usuario || currentUser?.id;
    try {
      await fetchJSON(`${API_BASE}/grupos/${id}/aprobar/`, {
        method: 'POST',
        body: JSON.stringify({ id_admin: adminId, comentario: 'Aprobado desde panel web' })
      });
      alert('Grupo aprobado');
      loadRequests();
      fetchGroups();
    } catch (err) {
      alert('Error al aprobar: ' + err.message);
    }
  }

  async function rechazarGrupo(id) {
    const adminId = currentUser?.id_usuario || currentUser?.id;
    const motivo = prompt('Motivo del rechazo:');
    if (!motivo) return;
    try {
      await fetchJSON(`${API_BASE}/grupos/${id}/rechazar/`, {
        method: 'POST',
        body: JSON.stringify({ id_admin: adminId, motivo })
      });
      alert('Grupo rechazado');
      loadRequests();
      fetchGroups();
    } catch (err) {
      alert('Error al rechazar: ' + err.message);
    }
  }

  // ==================== MODAL CREAR GRUPO ====================
  function showCreateModal(show) {
    if (!createGroupModal) return;
    if (show) {
      createGroupModal.classList.remove('hidden');
      createGroupModal.setAttribute('aria-hidden', 'false');
    } else {
      createGroupModal.classList.add('hidden');
      createGroupModal.setAttribute('aria-hidden', 'true');
      createGroupForm?.reset();
      createGroupMessage?.classList.add('hidden');
    }
  }

  createGroupBtn?.addEventListener('click', () => {
    if (!currentUser) { alert('Inicia sesion para crear grupos'); return; }
    showCreateModal(true);
  });
  createGroupCancel?.addEventListener('click', () => showCreateModal(false));

  createGroupForm?.addEventListener('submit', async (e) => {
    e.preventDefault();
    if (!currentUser || !authToken) {
      createGroupMessage.textContent = 'Debes iniciar sesion para crear un grupo.';
      createGroupMessage.className = 'message error';
      createGroupMessage.classList.remove('hidden');
      return;
    }
    const nombre = (document.getElementById('g-nombre') || {}).value || '';
    const area = (document.getElementById('g-area') || {}).value || '';
    const tipo = (document.getElementById('g-tipo') || {}).value || '';
    const correo = (document.getElementById('g-correo') || {}).value || '';
    const whatsapp = (document.getElementById('g-whatsapp') || {}).value || '';
    const descripcion = (document.getElementById('g-descripcion') || {}).value || '';
    const logoFile = (document.getElementById('g-logo') || {}).files?.[0];

    if (!nombre.trim() || !area.trim() || !tipo.trim() || !descripcion.trim()) {
      createGroupMessage.textContent = 'Completa los campos requeridos.';
      createGroupMessage.className = 'message error';
      createGroupMessage.classList.remove('hidden');
      return;
    }
    if (!correo.toLowerCase().endsWith('@unal.edu.co')) {
      createGroupMessage.textContent = 'El correo del grupo debe ser @unal.edu.co.';
      createGroupMessage.className = 'message error';
      createGroupMessage.classList.remove('hidden');
      return;
    }

    try {
      createGroupMessage.textContent = 'Creando grupo...';
      createGroupMessage.className = 'message success';
      createGroupMessage.classList.remove('hidden');

      const formData = new FormData();
      formData.append('nombre_grupo', nombre.trim());
      formData.append('area_interes', area.trim());
      formData.append('tipo_grupo', tipo.trim());
      formData.append('correo_grupo', correo.trim());
      formData.append('descripcion', descripcion.trim());
      formData.append('link_whatsapp', whatsapp.trim());
      if (logoFile) formData.append('logo', logoFile);

      const res = await fetch(`${API_BASE}/grupos/`, {
        method: 'POST',
        headers: { ...(authToken ? { Authorization: `Token ${authToken}` } : {}) },
        body: formData,
      });
      if (!res.ok) {
        const errText = await res.text();
        throw new Error(errText || `HTTP ${res.status}`);
      }
      createGroupMessage.textContent = 'Grupo creado correctamente.';
      fetchGroups();
      setTimeout(() => showCreateModal(false), 900);
    } catch (err) {
      createGroupMessage.textContent = 'Error: ' + err.message;
      createGroupMessage.className = 'message error';
      createGroupMessage.classList.remove('hidden');
    }
  });

  // ==================== ARRANQUE ====================
  async function bootstrapAfterAuth() {
    updateAuthUI();
    await loadRoles();
    updateRoleUI();
    await Promise.all([fetchGroups(), loadMyGroups(), loadCalendar()]);
    await loadRequests();
  }

  // Carga inicial
  updateAuthUI();
  if (currentUser && authToken) {
    bootstrapAfterAuth();
  }
});
