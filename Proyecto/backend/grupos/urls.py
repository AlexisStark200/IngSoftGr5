from django.urls import path
from . import views

urlpatterns = [
    path('grupo/<int:grupo_id>/', views.GrupoDetailView.as_view(), name='grupo_detail'),
    path('config/', views.ConfigView.as_view(), name='config'),
]
