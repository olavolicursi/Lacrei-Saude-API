# 📋 Plano de Implementação - API Lacrei Saúde

## 🎯 Visão Geral

API RESTful de Gerenciamento de Consultas Médicas com foco em qualidade, segurança e boas práticas.

---

## 📅 Cronograma de Implementação

### **FASE 1: Configuração do Ambiente** (Prioridade: ALTA)

**Tempo estimado: 2-4 horas**

#### 1.1 Inicialização do projeto Python

- [ ] Instalar Poetry: `pip install poetry`
- [ ] Inicializar projeto: `poetry init`
- [ ] Configurar Python 3.13+ no pyproject.toml

#### 1.2 Instalação de dependências base

```bash
poetry add django djangorestframework
poetry add psycopg2-binary python-decouple
poetry add django-cors-headers djangorestframework-simplejwt
poetry add --group dev pytest pytest-django pytest-cov
poetry add --group dev black flake8 isort pylint
```

#### 1.3 Criar projeto Django

```bash
poetry run django-admin startproject config .
poetry run python manage.py startapp professionals
poetry run python manage.py startapp appointments
```

#### 1.4 Estrutura de pastas

```
Lacrei-Saude-API/
├── config/                 # Configurações do Django
├── professionals/          # App de profissionais
├── appointments/           # App de consultas
├── core/                   # Utilidades compartilhadas
├── tests/                  # Testes organizados
├── docker/                 # Configurações Docker
├── .github/workflows/      # GitHub Actions
├── docs/                   # Documentação
├── .env.example           # Variáveis de ambiente
├── pyproject.toml         # Dependências Poetry
├── Dockerfile
├── docker-compose.yml
└── README.md
```

#### 1.5 Arquivos de configuração

- [x] Criar `.env.example` com variáveis necessárias
- [x] Configurar `.gitignore` adequado
- [x] Setup do `settings.py` com variáveis de ambiente

---

### **FASE 2: Modelagem e Banco de Dados** (Prioridade: ALTA)

**Tempo estimado: 3-4 horas**

#### 2.1 Modelo de Profissionais

```python
# professionals/models.py
from django.db import models
from django.core.validators import RegexValidator

class Professional(models.Model):
    PROFESSION_CHOICES = [
        ('MEDICO', 'Médico'),
        ('PSICOLOGO', 'Psicólogo'),
        ('NUTRICIONISTA', 'Nutricionista'),
        # ... outros
    ]

    nome_social = models.CharField(max_length=200)
    profissao = models.CharField(max_length=50, choices=PROFESSION_CHOICES)
    registro_profissional = models.CharField(max_length=50, unique=True)

    # Endereço
    cep = models.CharField(max_length=9)
    logradouro = models.CharField(max_length=200)
    numero = models.CharField(max_length=10)
    complemento = models.CharField(max_length=100, blank=True)
    bairro = models.CharField(max_length=100)
    cidade = models.CharField(max_length=100)
    estado = models.CharField(max_length=2)

    # Contato
    telefone = models.CharField(max_length=15)
    email = models.EmailField(unique=True)

    # Metadados
    ativo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['nome_social']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['registro_profissional']),
        ]
```

#### 2.2 Modelo de Consultas

```python
# appointments/models.py
from django.db import models
from professionals.models import Professional

class Appointment(models.Model):
    STATUS_CHOICES = [
        ('AGENDADA', 'Agendada'),
        ('CONFIRMADA', 'Confirmada'),
        ('REALIZADA', 'Realizada'),
        ('CANCELADA', 'Cancelada'),
    ]

    professional = models.ForeignKey(
        Professional,
        on_delete=models.PROTECT,
        related_name='appointments'
    )
    data_hora = models.DateTimeField()
    duracao_minutos = models.PositiveIntegerField(default=60)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='AGENDADA'
    )

    # Paciente (simplificado)
    paciente_nome = models.CharField(max_length=200)
    paciente_email = models.EmailField()
    paciente_telefone = models.CharField(max_length=15)

    observacoes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-data_hora']
        indexes = [
            models.Index(fields=['professional', 'data_hora']),
            models.Index(fields=['status']),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(duracao_minutos__gte=15),
                name='duracao_minima_15min'
            )
        ]
```

#### 2.3 Migrations

- [x] `poetry run python manage.py makemigrations`
- [x] `poetry run python manage.py migrate`
- [x] Criar dados de teste (fixtures ou script)

---

### **FASE 3: Implementação do CRUD** (Prioridade: ALTA)

**Tempo estimado: 6-8 horas**

#### 3.1 Serializers

