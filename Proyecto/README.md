# Hola Mundo - Django + MySQL (tutorial para Punto 1)

Este repositorio contiene un **esqueleto mínimo** para el Punto 1 (Hola Mundo) usando **Python + Django** y **MySQL** vía Docker Compose.

## ¿Qué incluye?
- `docker-compose.yml` para MySQL y el servicio web Django.
- `backend/` con Dockerfile, `manage.py`, proyecto Django y la app `grupos`.
- `setup.sh` para construir y levantar los servicios.
- `patterns.md` documentación de Singleton y Observer (solo documentados).

## Pasos rápidos para ejecutar (Linux/macOS)
1. Tener Docker y docker-compose instalados.
2. Desde la raíz del proyecto (donde está `docker-compose.yml`):

```bash
chmod +x setup.sh
./setup.sh
```

3. Abrir `http://localhost:8000/` (muestra `Grupo` con `id=1` si existe).
4. Para crear datos desde el contenedor web:
```bash
docker-compose exec web python manage.py shell
```
Dentro del shell de Django, puede ejecutar:

```py
from grupos.models import Grupo
g = Grupo(id_grupo=1, nombre_grupo="Tuna Ejemplo NL", descripcion="Hola mundo desde la tuna.", correo_grupo="tuna@ejemplo.edu")
g.save()
exit()
```

5. Refrescar `http://localhost:8000/` para ver el registro.

## Notas
- El proyecto es un esqueleto para el Punto 1. No incluye autenticación ni patrones implementados (solo documentados en `patterns.md`).
- Si al construir la imagen `mysqlclient` falla, asegúrate de que el sistema tenga las dependencias de compilación (el Dockerfile ya instala `default-libmysqlclient-dev` y `build-essential`).

