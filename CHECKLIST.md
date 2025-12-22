# ✅ Checklist de Implementação - Lacrei Saúde API

## 📋 FASE 1: Configuração do Ambiente

### Setup Python e Poetry
- [ ] Instalar Python 3.11+
- [ ] Instalar Poetry: `pip install poetry`
- [ ] Executar: `poetry init`
- [ ] Configurar `pyproject.toml` com metadados do projeto

### Dependências Base
- [ ] `poetry add django`
- [ ] `poetry add djangorestframework`
- [ ] `poetry add psycopg2-binary`
- [ ] `poetry add python-decouple`
- [ ] `poetry add django-cors-headers`
- [ ] `poetry add djangorestframework-simplejwt`
- [ ] `poetry add gunicorn`
- [ ] `poetry add --group dev pytest`
- [ ] `poetry add --group dev pytest-django`
- [ ] `poetry add --group dev pytest-cov`
- [ ] `poetry add --group dev black`
- [ ] `poetry add --group dev flake8`
- [ ] `poetry add --group dev isort`

### Estrutura do Projeto
- [ ] `poetry run django-admin startproject config .`
- [ ] `poetry run python manage.py startapp professionals`
- [ ] `poetry run python manage.py startapp appointments`
- [ ] `mkdir core tests docker docs scripts`
- [ ] `mkdir .github/workflows`

### Arquivos de Configuração
- [ ] Criar `.env.example`
- [ ] Criar `.env` local
- [ ] Atualizar `.gitignore`
- [ ] Configurar `settings.py` com `python-decouple`

---

## 📋 FASE 2: Modelagem e Banco de Dados

### Models
- [ ] Implementar modelo `Professional` em `professionals/models.py`
- [ ] Implementar modelo `Appointment` em `appointments/models.py`
- [ ] Adicionar validators customizados
- [ ] Configurar Meta classes (ordering, indexes)
- [ ] Adicionar `__str__` methods

### Migrations
- [ ] `poetry run python manage.py makemigrations`
- [ ] Revisar arquivos de migration
- [ ] `poetry run python manage.py migrate`
- [ ] Criar fixtures para dados de teste

### Admin
- [ ] Registrar models no Django Admin
- [ ] Customizar admin interfaces
- [ ] Testar CRUD via admin

---

## 📋 FASE 3: Implementação do CRUD

### Serializers
- [ ] Criar `ProfessionalSerializer` em `professionals/serializers.py`
- [ ] Criar `AppointmentSerializer` em `appointments/serializers.py`
- [ ] Adicionar validações customizadas
- [ ] Implementar campos read-only apropriados

### Views/ViewSets
- [ ] Implementar `ProfessionalViewSet`
- [ ] Implementar `AppointmentViewSet`
- [ ] Adicionar filtros (DjangoFilterBackend)
- [ ] Adicionar busca (SearchFilter)
- [ ] Implementar query para consultas por profissional

### URLs
- [ ] Configurar router no `config/urls.py`
- [ ] Registrar viewsets
- [ ] Testar endpoints no navegador/Postman

### Testes Manuais
- [ ] GET `/api/v1/professionals/`
- [ ] POST `/api/v1/professionals/`
- [ ] GET `/api/v1/professionals/{id}/`
- [ ] PUT `/api/v1/professionals/{id}/`
- [ ] DELETE `/api/v1/professionals/{id}/`
- [ ] GET `/api/v1/appointments/`
- [ ] POST `/api/v1/appointments/`
- [ ] GET `/api/v1/appointments/?professional_id={id}`

---

## 📋 FASE 4: Segurança e Validações

### Autenticação JWT
- [ ] Configurar SimpleJWT no `settings.py`
- [ ] Adicionar endpoints de token (obtain, refresh)
- [ ] Criar usuário de teste
- [ ] Testar autenticação

### CORS
- [ ] Instalar e configurar `django-cors-headers`
- [ ] Configurar origens permitidas
- [ ] Testar com frontend local

### Validações e Sanitização
- [ ] Criar `core/validators.py`
- [ ] Implementar sanitização de HTML
- [ ] Implementar validação anti-SQL injection
- [ ] Adicionar validators aos models e serializers

### Logging
- [ ] Configurar logging no `settings.py`
- [ ] Criar diretório `logs/`
- [ ] Implementar middleware de segurança customizado
- [ ] Testar logs

