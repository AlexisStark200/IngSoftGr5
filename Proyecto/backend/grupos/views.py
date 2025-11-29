# backend/grupos/views.py

from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views import View

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from project.singleton import config_manager
from .singletons import grupo_cache

from .models import (
    Usuario, Grupo, Evento,
    Comentario, Notificacion,
    UsuarioGrupo
)
from .serializers import (
    UsuarioSerializer,
    GrupoSerializer, GrupoDetalleSerializer,
    EventoSerializer,
    ParticipacionSerializer, RegistroParticipacionSerializer,
    ComentarioSerializer,
    NotificacionSerializer,
    UsuarioGrupoSerializer,
    AgregarMiembroSerializer,
    EnviarNotificacionSerializer,
    RechazarGrupoSerializer
)
from .services import (
    GrupoService,
    EventoService,
    UsuarioService,
    ParticipacionService,
    ComentarioService,
    NotificacionService
)

# -------------------------------------------------------------------
# Vistas clásicas (HTML / JSON) - opcionales para demo
# -------------------------------------------------------------------

def grupo_detail(request, pk=1):
    """Ejemplo de vista HTML simple usando templates."""
    grupo = get_object_or_404(Grupo, pk=pk)
    return render(request, "grupos/grupo_detail.html", {"grupo": grupo})


class GrupoDetailView(View):
    """Vista que usa el Singleton de caché para devolver info de un grupo en JSON."""

    def get(self, request, grupo_id):
        data = grupo_cache.get_grupo(grupo_id)
        if not data:
            return JsonResponse({'error': 'Grupo no encontrado'}, status=404)
        return JsonResponse({
            'grupo': data,
            'config': {
                'app_name': config_manager.get('app_name'),
                'max_grupos': config_manager.get('max_grupos_usuario')
            }
        })


class ConfigView(View):
    """Vista para leer/actualizar configuración del Singleton del proyecto."""

    def get(self, request):
        return JsonResponse({
            'configuracion': config_manager.get_all(),
            'estadisticas_cache': grupo_cache.get_estadisticas()
        })

    def post(self, request):
        key = request.POST.get('key')
        value = request.POST.get('value')
        if key and value is not None:
            config_manager.set(key, value)
            return JsonResponse({'status': 'Configuración actualizada'})
        return JsonResponse({'error': 'Key y value requeridos'}, status=400)


class BusquedaGruposView(viewsets.ViewSet):
    """Vista personalizada para búsqueda avanzada de grupos (JSON)."""

    @action(detail=False, methods=['get'])
    def buscar(self, request):
        """
        GET /grupos/buscar/?busqueda=Programación&area=Tecnología&tipo=Académico
        Parámetros: busqueda | area | tipo
        """
        filtros = {
            'busqueda': request.query_params.get('busqueda', ''),
            'area_interes': request.query_params.get('area', ''),
            'tipo_grupo': request.query_params.get('tipo', '')
        }
        filtros = {k: v for k, v in filtros.items() if v}

        if hasattr(GrupoService, "listar_grupos"):
            grupos = GrupoService.listar_grupos(filtros)
        else:
            # Fallback sencillo si el service no tuviera ese método
            grupos = Grupo.objects.all()
            if filtros.get('area_interes'):
                grupos = grupos.filter(area_interes__icontains=filtros['area_interes'])
            if filtros.get('tipo_grupo'):
                grupos = grupos.filter(tipo_grupo__icontains=filtros['tipo_grupo'])
            if filtros.get('busqueda'):
                q = filtros['busqueda']
                grupos = grupos.filter(
                    nombre_grupo__icontains=q
                ) | grupos.filter(descripcion__icontains=q)

        ser = GrupoSerializer(grupos, many=True)
        total = grupos.count() if hasattr(grupos, "count") else len(ser.data)
        return Response({"total": total, "resultados": ser.data})

# -------------------------------------------------------------------
# GRUPOS
# -------------------------------------------------------------------

