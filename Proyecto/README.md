# Hola Mundo — Django + MySQL

Repositorio con un **ejemplo mínimo** para levantar una aplicación Django que muestra el detalle de un "Grupo" usando MySQL como base de datos. Incluye instrucciones para ejecutar con Docker y comandos útiles para desarrollo local.

## Estructura sugerida
```
.
├── docker-compose.yml
├── backend/                 # Proyecto Django
│   ├── manage.py
│   └── project/
│       └── __init__.py      # aquí puede ir `pymysql.install_as_MySQLdb()`
└── requirements.txt
```

## Requisitos
- Docker y Docker Compose (recomendado).
- Alternativa sin Docker: Python 3.9+, virtualenv y MySQL 8.0 accesible.
- Puerto por defecto de la app: `8000`.

## Variables de entorno (usadas por docker / Django)
- `DB_HOST` (ej.: `db`)
- `DB_NAME` (ej.: `holamundo_db`)
- `DB_USER` (ej.: `hmuser`)
- `DB_PASSWORD` (ej.: `hmpass`)

> **Nota:** Nunca guardes credenciales en el repositorio. Usa `.env` o un gestor de secretos.

## Instrucciones rápidas (con Docker)

1. Construir y levantar los servicios:
```bash
docker-compose up --build -d
```

2. Ver logs del backend:
```bash
docker-compose logs -f web
```

3. Aplicar migraciones:
```bash
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate
```

4. Crear datos de prueba (ejemplo):
```bash
docker-compose exec web python manage.py shell
```
Dentro del shell:
```python
from grupos.models import Grupo

grupo = Grupo(
    id_grupo=1,
    nombre_grupo="Club de Desarrollo Web UNAL",
    area_interes="Tecnología",
    tipo_grupo="Semillero",
    correo_grupo="club.web@unal.edu.co",
    descripcion="Primer grupo de prueba para el Hola Mundo"
)
grupo.save()
exit()
```

5. Abrir en el navegador:
```
http://localhost:8000
```

## Alternativa sin Docker (local)
1. Crear y activar un entorno virtual:
```bash
python -m venv venv
source venv/bin/activate   # Linux / macOS
venv\Scripts\activate      # Windows (PowerShell)
```
2. Instalar dependencias:
```bash
pip install -r requirements.txt
```
3. Configurar variables de entorno para la conexión a MySQL y ejecutar migraciones como arriba.

## Problemas comunes
- **Errores de driver MySQL:** Si recibes errores relacionados con el conector, instala `pymysql` y añade en `backend/project/__init__.py`:
```python
import pymysql
pymysql.install_as_MySQLdb()
```
- **DB no accesible:** Revisa `docker-compose logs db` y `docker-compose logs web`. Asegúrate de que el contenedor de la base de datos esté sano y de que las credenciales coincidan.
- **Cambios no vistos en desarrollo:** Asegúrate de montar el volumen `./backend:/code` en docker-compose para reflejar cambios sin reconstruir la imagen.

## Buenas prácticas (resumen)
- No usar `runserver` en producción; emplear Gunicorn/uWSGI detrás de Nginx.
- Guardar archivos grandes (logos, imágenes) fuera de la base de datos (S3, MinIO o filesystem).
- Usar variables de entorno y gestores de secretos para credenciales.
- Mantener backups y probar migraciones en un entorno de staging antes de producción.

## Dependencias sugeridas (`requirements.txt`)
```
Django>=4.2,<5
pymysql>=1.0
cryptography>=3.0
```

## Licencia
Añade la licencia que prefieras (por ejemplo, MIT) o elimina esta sección si no aplica.

## Contribuciones
Si quieres mejorar este repo, abre un *issue* o un *pull request* con los cambios propuestos. Gracias por colaborar.