### Configurações de Segurança
- [ ] `SECRET_KEY` via variável de ambiente
- [ ] `DEBUG = False` em produção
- [ ] Configurar `ALLOWED_HOSTS`
- [ ] `SECURE_SSL_REDIRECT = True`
- [ ] `SESSION_COOKIE_SECURE = True`
- [ ] `CSRF_COOKIE_SECURE = True`

---

## 📋 FASE 5: Testes Automatizados

### Configuração
- [ ] Criar `pytest.ini`
- [ ] Criar `conftest.py` com fixtures
- [ ] Configurar database de teste

### Testes de Profissionais
- [ ] Teste: Listar profissionais
- [ ] Teste: Criar profissional válido
- [ ] Teste: Criar profissional inválido
- [ ] Teste: Atualizar profissional
- [ ] Teste: Deletar profissional
- [ ] Teste: Validação de email
- [ ] Teste: Validação de telefone

### Testes de Consultas
- [ ] Teste: Listar consultas
- [ ] Teste: Criar consulta
- [ ] Teste: Vincular consulta a profissional
- [ ] Teste: Buscar consultas por profissional
- [ ] Teste: Atualizar status da consulta
- [ ] Teste: Validação de data/hora

### Testes de Segurança
- [ ] Teste: Requisição não autenticada
- [ ] Teste: Tentativa de SQL injection
- [ ] Teste: Tentativa de XSS
- [ ] Teste: Rate limiting

### Cobertura
- [ ] Executar: `poetry run pytest --cov`
- [ ] Verificar cobertura mínima de 80%
- [ ] Gerar relatório HTML: `poetry run pytest --cov --cov-report=html`

---

## 📋 FASE 6: Docker e Containerização

### Arquivos Docker
- [ ] Criar `Dockerfile`
- [ ] Criar `docker-compose.yml`
- [ ] Criar `docker/entrypoint.sh`
- [ ] Criar `docker/nginx.conf`
- [ ] Tornar entrypoint executável: `chmod +x docker/entrypoint.sh`

### Build e Teste Local
- [ ] `docker-compose build`
- [ ] `docker-compose up`
- [ ] Testar acesso em `http://localhost:8000`
- [ ] Verificar logs: `docker-compose logs -f`

### Verificações
- [ ] Container web iniciando corretamente
- [ ] Container db conectando
- [ ] Migrations rodando automaticamente
- [ ] Static files servidos
- [ ] API respondendo

---

## 📋 FASE 7: CI/CD com GitHub Actions

### Configuração
- [ ] Criar `.github/workflows/ci-cd.yml`
- [ ] Configurar job de lint
- [ ] Configurar job de testes
- [ ] Configurar job de build
- [ ] Configurar jobs de deploy

### Secrets no GitHub
- [ ] Adicionar `DOCKER_USERNAME`
- [ ] Adicionar `DOCKER_PASSWORD`
- [ ] Adicionar `AWS_ACCESS_KEY_ID`
- [ ] Adicionar `AWS_SECRET_ACCESS_KEY`
- [ ] Adicionar `DJANGO_SECRET_KEY`

### Scripts
- [ ] Criar `scripts/deploy-ecs.sh`
- [ ] Criar `scripts/smoke-tests.sh`
- [ ] Tornar scripts executáveis

### Testes
- [ ] Fazer commit e push
- [ ] Verificar pipeline no GitHub Actions
- [ ] Corrigir erros de lint
- [ ] Garantir que testes passam

---

## 📋 FASE 8: Deploy AWS

### Planejamento
- [ ] Documentar arquitetura AWS
- [ ] Listar recursos necessários
- [ ] Estimar custos

### VPC e Rede (opcional Terraform)
- [ ] Criar VPC
- [ ] Criar subnets (públicas e privadas)
- [ ] Configurar Internet Gateway
- [ ] Configurar NAT Gateway
- [ ] Configurar Security Groups

### RDS PostgreSQL
- [ ] Criar instância RDS Staging
- [ ] Criar instância RDS Production
- [ ] Configurar backups automáticos
- [ ] Configurar parameter groups
- [ ] Testar conexão

