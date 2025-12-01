// explorar_intereses.js
document.addEventListener('DOMContentLoaded', function() {
    const API_BASE = localStorage.getItem('API_BASE') || 'http://localhost:8000/api';
    const interestsGrid = document.getElementById('interests-grid');
    const searchInput = document.querySelector('.search-input');
    const searchBtn = document.querySelector('.search-btn');

    // Función para cargar los intereses
    async function loadInterests() {
        try {
            interestsGrid.innerHTML = '<div class="loading">Cargando intereses...</div>';
            
            const response = await fetch(`${API_BASE}/intereses/populares/`);
            if (!response.ok) {
                throw new Error('Error al cargar los intereses');
            }
            
            const intereses = await response.json();
            displayInterests(intereses);
            setupSearch();
        } catch (error) {
            console.error('Error:', error);
            interestsGrid.innerHTML = `
                <div class="empty-state">
                    Error al cargar los intereses. Intenta nuevamente más tarde.
                </div>
            `;
        }
    }

    // Función para mostrar los intereses
    function displayInterests(intereses) {
        if (!intereses || intereses.length === 0) {
            interestsGrid.innerHTML = `
                <div class="empty-state">
                    No hay intereses disponibles en este momento.
                </div>
            `;
            return;
        }

        interestsGrid.innerHTML = intereses.map(interes => `
            <div class="interest-card">
                <div class="interest-header">
                    <div class="interest-name">${interes.area || 'Sin nombre'}</div>
                    <div class="interest-count">
                        ${interes.total_grupos || 0} grupo${interes.total_grupos !== 1 ? 's' : ''}
                    </div>
                </div>
                
                <div class="interest-content">
                    <h3>Grupos destacados:</h3>
                    ${interes.grupos_destacados && interes.grupos_destacados.length > 0 ? 
                        `<ul class="groups-list">
                            ${interes.grupos_destacados.map(grupo => `
                                <li class="group-item">
                                    <a href="#" class="group-link" data-group-id="${grupo.id || ''}">
                                        ${grupo.nombre_grupo || 'Grupo sin nombre'}
                                    </a>
                                    <div class="group-meta">
                                        ${grupo.tipo_grupo || ''} • ${grupo.fecha_creacion ? new Date(grupo.fecha_creacion).getFullYear() : 'N/A'}
                                    </div>
                                </li>
                            `).join('')}
                        </ul>` 
                        : 
                        '<p class="empty-state">No hay grupos en esta categoría</p>'
                    }
                    
                    <button class="btn ver-grupos-btn" data-area="${interes.area || ''}">
                        Ver todos los grupos de ${interes.area || 'esta área'}
                    </button>
                </div>
            </div>
        `).join('');

        // Agregar event listeners a los botones
        document.querySelectorAll('.ver-grupos-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                const area = this.getAttribute('data-area');
                window.location.href = `index.html?area=${encodeURIComponent(area)}`;
            });
        });

        // Agregar event listeners a los enlaces de grupos
        document.querySelectorAll('.group-link').forEach(link => {
            link.addEventListener('click', function(e) {
                e.preventDefault();
                const groupId = this.getAttribute('data-group-id');
                if (groupId) {
                    // Aquí podrías redirigir a una página de detalles del grupo
                    // Por ahora solo alert
                    alert(`Redirigiendo al grupo ${groupId}`);
                }
            });
        });
    }

    // Función para configurar la búsqueda
    function setupSearch() {
        if (!searchInput) return;

        // Búsqueda en tiempo real
        searchInput.addEventListener('input', function(e) {
            const searchTerm = e.target.value.toLowerCase();
            const interestCards = document.querySelectorAll('.interest-card');
            
            interestCards.forEach(card => {
                const interestName = card.querySelector('.interest-name').textContent.toLowerCase();
                const groupNames = card.querySelectorAll('.group-link');
                let hasMatch = interestName.includes(searchTerm);
                
                if (!hasMatch) {
                    groupNames.forEach(group => {
                        if (group.textContent.toLowerCase().includes(searchTerm)) {
                            hasMatch = true;
                        }
                    });
                }
                
                card.style.display = hasMatch ? 'block' : 'none';
            });
        });

        // Búsqueda con botón
        if (searchBtn) {
            searchBtn.addEventListener('click', function() {
                searchInput.dispatchEvent(new Event('input'));
            });
        }

        // Permitir búsqueda con Enter
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                searchInput.dispatchEvent(new Event('input'));
            }
        });
    }

    // Cargar intereses al inicio
    loadInterests();
});