"""
Capa de Servicios - ÁgoraUN
Lógica de Negocio separada de las vistas

Esta capa:
- Encapsula toda la lógica de negocio
- Interactúa con la base de datos
- Valida reglas de negocio
- Es consumida por las vistas

Patrón: Service Layer Pattern
"""

from django.db import transaction
from django.core.exceptions import ValidationError
from .models import (
    Usuario, Grupo, Evento, Participacion,
    Comentario, Notificacion,
    UsuarioGrupo, ParticipacionUsuario,
    UsuarioComentario, UsuarioNotificacion
)


# ===========================================================================
# SERVICIOS DE GRUPO
# ===========================================================================

class GrupoService:
    """Servicio de lógica de negocio para Grupos"""

    @staticmethod
    def listar_grupos(filtros=None):
        """
        Listar grupos con filtros opcionales

        Args:
            filtros (dict): Filtros opcionales (area_interes, tipo_grupo, etc.)

        Returns:
            QuerySet: Grupos filtrados
        """
        queryset = Grupo.objects.all()

        if filtros:
            if 'area_interes' in filtros:
                queryset = queryset.filter(area_interes=filtros['area_interes'])
            if 'tipo_grupo' in filtros:
                queryset = queryset.filter(tipo_grupo=filtros['tipo_grupo'])
            if 'busqueda' in filtros:
                queryset = queryset.filter(
                    nombre_grupo__icontains=filtros['busqueda']
                )

        return queryset.order_by('-fecha_creacion')

    @staticmethod
    def obtener_grupo(id_grupo):
        """
        Obtener un grupo específico

        Args:
            id_grupo (int): ID del grupo

        Returns:
            Grupo: Instancia del grupo

        Raises:
            Grupo.DoesNotExist: Si el grupo no existe
        """
        return Grupo.objects.get(id_grupo=id_grupo)

    @staticmethod
    @transaction.atomic
    def crear_grupo(datos_grupo, usuario_creador):
        """
        Crear un nuevo grupo con validaciones de negocio

        Reglas de Negocio:
        - Correo debe ser institucional (@unal.edu.co)
        - Nombre único
        - Usuario creador se asigna como admin

        Args:
            datos_grupo (dict): Datos del grupo
            usuario_creador (Usuario): Usuario que crea el grupo

        Returns:
            Grupo: Grupo creado

        Raises:
            ValidationError: Si las validaciones fallan
        """
        # Validación de negocio: Correo institucional
        if not datos_grupo.get('correo_grupo', '').endswith('@unal.edu.co'):
            raise ValidationError(
                "El correo debe ser institucional (@unal.edu.co)"
            )

        # Validación de negocio: Nombre único
        if Grupo.objects.filter(
            nombre_grupo=datos_grupo['nombre_grupo']
        ).exists():
            raise ValidationError(
                f"Ya existe un grupo con el nombre '{datos_grupo['nombre_grupo']}'"
            )

        # Crear grupo
        grupo = Grupo.objects.create(**datos_grupo)

        # Regla de negocio: Asignar creador como admin
        UsuarioGrupo.objects.create(
            usuario=usuario_creador,
            grupo=grupo,
            rol_en_grupo='ADMIN'
        )

        return grupo

    @staticmethod
    @transaction.atomic
    def actualizar_grupo(id_grupo, datos_actualizados):
        """
        Actualizar información del grupo

        Args:
            id_grupo (int): ID del grupo
            datos_actualizados (dict): Datos a actualizar

        Returns:
            Grupo: Grupo actualizado
        """
        grupo = Grupo.objects.get(id_grupo=id_grupo)

        for key, value in datos_actualizados.items():
            setattr(grupo, key, value)

        grupo.save()
        return grupo

    @staticmethod
    @transaction.atomic
    def eliminar_grupo(id_grupo):
        """
        Eliminar grupo (soft delete o hard delete según necesidad)

        Args:
            id_grupo (int): ID del grupo

        Returns:
            bool: True si se eliminó correctamente
        """
        grupo = Grupo.objects.get(id_grupo=id_grupo)
        grupo.delete()
        return True

    @staticmethod
    def agregar_miembro(id_grupo, id_usuario, rol='MIEMBRO'):
        """
        Agregar un miembro a un grupo

        Regla de Negocio:
        - Usuario no puede estar ya en el grupo
        - Rol por defecto es MIEMBRO

        Args:
            id_grupo (int): ID del grupo
            id_usuario (int): ID del usuario
            rol (str): Rol en el grupo (ADMIN/MIEMBRO)

        Returns:
            UsuarioGrupo: Relación creada
        """
        grupo = Grupo.objects.get(id_grupo=id_grupo)
        usuario = Usuario.objects.get(id_usuario=id_usuario)

        # Validación: No duplicar membresía
        if UsuarioGrupo.objects.filter(
            usuario=usuario,
            grupo=grupo
        ).exists():
            raise ValidationError("El usuario ya es miembro del grupo")

        return UsuarioGrupo.objects.create(
            usuario=usuario,
            grupo=grupo,
            rol_en_grupo=rol
        )

    @staticmethod
    def obtener_miembros(id_grupo):
        """
        Obtener todos los miembros de un grupo

        Args:
            id_grupo (int): ID del grupo

        Returns:
            QuerySet: Miembros del grupo
        """
        return UsuarioGrupo.objects.filter(
            grupo_id=id_grupo
        ).select_related('usuario')
    
    @staticmethod
    @transaction.atomic
    def eliminar_miembro(id_grupo, id_usuario):
        """
        Eliminar un miembro de un grupo.

        Levanta ValidationError si el usuario no pertenece al grupo.
        """
        grupo = Grupo.objects.get(id_grupo=id_grupo)
        usuario = Usuario.objects.get(id_usuario=id_usuario)

        deleted, _ = UsuarioGrupo.objects.filter(
            usuario=usuario,
            grupo=grupo
        ).delete()

        if deleted == 0:
            raise ValidationError("El usuario no es miembro del grupo")

        return True


