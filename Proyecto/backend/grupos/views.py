from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views import View

from project.singleton import config_manager
from .models import Grupo
from .singletons import grupo_cache


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

        return JsonResponse({'error': 'Key y value requeridos'}, status=400)
    