"""
Serializers - ÁgoraUN
Conversión de Modelos Python ↔ JSON

Valida formato de datos y convierte entre:
- Objetos Python (modelos) → JSON (para enviar al frontend)
- JSON (desde frontend) → Objetos Python (para guardar en BD)
"""

from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from rest_framework import serializers
from .models import (
    Usuario, Grupo, Evento, Participacion,
    Comentario, Notificacion, Rol,
    UsuarioGrupo, ParticipacionUsuario,
    UsuarioNotificacion, UsuarioRol
)


# ===========================================================================
# SERIALIZERS PRINCIPALES
# ===========================================================================

class UsuarioSerializer(serializers.ModelSerializer):
    """Serializer para Usuario"""

    class Meta:
        model = Usuario
        fields = [
            'id_usuario',
            'nombre_usuario',
            'apellido',
            'correo_usuario',
            'estado_usuario',
            'fecha_registro'
        ]
        read_only_fields = ['id_usuario', 'fecha_registro']

    def validate_correo_usuario(self, value):
        """Validar que el correo sea institucional"""
        if not value.endswith('@unal.edu.co'):
            raise serializers.ValidationError(
                "El correo debe ser institucional (@unal.edu.co)"
            )
        return value


class GrupoSerializer(serializers.ModelSerializer):
    """Serializer para Grupo"""

    total_miembros = serializers.SerializerMethodField()
    total_eventos = serializers.SerializerMethodField()
    estado_grupo = serializers.CharField(read_only=True)
    motivo_rechazo = serializers.CharField(read_only=True)

    class Meta:
        model = Grupo
        fields = [
            'id_grupo',
            'nombre_grupo',
            'area_interes',
            'fecha_creacion',
            'tipo_grupo',
            'logo',
            'correo_grupo',
            'descripcion',
            'link_whatsapp',
            'estado_grupo',
            'motivo_rechazo',
            'total_miembros',
            'total_eventos'
        ]
        read_only_fields = ['id_grupo', 'fecha_creacion', 'estado_grupo', 'motivo_rechazo']

    def get_total_miembros(self, obj):
        """Contar miembros del grupo"""
        return obj.miembros.count()

    def get_total_eventos(self, obj):
        """Contar eventos del grupo"""
        return obj.eventos.count()

    def validate_correo_grupo(self, value):
        """Validar correo institucional"""
        if not value.endswith('@unal.edu.co'):
            raise serializers.ValidationError(
                "El correo debe ser institucional (@unal.edu.co)"
            )
        return value


class GrupoDetalleSerializer(serializers.ModelSerializer):
    """Serializer detallado de Grupo con relaciones"""

    miembros = serializers.SerializerMethodField()
    eventos_proximos = serializers.SerializerMethodField()
    estado_grupo = serializers.CharField(read_only=True)
    motivo_rechazo = serializers.CharField(read_only=True)

    class Meta:
        model = Grupo
        fields = [
            'id_grupo',
            'nombre_grupo',
            'area_interes',
            'fecha_creacion',
            'tipo_grupo',
            'logo',
            'correo_grupo',
            'descripcion',
            'link_whatsapp',
            'estado_grupo',
            'motivo_rechazo',
            'miembros',
            'eventos_proximos'
        ]

    def get_miembros(self, obj):
        """Obtener lista de miembros"""
        usuarios = obj.miembros.all()[:10]  # Limitar a 10
        return UsuarioSerializer(usuarios, many=True).data

    def get_eventos_proximos(self, obj):
        """Obtener eventos próximos del grupo"""
        eventos = obj.eventos.filter(
            fecha_inicio__gte=timezone.now(),
            estado_evento='PROGRAMADO'
        ).order_by('fecha_inicio')[:5]
        return EventoSerializer(eventos, many=True).data

    def get_solicitante_nombre(self, obj):
        if obj.solicitante:
            return f"{obj.solicitante.nombre_usuario} {obj.solicitante.apellido}"
        return None

    def get_aprobado_por_nombre(self, obj):
        if obj.aprobado_por:
            return f"{obj.aprobado_por.nombre_usuario} {obj.aprobado_por.apellido}"
        return None