```python
# professionals/serializers.py
from rest_framework import serializers
from .models import Professional

class ProfessionalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Professional
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')

    def validate_email(self, value):
        # Validação customizada
        return value.lower()

    def validate_telefone(self, value):
        # Remover caracteres especiais e validar
        import re
        clean = re.sub(r'\D', '', value)
        if len(clean) < 10:
            raise serializers.ValidationError("Telefone inválido")
        return value
```

#### 3.2 ViewSets

```python
# professionals/views.py
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import Professional
from .serializers import ProfessionalSerializer

class ProfessionalViewSet(viewsets.ModelViewSet):
    queryset = Professional.objects.filter(ativo=True)
    serializer_class = ProfessionalSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['profissao', 'cidade', 'estado']
    search_fields = ['nome_social', 'email']
```

#### 3.3 URLs

```python
# config/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from professionals.views import ProfessionalViewSet
from appointments.views import AppointmentViewSet

router = DefaultRouter()
router.register('professionals', ProfessionalViewSet)
router.register('appointments', AppointmentViewSet)

urlpatterns = [
    path('api/v1/', include(router.urls)),
    path('api/auth/', include('rest_framework.urls')),
]
```

#### 3.4 Endpoints a implementar

- `GET /api/v1/professionals/` - Listar profissionais
- `POST /api/v1/professionals/` - Criar profissional
- `GET /api/v1/professionals/{id}/` - Detalhar profissional
- `PUT/PATCH /api/v1/professionals/{id}/` - Atualizar profissional
- `DELETE /api/v1/professionals/{id}/` - Deletar (soft delete)
- `GET /api/v1/appointments/` - Listar consultas
- `POST /api/v1/appointments/` - Criar consulta
- `GET /api/v1/appointments/{id}/` - Detalhar consulta
- `PUT/PATCH /api/v1/appointments/{id}/` - Atualizar consulta
- `GET /api/v1/appointments/?professional_id={id}` - Consultas por profissional

---

### **FASE 4: Segurança e Validações** (Prioridade: CRÍTICA)

**Tempo estimado: 4-6 horas**

#### 4.1 Autenticação JWT

```python
# config/settings.py
INSTALLED_APPS += ['rest_framework_simplejwt']

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour'
    }
}
```

#### 4.2 CORS

```python
INSTALLED_APPS += ['corsheaders']

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    # ... outros middlewares
]

# Staging/Dev
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "https://staging.lacrei.com",
]

# Produção - mais restritivo
if ENV == 'production':
    CORS_ALLOWED_ORIGINS = [
        "https://lacrei.com",
        "https://www.lacrei.com",
    ]
```

#### 4.3 Sanitização de inputs

```python
# core/validators.py
import bleach
from django.core.exceptions import ValidationError

def sanitize_html(value):
    """Remove tags HTML perigosas"""
    allowed_tags = []  # Nenhuma tag permitida
    return bleach.clean(value, tags=allowed_tags, strip=True)

def validate_no_sql_injection(value):
    """Verifica padrões suspeitos"""
    suspicious_patterns = [
        'DROP', 'DELETE', 'INSERT', 'UPDATE',
        '--', ';--', 'xp_', 'sp_'
    ]
    upper_value = value.upper()
    for pattern in suspicious_patterns:
        if pattern in upper_value:
            raise ValidationError(f"Entrada suspeita detectada")
```

#### 4.4 Logging

```python
# config/settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/api.log',
            'maxBytes': 1024*1024*15,  # 15MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'security_file': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/security.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
        'security': {
            'handlers': ['security_file'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}
```

#### 4.5 Middleware de segurança customizado

```python
# core/middleware.py
import logging

security_logger = logging.getLogger('security')

class SecurityLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Log de tentativas suspeitas
        if self._is_suspicious(request):
            security_logger.warning(
                f"Suspicious request from {request.META.get('REMOTE_ADDR')}: "
                f"{request.path}"
            )

        response = self.get_response(request)
        return response

    def _is_suspicious(self, request):
        # Implementar lógica de detecção
        return False
```

#### 4.6 Configurações de segurança Django

```python
# Security settings
SECURE_SSL_REDIRECT = True  # Produção
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Secrets
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')
DEBUG = os.getenv('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')
```

---

### **FASE 5: Testes Automatizados** (Prioridade: ALTA)

**Tempo estimado: 6-8 horas**

#### 5.1 Configuração de testes

