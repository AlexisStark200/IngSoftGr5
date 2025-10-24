from django.contrib import admin
from django.urls import include, path
from grupos.views import grupo_detail

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('grupos.urls')),
    path('', grupo_detail, name='home'),
    path('grupo/<int:pk>/', grupo_detail, name='grupo-detail'),
]
