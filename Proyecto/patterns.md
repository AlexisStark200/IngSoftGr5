# Patrones (documentación mínima) — Punto 1

## Singleton
**Qué es:** El patrón Singleton asegura que una clase tenga una única instancia y ofrece un punto de acceso global.  
**En el contexto de Django/this proyecto:** Django ORM maneja conexiones y no se requiere un Singleton manual para la conexión a la BD. Si el enunciado pide documentar Singleton, se sugiere:
- Documentarlo conceptualmente: un objeto `Repository` único por entidad que actúe como fachada al acceso a datos.
- No implementarlo para la conexión del ORM (Django ya gestiona pooling/connections).

**Ejemplo conceptual (no implementado):**
- `DatabaseSingleton` que crea/configura un motor y lo devuelve en `get_instance()`.

## Observer
**Qué es:** El patrón Observer permite que objetos (observadores) se suscriban a eventos emitidos por un sujeto.  
**En Django:** las **signals** (`post_save`, `pre_delete`) son el equivalente natural.  
**Recomendación:** documentar que, si se necesitara notificar otras partes del sistema cuando un `Grupo` cambia, usar `post_save` en lugar de implementar un sistema Observer desde cero.

**Ejemplo Django (documentado solo):**
```py
from django.db.models.signals import post_save
from django.dispatch import receiver
from grupos.models import Grupo

@receiver(post_save, sender=Grupo)
def on_grupo_saved(sender, instance, created, **kwargs):
    if created:
        # acción del observador: enviar notificación, actualizar cache...
        pass
```