# ===========================================================================
# SERVICIOS DE EVENTO
# ===========================================================================

class EventoService:
    """Servicio de lógica de negocio para Eventos"""

    @staticmethod
    def listar_eventos(filtros=None):
        """
        Listar eventos con filtros opcionales

        Args:
            filtros (dict): Filtros (grupo, estado_evento, fecha_inicio)

        Returns:
            QuerySet: Eventos filtrados
        """
        queryset = Evento.objects.all()

        if filtros:
            if 'grupo' in filtros:
                queryset = queryset.filter(grupo_id=filtros['grupo'])
            if 'estado_evento' in filtros:
                queryset = queryset.filter(
                    estado_evento=filtros['estado_evento']
                )
            if 'desde' in filtros:
                queryset = queryset.filter(
                    fecha_inicio__gte=filtros['desde']
                )

        return queryset.select_related('grupo').order_by('fecha_inicio')

    @staticmethod
    @transaction.atomic
    def crear_evento(datos_evento):
        """
        Crear un nuevo evento con validaciones

        Reglas de Negocio:
        - Fecha fin debe ser posterior a fecha inicio
        - Cupo debe ser positivo
        - Grupo debe existir

        Args:
            datos_evento (dict): Datos del evento

        Returns:
            Evento: Evento creado

        Raises:
            ValidationError: Si las validaciones fallan
        """
        # Validación de negocio: Fechas coherentes
        if datos_evento['fecha_fin'] <= datos_evento['fecha_inicio']:
            raise ValidationError(
                "La fecha de fin debe ser posterior a la fecha de inicio"
            )

        # Validación de negocio: Cupo positivo
        if datos_evento.get('cupo', 0) <= 0:
            raise ValidationError("El cupo debe ser un número positivo")

        return Evento.objects.create(**datos_evento)

    @staticmethod
    def obtener_evento(id_evento):
        """Obtener un evento específico"""
        return Evento.objects.select_related('grupo').get(
            id_evento=id_evento
        )

    @staticmethod
    @transaction.atomic
    def actualizar_evento(id_evento, datos_actualizados):
        """Actualizar información del evento"""
        evento = Evento.objects.get(id_evento=id_evento)

        for key, value in datos_actualizados.items():
            setattr(evento, key, value)

        evento.save()
        return evento

    @staticmethod
    @transaction.atomic
    def cancelar_evento(id_evento):
        """
        Cancelar un evento

        Regla de Negocio:
        - Cambiar estado a CANCELADO
        - Notificar a participantes

        Args:
            id_evento (int): ID del evento

        Returns:
            Evento: Evento actualizado
        """
        evento = Evento.objects.get(id_evento=id_evento)
        evento.estado_evento = 'CANCELADO'
        evento.save()

        return evento


