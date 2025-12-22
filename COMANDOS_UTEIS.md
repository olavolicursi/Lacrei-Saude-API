# 🚀 Comandos Úteis - Lacrei Saúde API

## 📦 Poetry

### Clonar Projeto em Novo Computador

```bash
# 1. Clone o repositório
git clone https://github.com/seu-usuario/Lacrei-Saude-API.git
cd Lacrei-Saude-API

# 2. Instale o Poetry (se ainda não tiver)
pip install poetry

# 3. Instale TODAS as dependências do projeto (lê do pyproject.toml e poetry.lock)
poetry install

# 4. Configure o .env
cp .env.example .env
# Edite o .env com suas configurações locais

# 5. Ative o ambiente virtual
poetry shell

# 6. Execute as migrations
poetry run python manage.py migrate

# 7. Crie um superusuário
poetry run python manage.py createsuperuser

# 8. Inicie o servidor
poetry run python manage.py runserver
```

### Instalação e Configuração

```bash
# Instalar Poetry
pip install poetry

# Inicializar projeto (apenas para projetos novos)
poetry init

# Instalar dependências do projeto (lê pyproject.toml e poetry.lock)
poetry install

# Instalar apenas dependências de produção (sem dev)
poetry install --only main
# OU (versões antigas do Poetry)
poetry install --no-dev

# Instalar e sincronizar exatamente com poetry.lock
poetry install --sync

# Adicionar dependência de produção
poetry add nome-do-pacote

# Adicionar dependência de desenvolvimento
poetry add --group dev nome-do-pacote

# Atualizar dependências
poetry update

# Remover dependência
poetry remove nome-do-pacote

# Ativar ambiente virtual
poetry shell

# Executar comando no ambiente
poetry run python manage.py comando
```

## 🎨 Linting e Formatação

### Black (Formatação)

```bash
# Formatar todos os arquivos
poetry run black .

# Verificar sem modificar
poetry run black --check .

# Formatar arquivo específico
poetry run black path/to/file.py
```

### Flake8 (Linting)

```bash
# Verificar todo o projeto
poetry run flake8 .

# Verificar arquivo específico
poetry run flake8 path/to/file.py

# Com configuração customizada
poetry run flake8 --max-line-length=100 .
```

### isort (Ordenação de imports)

```bash
# Ordenar imports
poetry run isort .

# Verificar sem modificar
poetry run isort --check-only .

# Ordenar arquivo específico
poetry run isort path/to/file.py
```

### Rodar todos de uma vez

```bash
poetry run black . && poetry run flake8 . && poetry run isort .
```

## 🗄️ Django

### Gerenciamento do Projeto

```bash
# Criar projeto
poetry run django-admin startproject config .

# Criar app
poetry run python manage.py startapp nome_do_app

# Iniciar servidor
poetry run python manage.py runserver

# Iniciar em porta específica
poetry run python manage.py runserver 8080

# Shell interativo
poetry run python manage.py shell

# Shell Plus (com django-extensions)
poetry run python manage.py shell_plus
```

### Migrations

```bash
# Criar migrations
poetry run python manage.py makemigrations

# Aplicar migrations
poetry run python manage.py migrate

# Ver SQL das migrations
poetry run python manage.py sqlmigrate app_name 0001

# Ver migrations aplicadas
poetry run python manage.py showmigrations

# Reverter migration
poetry run python manage.py migrate app_name 0001_previous

# Fake migration (marcar como aplicada)
poetry run python manage.py migrate --fake app_name 0001
```

### Usuários

```bash
# Criar superusuário
poetry run python manage.py createsuperuser

# Mudar senha
poetry run python manage.py changepassword username
```

### Dados

```bash
# Criar fixtures (backup de dados)
poetry run python manage.py dumpdata > fixtures.json

# Criar fixtures de um app específico
poetry run python manage.py dumpdata app_name > app_fixtures.json

# Carregar fixtures
poetry run python manage.py loaddata fixtures.json

# Flush database (CUIDADO!)
poetry run python manage.py flush
```

