"""
Modelos de Datos - ÁgoraUN (CORREGIDO)
Basados en ScriptProyecto.sql
Incluye todos los modelos del sistema:
- Usuario, Grupo, Evento
- Participación, Comentario, Notificación
- Relaciones Many-to-Many
"""

from django.db import models
from django.utils import timezone


class Usuario(models.Model):
    """Modelo de Usuario del sistema"""
    id_usuario = models.AutoField(primary_key=True)
    nombre_usuario = models.CharField(max_length=60)
    apellido = models.CharField(max_length=60)
    correo_usuario = models.EmailField(max_length=128, unique=True)
    estado_usuario = models.CharField(
        max_length=20,
        choices=[
            ('ACTIVO', 'Activo'),
            ('INACTIVO', 'Inactivo'),
            ('SUSPENDIDO', 'Suspendido')
        ],
        default='ACTIVO'
    )
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'USUARIO'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        return f"{self.nombre_usuario} {self.apellido}"


class Rol(models.Model):
    """Modelo de Roles del sistema"""
    id_rol = models.AutoField(primary_key=True)
    nombre_rol = models.CharField(
        max_length=20,
        choices=[
            ('ADMIN', 'Administrador'),
            ('MODERADOR', 'Moderador'),
            ('MIEMBRO', 'Miembro'),
            ('INVITADO', 'Invitado')
        ],
        default='MIEMBRO'  # ✅ CORREGIDO: Agregado default
    )

    class Meta:
        db_table = 'ROL'
        verbose_name = 'Rol'
        verbose_name_plural = 'Roles'

    def __str__(self):
        return self.nombre_rol


class Grupo(models.Model):
    """Modelo de Grupo/Club estudiantil"""
    id_grupo = models.AutoField(primary_key=True)
    nombre_grupo = models.CharField(max_length=60)
    area_interes = models.CharField(max_length=40)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    tipo_grupo = models.CharField(max_length=40)
    logo = models.ImageField(upload_to='logos/', blank=True, null=True)
    correo_grupo = models.EmailField(max_length=128)
    descripcion = models.TextField()
    link_whatsapp = models.CharField(max_length=128, blank=True, null=True)

    # Relaciones Many-to-Many
    miembros = models.ManyToManyField(
        Usuario,
        through='UsuarioGrupo',
        related_name='grupos'
    )

    class Meta:
        db_table = 'GRUPO'
        verbose_name = 'Grupo'
        verbose_name_plural = 'Grupos'

    def __str__(self):
        return self.nombre_grupo


class Evento(models.Model):
    """Modelo de Evento"""
    id_evento = models.AutoField(primary_key=True)
    grupo = models.ForeignKey(
        Grupo,
        on_delete=models.CASCADE,
        related_name='eventos'
    )
    nombre_evento = models.CharField(max_length=60)
    descripcion_evento = models.TextField()
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField()
    lugar = models.CharField(max_length=60)
    tipo_evento = models.CharField(max_length=40)
    cupo = models.IntegerField()
    estado_evento = models.CharField(
        max_length=20,
        choices=[
            ('PROGRAMADO', 'Programado'),
            ('EN_CURSO', 'En Curso'),
            ('FINALIZADO', 'Finalizado'),
            ('CANCELADO', 'Cancelado')
        ],
        default='PROGRAMADO'
    )

    class Meta:
        db_table = 'EVENTO'
        verbose_name = 'Evento'
        verbose_name_plural = 'Eventos'

    def __str__(self):
        return f"{self.nombre_evento} - {self.grupo.nombre_grupo}"


class Participacion(models.Model):
    """Modelo de Participación en eventos"""
    id_participaciones = models.AutoField(primary_key=True)
    # ✅ CORREGIDO: Agregado FK a Evento
    evento = models.ForeignKey(
        Evento,
        on_delete=models.CASCADE,
        related_name='participaciones'
    )
    fecha_registro = models.DateTimeField(auto_now_add=True)
    comentario = models.CharField(max_length=100, blank=True)
    estado_participacion = models.CharField(
        max_length=20,
        choices=[
            ('CONFIRMADO', 'Confirmado'),
            ('PENDIENTE', 'Pendiente'),
            ('CANCELADO', 'Cancelado')
        ],
        default='PENDIENTE'
    )

    # Relación Many-to-Many con Usuario
    usuarios = models.ManyToManyField(
        Usuario,
        through='ParticipacionUsuario',
        related_name='participaciones'
    )

    class Meta:
        db_table = 'PARTICIPACION'
        verbose_name = 'Participación'
        verbose_name_plural = 'Participaciones'

    def __str__(self):
        return f"Participación {self.id_participaciones} - {self.evento.nombre_evento}"


