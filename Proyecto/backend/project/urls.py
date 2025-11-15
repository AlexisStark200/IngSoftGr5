from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

def home(request):
    return JsonResponse({
        'message': 'Bienvenido a ÁgoraUN API', 
        'status': 'active',
        'version': '1.0.0'
    })

urlpatterns = [
    path('', home, name='home'),
    path('admin/', admin.site.urls),
    path('api/', include('grupos.urls')),  # ← Incluye las rutas de grupos
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]