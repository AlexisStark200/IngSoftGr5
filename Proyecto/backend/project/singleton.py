import logging
from django.core.cache import cache

logger = logging.getLogger(__name__)


class ConfigManager:
    """
    Singleton para gestión de configuración de la aplicación
    Caso REAL donde SÍ es útil
    """
    _instance = None
    _config_data = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_initial_config()
            logger.info("ConfigManager Singleton creado")
        return cls._instance

    def _load_initial_config(self):
        """Cargar configuración inicial"""
        self._config_data = {
            'app_name': 'Sistema de Grupos UN',
            'version': '1.0.0',
            'max_grupos_usuario': 5,
            'dias_expiracion_evento': 30,
            'notificaciones_activas': True,
        }

    def get(self, key, default=None):
        """Obtener valor de configuración"""
        cache_key = f"config_{key}"
        cached_value = cache.get(cache_key)
        if cached_value is not None:
            return cached_value

        value = self._config_data.get(key, default)
        cache.set(cache_key, value, 3600)
        return value

    def set(self, key, value):
        """Establecer valor de configuración"""
        self._config_data[key] = value
        cache_key = f"config_{key}"
        cache.set(cache_key, value, 3600)
        logger.info("Config: %s = %s", key, value)

    def get_all(self):
        """Obtener toda la configuración"""
        return self._config_data.copy()

    def reset(self):
        """Resetear a configuración inicial"""
        self._load_initial_config()
        for key in self._config_data:
            cache.delete(f"config_{key}")
        logger.info("ConfigManager reseteado")


config_manager = ConfigManager()
