# 🐳 Docker - Guia de Uso

Este guia explica como executar a API Lacrei Saúde usando Docker e Docker Compose.

## 📋 Pré-requisitos

- Docker 20.10+
- Docker Compose 2.0+

## 🚀 Quick Start

### 1. Build e Start

```bash
# Build das imagens e start dos containers
docker-compose up --build

# Ou em background
docker-compose up -d --build
```

### 2. Acessar a aplicação

- **API:** http://localhost:8000
- **Admin:** http://localhost:8000/admin
- **Nginx:** http://localhost
- **Health Check:** http://localhost:8000/api/v1/health/

**Credenciais padrão do admin:**
- Username: `admin`
- Password: `admin123`

## 📦 Serviços

A aplicação é composta por 3 serviços:

### 1. `db` - PostgreSQL 15
- Porta: `5432`
- Database: `lacrei_db`
- User: `lacrei_user`
- Password: `lacrei_pass`

### 2. `web` - Django + Gunicorn
- Porta: `8000`
- Workers: 3
- Timeout: 60s
- Auto-reload ativado em dev

### 3. `nginx` - Proxy Reverso
- Porta: `80`
- Serve arquivos estáticos
- Proxy para Django

## 🔧 Comandos Úteis

### Gerenciar containers

```bash
# Start
docker-compose up

# Start em background
docker-compose up -d

# Stop
docker-compose down

# Stop e remove volumes (CUIDADO: apaga o banco!)
docker-compose down -v

# Rebuild
docker-compose up --build

# Ver logs
docker-compose logs -f

# Logs de um serviço específico
docker-compose logs -f web
```

### Executar comandos Django

```bash
# Shell do Django
docker-compose exec web python manage.py shell

# Criar migrations
docker-compose exec web python manage.py makemigrations

# Aplicar migrations
docker-compose exec web python manage.py migrate

# Criar superuser
docker-compose exec web python manage.py createsuperuser

# Collectstatic
docker-compose exec web python manage.py collectstatic --noinput

# Executar testes
docker-compose exec web pytest

# Bash no container
docker-compose exec web bash
```

### Gerenciar banco de dados

```bash
# Acessar PostgreSQL
docker-compose exec db psql -U lacrei_user -d lacrei_db

# Backup
docker-compose exec db pg_dump -U lacrei_user lacrei_db > backup.sql

# Restore
docker-compose exec -T db psql -U lacrei_user lacrei_db < backup.sql

# Ver logs do banco
docker-compose logs -f db
```

## 🔐 Variáveis de Ambiente

Crie um arquivo `.env` baseado no `.env.docker`:

```bash
cp .env.docker .env
```

Principais variáveis:

```env
# Django
DEBUG=True
SECRET_KEY=sua-chave-secreta-aqui
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_HOST=db
DB_PORT=5432
DB_NAME=lacrei_db
DB_USER=lacrei_user
DB_PASSWORD=lacrei_pass

# Superuser
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@lacrei.com
DJANGO_SUPERUSER_PASSWORD=admin123
```

## 🧪 Testes

```bash
# Executar todos os testes
docker-compose exec web pytest

# Com cobertura
docker-compose exec web pytest --cov

# Teste específico
docker-compose exec web pytest tests/test_professionals.py

# Com output verbose
docker-compose exec web pytest -v
```

## 🐛 Troubleshooting

### Porta já em uso

```bash
# Se a porta 8000 já estiver em uso, pare o serviço ou altere a porta
# no docker-compose.yml:
ports:
  - "8080:8000"  # Usa porta 8080 no host
```

### Migrations não aplicadas

```bash
# Entre no container e aplique manualmente
docker-compose exec web python manage.py migrate
```

### Container não inicia

```bash
# Ver logs detalhados
docker-compose logs web

# Remover volumes e rebuildar
docker-compose down -v
docker-compose up --build
```

### Erro de conexão com banco

```bash
# Verificar se o banco está rodando
docker-compose ps

# Verificar logs do banco
docker-compose logs db

# Restart dos serviços
docker-compose restart
```

### Limpar tudo e recomeçar

```bash
# CUIDADO: Remove TODOS os containers, imagens e volumes
docker-compose down -v
docker system prune -a
docker-compose up --build
```

## 📊 Healthchecks

Os containers incluem healthchecks automáticos:

```bash
# Ver status dos healthchecks
docker-compose ps

# Output:
# NAME          STATUS                    PORTS
# lacrei-db     Up (healthy)             5432/tcp
# lacrei-web    Up (healthy)             8000/tcp
# lacrei-nginx  Up                       80/tcp
```

## 🔄 Hot Reload

O container `web` está configurado com hot reload em desenvolvimento:

- Alterações no código Python são detectadas automaticamente
- Gunicorn recarrega os workers
- Não é necessário restart manual

## 📝 Logs

Logs são enviados para stdout/stderr e podem ser visualizados:

```bash
# Todos os serviços
docker-compose logs -f

# Últimas 100 linhas
docker-compose logs --tail=100

# Serviço específico
docker-compose logs -f web
docker-compose logs -f db
docker-compose logs -f nginx
```

## 🚀 Produção

Para produção, faça os seguintes ajustes:

### 1. Variáveis de ambiente

```env
DEBUG=False
SECRET_KEY=use-uma-chave-forte-e-unica
ALLOWED_HOSTS=seu-dominio.com,www.seu-dominio.com
```

### 2. Docker Compose

Crie um `docker-compose.prod.yml`:

```yaml
version: '3.9'

services:
  web:
    command: gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4 --timeout 120
    volumes:
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    # Remover o volume de código (.)
```

### 3. SSL/TLS

Configure SSL no nginx ou use um reverse proxy como Traefik/Caddy.

## 📚 Referências

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/)