class EventoSerializer(serializers.ModelSerializer):
    """Serializer para Evento"""

    grupo_nombre = serializers.CharField(
        source='grupo.nombre_grupo',
        read_only=True
    )
    cupos_disponibles = serializers.SerializerMethodField()

    class Meta:
        model = Evento
        fields = [
            'id_evento',
            'grupo',
            'grupo_nombre',
            'nombre_evento',
            'descripcion_evento',
            'fecha_inicio',
            'fecha_fin',
            'lugar',
            'tipo_evento',
            'cupo',
            'cupos_disponibles',
            'estado_evento'
        ]
        read_only_fields = ['id_evento']

    def get_cupos_disponibles(self, obj):
        """Calcular cupos disponibles SOLO para este evento"""
        participaciones_confirmadas = ParticipacionUsuario.objects.filter(
            participacion__evento=obj,
            participacion__estado_participacion='CONFIRMADO'
        ).count()
        return max(0, obj.cupo - participaciones_confirmadas)

    def validate(self, data):
        """Validar fechas coherentes y cupo positivo"""
        if data.get('fecha_fin') and data.get('fecha_inicio'):
            if data['fecha_fin'] <= data['fecha_inicio']:
                raise serializers.ValidationError(
                    "La fecha de fin debe ser posterior a la fecha de inicio"
                )

        if data.get('cupo', 0) <= 0:
            raise serializers.ValidationError(
                "El cupo debe ser un número positivo"
            )

        return data


class ParticipacionSerializer(serializers.ModelSerializer):
    """Serializer para Participación en evento"""

    evento_info = EventoSerializer(source='evento', read_only=True)
    usuarios = serializers.SerializerMethodField()

    class Meta:
        model = Participacion
        fields = [
            'id_participaciones',
            'evento',
            'evento_info',
            'fecha_registro',
            'comentario',
            'estado_participacion',
            'usuarios',
        ]
        read_only_fields = ['id_participaciones', 'fecha_registro']

    def get_usuarios(self, obj):
        """Usuarios asociados a esta participación"""
        return UsuarioSerializer(obj.usuarios.all(), many=True).data


# ===========================================================================
# SERIALIZERS ESPECIALES (para operaciones específicas)
# ===========================================================================

class RegistroParticipacionSerializer(serializers.Serializer):
    """Serializer para registrar participación en evento

    El evento viene en la URL (/eventos/{id}/registrar-usuario/),
    por eso aquí solo pedimos id_usuario y comentario.
    """

    id_usuario = serializers.IntegerField()
    comentario = serializers.CharField(
        max_length=100,
        required=False,
        allow_blank=True
    )

    def validate_id_usuario(self, value):
        """Verificar que el usuario existe"""
        try:
            Usuario.objects.get(id_usuario=value)
        except ObjectDoesNotExist as exc:
            raise serializers.ValidationError("El usuario no existe") from exc
        return value


class ComentarioSerializer(serializers.ModelSerializer):
    """Serializer para Comentario"""

    autor = serializers.SerializerMethodField()

    class Meta:
        model = Comentario
        fields = [
            'id_comentario',
            'mensaje_comentario',
            'fecha_publicacion',
            'estado_comentario',
            'autor'
        ]
        read_only_fields = ['id_comentario', 'fecha_publicacion']

    def get_autor(self, obj):
        """Obtener información del autor"""
        usuario_comentario = obj.usuarios.first()
        if usuario_comentario:
            return {
                'id': usuario_comentario.id_usuario,
                'nombre': usuario_comentario.nombre_usuario,
                'apellido': usuario_comentario.apellido
            }
        return None