# ===========================================================================
# SERVICIOS DE USUARIO
# ===========================================================================

class UsuarioService:
    """Servicio de lógica de negocio para Usuarios"""

    @staticmethod
    def listar_usuarios(filtros=None):
        """Listar usuarios con filtros"""
        queryset = Usuario.objects.all()

        if filtros:
            if 'estado_usuario' in filtros:
                queryset = queryset.filter(
                    estado_usuario=filtros['estado_usuario']
                )
            if 'busqueda' in filtros:
                queryset = queryset.filter(
                    nombre_usuario__icontains=filtros['busqueda']
                )

        return queryset.order_by('apellido', 'nombre_usuario')

    @staticmethod
    @transaction.atomic
    def crear_usuario(datos_usuario):
        """
        Crear un nuevo usuario

        Reglas de Negocio:
        - Correo único e institucional
        - Estado inicial: ACTIVO

        Args:
            datos_usuario (dict): Datos del usuario

        Returns:
            Usuario: Usuario creado
        """
        # Validación: Correo institucional
        if not datos_usuario.get('correo_usuario', '').endswith('@unal.edu.co'):
            raise ValidationError(
                "El correo debe ser institucional (@unal.edu.co)"
            )

        # Validación: Correo único
        if Usuario.objects.filter(
            correo_usuario=datos_usuario['correo_usuario']
        ).exists():
            raise ValidationError("El correo ya está registrado")

        return Usuario.objects.create(**datos_usuario)

    @staticmethod
    def obtener_usuario(id_usuario):
        """Obtener un usuario específico"""
        return Usuario.objects.get(id_usuario=id_usuario)

    @staticmethod
    def obtener_grupos_usuario(id_usuario):
        """Obtener todos los grupos de un usuario"""
        return UsuarioGrupo.objects.filter(
            usuario_id=id_usuario
        ).select_related('grupo')


# ===========================================================================
# SERVICIOS DE PARTICIPACIÓN
# ===========================================================================

class ParticipacionService:
    """Servicio de lógica de negocio para Participaciones"""

    @staticmethod
    @transaction.atomic
    def registrar_participacion(id_evento, id_usuario, comentario=""):
        """
        Registrar participación de un usuario en un evento.

        Reglas de negocio:
        - Verificar que el evento exista
        - Verificar que el usuario exista
        - No permitir registros duplicados (mismo usuario + evento)
        - Verificar cupo disponible (sobre ese evento)
        - Estado inicial: PENDIENTE
        """
        # Bloqueamos la fila del evento para evitar condiciones de carrera de cupo
        evento = Evento.objects.select_for_update().get(id_evento=id_evento)
        usuario = Usuario.objects.get(id_usuario=id_usuario)

        # 1) Validar que el usuario no esté ya registrado en este evento
        ya_existe = ParticipacionUsuario.objects.filter(
            usuario=usuario,
            participacion__evento=evento,
        ).exists()
        if ya_existe:
            raise ValidationError("El usuario ya está registrado en este evento")

        # 2) Contar participaciones CONFIRMADAS de ESTE evento
        participaciones_confirmadas = ParticipacionUsuario.objects.filter(
            participacion__evento=evento,
            participacion__estado_participacion="CONFIRMADO",
        ).count()

        if participaciones_confirmadas >= evento.cupo:
            raise ValidationError("No hay cupos disponibles para este evento")

        # 3) Crear la Participación (estado inicial: PENDIENTE)
        participacion = Participacion.objects.create(
            evento=evento,
            comentario=comentario,
            estado_participacion="PENDIENTE",
        )

        # 4) Relacionarla con el usuario
        ParticipacionUsuario.objects.create(
            usuario=usuario,
            participacion=participacion,
        )

        return participacion

    @staticmethod
    @transaction.atomic
    def confirmar_participacion(id_participacion):
        """Confirmar una participación"""
        participacion = Participacion.objects.get(
            id_participaciones=id_participacion
        )
        participacion.estado_participacion = 'CONFIRMADO'
        participacion.save()
        return participacion

    @staticmethod
    def obtener_participaciones_evento(id_evento):
        """Obtener todas las participaciones de un evento"""
        return ParticipacionUsuario.objects.filter(
            participacion__estado_participacion='CONFIRMADO'
        ).select_related('usuario', 'participacion')


