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


# ===========================================================================
# ADMIN PERSONALIZADOS - MODELOS PRINCIPALES
# ===========================================================================

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    """Admin para Usuario"""

    list_display = [
        'id_usuario',
        'nombre_usuario',
        'apellido',
        'correo_usuario',
        'estado_usuario',
        'fecha_registro'
    ]
    list_filter = ['estado_usuario', 'fecha_registro']
    search_fields = ['nombre_usuario', 'apellido', 'correo_usuario']
    ordering = ['-fecha_registro']
    readonly_fields = ['id_usuario', 'fecha_registro']

    fieldsets = (
        ('Información Personal', {
            'fields': ('nombre_usuario', 'apellido', 'correo_usuario')
        }),
        ('Estado', {
            'fields': ('estado_usuario',)
        }),
        ('Auditoría', {
            'fields': ('id_usuario', 'fecha_registro'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Grupo)
class GrupoAdmin(admin.ModelAdmin):
    """Admin para Grupo"""

    list_display = [
        'id_grupo',
        'nombre_grupo',
        'tipo_grupo',
        'area_interes',
        'correo_grupo',
        'fecha_creacion',
        'total_miembros'
    ]
    list_filter = ['tipo_grupo', 'area_interes', 'fecha_creacion']
    search_fields = ['nombre_grupo', 'correo_grupo', 'descripcion']
    ordering = ['-fecha_creacion']
    readonly_fields = ['id_grupo', 'fecha_creacion', 'total_miembros']

    fieldsets = (
        ('Información General', {
            'fields': ('nombre_grupo', 'tipo_grupo', 'area_interes', 'descripcion')
        }),
        ('Contacto', {
            'fields': ('correo_grupo', 'link_whatsapp')
        }),
        ('Multimedia', {
            'fields': ('logo',)
        }),
        ('Estadísticas', {
            'fields': ('total_miembros', 'fecha_creacion'),
            'classes': ('collapse',)
        }),
    )

    def total_miembros(self, obj):
        """Mostrar total de miembros"""
        return obj.miembros.count()
    total_miembros.short_description = 'Total de Miembros'


@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    """Admin para Evento"""

    list_display = [
        'id_evento',
        'nombre_evento',
        'grupo',
        'fecha_inicio',
        'fecha_fin',
        'cupo',
        'estado_evento'
    ]
    list_filter = ['estado_evento', 'tipo_evento', 'fecha_inicio', 'grupo']
    search_fields = ['nombre_evento', 'descripcion_evento', 'lugar']
    ordering = ['-fecha_inicio']
    readonly_fields = ['id_evento']

    fieldsets = (
        ('Información General', {
            'fields': ('grupo', 'nombre_evento', 'descripcion_evento', 'tipo_evento')
        }),
        ('Ubicación y Horario', {
            'fields': ('lugar', 'fecha_inicio', 'fecha_fin')
        }),
        ('Capacidad', {
            'fields': ('cupo',)
        }),
        ('Estado', {
            'fields': ('estado_evento',)
        }),
    )


@admin.register(Participacion)
class ParticipacionAdmin(admin.ModelAdmin):
    """Admin para Participación"""

    list_display = [
        'id_participaciones',
        'fecha_registro',
        'estado_participacion',
        'comentario'
    ]
    list_filter = ['estado_participacion', 'fecha_registro']
    search_fields = ['comentario']
    ordering = ['-fecha_registro']
    readonly_fields = ['id_participaciones', 'fecha_registro']


@admin.register(Comentario)
class ComentarioAdmin(admin.ModelAdmin):
    """Admin para Comentario"""

    list_display = [
        'id_comentario',
        'mensaje_comentario',
        'fecha_publicacion',
        'estado_comentario'
    ]
    list_filter = ['estado_comentario', 'fecha_publicacion']
    search_fields = ['mensaje_comentario']
    ordering = ['-fecha_publicacion']
    readonly_fields = ['id_comentario', 'fecha_publicacion']


@admin.register(Notificacion)
class NotificacionAdmin(admin.ModelAdmin):
    """Admin para Notificación"""

    list_display = [
        'id_notificacion',
        'tipo_notificacion',
        'mensaje',
        'fecha_envio'
    ]
    list_filter = ['tipo_notificacion', 'fecha_envio']
    search_fields = ['mensaje']
    ordering = ['-fecha_envio']
    readonly_fields = ['id_notificacion', 'fecha_envio']


@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    """Admin para Rol"""

    list_display = ['id_rol', 'nombre_rol']
    readonly_fields = ['id_rol']


# ===========================================================================
# ADMIN PARA RELACIONES (Many-to-Many)
# ===========================================================================

@admin.register(UsuarioGrupo)
class UsuarioGrupoAdmin(admin.ModelAdmin):
    """Admin para relación Usuario-Grupo"""

    list_display = [
        'usuario',
        'grupo',
        'rol_en_grupo',
        'fecha_union'
    ]
    list_filter = ['rol_en_grupo', 'fecha_union', 'grupo']
    search_fields = ['usuario__nombre_usuario', 'grupo__nombre_grupo']
    ordering = ['-fecha_union']
    readonly_fields = ['fecha_union']


@admin.register(ParticipacionUsuario)
class ParticipacionUsuarioAdmin(admin.ModelAdmin):
    """Admin para relación Participación-Usuario"""

    list_display = ['usuario', 'participacion']
    list_filter = ['participacion__estado_participacion']
    search_fields = ['usuario__nombre_usuario']


@admin.register(UsuarioComentario)
class UsuarioComentarioAdmin(admin.ModelAdmin):
    """Admin para relación Usuario-Comentario"""

    list_display = ['usuario', 'comentario']
    search_fields = ['usuario__nombre_usuario', 'comentario__mensaje_comentario']


@admin.register(UsuarioNotificacion)
class UsuarioNotificacionAdmin(admin.ModelAdmin):
    """Admin para relación Usuario-Notificación"""

    list_display = ['usuario', 'notificacion', 'leida']
    list_filter = ['leida', 'notificacion__fecha_envio']
    search_fields = ['usuario__nombre_usuario', 'notificacion__mensaje']


@admin.register(UsuarioRol)
class UsuarioRolAdmin(admin.ModelAdmin):
    """Admin para relación Usuario-Rol"""

    list_display = ['usuario', 'rol']
    search_fields = ['usuario__nombre_usuario', 'rol__nombre_rol']

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
