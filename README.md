# 🏥 Lacrei Saúde API

> API RESTful de Gerenciamento de Consultas Médicas - Desafio Técnico Lacrei Saúde

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.0+-green.svg)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/DRF-3.14+-red.svg)](https://www.django-rest-framework.org/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## 📋 Sobre o Projeto

API funcional, segura e pronta para produção, desenvolvida com foco em qualidade de código, segurança dos dados e boas práticas de desenvolvimento. Este projeto faz parte do processo seletivo da Lacrei Saúde e foi projetado para ser base de integrações futuras.

### ✨ Funcionalidades

- ✅ **CRUD completo de profissionais da saúde**
- ✅ **CRUD completo de consultas médicas**
- ✅ **Busca de consultas por profissional**
- ✅ **Autenticação JWT** (access + refresh tokens)
- ✅ **Validação e sanitização de dados**
- ✅ **Proteção contra SQL Injection e XSS**
- ✅ **CORS configurado** por ambiente
- ✅ **Logs de segurança e acesso** estruturados
- ✅ **Testes automatizados** (80%+ cobertura)
- ✅ **Docker e Docker Compose** (3 serviços)
- ✅ **Health check endpoint** (`/api/v1/health/`)
- ✅ **Nginx como proxy reverso**
- ✅ **Gunicorn** servidor WSGI de produção
- ⏳ **CI/CD com GitHub Actions** (FASE 7)
- ⏳ **Deploy em AWS** (FASE 8 - Staging e Produção)

## 🚀 Quick Start

### Pré-requisitos

- Python 3.13+
- Poetry
- Docker e Docker Compose (opcional, mas recomendado)
- PostgreSQL 15 (se rodar sem Docker)

### Instalação Local

1. **Clone o repositório:**

```bash
git clone https://github.com/seu-usuario/Lacrei-Saude-API.git
cd Lacrei-Saude-API
```

2. **Instale o Poetry (se ainda não tiver):**

```bash
pip install poetry
```

3. **Instale as dependências:**

```bash
poetry install
```

4. **Configure as variáveis de ambiente:**

```bash
cp .env.example .env
# Edite o .env com suas configurações locais
```

5. **Execute as migrações:**

```bash
poetry run python manage.py migrate
```

6. **Crie um superusuário:**

```bash
poetry run python manage.py createsuperuser
```

7. **Inicie o servidor:**

```bash
poetry run python manage.py runserver
```

Acesse: http://localhost:8000

### 🐳 Instalação com Docker (Recomendado)

A forma mais rápida e confiável de rodar a aplicação é usando Docker Compose.

> ⚠️ **IMPORTANTE - Segurança:** Os arquivos `.env.docker` e `docker-compose.yml` contêm informações sensíveis e **NÃO** estão versionados. Você deve criá-los a partir dos exemplos fornecidos.

1. **Clone e configure:**

```bash
git clone https://github.com/seu-usuario/Lacrei-Saude-API.git
cd Lacrei-Saude-API

# Copie os arquivos de exemplo
cp .env.docker.example .env.docker
cp docker-compose.example.yml docker-compose.yml
```

2. **Edite `.env.docker` com suas credenciais reais:**

```bash
# No Windows
notepad .env.docker

# No Linux/Mac
nano .env.docker
```

**Altere pelo menos estas variáveis:**

- `SECRET_KEY` - Gere uma chave secreta forte (50+ caracteres)
- `DB_USER` - Usuário do PostgreSQL
- `DB_PASSWORD` - Senha segura do banco de dados
- `DJANGO_SUPERUSER_PASSWORD` - Senha do admin

3. **Inicie os containers:**

```bash
docker-compose up --build -d
```

Isso irá:

- ✅ Construir a imagem Docker da aplicação
- ✅ Iniciar PostgreSQL 15
- ✅ Executar migrations automaticamente
- ✅ Coletar arquivos estáticos
- ✅ Criar superuser (admin/admin123)
- ✅ Iniciar Gunicorn com 3 workers
- ✅ Configurar Nginx como proxy reverso

3. **Verifique os containers:**

```bash
docker-compose ps
```

Você deve ver 3 containers rodando:

- `lacrei-db` (PostgreSQL) - healthy
- `lacrei-web` (Django + Gunicorn) - healthy
- `lacrei-nginx` (Nginx) - running

4. **Acesse a aplicação:**

- **API:** http://localhost:8000
- **Admin:** http://localhost:8000/admin
- **Health Check:** http://localhost:8000/api/v1/health/
- **Nginx (proxy):** http://localhost

5. **Ver logs:**

```bash
# Todos os serviços
docker-compose logs -f

# Apenas a aplicação
docker-compose logs -f web

# Apenas o banco
docker-compose logs -f db
```

6. **Comandos úteis:**

```bash
# Executar migrations
docker-compose exec web python manage.py migrate

# Criar superuser adicional
docker-compose exec web python manage.py createsuperuser

# Executar testes
docker-compose exec web pytest

# Acessar shell Django
docker-compose exec web python manage.py shell

# Acessar bash no container
docker-compose exec web bash

# Parar containers
docker-compose down

# Parar e remover volumes (reset completo)
docker-compose down -v
```

**📚 Documentação completa do Docker:** [docker/README.md](docker/README.md)

## 📚 Documentação da API

A documentação interativa da API está disponível em:

- **Swagger UI:** http://localhost:8000/api/docs/
- **ReDoc:** http://localhost:8000/api/redoc/
- **Schema JSON:** http://localhost:8000/api/schema/

### Endpoints Principais

#### Profissionais

```
GET    /api/v1/professionals/          # Listar profissionais
POST   /api/v1/professionals/          # Criar profissional
GET    /api/v1/professionals/{id}/     # Detalhar profissional
PUT    /api/v1/professionals/{id}/     # Atualizar profissional
PATCH  /api/v1/professionals/{id}/     # Atualizar parcialmente
DELETE /api/v1/professionals/{id}/     # Deletar profissional
```

#### Consultas

```
GET    /api/v1/appointments/                    # Listar consultas
POST   /api/v1/appointments/                    # Criar consulta
GET    /api/v1/appointments/{id}/               # Detalhar consulta
PUT    /api/v1/appointments/{id}/               # Atualizar consulta
PATCH  /api/v1/appointments/{id}/               # Atualizar parcialmente
GET    /api/v1/appointments/?professional_id=1  # Consultas por profissional
```

#### Autenticação

```
POST   /api/auth/token/          # Obter token JWT
POST   /api/auth/token/refresh/  # Refresh token
```

### Exemplo de Uso

```bash
# Obter token
curl -X POST http://localhost:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "senha123"}'

# Listar profissionais (autenticado)
curl -X GET http://localhost:8000/api/v1/professionals/ \
  -H "Authorization: Bearer seu-token-jwt-aqui"
```

## 🧪 Executando Testes

### Todos os testes

```bash
poetry run pytest
```

### Com relatório de cobertura

```bash
poetry run pytest --cov
```

### Gerar relatório HTML de cobertura

```bash
poetry run pytest --cov --cov-report=html
```

### Testes específicos

```bash
poetry run pytest tests/test_professionals.py
poetry run pytest tests/test_appointments.py
poetry run pytest tests/test_security.py
```

### Rodar testes no Docker

```bash
docker-compose exec web pytest
docker-compose exec web pytest --cov
```

## 🐳 Docker - Informações Detalhadas

### Dockerfile

O projeto usa um Dockerfile otimizado multi-stage:

**Características:**

- Base: `python:3.13-slim` (imagem oficial leve)
- Poetry instalado para gerenciamento de dependências
- Dependências do sistema: gcc, postgresql-client, netcat
- Healthcheck integrado que verifica `/api/v1/health/`
- Servidor: Gunicorn com 3 workers e timeout de 60s
- Diretórios criados automaticamente: staticfiles, media, logs

**Build manual da imagem:**

```bash
# Build
docker build -t lacrei-api:latest .

# Run (sem docker-compose)
docker run -d \
  -p 8000:8000 \
  -e DB_HOST=host.docker.internal \
  -e DB_PORT=5432 \
  -e DB_NAME=lacrei_db \
  -e DB_USER=lacrei_user \
  -e DB_PASSWORD=lacrei_pass \
  --name lacrei-web \
  lacrei-api:latest
```

### Docker Compose

O `docker-compose.yml` orquestra todos os serviços necessários:

**Recursos:**

- Networking automático entre containers
- Volumes persistentes para dados
- Healthchecks para garantir disponibilidade
- Variáveis de ambiente configuráveis via `.env`
- Dependências gerenciadas (web espera db estar healthy)

**Arquivo de configuração:** `.env.docker`

```env
# Copie para .env e ajuste conforme necessário
DEBUG=True
SECRET_KEY=change-this-in-production
ALLOWED_HOSTS=localhost,127.0.0.1,web

DB_HOST=db
DB_PORT=5432
DB_NAME=lacrei_db
DB_USER=lacrei_user
DB_PASSWORD=lacrei_pass

DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@lacrei.com
DJANGO_SUPERUSER_PASSWORD=admin123
```

### Entrypoint Script

O script `docker/entrypoint.sh` é executado na inicialização e:

1. ✅ Aguarda PostgreSQL ficar disponível
2. ✅ Cria diretórios necessários (logs, static, media)
3. ✅ Executa migrations automaticamente
4. ✅ Coleta arquivos estáticos
5. ✅ Cria superuser se não existir
6. ✅ Inicia a aplicação (Gunicorn)

### Nginx

Configuração em `docker/nginx.conf`:

- **Proxy reverso:** Encaminha requisições para Django (porta 8000)
- **Static files:** Serve diretamente `/static/` e `/media/`
- **Headers de segurança:** X-Frame-Options, X-Content-Type-Options, etc.
- **Cache:** Headers otimizados para performance
- **Timeouts:** Configurados para 60s

### Volumes Docker

```bash
# Ver volumes criados
docker volume ls | grep lacrei

# Inspecionar volume
docker volume inspect lacrei-saude-api_postgres_data

# Backup do banco de dados
docker-compose exec db pg_dump -U lacrei_user lacrei_db > backup.sql

# Restore do backup
docker-compose exec -T db psql -U lacrei_user lacrei_db < backup.sql
```

### Troubleshooting Docker

**Problema: Container não inicia**

```bash
docker-compose logs web
docker-compose restart web
```

**Problema: Porta já em uso**

```bash
# Alterar porta no docker-compose.yml
ports:
  - "8080:8000"  # Usa 8080 no host ao invés de 8000
```

**Problema: Migrations não aplicadas**

```bash
docker-compose exec web python manage.py migrate
```

**Reset completo:**

```bash
docker-compose down -v  # Remove volumes
docker-compose up --build -d
```

## 🔒 Segurança

Este projeto implementa diversas camadas de segurança:

- **Autenticação JWT:** Tokens com expiração configurável (1h access, 7 dias refresh)
- **Rate Limiting:** Proteção contra abuso (100 req/h anônimo, 1000 req/h autenticado)
- **CORS:** Configurado por ambiente (dev/staging/production)
- **Sanitização de Inputs:** Prevenção de XSS com validadores customizados
- **SQL Injection:** Proteção via ORM + validadores anti-injection
- **HTTPS:** Redirecionamento forçado em produção
- **Logs de Segurança:** Monitoramento de atividades suspeitas
- **Validações:** Camadas múltiplas de validação de dados

### 🛡️ Sanitização e Validação de Inputs

A API implementa validadores customizados no módulo `core` para proteger contra ataques:

**Proteção contra XSS (Cross-Site Scripting):**

```python
# Entrada maliciosa
nome = "<script>alert('XSS')</script>Dr. João Silva"
# Após sanitização: "Dr. João Silva" (tags HTML removidas)
```

**Proteção contra SQL Injection:**

```python
# Entrada maliciosa
nome = "'; DROP TABLE users; --"
# Resultado: ValidationError - "Entrada suspeita detectada"
```

**Campos protegidos automaticamente:**

- **Professional:** nome_social, logradouro, complemento, bairro, cidade, email, telefone
- **Appointment:** paciente_nome, paciente_email, paciente_telefone, observacoes

📖 **Documentação completa:** [core/README.md](core/README.md)

🧪 **Testes de segurança:** 28 testes automatizados com 95% de cobertura

## 🏗️ Arquitetura

### Arquitetura de Produção (AWS)

```
┌─────────────┐
│   Cliente   │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│   CloudFront    │ (CDN)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│      ALB        │ (Load Balancer)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   ECS/Fargate   │ (Containers)
└────┬────────┬───┘
     │        │
     ▼        ▼
┌─────────┐  ┌────────────┐
│   RDS   │  │ ElastiCache│
│PostgreSQL│  │   Redis    │
└─────────┘  └────────────┘
```

### Arquitetura Docker Local

```
┌──────────────────────────────────────┐
│          docker-compose              │
├──────────────────────────────────────┤
│                                      │
│  ┌────────────┐    ┌─────────────┐ │
│  │   Nginx    │◄───┤   Django    │ │
│  │  (port 80) │    │  + Gunicorn │ │
│  │            │    │  (port 8000)│ │
│  └────────────┘    └──────┬──────┘ │
│                           │         │
│                           ▼         │
│                    ┌──────────────┐ │
│                    │  PostgreSQL  │ │
│                    │   (port     │ │
│                    │    5432)     │ │
│                    └──────────────┘ │
│                                      │
│  Volumes:                            │
│  • postgres_data (persistente)       │
│  • static_volume (estáticos)         │
│  • media_volume (uploads)            │
└──────────────────────────────────────┘
```

**Serviços Docker:**

1. **db (PostgreSQL 15)**

   - Banco de dados principal
   - Healthcheck configurado
   - Volume persistente para dados

2. **web (Django + Gunicorn)**

   - Aplicação Python/Django
   - 3 workers Gunicorn
   - Auto-reload em desenvolvimento
   - Migrations e collectstatic automáticos

3. **nginx (Nginx Alpine)**
   - Proxy reverso
   - Serve arquivos estáticos
   - Headers de segurança
   - Cache otimizado

**Características:**

- ✅ **Inicialização automática:** Migrations, collectstatic e superuser
- ✅ **Healthchecks:** Monitora saúde de db e web
- ✅ **Hot reload:** Código atualiza automaticamente em dev
- ✅ **Logs estruturados:** Todos os logs acessíveis via `docker-compose logs`
- ✅ **Isolamento:** Cada serviço em container separado
- ✅ **Persistência:** Dados do banco mantidos em volumes

## 📦 Estrutura do Projeto

```
Lacrei-Saude-API/
├── config/                 # Configurações Django
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── professionals/          # App de profissionais
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
├── appointments/           # App de consultas
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
├── core/                   # Utilidades compartilhadas
│   ├── validators.py
│   └── middleware.py
├── tests/                  # Testes organizados
│   ├── test_professionals.py
│   ├── test_appointments.py
│   └── test_security.py
├── docker/                 # Configurações Docker
│   ├── entrypoint.sh
│   └── nginx.conf
├── .github/workflows/      # GitHub Actions
│   └── ci-cd.yml
├── docs/                   # Documentação adicional
│   ├── DECISOES_TECNICAS.md
│   └── DIARIO.md
├── scripts/                # Scripts utilitários
├── .env.example           # Template de variáveis
├── pyproject.toml         # Dependências Poetry
├── Dockerfile
├── docker-compose.yml
├── pytest.ini
├── PLANO_IMPLEMENTACAO.md
├── CHECKLIST.md
└── README.md
```

## 🚀 Deploy e CI/CD

### Pipeline GitHub Actions

O projeto possui um pipeline completo de CI/CD:

1. **Lint:** Black, Flake8, isort
2. **Tests:** pytest com cobertura
3. **Build:** Construção da imagem Docker
4. **Deploy Staging:** Deploy automático (branch `develop`)
5. **Deploy Production:** Deploy automático (branch `main`)

### Ambientes

- **Staging:** https://staging-api.lacrei.com (branch: develop)
- **Production:** https://api.lacrei.com (branch: main)

### Como fazer deploy

1. **Para Staging:**

```bash
git checkout develop
git add .
git commit -m "feat: nova funcionalidade"
git push origin develop
```

2. **Para Production:**

```bash
git checkout main
git merge develop
git push origin main
```

### Rollback

Em caso de problemas, consulte [docs/ROLLBACK.md](docs/ROLLBACK.md) para procedimentos de rollback.

**Rollback rápido via GitHub Actions:**

```bash
git revert HEAD
git push origin main
```

## 🛠️ Tecnologias Utilizadas

- **Backend:** Python 3.11, Django 5.0, Django REST Framework
- **Database:** PostgreSQL 15
- **Cache:** Redis (opcional)
- **Autenticação:** JWT (Simple JWT)
- **Containerização:** Docker, Docker Compose
- **CI/CD:** GitHub Actions
- **Deploy:** AWS ECS, RDS, ALB, CloudFront
- **Monitoramento:** CloudWatch, Sentry (opcional)
- **Testes:** pytest, pytest-django, pytest-cov
- **Linting:** Black, Flake8, isort
- **Gerenciamento de Dependências:** Poetry

## 📖 Documentação Adicional

- [Plano de Implementação](PLANO_IMPLEMENTACAO.md) - Guia completo fase por fase
- [Checklist](CHECKLIST.md) - Lista de verificação de todas as tarefas
- [Docker - Guia Completo](docker/README.md) - Documentação detalhada do Docker
- [FASE 6 - Docker Completa](FASE_6_DOCKER_COMPLETA.md) - Implementação da containerização
- [Checklist Docker](CHECKLIST_FASE_6.md) - Verificação de funcionalidades Docker
- [Decisões Técnicas](docs/DECISOES_TECNICAS.md) - Justificativas das escolhas
- [Diário de Desenvolvimento](docs/DIARIO.md) - Problemas e soluções
- [Estratégia de Rollback](docs/ROLLBACK.md) - Procedimentos de rollback
- [Validações e Segurança](core/README.md) - Sanitização e validação de inputs

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'feat: Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

### Padrões de Commit

Seguimos o padrão [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` Nova funcionalidade
- `fix:` Correção de bug
- `docs:` Documentação
- `test:` Testes
- `refactor:` Refatoração
- `chore:` Tarefas de manutenção

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 👥 Autor

**Seu Nome**

- GitHub: [@seu-usuario](https://github.com/seu-usuario)
- LinkedIn: [Seu Nome](https://linkedin.com/in/seu-perfil)
- Email: seu.email@example.com

## 🙏 Agradecimentos

- Lacrei Saúde pela oportunidade do desafio
- Comunidade Django e DRF
- Todos os mantenedores das bibliotecas utilizadas

---

**Desenvolvido com ❤️ para o desafio técnico da Lacrei Saúde**
