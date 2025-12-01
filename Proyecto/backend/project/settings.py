"""
Configuración de Django - ÁgoraUN

Basado en Django 4.2 + DRF
"""

from pathlib import Path

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-your-secret-key-change-this-in-production'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
ALLOWED_HOSTS = ['*', 'localhost', '127.0.0.1']

# ===========================================================================
# APLICACIONES INSTALADAS
# ===========================================================================

INSTALLED_APPS = [
    # Django apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party apps
    'rest_framework',                    # Django REST Framework
    'rest_framework.authtoken',          # Tokens de autenticación
    'corsheaders',                       # CORS para comunicación frontend-backend
    'drf_spectacular',                   # Documentación Swagger/OpenAPI

    # Nuestras apps
    'grupos',
]

# ===========================================================================
# MIDDLEWARE
# ===========================================================================

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # CORS debe estar arriba
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'project.urls'

# ===========================================================================
# PLANTILLAS
# ===========================================================================

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'project.wsgi.application'

# ===========================================================================
# BASE DE DATOS - MySQL
# ===========================================================================

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'proyecto_agoraun',
        'USER': 'hmuser',
        'PASSWORD': 'hmpass',
        'HOST': 'db',  # Nombre del servicio en docker-compose
        'PORT': '3306',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'charset': 'utf8mb4',
        }
    }
}

# ===========================================================================
# VALIDACIÓN DE CONTRASEÑAS
# ===========================================================================

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# ===========================================================================
# INTERNACIONALIZACIÓN
# ===========================================================================

LANGUAGE_CODE = 'es-es'
TIME_ZONE = 'America/Bogota'
USE_I18N = True
USE_TZ = True

# ===========================================================================
# ARCHIVOS ESTÁTICOS Y MEDIA
# ===========================================================================

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ===========================================================================
# CONFIGURACIÓN DE REST FRAMEWORK
# ===========================================================================

REST_FRAMEWORK = {
    # Paginación
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,

    # Autenticación
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'grupos.auth.UsuarioTokenAuthentication',            # <-- nuestra clase
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],

    # Permisos
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],

    # Filtrado y búsqueda
    'DEFAULT_FILTER_BACKENDS': [
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],

    # Documentación
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# ===========================================================================
# DOCUMENTACIÓN API (Swagger/OpenAPI)
# ===========================================================================

SPECTACULAR_SETTINGS = {
    'TITLE': 'ÁgoraUN API',
    'DESCRIPTION': 'API REST para gestión de grupos y eventos estudiantiles',
    'VERSION': '1.0.0',
    'SERVE_PERMISSIONS': ['rest_framework.permissions.AllowAny'],
}

# ===========================================================================
# CORS (Cross-Origin Resource Sharing)
# ===========================================================================

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",      # React desarrollo
    "http://localhost:5173",      # Vue/Vite desarrollo
    "http://localhost:4200",      # Angular desarrollo
    "http://localhost",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5500",
    "http://localhost:5500",
]

CORS_ALLOW_CREDENTIALS = True

# ===========================================================================
# EMAIL (para notificaciones)
# ===========================================================================

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # Consola (desarrollo)
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'  # SMTP (producción)
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'tu-email@gmail.com'
EMAIL_HOST_PASSWORD = 'tu-contraseña-app'

# ===========================================================================
# LOGGING
# ===========================================================================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'django.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
        },
        'grupos': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
        },
    },
}

# ===========================================================================
# CLAVE PRIMARIA POR DEFECTO
# ===========================================================================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Configuración CORS para desarrollo
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True
