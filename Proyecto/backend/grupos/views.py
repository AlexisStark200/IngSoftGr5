from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views import View

from project.singleton import config_manager
from .models import Grupo
from .singletons import grupo_cache


from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.core.exceptions import ObjectDoesNotExist

from .models import (
    Usuario, Grupo, Evento,
    Comentario, Notificacion,
    UsuarioGrupo
)
from .serializers import (
    UsuarioSerializer,
    GrupoSerializer, GrupoDetalleSerializer,
    EventoSerializer,
    ParticipacionSerializer,
    ComentarioSerializer,
    NotificacionSerializer,
    UsuarioGrupoSerializer,
    RegistroParticipacionSerializer,
    AgregarMiembroSerializer,
    EnviarNotificacionSerializer
)
from .services import (
    GrupoService,
    EventoService,
    UsuarioService,
    ParticipacionService,
    ComentarioService,
    NotificacionService
)
def grupo_detail(request, pk=1):
    grupo = get_object_or_404(Grupo, pk=pk)
    return render(request, "grupos/grupo_detail.html", {"grupo": grupo})


class GrupoDetailView(View):
    def get(self, request, grupo_id):
        """Vista que usa el Singleton de cache"""
        # Usar el singleton para obtener el grupo
        grupo_data = grupo_cache.get_grupo(grupo_id)

        if not grupo_data:
            return JsonResponse({'error': 'Grupo no encontrado'}, status=404)

class GrupoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para operaciones CRUD de Grupos

    Endpoints:
    - GET    /grupos/                          → Listar todos
    - POST   /grupos/                          → Crear nuevo
    - GET    /grupos/{id}/                     → Obtener uno
    - PUT    /grupos/{id}/                     → Actualizar completo
    - PATCH  /grupos/{id}/                     → Actualizar parcial
    - DELETE /grupos/{id}/                     → Eliminar
    - GET    /grupos/{id}/miembros/            → Listar miembros
    - POST   /grupos/{id}/agregar-miembro/     → Agregar miembro
    - DELETE /grupos/{id}/eliminar-miembro/    → Eliminar miembro
    - GET    /grupos/{id}/eventos/             → Listar eventos
    """

    queryset = Grupo.objects.all()
    serializer_class = GrupoSerializer

    def get_serializer_class(self):
        """Usar serializer detallado en retrieve"""
        if self.action == 'retrieve':
            return GrupoDetalleSerializer
        return super().get_serializer_class()

    def create(self, request, *args, **kwargs):
        """
        Crear nuevo grupo

        Lógica:
        1. Validar datos con serializer
        2. Llamar a GrupoService para lógica de negocio
        3. Retornar grupo creado
        """
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            # Llamar a service (aquí va toda la lógica de negocio)
            grupo = GrupoService.crear_grupo(
                serializer.validated_data,
                request.user  # Usuario creador
            )

            # Retornar grupo creado
            resultado = GrupoSerializer(grupo)
            return Response(resultado.data, status=status.HTTP_201_CREATED)

        except ValidationError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    def update(self, request, *args, **kwargs):
        """Actualizar grupo completo"""
        try:
            grupo = self.get_object()
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            grupo_actualizado = GrupoService.actualizar_grupo(
                grupo.id_grupo,
                serializer.validated_data
            )

            return Response(GrupoSerializer(grupo_actualizado).data)

        except ObjectDoesNotExist:
            return Response(
                {"error": "Grupo no encontrado"},
                status=status.HTTP_404_NOT_FOUND
            )

    def destroy(self, request, *args, **kwargs):
        """Eliminar grupo"""
        try:
            grupo = self.get_object()
            GrupoService.eliminar_grupo(grupo.id_grupo)
            return Response(status=status.HTTP_204_NO_CONTENT)

        except ObjectDoesNotExist:
            return Response(
                {"error": "Grupo no encontrado"},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['get'])
    def miembros(self, request, pk=None):
        """
        GET /grupos/{id}/miembros/
        Listar todos los miembros de un grupo
        """
        try:
            grupo = self.get_object()
            miembros = GrupoService.obtener_miembros(grupo.id_grupo)
            serializer = UsuarioGrupoSerializer(miembros, many=True)
            return Response(serializer.data)

        except ObjectDoesNotExist:
            return Response(
                {"error": "Grupo no encontrado"},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'])
    def agregar_miembro(self, request, pk=None):
        """
        POST /grupos/{id}/agregar-miembro/

        Body:
        {
            "id_usuario": 5,
            "rol_en_grupo": "MIEMBRO"  # Opcional, default MIEMBRO
        }
        """
        try:
            grupo = self.get_object()
            serializer = AgregarMiembroSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            relacion = GrupoService.agregar_miembro(
                grupo.id_grupo,
                serializer.validated_data['id_usuario'],
                serializer.validated_data.get('rol_en_grupo', 'MIEMBRO')
            )

            resultado = UsuarioGrupoSerializer(relacion)
            return Response(
                resultado.data,
                status=status.HTTP_201_CREATED
            )

        except ValidationError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['delete'])
    def eliminar_miembro(self, request, pk=None):
        """
        DELETE /grupos/{id}/eliminar-miembro/?id_usuario=5
        """
        try:
            grupo = self.get_object()
            id_usuario = request.query_params.get('id_usuario')

            if not id_usuario:
                return Response(
                    {"error": "Falta parámetro id_usuario"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            UsuarioGrupo.objects.get(
                usuario_id=id_usuario,
                grupo_id=grupo.id_grupo
            ).delete()

            return Response(status=status.HTTP_204_NO_CONTENT)

        except ObjectDoesNotExist:
            return Response(
                {"error": "Relación no encontrada"},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['get'])
    def eventos(self, request, pk=None):
        """
        GET /grupos/{id}/eventos/
        Listar eventos del grupo
        """
        try:
            grupo = self.get_object()
            eventos = grupo.eventos.all()
            serializer = EventoSerializer(eventos, many=True)
            return Response(serializer.data)

        except ObjectDoesNotExist:
            return Response(
                {"error": "Grupo no encontrado"},
                status=status.HTTP_404_NOT_FOUND
            )


class EventoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para operaciones CRUD de Eventos

    Endpoints:
    - GET    /eventos/                         → Listar
    - POST   /eventos/                         → Crear
    - GET    /eventos/{id}/                    → Obtener
    - PUT    /eventos/{id}/                    → Actualizar
    - PATCH  /eventos/{id}/                    → Actualizar parcial
    - DELETE /eventos/{id}/                    → Eliminar
    - POST   /eventos/{id}/cancelar/           → Cancelar evento
    - POST   /eventos/{id}/registrar-usuario/  → Registrar participante
    """

    queryset = Evento.objects.all()
    serializer_class = EventoSerializer

    def create(self, request, *args, **kwargs):
        """Crear nuevo evento"""
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            evento = EventoService.crear_evento(serializer.validated_data)

            return Response(
                EventoSerializer(evento).data,
                status=status.HTTP_201_CREATED
            )

        except ValidationError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    def update(self, request, *args, **kwargs):
        """Actualizar evento"""
        try:
            evento = self.get_object()
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            evento_actualizado = EventoService.actualizar_evento(
                evento.id_evento,
                serializer.validated_data
            )

            return Response(EventoSerializer(evento_actualizado).data)

        except ObjectDoesNotExist:
            return Response(
                {"error": "Evento no encontrado"},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'])
    def cancelar(self, request, pk=None):
        """
        POST /eventos/{id}/cancelar/
        Cancelar un evento
        """
        try:
            evento = self.get_object()
            evento_cancelado = EventoService.cancelar_evento(evento.id_evento)
            return Response(EventoSerializer(evento_cancelado).data)

        except ObjectDoesNotExist:
            return Response(
                {"error": "Evento no encontrado"},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'])
    def registrar_usuario(self, request, pk=None):
        """
        POST /eventos/{id}/registrar-usuario/

        Body:
        {
            "id_usuario": 3,
            "comentario": "Quiero asistir"  # Opcional
        }
        """
        try:
            evento = self.get_object()
            serializer = RegistroParticipacionSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            participacion = ParticipacionService.registrar_participacion(
                evento.id_evento,
                serializer.validated_data.get('id_usuario'),
                serializer.validated_data.get('comentario', '')
            )

            return Response(
                ParticipacionSerializer(participacion).data,
                status=status.HTTP_201_CREATED
            )

        except ValidationError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class UsuarioViewSet(viewsets.ModelViewSet):
    """
    ViewSet para operaciones CRUD de Usuarios
    """

    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer

    def create(self, request, *args, **kwargs):
        """Crear nuevo usuario"""
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            usuario = UsuarioService.crear_usuario(serializer.validated_data)

            return Response(
                UsuarioSerializer(usuario).data,
                status=status.HTTP_201_CREATED
            )

        except ValidationError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['get'])
    def grupos(self, request, pk=None):
        """
        GET /usuarios/{id}/grupos/
        Listar grupos del usuario
        """
        try:
            usuario = self.get_object()
            grupos_usuario = UsuarioService.obtener_grupos_usuario(usuario.id_usuario)
            serializer = UsuarioGrupoSerializer(grupos_usuario, many=True)
            return Response(serializer.data)

        except ObjectDoesNotExist:
            return Response(
                {"error": "Usuario no encontrado"},
                status=status.HTTP_404_NOT_FOUND
            )


class ComentarioViewSet(viewsets.ModelViewSet):
    """ViewSet para operaciones CRUD de Comentarios"""

    queryset = Comentario.objects.all()
    serializer_class = ComentarioSerializer

    def create(self, request, *args, **kwargs):
        """Crear nuevo comentario"""
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            comentario = ComentarioService.crear_comentario(
                request.user.id,
                serializer.validated_data['mensaje_comentario']
            )

            return Response(
                ComentarioSerializer(comentario).data,
                status=status.HTTP_201_CREATED
            )

        except ValidationError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class NotificacionViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para lectura de Notificaciones (solo GET)"""

    queryset = Notificacion.objects.all()
    serializer_class = NotificacionSerializer

    @action(detail=True, methods=['post'])
    def marcar_leida(self, request, pk=None):
        """
        POST /notificaciones/{id}/marcar-leida/
        Marcar notificación como leída
        """
        try:
            notificacion = self.get_object()

            NotificacionService.marcar_como_leida(
                request.user.id,
                notificacion.id_notificacion
            )

            return Response(
                {"message": "Notificación marcada como leída"},
                status=status.HTTP_200_OK
            )

        except ObjectDoesNotExist:
            return Response(
                {"error": "Notificación no encontrada"},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['post'])
    def enviar_masiva(self, request):
        """
        POST /notificaciones/enviar-masiva/

        Body:
        {
            "ids_usuarios": [1, 2, 3],
            "tipo_notificacion": "EVENTO_CREADO",
            "mensaje": "Se creó un nuevo evento"
        }
        """
        try:
            serializer = EnviarNotificacionSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            notificacion = NotificacionService.enviar_notificacion(
                serializer.validated_data['ids_usuarios'],
                serializer.validated_data['tipo_notificacion'],
                serializer.validated_data['mensaje']
            )

            return Response(
                NotificacionSerializer(notificacion).data,
                status=status.HTTP_201_CREATED
            )

        except ValidationError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        return JsonResponse({
            'grupo': grupo_data,
            'config': {
                'app_name': config_manager.get('app_name'),
                'max_grupos': config_manager.get('max_grupos_usuario')
            }
        })


class ConfigView(View):
    def get(self, request):
        """Vista para ver/configurar el Singleton"""
        return JsonResponse({
            'configuracion': config_manager.get_all(),
            'estadisticas_cache': grupo_cache.get_estadisticas()
        })

    def post(self, request):
        """Actualizar configuración"""
        key = request.POST.get('key')
        value = request.POST.get('value')

        if key and value is not None:
            config_manager.set(key, value)
            return JsonResponse({'status': 'Configuración actualizada'})

class BusquedaGruposView(viewsets.ViewSet):
    """Vista personalizada para búsqueda avanzada de grupos"""

    @action(detail=False, methods=['get'])
    def buscar(self, request):
        """
        GET /grupos/buscar/?busqueda=Programación&area=Tecnología

        Parámetros:
        - busqueda: término de búsqueda
        - area: área de interés
        - tipo: tipo de grupo
        """
        filtros = {
            'busqueda': request.query_params.get('busqueda', ''),
            'area_interes': request.query_params.get('area', ''),
            'tipo_grupo': request.query_params.get('tipo', '')
        }

        # Limpiar filtros vacíos
        filtros = {k: v for k, v in filtros.items() if v}

        grupos = GrupoService.listar_grupos(filtros)
        serializer = GrupoSerializer(grupos, many=True)

        return Response({
            "total": grupos.count(),
            "resultados": serializer.data
        })
        return JsonResponse({'error': 'Key y value requeridos'}, status=400)
    