### Arquivos Estáticos

```bash
# Coletar arquivos estáticos
poetry run python manage.py collectstatic

# Coletar sem confirmação
poetry run python manage.py collectstatic --noinput
```

## 🧪 Testes

### pytest

```bash
# Rodar todos os testes
poetry run pytest

# Com verbose
poetry run pytest -v

# Com cobertura
poetry run pytest --cov

# Cobertura com relatório HTML
poetry run pytest --cov --cov-report=html

# Abrir relatório HTML
start htmlcov/index.html  # Windows
open htmlcov/index.html   # macOS
xdg-open htmlcov/index.html  # Linux

# Testes específicos
poetry run pytest tests/test_professionals.py
poetry run pytest tests/test_professionals.py::TestProfessionalCRUD
poetry run pytest tests/test_professionals.py::TestProfessionalCRUD::test_create_professional

# Parar no primeiro erro
poetry run pytest -x

# Mostrar print statements
poetry run pytest -s

# Rodar testes em paralelo (com pytest-xdist)
poetry run pytest -n auto

# Rerun apenas testes que falharam
poetry run pytest --lf

# Ver testes lentos
poetry run pytest --durations=10
```

### Django Test Runner (alternativa)

```bash
# Rodar todos os testes
poetry run python manage.py test

# Testar app específico
poetry run python manage.py test professionals

# Teste específico
poetry run python manage.py test professionals.tests.test_models.ProfessionalModelTest.test_creation
```

## 🐳 Docker

### Build e Run

```bash
# Build da imagem
docker build -t lacrei-api .

# Build com docker-compose
docker-compose build

# Subir containers
docker-compose up

# Subir em background
docker-compose up -d

# Rebuild e subir
docker-compose up --build

# Parar containers
docker-compose down

# Parar e remover volumes
docker-compose down -v
```

### Logs e Debug

```bash
# Ver logs
docker-compose logs

# Seguir logs em tempo real
docker-compose logs -f

# Logs de serviço específico
docker-compose logs web

# Executar comando em container
docker-compose exec web python manage.py shell

# Executar comando one-off
docker-compose run --rm web python manage.py migrate

# Listar containers
docker-compose ps

# Entrar no container
docker-compose exec web bash
docker-compose exec db psql -U lacrei_user -d lacrei_db
```

### Limpeza

```bash
# Remover containers parados
docker container prune

# Remover imagens não utilizadas
docker image prune

# Remover tudo não utilizado
docker system prune

# Remover volumes
docker volume prune
```

## 🗃️ PostgreSQL

### Conexão

```bash
# Conectar via psql
psql -h localhost -U lacrei_user -d lacrei_db

# Conectar em container Docker
docker-compose exec db psql -U lacrei_user -d lacrei_db
```

### Comandos SQL Úteis

```sql
-- Listar databases
\l

-- Listar tabelas
\dt

-- Descrever tabela
\d nome_da_tabela

-- Listar usuários
\du

-- Conectar a outro database
\c nome_do_database

-- Executar arquivo SQL
\i path/to/file.sql

-- Sair
\q
```

### Backup e Restore

```bash
# Backup
pg_dump -h localhost -U lacrei_user lacrei_db > backup.sql

# Backup com Docker
docker-compose exec -T db pg_dump -U lacrei_user lacrei_db > backup.sql

# Restore
psql -h localhost -U lacrei_user lacrei_db < backup.sql

# Restore com Docker
docker-compose exec -T db psql -U lacrei_user lacrei_db < backup.sql

# Backup compactado
pg_dump -h localhost -U lacrei_user lacrei_db | gzip > backup.sql.gz

# Restore de backup compactado
gunzip -c backup.sql.gz | psql -h localhost -U lacrei_user lacrei_db
```

## 🚀 Git

