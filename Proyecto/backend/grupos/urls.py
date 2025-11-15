"""
URLs - ÁgoraUN
Enrutamiento de la API REST

Usa Django REST Framework Routers para generar automáticamente
todos los endpoints CRUD.

Documentación: http://localhost:8000/api/docs/
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    GrupoViewSet,
    EventoViewSet,
    UsuarioViewSet,
    ComentarioViewSet,
    NotificacionViewSet
)

# Crear router y registrar ViewSets
router = DefaultRouter()

# Registrar cada ViewSet
# Esto genera automáticamente:
# - GET    /grupos/
# - POST   /grupos/
# - GET    /grupos/{id}/
# - PUT    /grupos/{id}/
# - DELETE /grupos/{id}/
# etc...

router.register(r'grupos', GrupoViewSet, basename='grupo')
router.register(r'eventos', EventoViewSet, basename='evento')
router.register(r'usuarios', UsuarioViewSet, basename='usuario')
router.register(r'comentarios', ComentarioViewSet, basename='comentario')
router.register(r'notificaciones', NotificacionViewSet, basename='notificacion')

# Incluir rutas del router
urlpatterns = [
    path('grupo/<int:grupo_id>/', views.GrupoDetailView.as_view(), name='grupo_detail'),
    path('config/', views.ConfigView.as_view(), name='config'),
]
