# 🏥 Lacrei Saúde API

> API RESTful de Gerenciamento de Consultas Médicas - Desafio Técnico Lacrei Saúde

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.0+-green.svg)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/DRF-3.14+-red.svg)](https://www.django-rest-framework.org/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## 📋 Sobre o Projeto

API funcional, segura e pronta para produção, desenvolvida com foco em qualidade de código, segurança dos dados e boas práticas de desenvolvimento. Este projeto faz parte do processo seletivo da Lacrei Saúde e foi projetado para ser base de integrações futuras.

### ✨ Funcionalidades

- ✅ CRUD completo de profissionais da saúde
- ✅ CRUD completo de consultas médicas
- ✅ Busca de consultas por profissional
- ✅ Autenticação JWT
- ✅ Validação e sanitização de dados
- ✅ Proteção contra SQL Injection e XSS
- ✅ CORS configurado
- ✅ Logs de segurança e acesso
- ✅ Testes automatizados (80%+ cobertura)
- ✅ Docker e Docker Compose
- ✅ CI/CD com GitHub Actions
- ✅ Deploy em AWS (Staging e Produção)

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

1. **Clone e configure:**

```bash
git clone https://github.com/seu-usuario/Lacrei-Saude-API.git
cd Lacrei-Saude-API
cp .env.example .env
```

2. **Inicie os containers:**

```bash
docker-compose up --build
```

3. **Acesse a aplicação:**

- API: http://localhost:8000
- Admin: http://localhost:8000/admin

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
docker-compose run --rm web pytest
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
- [Decisões Técnicas](docs/DECISOES_TECNICAS.md) - Justificativas das escolhas
- [Diário de Desenvolvimento](docs/DIARIO.md) - Problemas e soluções
- [Estratégia de Rollback](docs/ROLLBACK.md) - Procedimentos de rollback

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