```python
# pytest.ini
[pytest]
DJANGO_SETTINGS_MODULE = config.settings
python_files = tests.py test_*.py *_tests.py
addopts = --cov=. --cov-report=html --cov-report=term

# conftest.py
import pytest
from rest_framework.test import APIClient
from django.contrib.auth.models import User

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def authenticated_client(db):
    user = User.objects.create_user(
        username='testuser',
        password='testpass123'
    )
    client = APIClient()
    client.force_authenticate(user=user)
    return client

@pytest.fixture
def sample_professional(db):
    from professionals.models import Professional
    return Professional.objects.create(
        nome_social="Dr. João Silva",
        profissao="MEDICO",
        # ... outros campos
    )
```

#### 5.2 Testes de Profissionais

```python
# tests/test_professionals.py
import pytest
from rest_framework import status
from professionals.models import Professional

@pytest.mark.django_db
class TestProfessionalCRUD:

    def test_list_professionals(self, authenticated_client):
        response = authenticated_client.get('/api/v1/professionals/')
        assert response.status_code == status.HTTP_200_OK

    def test_create_professional(self, authenticated_client):
        data = {
            'nome_social': 'Dra. Maria Santos',
            'profissao': 'PSICOLOGO',
            'email': 'maria@example.com',
            # ... outros campos obrigatórios
        }
        response = authenticated_client.post(
            '/api/v1/professionals/',
            data
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert Professional.objects.count() == 1

    def test_create_professional_invalid_email(self, authenticated_client):
        data = {
            'nome_social': 'Dr. João',
            'email': 'invalid-email',
            # ...
        }
        response = authenticated_client.post(
            '/api/v1/professionals/',
            data
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_update_professional(
        self,
        authenticated_client,
        sample_professional
    ):
        data = {'nome_social': 'Dr. João Silva Junior'}
        response = authenticated_client.patch(
            f'/api/v1/professionals/{sample_professional.id}/',
            data
        )
        assert response.status_code == status.HTTP_200_OK
        sample_professional.refresh_from_db()
        assert sample_professional.nome_social == data['nome_social']

    def test_delete_professional(
        self,
        authenticated_client,
        sample_professional
    ):
        response = authenticated_client.delete(
            f'/api/v1/professionals/{sample_professional.id}/'
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT
```

#### 5.3 Testes de Consultas

```python
# tests/test_appointments.py
import pytest
from datetime import datetime, timedelta
from rest_framework import status

@pytest.mark.django_db
class TestAppointmentCRUD:

    def test_create_appointment(
        self,
        authenticated_client,
        sample_professional
    ):
        future_date = datetime.now() + timedelta(days=7)
        data = {
            'professional': sample_professional.id,
            'data_hora': future_date.isoformat(),
            'paciente_nome': 'Paciente Teste',
            'paciente_email': 'paciente@test.com',
            'paciente_telefone': '11999999999',
        }
        response = authenticated_client.post(
            '/api/v1/appointments/',
            data
        )
        assert response.status_code == status.HTTP_201_CREATED

    def test_list_appointments_by_professional(
        self,
        authenticated_client,
        sample_professional
    ):
        # Criar algumas consultas
        # ...

        response = authenticated_client.get(
            f'/api/v1/appointments/?professional_id={sample_professional.id}'
        )
        assert response.status_code == status.HTTP_200_OK
        # Verificar que retornou apenas consultas deste profissional
```

#### 5.4 Testes de Segurança

```python
# tests/test_security.py
import pytest
from rest_framework import status

@pytest.mark.django_db
class TestSecurity:

    def test_unauthenticated_request(self, api_client):
        response = api_client.get('/api/v1/professionals/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_sql_injection_prevention(self, authenticated_client):
        malicious_data = {
            'nome_social': "'; DROP TABLE professionals; --",
            'email': 'test@test.com',
            # ...
        }
        response = authenticated_client.post(
            '/api/v1/professionals/',
            malicious_data
        )
        # Deve falhar na validação ou ser sanitizado
        # Verificar que a tabela ainda existe

    def test_xss_prevention(self, authenticated_client):
        xss_data = {
            'nome_social': '<script>alert("XSS")</script>',
            'email': 'xss@test.com',
            # ...
        }
        response = authenticated_client.post(
            '/api/v1/professionals/',
            xss_data
        )
        if response.status_code == 201:
            # Verificar que o script foi sanitizado
            assert '<script>' not in response.data['nome_social']
```

#### 5.5 Cobertura de testes

- [ ] Meta: mínimo 80% de cobertura
- [ ] Executar: `poetry run pytest --cov`
- [ ] Gerar relatório HTML: `poetry run pytest --cov --cov-report=html`

---

### **FASE 6: Docker e Containerização** (Prioridade: ALTA)

**Tempo estimado: 4-6 horas**

