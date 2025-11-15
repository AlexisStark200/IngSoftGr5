"""
Admin - ÁgoraUN
Configuración del panel de administración de Django

Acceso: http://localhost:8000/admin/
Usuario: admin
Contraseña: admin123

Permite gestionar datos sin API (interfaz visual)
"""

from django.contrib import admin
from .models import (
    Grupo,
    Evento,
    Usuario,
    Comentario,
    Notificacion,
    Participacion,
    Rol,
    UsuarioGrupo,
    UsuarioComentario,
    UsuarioNotificacion,
    UsuarioRol,
    ParticipacionUsuario
)

@admin.register(UsuarioNotificacion)
class UsuarioNotificacionAdmin(admin.ModelAdmin):
    """Admin para relación Usuario-Notificación"""
    
    list_display = ['usuario', 'notificacion', 'leida']
    list_filter = ['leida', 'notificacion__fecha_envio']
    search_fields = ['usuario__nombre_usuario', 'notificacion__mensaje']

models_list = [
    Grupo,
    Evento,
    Usuario,
    Comentario,
    Notificacion,
    Participacion,
    Rol,
    UsuarioGrupo,
    UsuarioComentario,
    UsuarioNotificacion,
    UsuarioRol,
    ParticipacionUsuario
]

for model in models_list:
    admin.site.register(model)
