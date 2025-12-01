// ÁgoraUN - Frontend Corregido
console.log("=== ÁGORAUN FRONTEND INICIADO ===");

// Esperar a que el DOM esté completamente cargado
document.addEventListener('DOMContentLoaded', function() {
    console.log("DOM cargado - inicializando event listeners");
    
    // Selectores
    const $ = (q) => document.querySelector(q);
    const $$ = (q) => document.querySelectorAll(q);
    
    // Elementos principales
    const apiBaseInput = $("#apiBase");
    const saveBaseBtn = $("#saveBase");
    const searchBtn = $("#searchBtn");
    const qInput = $("#q");
    const areaSel = $("#area");
    const groupsDiv = $("#groups");
    const cardTpl = $("#cardTpl");
    
    // Elementos de autenticación
    const authLoggedOut = $("#auth-logged-out");
    const authLoggedIn = $("#auth-logged-in");
    const loginForm = $("#login-form");
    const registerForm = $("#register-form");
    const authMessage = $("#auth-message");
    const userName = $("#user-name");
    const logoutBtn = $("#logout-btn");
    const authTabs = $$(".auth-tab");
    // Elementos crear grupo
    const createGroupBtn = $("#create-group-btn");
    const createGroupModal = $("#create-group-modal");
    const createGroupForm = $("#create-group-form");
    const createGroupCancel = $("#g-cancel");
    const createGroupMessage = $("#g-message");
    
    // Estado
    let API_BASE = localStorage.getItem("API_BASE") || "http://localhost:8000/api";
    let currentUser = JSON.parse(localStorage.getItem("currentUser") || "null");
    let authToken = localStorage.getItem("authToken") || "";
    
    // Inicialización
    console.log("Estado inicial:", { API_BASE, currentUser, authToken });
    apiBaseInput.value = API_BASE;
    updateAuthUI();
    
    // ==================== EVENT LISTENERS ====================
    
    // Configuración API
    saveBaseBtn.addEventListener("click", () => {
        API_BASE = apiBaseInput.value.trim().replace(/\/+$/, "");
        localStorage.setItem("API_BASE", API_BASE);
        console.log("API Base actualizada:", API_BASE);
        fetchGroups();
    });
    
    searchBtn.addEventListener("click", () => {
        console.log("Búsqueda activada");
        fetchGroups();
    });
    
    // Tabs de autenticación
    authTabs.forEach(tab => {
        tab.addEventListener("click", (e) => {
            e.preventDefault();
            const tabName = tab.dataset.tab;
            console.log("Cambiando a tab:", tabName);
            
            // Actualizar tabs activos
            authTabs.forEach(t => t.classList.remove("active"));
            tab.classList.add("active");
            
            // Mostrar formulario activo
            $$(".auth-form").forEach(form => form.classList.remove("active"));
            $(`#${tabName}-form`).classList.add("active");
            
            hideAuthMessage();
        });
    });
    
    // LOGIN
    loginForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        console.log("Login form submitted");
        
        const email = $("#login-email").value;
        const password = $("#login-password").value;
        
        console.log("Datos login:", { email, password });
        
        if (!isValidUNALEmail(email)) {
            showAuthMessage("❌ Solo se permiten correos @unal.edu.co", "error");
            return;
        }
        
        try {
            showAuthMessage("⏳ Iniciando sesión...", "success");
            
            const response = await fetch(`${API_BASE}/auth/login/`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    correo: email,
                    password: password
                })
            });
            
            console.log("Respuesta login:", response.status);
            
            const data = await response.json();
            console.log("Datos respuesta login:", data);
            
            if (response.ok) {
                authToken = data.token;
                currentUser = data.usuario;
                
                localStorage.setItem("authToken", authToken);
                localStorage.setItem("currentUser", JSON.stringify(currentUser));
                
                showAuthMessage("✅ ¡Login exitoso!", "success");
                updateAuthUI();
                fetchGroups();
                
                // Limpiar formulario
                loginForm.reset();
            } else {
                showAuthMessage(`❌ ${data.error || "Error en el login"}`, "error");
            }
        } catch (error) {
            console.error("Error login:", error);
            showAuthMessage(`❌ Error de conexión: ${error.message}`, "error");
        }
    });
    
    // REGISTRO
    registerForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        console.log("Register form submitted");
        
        const nombre = $("#register-nombre").value;
        const apellido = $("#register-apellido").value;
        const email = $("#register-email").value;
        const password = $("#register-password").value;
        const passwordConfirm = $("#register-password-confirm").value;
        
        console.log("Datos registro:", { nombre, apellido, email });
        
        // Validaciones
        if (!isValidUNALEmail(email)) {
            showAuthMessage("❌ Solo se permiten correos @unal.edu.co", "error");
            return;
        }
        
        if (password !== passwordConfirm) {
            showAuthMessage("❌ Las contraseñas no coinciden", "error");
            return;
        }
        
        if (password.length < 8) {
            showAuthMessage("❌ La contraseña debe tener al menos 8 caracteres", "error");
            return;
        }
        
        try {
            showAuthMessage("⏳ Creando cuenta...", "success");
            
            const response = await fetch(`${API_BASE}/auth/register/`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    nombre_usuario: nombre,
                    apellido: apellido,
                    correo: email,
                    password: password
                })
            });
            
            console.log("Respuesta registro:", response.status);
            
            const data = await response.json();
            console.log("Datos respuesta registro:", data);
            
            if (response.ok) {
                authToken = data.token;
                currentUser = data.usuario;
                
                localStorage.setItem("authToken", authToken);
                localStorage.setItem("currentUser", JSON.stringify(currentUser));
                
                showAuthMessage("✅ ¡Registro exitoso! Bienvenido/a", "success");
                updateAuthUI();
                fetchGroups();
                
                // Limpiar formulario y cambiar a login
                registerForm.reset();
                authTabs[0].click(); // Cambiar a tab de login
            } else {
                showAuthMessage(`❌ ${data.error || "Error en el registro"}`, "error");
            }
        } catch (error) {
            console.error("Error registro:", error);
            showAuthMessage(`❌ Error de conexión: ${error.message}`, "error");
        }
    });
    
    // LOGOUT
    logoutBtn.addEventListener("click", () => {
        console.log("Logout clicked");
        authToken = "";
        currentUser = null;
        localStorage.removeItem("authToken");
        localStorage.removeItem("currentUser");
        updateAuthUI();
        fetchGroups();
        showAuthMessage("👋 Sesión cerrada", "success");
    });
    
    // ==================== FUNCIONES ====================
    
    function isValidUNALEmail(email) {
        return email.toLowerCase().endsWith("@unal.edu.co");
    }
    
    function showAuthMessage(text, type = "error") {
        authMessage.textContent = text;
        authMessage.className = `message ${type}`;
        authMessage.classList.remove("hidden");
    }
    
    function hideAuthMessage() {
        authMessage.classList.add("hidden");
    }
    
    function updateAuthUI() {
        console.log("Actualizando UI con usuario:", currentUser);
        
        if (currentUser && authToken) {
            authLoggedOut.classList.add("hidden");
            authLoggedIn.classList.remove("hidden");
            
            // CORRECCIÓN: Manejar diferentes estructuras de datos del usuario
            const nombre = currentUser.nombre_usuario || currentUser.nombre || currentUser.firstName || "";
            const apellido = currentUser.apellido || currentUser.lastName || "";
            
            console.log("Nombre completo:", { nombre, apellido });
            userName.textContent = `${nombre} ${apellido}`.trim();
            
            console.log("Usuario autenticado:", currentUser);
        } else {
            authLoggedOut.classList.remove("hidden");
            authLoggedIn.classList.add("hidden");
            console.log("Usuario no autenticado");
        }

        // Mostrar/ocultar botón de crear grupo y calendario
        try {
            const btn = document.getElementById('create-group-btn');
            const calBtn = document.getElementById('calendar-btn');
            if (btn) {
                if (currentUser && authToken) {
                    btn.classList.remove('hidden');
                    btn.style.display = 'inline-block';
                    btn.removeAttribute('aria-hidden');
                } else {
                    btn.classList.add('hidden');
                }
            }
            if (calBtn) {
                if (currentUser && authToken) {
                    calBtn.classList.remove('hidden');
                    calBtn.style.display = 'inline-block';
                    calBtn.removeAttribute('aria-hidden');
                } else {
                    calBtn.classList.add('hidden');
                    calBtn.style.display = 'none';
                }
            }
            // Mostrar/ocultar botón Mi Club
            const clubBtn = document.getElementById('club-btn');
            if (clubBtn) {
                if (currentUser && authToken) {
                    clubBtn.classList.remove('hidden');
                    clubBtn.style.display = 'inline-block';
                    clubBtn.removeAttribute('aria-hidden');
                } else {
                    clubBtn.classList.add('hidden');
                    clubBtn.style.display = 'none';
                }
            }
        } catch (dbgErr) {
            console.warn('DEBUG: error mostrando/ocultando createGroupBtn/calBtn', dbgErr);
        }
    }
    
    function headers() {
        const h = { "Content-Type": "application/json" };
        if (authToken) h["Authorization"] = `Token ${authToken}`;
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

        if (res.status === 204 || res.status === 205) {
            return null;
        }

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

            if (q) params.set("search", q);
            if (area) params.set("area", area);

            const query = params.toString();
            const url = query
                ? `${API_BASE}/grupos/?${query}`
                : `${API_BASE}/grupos/`;

            console.log("Fetching groups from:", url);
            const data = await fetchJSON(url);
            const items = Array.isArray(data) ? data : data?.results || [];
            await renderGroups(items);
        } catch (err) {
            console.error("Error fetchGroups:", err);
            groupsDiv.innerHTML = `<p class="error">${err.message}</p>`;
        }
    }

    // Mostrar u ocultar modal crear grupo
    function showCreateModal(show) {
        if (!createGroupModal) return;
        if (show) {
            createGroupModal.classList.remove('hidden');
            createGroupModal.setAttribute('aria-hidden', 'false');
        } else {
            createGroupModal.classList.add('hidden');
            createGroupModal.setAttribute('aria-hidden', 'true');
            if (createGroupForm) createGroupForm.reset();
            if (createGroupMessage) createGroupMessage.classList.add('hidden');
        }
    }

    // Eventos crear grupo
    if (createGroupBtn) {
        createGroupBtn.addEventListener('click', () => showCreateModal(true));
    }

    if (createGroupCancel) {
        createGroupCancel.addEventListener('click', () => showCreateModal(false));
    }

    if (createGroupForm) {
        createGroupForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            if (!currentUser || !authToken) {
                if (createGroupMessage) {
                    createGroupMessage.textContent = 'Debes iniciar sesión para crear un grupo.';
                    createGroupMessage.className = 'message error';
                    createGroupMessage.classList.remove('hidden');
                }
                return;
            }

            const nombre = (document.getElementById('g-nombre')||{}).value || '';
            const area = (document.getElementById('g-area')||{}).value || '';
            const tipo = (document.getElementById('g-tipo')||{}).value || '';
            const correo = (document.getElementById('g-correo')||{}).value || '';
            const whatsapp = (document.getElementById('g-whatsapp')||{}).value || '';
            const descripcion = (document.getElementById('g-descripcion')||{}).value || '';

            // Validaciones básicas
            if (!nombre.trim() || !area.trim() || !tipo.trim() || !descripcion.trim()) {
                createGroupMessage.textContent = 'Por favor completa los campos requeridos.';
                createGroupMessage.className = 'message error';
                createGroupMessage.classList.remove('hidden');
                return;
            }

            if (!correo.toLowerCase().endsWith('@unal.edu.co')) {
                createGroupMessage.textContent = 'El correo del grupo debe ser institucional (@unal.edu.co).';
                createGroupMessage.className = 'message error';
                createGroupMessage.classList.remove('hidden');
                return;
            }

            const payload = {
                nombre_grupo: nombre.trim(),
                area_interes: area.trim(),
                tipo_grupo: tipo.trim(),
                correo_grupo: correo.trim(),
                descripcion: descripcion.trim(),
                // Enviar cadena vacía en lugar de `null` para evitar errores
                // si el campo en la base de datos no acepta NULL.
                link_whatsapp: whatsapp.trim() || ""
            };

            try {
                createGroupMessage.textContent = 'Creando grupo...';
                createGroupMessage.className = 'message success';
                createGroupMessage.classList.remove('hidden');

                const res = await fetchJSON(`${API_BASE}/grupos/`, {
                    method: 'POST',
                    body: JSON.stringify(payload)
                });

                console.log('Grupo creado:', res);
                createGroupMessage.textContent = '✅ Grupo creado correctamente.';
                createGroupMessage.className = 'message success';

                // refrescar listado y cerrar modal
                fetchGroups();
                setTimeout(() => showCreateModal(false), 900);
            } catch (err) {
                console.error('Error creando grupo:', err);
                createGroupMessage.textContent = 'Error: ' + err.message;
                createGroupMessage.className = 'message error';
                createGroupMessage.classList.remove('hidden');
            }
        });
    }

    // Cache para los ids de grupos del usuario
    let _userGroupIdsCache = null;
    async function getUserGroupIds() {
        if (!currentUser) return [];
        if (_userGroupIdsCache) return _userGroupIdsCache;
        try {
            const uid = currentUser.id_usuario || currentUser.id;
            const res = await fetchJSON(`${API_BASE}/usuarios/${uid}/grupos/`);
            const list = Array.isArray(res) ? res : res?.results || [];
            // Los objetos pueden venir con la forma { grupo: <id> } o con id directo
            _userGroupIdsCache = list.map(g => g.grupo || g.id_grupo || g.id || g.grupo_id).filter(x => x != null);
            return _userGroupIdsCache;
        } catch (err) {
            console.warn('No se pudo obtener grupos del usuario:', err);
            _userGroupIdsCache = [];
            return _userGroupIdsCache;
        }
    }

    async function renderGroups(items) {
        groupsDiv.innerHTML = "";
        if (!items.length) {
            groupsDiv.innerHTML = `
                <div class="no-results">
                    <h3>Sin resultados</h3>
                    <p>No se encontraron grupos con los criterios de búsqueda.</p>
                </div>
            `;
            return;
        }

        // Obtener lista de grupos del usuario (para decidir botones)
        const userGroupIds = currentUser ? await getUserGroupIds() : [];

        items.forEach((g) => {
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

            // Mostrar/ocultar botones según autenticación y pertenencia
            if (!currentUser) {
                btnJoin.style.display = "none";
                btnLeave.style.display = "none";
            } else {
                // Determinar si el usuario está en este grupo.
                const uid = currentUser.id_usuario || currentUser.id;
                const possibleFlags = [
                    g.usuario_inscrito, g.esta_inscrito, g.is_member, g.en_miembros, g.miembro, g.user_is_member
                ];
                let isMember = false;
                // Chequear banderas directas
                for (const f of possibleFlags) if (f) { isMember = true; break; }
                // Chequear lista de miembros incluida en el objeto
                if (!isMember && Array.isArray(g.miembros)) {
                    // miembros puede ser lista de ids o de objetos con id
                    isMember = g.miembros.some(m => m === uid || m.id === uid || m.id_usuario === uid);
                }
                // Chequear cache de grupos del usuario
                if (!isMember && userGroupIds && userGroupIds.length) {
                    isMember = userGroupIds.includes(id);
                }

                if (isMember) {
                    btnJoin.style.display = 'none';
                    btnLeave.style.display = 'inline-block';
                } else {
                    btnJoin.style.display = 'inline-block';
                    btnLeave.style.display = 'none';
                }
            }

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
                            const titulo = e.nombre_evento || e.titulo || e.nombre || "Evento";
                            const fecha = e.fecha_inicio || e.fecha || "";
                            const lugar = e.lugar || "";
                            const fechaTxt = fecha ? new Date(fecha).toLocaleString() : "";
                            li.textContent = `${titulo}${fechaTxt ? " — " + fechaTxt : ""}${lugar ? " @ " + lugar : ""}`;
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
                if (!currentUser) {
                    alert("Debes iniciar sesión para unirte a grupos");
                    return;
                }

                try {
                    await fetchJSON(`${API_BASE}/grupos/${id}/agregar_miembro/`, {
                        method: "POST",
                        body: JSON.stringify({
                            id_usuario: currentUser.id_usuario || currentUser.id,
                        }),
                    });
                    // Invalidate cache y refrescar listado
                    _userGroupIdsCache = null;
                    alert("¡Te uniste al grupo!");
                    fetchGroups();
                } catch (err) {
                    console.error(err);
                    alert("Error al unirte: " + err.message);
                }
            };

            // Salir del grupo
            btnLeave.onclick = async () => {
                if (!currentUser) {
                    alert("Debes iniciar sesión para salir de grupos");
                    return;
                }

                try {
                    const userId = currentUser.id_usuario || currentUser.id;
                    const url = `${API_BASE}/grupos/${id}/eliminar_miembro/?id_usuario=${userId}`;
                    await fetchJSON(url, { method: "DELETE" });
                    // Invalidate cache y refrescar listado
                    _userGroupIdsCache = null;
                    alert("Has salido del grupo.");
                    fetchGroups();
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
});