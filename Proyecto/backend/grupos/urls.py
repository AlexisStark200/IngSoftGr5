"""
URLs - AgoraUN
Enrutamiento de la API REST

Usa Django REST Framework Routers para generar automáticamente
todos los endpoints CRUD.

Documentación: http://localhost:8000/api/docs/
"""
# grupos/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    GrupoViewSet,
    EventoViewSet,
    UsuarioViewSet,
    ComentarioViewSet,
    NotificacionViewSet,
    AuthView,
    perfil_usuario,
    explorar_intereses,
    editar_perfil,
    actualizar_intereses,
    # GrupoDetailView,  # si usas vistas de detalle clásicas
    # ConfigView,
)

router = DefaultRouter()
router.register(r"grupos", GrupoViewSet, basename="grupo")
router.register(r"eventos", EventoViewSet, basename="evento")
router.register(r"usuarios", UsuarioViewSet, basename="usuario")
router.register(r"comentarios", ComentarioViewSet, basename="comentario")
router.register(r"notificaciones", NotificacionViewSet, basename="notificacion")

urlpatterns = [
    path('perfil/<int:usuario_id>/', perfil_usuario, name='perfil_usuario'),
    path('perfil/<int:usuario_id>/editar/', editar_perfil, name='editar_perfil'),
    path('perfil/<int:usuario_id>/intereses/', actualizar_intereses, name='actualizar_intereses'),
    path('intereses/', explorar_intereses, name='explorar_intereses'),
    path("", include(router.urls)),
    path("auth/register/", AuthView.as_view({"post": "register"}), name="auth-register"),
    path("auth/login/",    AuthView.as_view({"post": "login"}),    name="auth-login"),
    path("auth/logout/",   AuthView.as_view({"post": "logout"}),   name="auth-logout"),
]
