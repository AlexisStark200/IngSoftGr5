from django.test import TestCase
from .singletons import grupo_cache
from project.singleton import config_manager

class SingletonTest(TestCase):
    def test_singleton_instances(self):
        """Verificar que siempre es la misma instancia"""
        cache1 = grupo_cache
        cache2 = grupo_cache
        self.assertIs(cache1, cache2)  # Mismo objeto en memoria
        
        config1 = config_manager
        config2 = config_manager
        self.assertIs(config1, config2)