### Workflow Básico

```bash
# Status
git status

# Adicionar arquivos
git add .
git add arquivo.py

# Commit
git commit -m "feat: adiciona nova funcionalidade"

# Push
git push origin branch-name

# Pull
git pull origin branch-name

# Criar branch
git checkout -b feature/nova-funcionalidade

# Trocar de branch
git checkout main

# Merge
git merge feature/nova-funcionalidade

# Ver histórico
git log
git log --oneline --graph
```

### Correções

```bash
# Desfazer último commit (mantém mudanças)
git reset --soft HEAD~1

# Desfazer último commit (remove mudanças)
git reset --hard HEAD~1

# Reverter commit específico
git revert commit-hash

# Descartar mudanças locais
git checkout -- arquivo.py
git restore arquivo.py

# Limpar arquivos não rastreados
git clean -fd
```

## ☁️ AWS CLI

### ECS

```bash
# Listar clusters
aws ecs list-clusters

# Listar services
aws ecs list-services --cluster cluster-name

# Descrever service
aws ecs describe-services --cluster cluster-name --services service-name

# Atualizar service (force new deployment)
aws ecs update-service --cluster cluster-name --service service-name --force-new-deployment

# Ver tasks
aws ecs list-tasks --cluster cluster-name --service-name service-name

# Logs
aws logs tail /ecs/service-name --follow
```

### RDS

```bash
# Listar instâncias
aws rds describe-db-instances

# Criar snapshot
aws rds create-db-snapshot --db-instance-identifier instance-name --db-snapshot-identifier snapshot-name

# Restaurar de snapshot
aws rds restore-db-instance-from-db-snapshot --db-instance-identifier new-instance --db-snapshot-identifier snapshot-name
```

## 🔍 Debugging

### Django Debug Toolbar

```python
# settings.py
if DEBUG:
    INSTALLED_APPS += ['debug_toolbar']
    MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
    INTERNAL_IPS = ['127.0.0.1']
```

### IPython

```bash
# Instalar
poetry add --group dev ipython

# Usar no código
import IPython; IPython.embed()
```

### Django Shell Plus

```bash
# Instalar django-extensions
poetry add --group dev django-extensions

# settings.py
INSTALLED_APPS += ['django_extensions']

# Usar
poetry run python manage.py shell_plus

# Com IPython
poetry run python manage.py shell_plus --ipython
```

## 📊 Performance

### Profiling

```bash
# Profile de código
poetry add --group dev line_profiler

# Django Silk (profiling de requests)
poetry add --group dev django-silk
```

### Query Optimization

```python
# No shell
from django.db import connection
from django.db import reset_queries

# Ver queries executadas
print(connection.queries)

# Contar queries
print(len(connection.queries))

# Reset
reset_queries()
```

## 🔐 Segurança

### Gerar SECRET_KEY

```python
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### Verificar segurança

```bash
poetry run python manage.py check --deploy
```

## 📝 Outras Utilidades

### Criar requirements.txt do Poetry

```bash
poetry export -f requirements.txt --output requirements.txt --without-hashes
```

### Ver tamanho do projeto

```bash
# Windows PowerShell
Get-ChildItem -Recurse | Measure-Object -Property Length -Sum

# Linux/macOS
du -sh .
```

### Contar linhas de código

```bash
# Linux/macOS
find . -name '*.py' | xargs wc -l

# Windows PowerShell
Get-ChildItem -Recurse -Include *.py | Get-Content | Measure-Object -Line
```

---

## 📚 Referências Rápidas

- [Django Docs](https://docs.djangoproject.com/)
- [DRF Docs](https://www.django-rest-framework.org/)
- [Poetry Docs](https://python-poetry.org/docs/)
- [Docker Docs](https://docs.docker.com/)
- [PostgreSQL Docs](https://www.postgresql.org/docs/)
- [pytest Docs](https://docs.pytest.org/)
