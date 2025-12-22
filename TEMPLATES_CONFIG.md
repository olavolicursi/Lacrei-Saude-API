# 🎨 Templates de Configuração

> Templates prontos para copiar e colar nas configurações do projeto

## 📄 pyproject.toml (completo)

```toml
[tool.poetry]
name = "lacrei-saude-api"
version = "0.1.0"
description = "API RESTful de Gerenciamento de Consultas Médicas"
authors = ["Seu Nome <seu.email@example.com>"]
license = "MIT"
readme = "README.md"

[tool.poetry.dependencies]
python = "^3.11"
django = "^5.0"
djangorestframework = "^3.14"
psycopg2-binary = "^2.9"
python-decouple = "^3.8"
django-cors-headers = "^4.3"
djangorestframework-simplejwt = "^5.3"
gunicorn = "^21.2"
drf-spectacular = "^0.27"

[tool.poetry.group.dev.dependencies]
pytest = "^7.4"
pytest-django = "^4.7"
pytest-cov = "^4.1"
black = "^23.12"
flake8 = "^7.0"
isort = "^5.13"
ipython = "^8.19"
django-extensions = "^3.2"

[tool.black]
line-length = 100
target-version = ['py311']
include = '\.pyi?$'
exclude = '''
/(
    \.git
  | \.venv
  | migrations
  | __pycache__
)/
'''

[tool.isort]
profile = "black"
line_length = 100
skip_glob = ["*/migrations/*"]

[tool.pytest.ini_options]
DJANGO_SETTINGS_MODULE = "config.settings"
python_files = ["tests.py", "test_*.py", "*_tests.py"]
addopts = "--cov=. --cov-report=html --cov-report=term-missing"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
```

---

## ⚙️ config/settings.py (segmentos importantes)

### Imports e Configurações Base

```python
from pathlib import Path
from decouple import config
from datetime import timedelta
import os

BASE_DIR = Path(__file__).resolve().parent.parent

# Security
SECRET_KEY = config('DJANGO_SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='').split(',')

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third party apps
    'rest_framework',
    'corsheaders',
    'rest_framework_simplejwt',
    'drf_spectacular',

    # Local apps
    'professionals',
    'appointments',
    'core',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # CORS - deve vir cedo
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 'core.middleware.SecurityLoggingMiddleware',  # Custom - adicionar depois
]

ROOT_URLCONF = 'config.urls'

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

WSGI_APPLICATION = 'config.wsgi.application'
```

### Database

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'),
        'PORT': config('DB_PORT', default='5432'),
    }
}
```

### Password Validation

```python
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]
```

### Internationalization

```python
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True
```

### Static Files

```python
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

### Default Primary Key

```python
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
```

### REST Framework

```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour',
    },
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
}

# Em desenvolvimento, adicionar BrowsableAPIRenderer
if DEBUG:
    REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'].append(
        'rest_framework.renderers.BrowsableAPIRenderer'
    )
```

### JWT Settings

```python
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=config('JWT_ACCESS_TOKEN_LIFETIME', default=60, cast=int)),
    'REFRESH_TOKEN_LIFETIME': timedelta(minutes=config('JWT_REFRESH_TOKEN_LIFETIME', default=1440, cast=int)),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
}
```

### CORS Settings

```python
CORS_ALLOWED_ORIGINS = config('CORS_ALLOWED_ORIGINS', default='').split(',')
CORS_ALLOW_CREDENTIALS = True
```

### DRF Spectacular (Swagger)

```python
SPECTACULAR_SETTINGS = {
    'TITLE': 'Lacrei Saúde API',
    'DESCRIPTION': 'API RESTful de Gerenciamento de Consultas Médicas',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
}
```