### ECS/Fargate
- [ ] Criar cluster ECS Staging
- [ ] Criar cluster ECS Production
- [ ] Criar Task Definitions
- [ ] Criar Services
- [ ] Configurar Auto Scaling

### Load Balancer
- [ ] Criar Application Load Balancer
- [ ] Configurar Target Groups
- [ ] Configurar Health Checks
- [ ] Configurar HTTPS/SSL

### Deploy
- [ ] Deploy manual em Staging
- [ ] Verificar funcionamento
- [ ] Deploy via GitHub Actions em Staging
- [ ] Deploy em Production

---

## 📋 FASE 9: Documentação

### README Principal
- [ ] Seção de introdução
- [ ] Setup local
- [ ] Setup com Docker
- [ ] Instruções de testes
- [ ] Documentação da API
- [ ] Arquitetura
- [ ] Deploy e CI/CD
- [ ] Rollback

### Documentação da API
- [ ] Instalar `drf-spectacular`
- [ ] Configurar Swagger
- [ ] Configurar ReDoc
- [ ] Adicionar docstrings nos endpoints
- [ ] Testar documentação gerada

### Documentação Técnica
- [ ] Criar `docs/DECISOES_TECNICAS.md`
- [ ] Documentar escolhas de tecnologia
- [ ] Justificar decisões arquiteturais
- [ ] Criar `docs/DIARIO.md`
- [ ] Documentar problemas encontrados
- [ ] Documentar soluções aplicadas

### Diagramas
- [ ] Diagrama de arquitetura AWS
- [ ] Diagrama de fluxo de dados
- [ ] Diagrama de CI/CD pipeline
- [ ] Diagrama de database

---

## 📋 FASE 10: Melhorias e Bônus

### Integração Asaas (Bônus)
- [ ] Estudar documentação Asaas
- [ ] Criar conta sandbox
- [ ] Implementar `payments/services.py`
- [ ] Implementar webhook handler
- [ ] Criar mock para testes
- [ ] Documentar integração proposta

### Documentação API Avançada
- [ ] Configurar Swagger UI completo
- [ ] Adicionar exemplos de requisições
- [ ] Documentar códigos de erro
- [ ] Criar collection do Postman

### Performance
- [ ] Adicionar Redis para cache
- [ ] Implementar cache em endpoints
- [ ] Otimizar queries com select_related
- [ ] Adicionar índices adicionais no DB

### Monitoring
- [ ] Integrar Sentry
- [ ] Configurar Prometheus metrics
- [ ] Configurar CloudWatch alarms
- [ ] Criar dashboard de monitoramento

### Rollback
- [ ] Documentar estratégia Blue-Green
- [ ] Implementar scripts de rollback
- [ ] Testar rollback em Staging
- [ ] Documentar processo completo

---

## 📊 Verificação Final

### Requisitos Obrigatórios
- [ ] ✅ CRUD completo de profissionais
- [ ] ✅ CRUD completo de consultas
- [ ] ✅ Busca de consultas por profissional
- [ ] ✅ Sanitização e validação de dados
- [ ] ✅ Proteção contra SQL Injection
- [ ] ✅ CORS configurado
- [ ] ✅ Autenticação implementada
- [ ] ✅ Logs de acesso e erros
- [ ] ✅ Django + DRF + Poetry + PostgreSQL
- [ ] ✅ Docker funcional
- [ ] ✅ GitHub Actions CI/CD
- [ ] ✅ Testes com APITestCase (80%+ cobertura)
- [ ] ✅ Deploy Staging e Production
- [ ] ✅ README completo
- [ ] ✅ Documentação técnica
- [ ] ✅ Proposta de rollback

### Bônus
- [ ] ⭐ Integração Asaas
- [ ] ⭐ Swagger/ReDoc
- [ ] ⭐ Cache Redis
- [ ] ⭐ Monitoring avançado
- [ ] ⭐ Performance optimization

---

## 🎉 Finalização

- [ ] Revisão completa do código
- [ ] Linting em todo o projeto
- [ ] Todos os testes passando
- [ ] Coverage report gerado
- [ ] README revisado
- [ ] Documentação completa
- [ ] Deploy funcionando
- [ ] Smoke tests passando
- [ ] Criar release tag
- [ ] Preparar apresentação do projeto

---

**Status Geral:** 0% completo
**Última atualização:** 22/12/2025