class NotificacionSerializer(serializers.ModelSerializer):
    """Serializer para Notificación"""

    leida = serializers.SerializerMethodField()

    class Meta:
        model = Notificacion
        fields = [
            'id_notificacion',
            'tipo_notificacion',
            'mensaje',
            'fecha_envio',
            'leida'
        ]
        read_only_fields = ['id_notificacion', 'fecha_envio']

    def get_leida(self, obj):
        """
        Verificar si fue leída por el usuario indicado en el contexto.
        Si no se pasa usuario, se asume no leída.
        """
        id_usuario = self.context.get('id_usuario')
        if not id_usuario:
            return False

        return UsuarioNotificacion.objects.filter(
            usuario_id=id_usuario,   # ← usamos el id de Usuario, no request.user
            notificacion=obj,
            leida=True
        ).exists()



class RolSerializer(serializers.ModelSerializer):
    """Serializer para Rol"""

    class Meta:
        model = Rol
        fields = ['id_rol', 'nombre_rol']


# ===========================================================================
# SERIALIZERS DE RELACIONES (Many-to-Many)
# ===========================================================================

class UsuarioGrupoSerializer(serializers.ModelSerializer):
    """Serializer para relación Usuario-Grupo"""

    usuario_nombre = serializers.CharField(
        source='usuario.nombre_usuario',
        read_only=True
    )
    grupo_nombre = serializers.CharField(
        source='grupo.nombre_grupo',
        read_only=True
    )

    class Meta:
        model = UsuarioGrupo
        fields = [
            'usuario',
            'usuario_nombre',
            'grupo',
            'grupo_nombre',
            'fecha_union',
            'rol_en_grupo'
        ]
        read_only_fields = ['fecha_union']


class ParticipacionUsuarioSerializer(serializers.ModelSerializer):
    """Serializer para relación Participación-Usuario"""

    usuario_info = UsuarioSerializer(source='usuario', read_only=True)
    participacion_info = ParticipacionSerializer(
        source='participacion',
        read_only=True
    )

    class Meta:
        model = ParticipacionUsuario
        fields = [
            'usuario',
            'usuario_info',
            'participacion',
            'participacion_info'
        ]


class UsuarioRolSerializer(serializers.ModelSerializer):
    """Serializer para relación Usuario-Rol"""

    rol_nombre = serializers.CharField(source='rol.nombre_rol', read_only=True)

    class Meta:
        model = UsuarioRol
        fields = ['usuario', 'rol', 'rol_nombre']


# ===========================================================================
# OTROS SERIALIZERS ESPECIALES
# ===========================================================================

class AgregarMiembroSerializer(serializers.Serializer):
    """Serializer para agregar miembro a grupo"""

    id_usuario = serializers.IntegerField()
    rol_en_grupo = serializers.ChoiceField(
        choices=['ADMIN', 'MIEMBRO'],
        default='MIEMBRO'
    )

    def validate_id_usuario(self, value):
        """Verificar que el usuario existe"""
        try:
            Usuario.objects.get(id_usuario=value)
        except ObjectDoesNotExist as exc:
            raise serializers.ValidationError("El usuario no existe") from exc
        return value


class EnviarNotificacionSerializer(serializers.Serializer):
    """Serializer para enviar notificación"""

    ids_usuarios = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1
    )
    tipo_notificacion = serializers.CharField(max_length=20)
    mensaje = serializers.CharField()

    def validate_ids_usuarios(self, value):
        """Verificar que todos los usuarios existen"""
        usuarios_existentes = Usuario.objects.filter(
            id_usuario__in=value
        ).count()
        if usuarios_existentes != len(value):
            raise serializers.ValidationError(
                "Algunos usuarios no existen"
            )
        return value


class RechazarGrupoSerializer(serializers.Serializer):
    """Serializer para rechazo de grupo (RF_14)"""

    motivo = serializers.CharField(allow_blank=False, allow_null=False)