### Logging

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'api.log',
            'maxBytes': 1024 * 1024 * 15,  # 15MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'security_file': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'security.log',
            'maxBytes': 1024 * 1024 * 15,
            'backupCount': 10,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
        'security': {
            'handlers': ['security_file', 'console'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}

# Criar diretório de logs se não existir
os.makedirs(BASE_DIR / 'logs', exist_ok=True)
```

### Security Settings (Production)

```python
if not DEBUG:
    # HTTPS
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

    # Security Headers
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
```

---

## 🌐 config/urls.py

```python
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

# Imports dos viewsets (adicionar depois que criar)
# from professionals.views import ProfessionalViewSet
# from appointments.views import AppointmentViewSet

router = DefaultRouter()
# router.register('professionals', ProfessionalViewSet, basename='professional')
# router.register('appointments', AppointmentViewSet, basename='appointment')

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # API v1
    path('api/v1/', include(router.urls)),

    # Authentication
    path('api/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

# Servir arquivos estáticos em desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Customizar admin
admin.site.site_header = "Lacrei Saúde Admin"
admin.site.site_title = "Lacrei Saúde"
admin.site.index_title = "Gerenciamento da API"
```

---

## 📝 pytest.ini

```ini
[pytest]
DJANGO_SETTINGS_MODULE = config.settings
python_files = tests.py test_*.py *_tests.py
python_classes = Test*
python_functions = test_*
addopts =
    --cov=.
    --cov-report=html
    --cov-report=term-missing
    --cov-report=xml
    --strict-markers
    --disable-warnings
testpaths = tests
```

---

## 🐳 .dockerignore

```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
.venv
pip-log.txt
pip-delete-this-directory.txt
.tox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
.hypothesis/
.pytest_cache/

# Django
*.log
db.sqlite3
db.sqlite3-journal
/staticfiles/
/media/

# Environment
.env
.env.local

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Git
.git/
.gitignore

# Documentation
*.md
docs/

# Tests
htmlcov/
.coverage

# Build
dist/
build/
*.egg-info/
```

---

## 📋 .flake8

```ini
[flake8]
max-line-length = 100
exclude =
    .git,
    __pycache__,
    */migrations/*,
    */settings.py,
    venv,
    .venv,
    env,
    ENV
ignore =
    E203,  # whitespace before ':'
    E266,  # too many leading '#' for block comment
    E501,  # line too long (handled by Black)
    W503,  # line break before binary operator
per-file-ignores =
    __init__.py:F401
```

---

## 🔧 setup.cfg

```ini
[metadata]
name = lacrei-saude-api
version = 0.1.0
description = API RESTful de Gerenciamento de Consultas Médicas
author = Seu Nome
author_email = seu.email@example.com

[options]
python_requires = >=3.11
include_package_data = True

[coverage:run]
source = .
omit =
    */migrations/*
    */tests/*
    */test_*.py
    */__pycache__/*
    */venv/*
    */env/*
    manage.py
    config/wsgi.py
    config/asgi.py

[coverage:report]
precision = 2
show_missing = True
skip_covered = False
exclude_lines =
    pragma: no cover
    def __repr__
    def __str__
    raise AssertionError
    raise NotImplementedError
    if __name__ == .__main__.:
    if TYPE_CHECKING:
```

---

## 📂 Criar estrutura de diretórios

```powershell
# Windows PowerShell
New-Item -ItemType Directory -Force -Path logs, staticfiles, media, templates
```

---

## ✅ Checklist de Configuração

Após copiar e configurar tudo acima:

- [ ] pyproject.toml configurado
- [ ] config/settings.py atualizado
- [ ] config/urls.py atualizado
- [ ] pytest.ini criado
- [ ] .dockerignore criado
- [ ] .flake8 criado
- [ ] setup.cfg criado
- [ ] Diretórios logs/, staticfiles/, media/ criados
- [ ] .env configurado com SECRET_KEY gerada

**Tudo pronto? Faça o primeiro commit!**

```powershell
git add .
git commit -m "chore: configuração inicial do projeto"
git push origin main
```

---

## 🎯 Próximo Passo

Agora vá para **[CHECKLIST.md](CHECKLIST.md) - Fase 2** e comece a implementar os models!