class GrupoViewSet(viewsets.ModelViewSet):
    """
    CRUD de Grupos + acciones: miembros, agregar_miembro, eliminar_miembro, eventos.

    Query params útiles:
      ?search= (nombre_grupo/area_interes/tipo_grupo/descripcion/correo_grupo)
      ?ordering=nombre_grupo|area_interes|tipo_grupo|id_grupo|fecha_creacion
      ?area= (filtro exacto por área → area_interes)
    """

    queryset = Grupo.objects.all()
    serializer_class = GrupoSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    # DRF filters
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = [
        "nombre_grupo",
        "area_interes",
        "tipo_grupo",
        "descripcion",
        "correo_grupo",
    ]
    ordering_fields = [
        "nombre_grupo",
        "area_interes",
        "tipo_grupo",
        "id_grupo",
        "fecha_creacion",
    ]
    ordering = ["nombre_grupo"]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return GrupoDetalleSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        qs = super().get_queryset()
        area = self.request.query_params.get("area")
        estado = self.request.query_params.get("estado")
        if area:
            qs = qs.filter(area_interes__iexact=area)
        if estado:
            qs = qs.filter(estado_grupo=estado)
        return qs

    # ----------------------- CRUD con services -----------------------------

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        try:
            ser = self.get_serializer(data=request.data)
            ser.is_valid(raise_exception=True)
            grupo = GrupoService.crear_grupo(ser.validated_data, request.user)
            return Response(GrupoSerializer(grupo).data, status=status.HTTP_201_CREATED)
        except (ValidationError, DRFValidationError) as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        try:
            grupo = self.get_object()
            ser = self.get_serializer(data=request.data)
            ser.is_valid(raise_exception=True)
            actualizado = GrupoService.actualizar_grupo(grupo.id_grupo, ser.validated_data)
            return Response(GrupoSerializer(actualizado).data)
        except ObjectDoesNotExist:
            return Response({"error": "Grupo no encontrado"}, status=status.HTTP_404_NOT_FOUND)
        except (ValidationError, DRFValidationError) as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @transaction.atomic
    def partial_update(self, request, *args, **kwargs):
        try:
            grupo = self.get_object()
            ser = self.get_serializer(data=request.data, partial=True)
            ser.is_valid(raise_exception=True)
            actualizado = GrupoService.actualizar_grupo(grupo.id_grupo, ser.validated_data)
            return Response(GrupoSerializer(actualizado).data)
        except ObjectDoesNotExist:
            return Response({"error": "Grupo no encontrado"}, status=status.HTTP_404_NOT_FOUND)
        except (ValidationError, DRFValidationError) as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        try:
            grupo = self.get_object()
            GrupoService.eliminar_grupo(grupo.id_grupo)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ObjectDoesNotExist:
            return Response({"error": "Grupo no encontrado"}, status=status.HTTP_404_NOT_FOUND)

    # ----------------------- Acciones personalizadas -----------------------

    @action(detail=True, methods=["get"])
    def miembros(self, request, pk=None):
        try:
            grupo = self.get_object()
            miembros = GrupoService.obtener_miembros(grupo.id_grupo)
            return Response(UsuarioGrupoSerializer(miembros, many=True).data)
        except ObjectDoesNotExist:
            return Response({"error": "Grupo no encontrado"}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticatedOrReadOnly])
    def agregar_miembro(self, request, pk=None):
        """Body: {"id_usuario": 5, "rol_en_grupo": "MIEMBRO"}"""
        try:
            grupo = self.get_object()
            payload = AgregarMiembroSerializer(data=request.data)
            payload.is_valid(raise_exception=True)
            rel = GrupoService.agregar_miembro(
                id_grupo=grupo.id_grupo,
                id_usuario=payload.validated_data["id_usuario"],
                rol=payload.validated_data.get("rol_en_grupo", "MIEMBRO"),
            )
            return Response(UsuarioGrupoSerializer(rel).data, status=status.HTTP_201_CREATED)

        except ObjectDoesNotExist:
            return Response({"error": "Grupo o usuario no encontrado"}, status=status.HTTP_404_NOT_FOUND)
        except (ValidationError, DRFValidationError) as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["delete"], permission_classes=[IsAuthenticatedOrReadOnly])
    def eliminar_miembro(self, request, pk=None):
        """DELETE /grupos/{id}/eliminar-miembro/?id_usuario=5"""
        try:
            grupo = self.get_object()
            id_usuario = request.query_params.get("id_usuario")
            if not id_usuario:
                return Response({"error": "Falta parámetro id_usuario"}, status=status.HTTP_400_BAD_REQUEST)
            GrupoService.eliminar_miembro(id_grupo=grupo.id_grupo, id_usuario=id_usuario)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ObjectDoesNotExist:
            return Response({"error": "Relación no encontrada"}, status=status.HTTP_404_NOT_FOUND)


    @action(detail=True, methods=["post"])
    def aprobar(self, request, pk=None):
        """POST /grupos/{id}/aprobar/ -> cambia estado a APROBADO (RF_14)."""
        try:
            grupo = GrupoService.aprobar_grupo(pk)
            return Response(GrupoSerializer(grupo).data, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response({"error": "Grupo no encontrado"}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=["post"])
    def rechazar(self, request, pk=None):
        """POST /grupos/{id}/rechazar/ Body: {"motivo": "Falta correo institucional"} (RF_14)."""
        try:
            payload = RechazarGrupoSerializer(data=request.data)
            payload.is_valid(raise_exception=True)
            grupo = GrupoService.rechazar_grupo(pk, payload.validated_data["motivo"])
            return Response(GrupoSerializer(grupo).data, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response({"error": "Grupo no encontrado"}, status=status.HTTP_404_NOT_FOUND)
        except (ValidationError, DRFValidationError) as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["get"])
    def eventos(self, request, pk=None):
        try:
            grupo = self.get_object()
            eventos = (
                GrupoService.obtener_eventos(grupo.id_grupo)
                if hasattr(GrupoService, "obtener_eventos")
                else grupo.eventos.all()
            )
            return Response(EventoSerializer(eventos, many=True).data)
        except ObjectDoesNotExist:
            return Response({"error": "Grupo no encontrado"}, status=status.HTTP_404_NOT_FOUND)

# -------------------------------------------------------------------
# EVENTOS
# -------------------------------------------------------------------

class EventoViewSet(viewsets.ModelViewSet):
    """CRUD de Eventos + cancelar + registrar_usuario."""

    queryset = Evento.objects.select_related("grupo").all()
    serializer_class = EventoSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["nombre_evento", "descripcion_evento", "lugar", "tipo_evento"]
    ordering_fields = ["fecha_inicio", "fecha_fin", "nombre_evento", "cupo"]
    ordering = ["-fecha_inicio"]

    def get_queryset(self):
        qs = super().get_queryset()
        grupo = self.request.query_params.get("grupo")
        estado = self.request.query_params.get("estado")
        desde = self.request.query_params.get("desde")
        if grupo:
            qs = qs.filter(grupo_id=grupo)
        if estado:
            qs = qs.filter(estado_evento=estado)
        if desde:
            qs = qs.filter(fecha_inicio__date__gte=desde)
        return qs

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        try:
            ser = self.get_serializer(data=request.data)
            ser.is_valid(raise_exception=True)
            evento = EventoService.crear_evento(ser.validated_data)
            return Response(EventoSerializer(evento).data, status=status.HTTP_201_CREATED)
        except (ValidationError, DRFValidationError) as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        try:
            evento = self.get_object()
            ser = self.get_serializer(data=request.data)
            ser.is_valid(raise_exception=True)
            actualizado = EventoService.actualizar_evento(evento.id_evento, ser.validated_data)
            return Response(EventoSerializer(actualizado).data)
        except ObjectDoesNotExist:
            return Response({"error": "Evento no encontrado"}, status=status.HTTP_404_NOT_FOUND)
        except (ValidationError, DRFValidationError) as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @transaction.atomic
    def partial_update(self, request, *args, **kwargs):
        try:
            evento = self.get_object()
            ser = self.get_serializer(data=request.data, partial=True)
            ser.is_valid(raise_exception=True)
            actualizado = EventoService.actualizar_evento(evento.id_evento, ser.validated_data)
            return Response(EventoSerializer(actualizado).data)
        except ObjectDoesNotExist:
            return Response({"error": "Evento no encontrado"}, status=status.HTTP_404_NOT_FOUND)
        except (ValidationError, DRFValidationError) as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        try:
            evento = self.get_object()
            EventoService.eliminar_evento(evento.id_evento)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ObjectDoesNotExist:
            return Response({"error": "Evento no encontrado"}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=["post"])
    def cancelar(self, request, pk=None):
        """POST /eventos/{id}/cancelar/ → estado=CANCELADO"""
        try:
            ev = EventoService.cancelar_evento(pk)
            return Response({"status": "ok", "estado": ev.estado_evento})
        except ObjectDoesNotExist:
            return Response({"error": "Evento no encontrado"}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=["post"])
    def registrar_usuario(self, request, pk=None):
        """
        POST /eventos/{id}/registrar-usuario/
        Body: {"id_usuario": 3, "comentario": "Quiero asistir"}
        """
        try:
            evento = self.get_object()
            payload = RegistroParticipacionSerializer(data=request.data)
            payload.is_valid(raise_exception=True)
            participacion = ParticipacionService.registrar_participacion(
                id_evento=evento.id_evento,
                id_usuario=payload.validated_data.get("id_usuario"),
                comentario=payload.validated_data.get("comentario", ""),
            )
            return Response(ParticipacionSerializer(participacion).data, status=status.HTTP_201_CREATED)
        except ObjectDoesNotExist:
            return Response({"error": "Evento o usuario no encontrado"}, status=status.HTTP_404_NOT_FOUND)
        except (ValidationError, DRFValidationError) as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# -------------------------------------------------------------------
# USUARIOS
# -------------------------------------------------------------------

class UsuarioViewSet(viewsets.ModelViewSet):
    """CRUD de Usuarios."""

    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        try:
            ser = self.get_serializer(data=request.data)
            ser.is_valid(raise_exception=True)
            usuario = UsuarioService.crear_usuario(ser.validated_data)
            return Response(UsuarioSerializer(usuario).data, status=status.HTTP_201_CREATED)
        except (ValidationError, DRFValidationError) as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def grupos(self, request, pk=None):
        """GET /usuarios/{id}/grupos/ → grupos del usuario."""
        try:
            usuario = self.get_object()
            grupos_usuario = UsuarioService.obtener_grupos_usuario(usuario.id_usuario)
            return Response(UsuarioGrupoSerializer(grupos_usuario, many=True).data)
        except ObjectDoesNotExist:
            return Response({"error": "Usuario no encontrado"}, status=status.HTTP_404_NOT_FOUND)

# -------------------------------------------------------------------
# COMENTARIOS
# -------------------------------------------------------------------

class ComentarioViewSet(viewsets.ModelViewSet):
    """CRUD de Comentarios."""

    queryset = Comentario.objects.all()
    serializer_class = ComentarioSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        try:
            ser = self.get_serializer(data=request.data)
            ser.is_valid(raise_exception=True)
            comentario = ComentarioService.crear_comentario(
                request.user.id, ser.validated_data['mensaje_comentario']
            )
            return Response(ComentarioSerializer(comentario).data, status=status.HTTP_201_CREATED)
        except (ValidationError, DRFValidationError) as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# -------------------------------------------------------------------
# NOTIFICACIONES
# -------------------------------------------------------------------

class NotificacionViewSet(viewsets.ReadOnlyModelViewSet):
    """Lectura de Notificaciones (solo GET)."""

    queryset = Notificacion.objects.all()
    serializer_class = NotificacionSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    # NUEVO: filtrar por usuario=? usando tu modelo Usuario
    def get_queryset(self):
        qs = super().get_queryset().order_by('-fecha_envio')
        usuario_id = self.request.query_params.get('usuario')
        if usuario_id:
            qs = qs.filter(usuarios__id_usuario=usuario_id)
        return qs

    # NUEVO: pasar id_usuario al serializer para calcular "leida"
    def get_serializer_context(self):
        context = super().get_serializer_context()
        usuario_id = self.request.query_params.get('usuario')
        if usuario_id:
            context['id_usuario'] = usuario_id
        return context

    @action(detail=True, methods=['post'])
    def marcar_leida(self, request, pk=None):
        """POST /notificaciones/{id}/marcar-leida/"""
        try:
            notificacion = self.get_object()
            NotificacionService.marcar_como_leida(
                request.user.id,  # esto lo revisamos luego si queremos mapear User→Usuario
                notificacion.id_notificacion
            )
            return Response({"message": "Notificación marcada como leída"},
                            status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response({"error": "Notificación no encontrada"},
                            status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['post'])
    def enviar_masiva(self, request):

        """
        POST /notificaciones/enviar-masiva/
        Body: {"ids_usuarios":[1,2,3], "tipo_notificacion":"EVENTO_CREADO", "mensaje":"Se creó un nuevo evento"}
        """
        try:
            ser = EnviarNotificacionSerializer(data=request.data)
            ser.is_valid(raise_exception=True)
            notif = NotificacionService.enviar_notificacion(
                ser.validated_data['ids_usuarios'],
                ser.validated_data['tipo_notificacion'],
                ser.validated_data['mensaje']
            )
            return Response(NotificacionSerializer(notif).data, status=status.HTTP_201_CREATED)
        except (ValidationError, DRFValidationError) as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
