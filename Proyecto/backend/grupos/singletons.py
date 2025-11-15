import logging
from django.core.cache import cache

from .models import Grupo

logger = logging.getLogger(__name__)


class GrupoCacheManager:
    """
    Singleton para cache específico de grupos
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._cache_prefix = "grupo_"
            logger.info("GrupoCacheManager Singleton creado")
        return cls._instance

    def get_grupo(self, grupo_id):
        """Obtener grupo desde cache o BD"""
        cache_key = f"{self._cache_prefix}{grupo_id}"
        grupo_data = cache.get(cache_key)

        if grupo_data is None:
            # Simular carga desde BD
            try:
                grupo = Grupo.objects.get(id_grupo=grupo_id)
                grupo_data = {
                    'id': grupo.id_grupo,
                    'nombre': grupo.nombre_grupo,
                    'area': grupo.area_interes
                }
                # Guardar en cache por 15 minutos
                cache.set(cache_key, grupo_data, 900)
                logger.info("Grupo %s cargado desde BD y cacheado", grupo_id)
            except Grupo.DoesNotExist:
                return None

        return grupo_data

    def invalidate_grupo(self, grupo_id):
        """Invalidar cache de un grupo"""
        cache_key = f"{self._cache_prefix}{grupo_id}"
        cache.delete(cache_key)
        logger.info("Cache de grupo %s invalidado", grupo_id)

    def get_estadisticas(self):
        """Obtener estadísticas de cache"""
        return {
            'total_grupos_cache': len([key for key in cache.keys() if key.startswith(self._cache_prefix)]),
            'cache_prefix': self._cache_prefix
        }


# Instancia global
grupo_cache = GrupoCacheManager()