#### 6.1 Dockerfile

```dockerfile
# Dockerfile
FROM python:3.13-slim

# Variáveis de ambiente
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    POETRY_VERSION=1.7.1 \
    POETRY_HOME="/opt/poetry" \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Instalar Poetry
RUN pip install "poetry==$POETRY_VERSION"

# Diretório de trabalho
WORKDIR /app

# Copiar arquivos de dependências
COPY pyproject.toml poetry.lock ./

# Instalar dependências Python
RUN poetry install --no-root --no-dev

# Copiar código da aplicação
COPY . .

# Coletar arquivos estáticos
RUN python manage.py collectstatic --noinput

# Expor porta
EXPOSE 8000

# Script de inicialização
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
```

#### 6.2 docker-compose.yml

```yaml
version: "3.9"

services:
  db:
    image: postgres:15-alpine
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      POSTGRES_DB: ${DB_NAME:-lacrei_db}
      POSTGRES_USER: ${DB_USER:-lacrei_user}
      POSTGRES_PASSWORD: ${DB_PASSWORD:-lacrei_pass}
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-BATCH", "pg_isready -U ${DB_USER:-lacrei_user}"]
      interval: 10s
      timeout: 5s
      retries: 5

  web:
    build: .
    command: python manage.py runserver 0.0.0.0:8000
    volumes:
      - .:/app
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    ports:
      - "8000:8000"
    environment:
      - DEBUG=True
      - DB_HOST=db
      - DB_PORT=5432
      - DB_NAME=${DB_NAME:-lacrei_db}
      - DB_USER=${DB_USER:-lacrei_user}
      - DB_PASSWORD=${DB_PASSWORD:-lacrei_pass}
    depends_on:
      db:
        condition: service_healthy

  nginx:
    image: nginx:alpine
    volumes:
      - ./docker/nginx.conf:/etc/nginx/nginx.conf:ro
      - static_volume:/app/staticfiles:ro
      - media_volume:/app/media:ro
    ports:
      - "80:80"
    depends_on:
      - web

volumes:
  postgres_data:
  static_volume:
  media_volume:
```

#### 6.3 Entrypoint script

```bash
#!/bin/bash
# docker/entrypoint.sh

set -e

echo "Waiting for PostgreSQL..."
while ! nc -z $DB_HOST $DB_PORT; do
  sleep 0.1
done
echo "PostgreSQL started"

echo "Running migrations..."
python manage.py migrate --noinput

echo "Creating superuser if needed..."
python manage.py shell << END
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@lacrei.com', 'admin123')
END

exec "$@"
```

#### 6.4 Nginx configuration

```nginx
# docker/nginx.conf
upstream django {
    server web:8000;
}

server {
    listen 80;
    server_name localhost;

    location /static/ {
        alias /app/staticfiles/;
    }

    location /media/ {
        alias /app/media/;
    }

    location / {
        proxy_pass http://django;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

### **FASE 7: CI/CD com GitHub Actions** (Prioridade: ALTA)

**Tempo estimado: 4-6 horas**

#### 7.1 Workflow principal

```yaml
# .github/workflows/ci-cd.yml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

env:
  PYTHON_VERSION: "3.11"
  POETRY_VERSION: "1.7.1"