# ===========================================================================
# SERVICIOS DE COMENTARIO
# ===========================================================================

class ComentarioService:
    """Servicio de lógica de negocio para Comentarios"""

    @staticmethod
    @transaction.atomic
    def crear_comentario(id_usuario, mensaje):
        """
        Crear un nuevo comentario

        Args:
            id_usuario (int): ID del usuario
            mensaje (str): Mensaje del comentario

        Returns:
            Comentario: Comentario creado
        """
        usuario = Usuario.objects.get(id_usuario=id_usuario)

        # Validación: Mensaje no vacío
        if not mensaje or len(mensaje.strip()) == 0:
            raise ValidationError("El mensaje no puede estar vacío")

        comentario = Comentario.objects.create(
            mensaje_comentario=mensaje,
            estado_comentario='PUBLICADO'
        )

        # Relacionar con usuario
        UsuarioComentario.objects.create(
            usuario=usuario,
            comentario=comentario
        )

        return comentario

    @staticmethod
    def listar_comentarios(filtros=None):
        """Listar comentarios"""
        queryset = Comentario.objects.all()

        if filtros and 'estado' in filtros:
            queryset = queryset.filter(
                estado_comentario=filtros['estado']
            )

        return queryset.order_by('-fecha_publicacion')


# ===========================================================================
# SERVICIOS DE NOTIFICACIÓN
# ===========================================================================

class NotificacionService:
    """Servicio de lógica de negocio para Notificaciones"""

    @staticmethod
    @transaction.atomic
    def enviar_notificacion(ids_usuarios, tipo, mensaje):
        """
        Enviar notificación a múltiples usuarios

        Args:
            ids_usuarios (list): Lista de IDs de usuarios
            tipo (str): Tipo de notificación
            mensaje (str): Mensaje

        Returns:
            Notificacion: Notificación creada
        """
        notificacion = Notificacion.objects.create(
            tipo_notificacion=tipo,
            mensaje=mensaje
        )

        # Relacionar con usuarios
        for id_usuario in ids_usuarios:
            usuario = Usuario.objects.get(id_usuario=id_usuario)
            UsuarioNotificacion.objects.create(
                usuario=usuario,
                notificacion=notificacion,
                leida=False
            )

        return notificacion

    @staticmethod
    def obtener_notificaciones_usuario(id_usuario):
        """Obtener notificaciones de un usuario"""
        return UsuarioNotificacion.objects.filter(
            usuario_id=id_usuario
        ).select_related('notificacion').order_by(
            '-notificacion__fecha_envio'
        )

    @staticmethod
    @transaction.atomic
    def marcar_como_leida(id_usuario, id_notificacion):
        """Marcar notificación como leída"""
        relacion = UsuarioNotificacion.objects.get(
            usuario_id=id_usuario,
            notificacion_id=id_notificacion
        )
        relacion.leida = True
        relacion.save()
        return relacion
