# backend/grupos/views.py

from django.shortcuts import redirect
from django.contrib import messages
from django.db.models import Count
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views import View

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from rest_framework.serializers import Serializer, CharField, EmailField

from project.singleton import config_manager
from .singletons import grupo_cache

from .models import (
    Participacion, ParticipacionUsuario, Usuario, Grupo, Evento,
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


# -------------------------------------------------------------------
# AUTH (Register / Login / Logout)
# -------------------------------------------------------------------

from .auth import UsuarioAuthToken  # import del nuevo módulo de auth


class RegisterSerializer(Serializer):
    nombre_usuario = CharField(max_length=60)
    apellido = CharField(max_length=60)
    correo = EmailField()
    password = CharField(min_length=8)


class LoginSerializer(Serializer):
    correo = EmailField()
    password = CharField()


class AuthView(viewsets.ViewSet):
    """
    ViewSet mínimo para manejo de registro/login con validación de dominio @unal.edu.co
    Endpoints:
      POST /grupos/auth/register/  -> register
      POST /grupos/auth/login/     -> login
      POST /grupos/auth/logout/    -> logout
    """
    permission_classes = [AllowAny]
    parser_classes = [JSONParser]

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def register(self, request):
        ser = RegisterSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data
        correo = data['correo'].lower().strip()

        # Validar dominio UNAL
        if not correo.endswith('@unal.edu.co'):
            return Response({'error': 'Registro permitido solo con correo @unal.edu.co'}, status=status.HTTP_400_BAD_REQUEST)

        if Usuario.objects.filter(correo_usuario__iexact=correo).exists():
            return Response({'error': 'Ya existe una cuenta con ese correo'}, status=status.HTTP_400_BAD_REQUEST)

        usuario = Usuario(
            nombre_usuario=data['nombre_usuario'].strip(),
            apellido=data['apellido'].strip(),
            correo_usuario=correo
        )
        usuario.set_password(data['password'])
        usuario.save()

        token = UsuarioAuthToken.create(usuario)

        return Response({
            'message': 'Registrado correctamente',
            'usuario': {
                'id_usuario': usuario.id_usuario,
                'nombre': usuario.nombre_usuario,
                'apellido': usuario.apellido,
                'correo': usuario.correo_usuario
            },
            'token': token.key
        }, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def login(self, request):
        ser = LoginSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data
        correo = data['correo'].lower().strip()

        try:
            usuario = Usuario.objects.get(correo_usuario__iexact=correo)
        except Usuario.DoesNotExist:
            return Response({'error': 'Credenciales inválidas'}, status=status.HTTP_401_UNAUTHORIZED)

        if not usuario.check_password(data['password']):
            return Response({'error': 'Credenciales inválidas'}, status=status.HTTP_401_UNAUTHORIZED)

        # crear token nuevo cada login (o reutilizar si prefieres)
        token = UsuarioAuthToken.create(usuario)
        return Response({
            'message': 'Login correcto',
            'usuario': {
                'id_usuario': usuario.id_usuario,
                'nombre': usuario.nombre_usuario,
                'apellido': usuario.apellido,
                'correo': usuario.correo_usuario
            },
            'token': token.key
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def logout(self, request):
        """
        Borra el token que fue usado en la petición (logout).
        request.auth será la instancia UsuarioAuthToken (gracias a nuestra auth class).
        """
        token = request.auth
        if token:
            try:
                token.delete()
            except Exception:
                pass
        return Response({'message': 'Logged out'}, status=status.HTTP_200_OK)


# -------------------------------------------------------------------
# PERFIL (HTML)
# -------------------------------------------------------------------

def perfil_usuario(request, usuario_id):
    """Página de perfil usando la estructura existente."""
    usuario = get_object_or_404(Usuario, id_usuario=usuario_id)

    grupos_usuario = UsuarioGrupo.objects.filter(usuario=usuario).select_related('grupo')
    areas_interes = {ug.grupo.area_interes for ug in grupos_usuario if ug.grupo.area_interes}

    participaciones_del_usuario = Participacion.objects.filter(
        usuarios=usuario
    ).select_related('evento__grupo')

    stats = {
        'total_grupos': grupos_usuario.count(),
        'total_eventos': participaciones_del_usuario.count(),
        'eventos_confirmados': participaciones_del_usuario.filter(
            estado_participacion='CONFIRMADO'
        ).count(),
    }

    context = {
        'usuario': usuario,
        'grupos_usuario': grupos_usuario,
        'areas_interes': sorted(list(areas_interes)),
        'participaciones': participaciones_del_usuario,
        'stats': stats,
    }

    return render(request, 'perfil/completo.html', context)


def explorar_intereses(request):
    """Página para explorar todas las áreas de interés disponibles."""
    grupos_por_interes = (
        Grupo.objects.values('area_interes')
        .annotate(total_grupos=Count('id_grupo'))
        .order_by('area_interes')
    )

    intereses_populares = []
    for interes in grupos_por_interes:
        if interes['area_interes']:
            grupos = Grupo.objects.filter(area_interes=interes['area_interes'])[:5]
            intereses_populares.append({
                'area': interes['area_interes'],
                'total_grupos': interes['total_grupos'],
                'grupos_destacados': grupos
            })

    return render(request, 'perfil/explorar_intereses.html', {
        'intereses_populares': intereses_populares
    })


def editar_perfil(request, usuario_id):
    """Vista para editar el perfil del usuario."""
    usuario = get_object_or_404(Usuario, id_usuario=usuario_id)

    if request.method == 'POST':
        nombre = request.POST.get('nombre_usuario')
        apellido = request.POST.get('apellido')
        correo = request.POST.get('correo_usuario')

        if nombre and apellido and correo:
            usuario.nombre_usuario = nombre
            usuario.apellido = apellido
            usuario.correo_usuario = correo
            usuario.save()

            messages.success(request, 'Perfil actualizado correctamente!')
            return redirect('perfil_usuario', usuario_id=usuario.id_usuario)
        messages.error(request, 'Por favor completa todos los campos obligatorios')

    return render(request, 'perfil/editar.html', {'usuario': usuario})


def actualizar_intereses(request, usuario_id):
    """Vista para actualizar intereses del usuario."""
    usuario = get_object_or_404(Usuario, id_usuario=usuario_id)

    if request.method == 'POST':
        messages.success(request, 'Intereses actualizados correctamente!')
        return redirect('perfil_usuario', usuario_id=usuario.id_usuario)

    return render(request, 'perfil/editar_intereses.html', {'usuario': usuario})