jobs:
  lint:
    name: Lint Code
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ env.PYTHON_VERSION }}

      - name: Install Poetry
        run: |
          pip install poetry==${{ env.POETRY_VERSION }}
          poetry config virtualenvs.create false

      - name: Install dependencies
        run: poetry install

      - name: Run Black
        run: poetry run black --check .

      - name: Run Flake8
        run: poetry run flake8 .

      - name: Run isort
        run: poetry run isort --check-only .

  test:
    name: Run Tests
    runs-on: ubuntu-latest
    needs: lint

    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_DB: test_db
          POSTGRES_USER: test_user
          POSTGRES_PASSWORD: test_pass
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ env.PYTHON_VERSION }}

      - name: Install dependencies
        run: |
          pip install poetry==${{ env.POETRY_VERSION }}
          poetry install

      - name: Run migrations
        env:
          DB_HOST: localhost
          DB_PORT: 5432
          DB_NAME: test_db
          DB_USER: test_user
          DB_PASSWORD: test_pass
        run: poetry run python manage.py migrate

      - name: Run tests with coverage
        env:
          DB_HOST: localhost
          DB_PORT: 5432
          DB_NAME: test_db
          DB_USER: test_user
          DB_PASSWORD: test_pass
        run: poetry run pytest --cov --cov-report=xml

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage.xml

  build:
    name: Build Docker Image
    runs-on: ubuntu-latest
    needs: test
    if: github.event_name == 'push'

    steps:
      - uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Login to Docker Hub
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}

      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: |
            ${{ secrets.DOCKER_USERNAME }}/lacrei-api:${{ github.sha }}
            ${{ secrets.DOCKER_USERNAME }}/lacrei-api:latest
          cache-from: type=registry,ref=${{ secrets.DOCKER_USERNAME }}/lacrei-api:buildcache
          cache-to: type=registry,ref=${{ secrets.DOCKER_USERNAME }}/lacrei-api:buildcache,mode=max

  deploy-staging:
    name: Deploy to Staging
    runs-on: ubuntu-latest
    needs: build
    if: github.ref == 'refs/heads/develop'
    environment:
      name: staging
      url: https://staging-api.lacrei.com

    steps:
      - uses: actions/checkout@v4

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1

      - name: Deploy to ECS
        run: |
          # Script de deploy para staging
          ./scripts/deploy-ecs.sh staging

  deploy-production:
    name: Deploy to Production
    runs-on: ubuntu-latest
    needs: build
    if: github.ref == 'refs/heads/main'
    environment:
      name: production
      url: https://api.lacrei.com

    steps:
      - uses: actions/checkout@v4

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1

      - name: Deploy to ECS
        run: |
          # Script de deploy para produção
          ./scripts/deploy-ecs.sh production

      - name: Run smoke tests
        run: |
          # Verificar se a aplicação está funcionando
          ./scripts/smoke-tests.sh https://api.lacrei.com
```

#### 7.2 Secrets necessários no GitHub

- `DOCKER_USERNAME`
- `DOCKER_PASSWORD`
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `DJANGO_SECRET_KEY`
- `DB_PASSWORD`

---

### **FASE 8: Deploy AWS (Staging/Produção)** (Prioridade: ALTA)

**Tempo estimado: 8-12 horas**

#### 8.1 Arquitetura AWS proposta

```
Internet → Route53 → CloudFront → ALB → ECS/Fargate → RDS PostgreSQL
                                                    ↓
                                              ElastiCache Redis
                                                    ↓
                                              S3 (static/media)
```

#### 8.2 Recursos AWS necessários

**VPC e Rede:**

- VPC com subnets públicas e privadas
- Internet Gateway
- NAT Gateway
- Security Groups configurados

**Compute:**

- ECS Cluster
- Task Definitions (staging e production)
- Fargate para execução dos containers
- Auto Scaling configurado

**Database:**

- RDS PostgreSQL (Multi-AZ para produção)
- Parameter Group otimizado
- Automated backups
- Encryption at rest

**Load Balancing:**

- Application Load Balancer
- Target Groups
- Health checks configurados

**Storage:**

- S3 bucket para arquivos estáticos
- S3 bucket para media files
- CloudFront para CDN

**Cache (opcional):**

- ElastiCache Redis para sessões e cache

**Monitoring:**

- CloudWatch Logs
- CloudWatch Alarms
- X-Ray para tracing

#### 8.3 Terraform/IaC (Recomendado)

```hcl
# terraform/main.tf - exemplo básico
terraform {
  required_version = ">= 1.0"

  backend "s3" {
    bucket = "lacrei-terraform-state"
    key    = "api/terraform.tfstate"
    region = "us-east-1"
  }
}

provider "aws" {
  region = var.aws_region
}

module "vpc" {
  source = "./modules/vpc"

  environment = var.environment
  cidr_block  = var.vpc_cidr
}

module "rds" {
  source = "./modules/rds"

  environment      = var.environment
  vpc_id          = module.vpc.vpc_id
  private_subnets = module.vpc.private_subnets
  instance_class  = var.db_instance_class
}

module "ecs" {
  source = "./modules/ecs"

  environment     = var.environment
  vpc_id         = module.vpc.vpc_id
  public_subnets = module.vpc.public_subnets
  image_url      = var.docker_image
  db_endpoint    = module.rds.endpoint
}
```

#### 8.4 Scripts de deploy

```bash
# scripts/deploy-ecs.sh
#!/bin/bash

ENVIRONMENT=$1
IMAGE_TAG=${2:-latest}

if [ -z "$ENVIRONMENT" ]; then
  echo "Usage: $0 <staging|production> [image-tag]"
  exit 1
fi

# Configurações por ambiente
if [ "$ENVIRONMENT" == "staging" ]; then
  CLUSTER="lacrei-staging-cluster"
  SERVICE="lacrei-staging-service"
  TASK_FAMILY="lacrei-staging-task"
