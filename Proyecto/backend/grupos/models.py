# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models



class Comentario(models.Model):
    id_comentario = models.IntegerField(db_column='ID_COMENTARIO', primary_key=True)  # Field name made lowercase.
    mensaje_comentario = models.TextField(db_column='MENSAJE_COMENTARIO')  # Field name made lowercase.
    fecha_publicacion = models.DateTimeField(db_column='FECHA_PUBLICACION')  # Field name made lowercase.
    estado_comentario = models.CharField(db_column='ESTADO_COMENTARIO', max_length=20)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'comentario'



class Evento(models.Model):
    id_evento = models.IntegerField(db_column='ID_EVENTO', primary_key=True)  # Field name made lowercase.
    id_grupo = models.ForeignKey('Grupo', models.DO_NOTHING, db_column='ID_GRUPO')  # Field name made lowercase.
    nombre_evento = models.CharField(db_column='NOMBRE_EVENTO', max_length=60)  # Field name made lowercase.
    descripcion_evento = models.TextField(db_column='DESCRIPCION_EVENTO')  # Field name made lowercase.
    fecha_inicio = models.DateTimeField(db_column='FECHA_INICIO')  # Field name made lowercase.
    fecha_fin = models.DateTimeField(db_column='FECHA_FIN')  # Field name made lowercase.
    lugar = models.CharField(db_column='LUGAR', max_length=60)  # Field name made lowercase.
    tipo_evento = models.CharField(db_column='TIPO_EVENTO', max_length=40)  # Field name made lowercase.
    cupo = models.CharField(db_column='CUPO', max_length=20)  # Field name made lowercase.
    estado_evento = models.CharField(db_column='ESTADO_EVENTO', max_length=20)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'evento'


class Grupo(models.Model):
    id_grupo = models.IntegerField(db_column='ID_GRUPO', primary_key=True)  # Field name made lowercase.
    nombre_grupo = models.CharField(db_column='NOMBRE_GRUPO', max_length=60)  # Field name made lowercase.
    area_interes = models.CharField(db_column='AREA_INTERES', max_length=40)  # Field name made lowercase.
    fecha_creacion = models.DateField(db_column='FECHA_CREACION')  # Field name made lowercase.
    tipo_grupo = models.CharField(db_column='TIPO_GRUPO', max_length=40)  # Field name made lowercase.
    logo = models.TextField(db_column='LOGO')  # Field name made lowercase.
    correo_grupo = models.CharField(db_column='CORREO_GRUPO', max_length=128)  # Field name made lowercase.
    descripcion = models.TextField(db_column='DESCRIPCION')  # Field name made lowercase.
    link_whatsapp = models.CharField(db_column='LINK_WHATSAPP', max_length=128, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'grupo'


class Notificacion(models.Model):
    id_notificacion = models.IntegerField(db_column='ID_NOTIFICACION', primary_key=True)  # Field name made lowercase.
    tipo_notificacion = models.CharField(db_column='TIPO_NOTIFICACION', max_length=20)  # Field name made lowercase.
    mensaje = models.TextField(db_column='MENSAJE')  # Field name made lowercase.
    fecha_envio = models.DateTimeField(db_column='FECHA_ENVIO')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'notificacion'


class Participacion(models.Model):
    id_participaciones = models.IntegerField(db_column='ID_PARTICIPACIONES', primary_key=True)  # Field name made lowercase.
    fecha_registro = models.DateField(db_column='FECHA_REGISTRO')  # Field name made lowercase.
    comentario = models.CharField(db_column='COMENTARIO', max_length=100)  # Field name made lowercase.
    estado_participacion = models.CharField(db_column='ESTADO_PARTICIPACION', max_length=20)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'participacion'


class ParticipacionUsuario(models.Model):
    id_usuario = models.OneToOneField('Usuario', models.DO_NOTHING, db_column='ID_USUARIO', primary_key=True)  # Field name made lowercase. The composite primary key (ID_USUARIO, ID_PARTICIPACIONES) found, that is not supported. The first column is selected.
    id_participaciones = models.ForeignKey(Participacion, models.DO_NOTHING, db_column='ID_PARTICIPACIONES')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'participacion_usuario'
        unique_together = (('id_usuario', 'id_participaciones'),)


class Rol(models.Model):
    id_rol = models.IntegerField(db_column='ID_ROL', primary_key=True)  # Field name made lowercase.
    nombre_rol = models.CharField(db_column='NOMBRE_ROL', max_length=20)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'rol'


class Usuario(models.Model):
    id_usuario = models.IntegerField(db_column='ID_USUARIO', primary_key=True)  # Field name made lowercase.
    nombre_usuario = models.CharField(db_column='NOMBRE_USUARIO', max_length=60)  # Field name made lowercase.
    apellido = models.CharField(db_column='APELLIDO', max_length=60)  # Field name made lowercase.
    correo_usuario = models.CharField(db_column='CORREO_USUARIO', max_length=128)  # Field name made lowercase.
    estado_usuario = models.CharField(db_column='ESTADO_USUARIO', max_length=20)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'usuario'


class UsuarioComentario(models.Model):
    id_comentario = models.OneToOneField(Comentario, models.DO_NOTHING, db_column='ID_COMENTARIO', primary_key=True)  # Field name made lowercase. The composite primary key (ID_COMENTARIO, ID_USUARIO) found, that is not supported. The first column is selected.
    id_usuario = models.ForeignKey(Usuario, models.DO_NOTHING, db_column='ID_USUARIO')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'usuario_comentario'
        unique_together = (('id_comentario', 'id_usuario'),)


class UsuarioGrupo(models.Model):
    id_grupo = models.OneToOneField(Grupo, models.DO_NOTHING, db_column='ID_GRUPO', primary_key=True)  # Field name made lowercase. The composite primary key (ID_GRUPO, ID_USUARIO) found, that is not supported. The first column is selected.
    id_usuario = models.ForeignKey(Usuario, models.DO_NOTHING, db_column='ID_USUARIO')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'usuario_grupo'
        unique_together = (('id_grupo', 'id_usuario'),)


class UsuarioNotificacion(models.Model):
    id_notificacion = models.OneToOneField(Notificacion, models.DO_NOTHING, db_column='ID_NOTIFICACION', primary_key=True)  # Field name made lowercase. The composite primary key (ID_NOTIFICACION, ID_USUARIO) found, that is not supported. The first column is selected.
    id_usuario = models.ForeignKey(Usuario, models.DO_NOTHING, db_column='ID_USUARIO')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'usuario_notificacion'
        unique_together = (('id_notificacion', 'id_usuario'),)


class UsuarioRol(models.Model):
    id_rol = models.OneToOneField(Rol, models.DO_NOTHING, db_column='ID_ROL', primary_key=True)  # Field name made lowercase. The composite primary key (ID_ROL, ID_USUARIO) found, that is not supported. The first column is selected.
    id_usuario = models.ForeignKey(Usuario, models.DO_NOTHING, db_column='ID_USUARIO')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'usuario_rol'
        unique_together = (('id_rol', 'id_usuario'),)
