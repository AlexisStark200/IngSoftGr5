"""
URLs - ÁgoraUN
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
    # path("grupo/<int:grupo_id>/", GrupoDetailView.as_view(), name="grupo_detail"),  # opcional
    # path("config/", ConfigView.as_view(), name="config"),  # opcional
    path("", include(router.urls)),  # ← ¡esto es lo que faltaba!
]