elif [ "$ENVIRONMENT" == "production" ]; then
  CLUSTER="lacrei-production-cluster"
  SERVICE="lacrei-production-service"
  TASK_FAMILY="lacrei-production-task"
else
  echo "Invalid environment: $ENVIRONMENT"
  exit 1
fi

echo "Deploying to $ENVIRONMENT..."

# Atualizar task definition
NEW_TASK_DEF=$(aws ecs describe-task-definition \
  --task-definition $TASK_FAMILY \
  --query 'taskDefinition' \
  | jq --arg IMAGE "$DOCKER_IMAGE:$IMAGE_TAG" \
    '.containerDefinitions[0].image=$IMAGE')

# Registrar nova versão
NEW_TASK_INFO=$(aws ecs register-task-definition \
  --cli-input-json "$NEW_TASK_DEF")

NEW_REVISION=$(echo $NEW_TASK_INFO | jq -r '.taskDefinition.revision')

# Atualizar service
aws ecs update-service \
  --cluster $CLUSTER \
  --service $SERVICE \
  --task-definition $TASK_FAMILY:$NEW_REVISION \
  --force-new-deployment

# Aguardar deploy
aws ecs wait services-stable \
  --cluster $CLUSTER \
  --services $SERVICE

echo "Deploy completed successfully!"
```

#### 8.5 Variáveis de ambiente por ambiente

**Staging:**

```env
ENVIRONMENT=staging
DEBUG=False
ALLOWED_HOSTS=staging-api.lacrei.com
DATABASE_URL=postgresql://user:pass@staging-db.xxx.rds.amazonaws.com/lacrei_staging
CORS_ALLOWED_ORIGINS=https://staging.lacrei.com
```

**Production:**

```env
ENVIRONMENT=production
DEBUG=False
ALLOWED_HOSTS=api.lacrei.com
DATABASE_URL=postgresql://user:pass@prod-db.xxx.rds.amazonaws.com/lacrei_production
CORS_ALLOWED_ORIGINS=https://lacrei.com,https://www.lacrei.com
```

---

### **FASE 9: Documentação Completa** (Prioridade: MÉDIA)

**Tempo estimado: 4-6 horas**

#### 9.1 README.md principal

````markdown
# 🏥 Lacrei Saúde API

API RESTful para gerenciamento de consultas médicas com foco em segurança e qualidade.

## 🚀 Quick Start

### Pré-requisitos

- Python 3.11+
- Poetry
- Docker & Docker Compose
- PostgreSQL 15

### Setup Local

1. Clone o repositório:

```bash
git clone https://github.com/seu-usuario/Lacrei-Saude-API.git
cd Lacrei-Saude-API
```
````

2. Instale as dependências:

```bash
poetry install
```

3. Configure variáveis de ambiente:

```bash
cp .env.example .env
# Edite o .env com suas configurações
```

4. Execute as migrações:

```bash
poetry run python manage.py migrate
```

5. Inicie o servidor:

```bash
poetry run python manage.py runserver
```

### Setup com Docker

```bash
docker-compose up --build
```

Acesse: http://localhost:8000

## 📚 Documentação da API

Documentação interativa disponível em:

- Swagger UI: http://localhost:8000/api/docs/
- ReDoc: http://localhost:8000/api/redoc/

## 🧪 Executando Testes

```bash
# Todos os testes
poetry run pytest

# Com cobertura
poetry run pytest --cov

# Testes específicos
poetry run pytest tests/test_professionals.py
```

## 🔒 Segurança

- Autenticação JWT
- Rate limiting
- CORS configurado
- Sanitização de inputs
- Proteção contra SQL Injection
- Logs de segurança

## 🏗️ Arquitetura

[Incluir diagrama da arquitetura]

## 📦 Deploy

### CI/CD Pipeline

O projeto usa GitHub Actions com os seguintes stages:

1. Lint (Black, Flake8, isort)
2. Tests (pytest com cobertura)
3. Build (Docker image)
4. Deploy Staging (branch develop)
5. Deploy Production (branch main)

### Ambientes

- **Staging:** https://staging-api.lacrei.com
- **Production:** https://api.lacrei.com

### Rollback

[Instruções de rollback]

## 🤝 Contribuindo

[Guidelines de contribuição]

## 📄 Licença

MIT

````

#### 9.2 Documentação API (Swagger/OpenAPI)
```python
# config/settings.py
INSTALLED_APPS += [
    'drf_spectacular',
]

REST_FRAMEWORK = {
    # ... outras configs
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'Lacrei Saúde API',
    'DESCRIPTION': 'API para gerenciamento de consultas médicas',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}

