# Dockerfile
FROM python:3.13-slim

# Variáveis de ambiente
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    POETRY_VERSION=1.8.5 \
    POETRY_HOME="/opt/poetry" \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

# Instalar Poetry
RUN pip install --no-cache-dir "poetry==$POETRY_VERSION"

# Diretório de trabalho
WORKDIR /app

# Copiar arquivos de dependências
COPY pyproject.toml poetry.lock* ./

# Instalar dependências Python manualmente (pyproject.toml não é package)
RUN pip install --no-cache-dir \
    "django>=6.0,<7.0" \
    "djangorestframework>=3.16.1,<4.0.0" \
    "psycopg2-binary>=2.9.11,<3.0.0" \
    "python-decouple>=3.8,<4.0" \
    "django-cors-headers>=4.9.0,<5.0.0" \
    "djangorestframework-simplejwt>=5.5.1,<6.0.0" \
    "gunicorn>=23.0.0,<24.0.0" \
    "django-filter>=25.2,<26.0" \
    "bleach>=6.3.0,<7.0.0"

# Copiar código da aplicação
COPY . .

# Criar diretórios necessários
RUN mkdir -p /app/staticfiles /app/media /app/logs

# Coletar arquivos estáticos (rodará novamente no entrypoint se necessário)
RUN python manage.py collectstatic --noinput || true

# Script de inicialização
COPY docker/entrypoint.sh /entrypoint.sh
RUN sed -i 's/\r$//' /entrypoint.sh && chmod +x /entrypoint.sh

# Expor porta
EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/v1/health/').read()" || exit 1

ENTRYPOINT ["/entrypoint.sh"]
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "60", "--access-logfile", "-", "--error-logfile", "-"]