class Comentario(models.Model):
    """Modelo de Comentarios"""
    id_comentario = models.AutoField(primary_key=True)
    mensaje_comentario = models.TextField()
    fecha_publicacion = models.DateTimeField(auto_now_add=True)
    estado_comentario = models.CharField(
        max_length=20,
        choices=[
            ('PUBLICADO', 'Publicado'),
            ('PENDIENTE', 'Pendiente'),
            ('RECHAZADO', 'Rechazado')
        ],
        default='PUBLICADO'
    )

    # Relación Many-to-Many con Usuario
    usuarios = models.ManyToManyField(
        Usuario,
        through='UsuarioComentario',
        related_name='comentarios'
    )

    class Meta:
        db_table = 'COMENTARIO'
        verbose_name = 'Comentario'
        verbose_name_plural = 'Comentarios'

    def __str__(self):
        return f"Comentario {self.id_comentario}"


class Notificacion(models.Model):
    """Modelo de Notificaciones"""
    id_notificacion = models.AutoField(primary_key=True)
    tipo_notificacion = models.CharField(max_length=20)
    mensaje = models.TextField()
    fecha_envio = models.DateTimeField(auto_now_add=True)

    # Relación Many-to-Many con Usuario
    usuarios = models.ManyToManyField(
        Usuario,
        through='UsuarioNotificacion',
        related_name='notificaciones'
    )

    class Meta:
        db_table = 'NOTIFICACION'
        verbose_name = 'Notificación'
        verbose_name_plural = 'Notificaciones'

    def __str__(self):
        return f"{self.tipo_notificacion} - {self.fecha_envio}"


# ===========================================================================
# TABLAS INTERMEDIAS (Many-to-Many)
# ===========================================================================

class UsuarioGrupo(models.Model):
    """Relación Usuario-Grupo"""
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    grupo = models.ForeignKey(Grupo, on_delete=models.CASCADE)
    fecha_union = models.DateTimeField(auto_now_add=True)
    rol_en_grupo = models.CharField(
        max_length=20,
        choices=[
            ('ADMIN', 'Administrador'),
            ('MIEMBRO', 'Miembro')
        ],
        default='MIEMBRO'
    )

    class Meta:
        db_table = 'USUARIO_GRUPO'
        unique_together = ('usuario', 'grupo')

    def __str__(self):
        return f"{self.usuario} en {self.grupo}"


class ParticipacionUsuario(models.Model):
    """Relación Participación-Usuario"""
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    participacion = models.ForeignKey(Participacion, on_delete=models.CASCADE)

    class Meta:
        db_table = 'PARTICIPACION_USUARIO'
        unique_together = ('usuario', 'participacion')


class UsuarioComentario(models.Model):
    """Relación Usuario-Comentario"""
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    comentario = models.ForeignKey(Comentario, on_delete=models.CASCADE)

    class Meta:
        db_table = 'USUARIO_COMENTARIO'
        unique_together = ('usuario', 'comentario')


class UsuarioNotificacion(models.Model):
    """Relación Usuario-Notificación"""
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    notificacion = models.ForeignKey(Notificacion, on_delete=models.CASCADE)
    leida = models.BooleanField(default=False)

    class Meta:
        db_table = 'USUARIO_NOTIFICACION'
        unique_together = ('usuario', 'notificacion')


class UsuarioRol(models.Model):
    """Relación Usuario-Rol"""
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    rol = models.ForeignKey(Rol, on_delete=models.CASCADE)

    class Meta:
        db_table = 'USUARIO_ROL'
        unique_together = ('usuario', 'rol')