# config/urls.py
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView
)

urlpatterns += [
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema')),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema')),
]
````

#### 9.3 Documentação de Decisões Técnicas

```markdown
# docs/DECISOES_TECNICAS.md

## Escolhas de Tecnologia

### Django + Django REST Framework

**Decisão:** Framework principal
**Justificativa:**

- ORM robusto com proteção contra SQL Injection
- Admin panel built-in para gestão
- Ecossistema maduro e bem documentado
- DRF oferece serializers, viewsets e autenticação pronta

### Poetry

**Decisão:** Gerenciador de dependências
**Justificativa:**

- Resolução de dependências determinística
- Separação clara entre dev/prod
- Melhor que pip + requirements.txt

### PostgreSQL

**Decisão:** Banco de dados
**Justificativa:**

- ACID compliance
- Melhor para dados relacionais
- Suporte a índices avançados
- Maturidade e performance

### JWT para autenticação

**Decisão:** Simple JWT
**Justificativa:**

- Stateless authentication
- Escalável horizontalmente
- Tokens com expiração configurável

### Docker

**Decisão:** Containerização
**Justificativa:**

- Ambiente consistente dev/staging/prod
- Facilita deploy e scaling
- Integração com orquestradores

### AWS ECS

**Decisão:** Plataforma de deploy
**Justificativa:**

- Gerenciamento simplificado de containers
- Auto-scaling nativo
- Integração com outros serviços AWS
- Menor overhead operacional que Kubernetes
```

#### 9.4 Diário de Desenvolvimento

```markdown
# docs/DIARIO.md

## Dia 1 - Setup inicial

- ✅ Configuração do Poetry
- ✅ Estrutura de pastas
- ⚠️ Problema: Conflito de versão do psycopg2
  - Solução: Usar psycopg2-binary

## Dia 2 - Modelagem

- ✅ Models de Professional e Appointment
- ✅ Migrations iniciais
- 💡 Decisão: Adicionar soft delete

[... continuar documentando]
```

---

### **FASE 10: Melhorias e Bônus** (Prioridade: BAIXA)

**Tempo estimado: 6-8 horas**

#### 10.1 Integração com Asaas (Split de Pagamento)

**Proposta de Arquitetura:**

```
Consulta Criada → Event → Payment Service → Asaas API
                                         ↓
                                   Split configurado
                                         ↓
                        80% Profissional | 20% Plataforma
```

**Implementação Mock:**

```python
# payments/services.py
import requests
from decimal import Decimal

class AsaasPaymentService:
    BASE_URL = "https://sandbox.asaas.com/api/v3"

    def __init__(self, api_key):
        self.api_key = api_key
        self.headers = {
            "access_token": api_key,
            "Content-Type": "application/json"
        }

    def create_payment_with_split(
        self,
        appointment_id,
        total_value,
        professional_wallet_id
    ):
        """
        Cria cobrança com split de pagamento
        """
        platform_fee = total_value * Decimal('0.20')
        professional_amount = total_value - platform_fee

        payload = {
            "customer": appointment.paciente_email,
            "billingType": "CREDIT_CARD",
            "value": float(total_value),
            "dueDate": appointment.data_hora.date(),
            "description": f"Consulta #{appointment_id}",
            "split": [
                {
                    "walletId": professional_wallet_id,
                    "fixedValue": float(professional_amount)
                }
            ]
        }

        response = requests.post(
            f"{self.BASE_URL}/payments",
            json=payload,
            headers=self.headers
        )

        return response.json()

    def create_subaccount(self, professional):
        """
        Cria subconta para o profissional
        """
        payload = {
            "name": professional.nome_social,
            "email": professional.email,
            "cpfCnpj": professional.cpf,
            "phone": professional.telefone,
            # ... outros dados
        }

        response = requests.post(
            f"{self.BASE_URL}/accounts",
            json=payload,
            headers=self.headers
        )

        return response.json()
```

**Webhook Handler:**

```python
# payments/views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
import hmac
import hashlib

@api_view(['POST'])
def asaas_webhook(request):
    # Validar assinatura
    signature = request.headers.get('asaas-signature')
    if not validate_webhook_signature(request.body, signature):
        return Response({'error': 'Invalid signature'}, status=401)

    event = request.data.get('event')
    payment_data = request.data.get('payment')

    if event == 'PAYMENT_CONFIRMED':
        # Atualizar status da consulta
        appointment = Appointment.objects.get(
            payment_id=payment_data['id']
        )
        appointment.status = 'CONFIRMADA'
        appointment.save()

        # Enviar notificações
        send_confirmation_email(appointment)

    return Response({'status': 'processed'})
```

