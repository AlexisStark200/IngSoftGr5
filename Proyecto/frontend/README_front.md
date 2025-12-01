# Frontend mínimo — ÁgoraUN

Este micro-front (HTML+JS plano) consume la API de Django/DRF:

- Listado de **grupos** con búsqueda (`search`) y filtro por `area`.
- Ver **eventos** de un grupo (`/grupos/{id}/eventos/`).
- Botones **Unirme** (`POST /grupos/{id}/agregar-miembro/`) y **Salir** (`DELETE /grupos/{id}/eliminar-miembro/`).
- Bandejas de entrada simples (`bandejas.html`) para roles: admin general aprueba/rechaza grupos pendientes (`/grupos/{id}/aprobar|rechazar/`); admin/estudiante consulta notificaciones (`/notificaciones/?usuario={id}`).

## Uso

1. Sirve estos archivos de forma estática, por ejemplo:

```bash
cd frontend_min
python -m http.server 5173
