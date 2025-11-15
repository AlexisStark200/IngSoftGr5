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