#### 10.2 Melhorias de Performance

**Cache com Redis:**

```python
# config/settings.py
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.getenv('REDIS_URL'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# professionals/views.py
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator

class ProfessionalViewSet(viewsets.ModelViewSet):
    @method_decorator(cache_page(60 * 15))  # 15 minutos
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
```

**Database Optimization:**

```python
# Usar select_related e prefetch_related
class AppointmentViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        return Appointment.objects.select_related(
            'professional'
        ).prefetch_related(
            'professional__specialties'
        )
```

#### 10.3 Monitoramento Avançado

**Sentry para Error Tracking:**

```python
# config/settings.py
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn=os.getenv('SENTRY_DSN'),
    integrations=[DjangoIntegration()],
    traces_sample_rate=1.0,
    send_default_pii=True,
    environment=os.getenv('ENVIRONMENT', 'development'),
)
```

**Prometheus Metrics:**

```python
# requirements
django-prometheus

# config/settings.py
INSTALLED_APPS += ['django_prometheus']

MIDDLEWARE = [
    'django_prometheus.middleware.PrometheusBeforeMiddleware',
    # ... outros middlewares
    'django_prometheus.middleware.PrometheusAfterMiddleware',
]

# config/urls.py
urlpatterns += [
    path('', include('django_prometheus.urls')),
]
```

#### 10.4 Rollback Strategy

**Estratégia Blue-Green Deploy:**

````markdown
# docs/ROLLBACK.md

## Estratégia de Rollback

### Blue-Green Deployment

**Setup:**

- Dois ambientes idênticos (Blue e Green)
- ALB com Target Groups para cada ambiente
- Route53 para switch de DNS

**Processo de Deploy:**

1. Produção ativa em Blue
2. Deploy nova versão em Green
3. Executar smoke tests em Green
4. Se OK: Switch ALB para Green
5. Blue fica em standby por 24h

**Rollback:**

- Se problema detectado: Switch ALB de volta para Blue
- Tempo de rollback: < 5 minutos
- Zero downtime

**Comandos:**

```bash
# Deploy to Green
./scripts/deploy-blue-green.sh green

# Smoke tests
./scripts/smoke-tests.sh https://green.lacrei.com

# Switch traffic
./scripts/switch-traffic.sh green

# Rollback se necessário
./scripts/switch-traffic.sh blue
```
````

### Alternativa: Revert no GitHub Actions

**Processo:**

1. Identificar commit problemático
2. Revert no Git:
   ```bash
   git revert <commit-hash>
   git push origin main
   ```
3. Pipeline automaticamente faz deploy da versão anterior

### Database Migrations Rollback

**Cuidados:**

- Sempre fazer backup antes de migrations
- Migrations devem ser reversíveis
- Testar rollback em staging primeiro

```bash
# Backup
pg_dump -h $DB_HOST -U $DB_USER $DB_NAME > backup.sql

# Rollback migration
python manage.py migrate app_name 0001_previous_migration

# Restaurar backup se necessário
psql -h $DB_HOST -U $DB_USER $DB_NAME < backup.sql
```

```

---

## 🎯 Resumo de Prioridades

### Alta Prioridade (MVP)
1. ✅ Setup ambiente e dependências
2. ✅ Modelagem de dados
3. ✅ CRUD completo
4. ✅ Segurança e validações
5. ✅ Testes automatizados (80%+ cobertura)
6. ✅ Docker funcional
7. ✅ CI/CD pipeline
8. ✅ Deploy staging/production

### Média Prioridade
9. ✅ Documentação completa
10. ✅ Swagger/OpenAPI
11. ✅ Logs e monitoring básico

### Baixa Prioridade (Bônus)
12. ⭐ Integração Asaas
13. ⭐ Cache Redis
14. ⭐ Sentry/Prometheus
15. ⭐ Performance optimization

---

## 📊 Estimativa Total

- **MVP Completo:** 35-45 horas
- **Com Bônus:** 45-60 horas
- **Tempo recomendado:** 1-2 semanas

---

## 🛠️ Próximos Passos Imediatos

1. **Agora:** Setup do ambiente Python + Poetry
2. **Depois:** Criar estrutura Django e apps
3. **Em seguida:** Implementar models e migrations
4. **Continuar:** Seguir fases sequencialmente

---

## 📞 Suporte e Dúvidas

- Consultar este plano regularmente
- Documentar decisões e problemas
- Commitar frequentemente
- Testar cada fase antes de avançar

---

**Boa sorte com o desafio! 🚀**
```
