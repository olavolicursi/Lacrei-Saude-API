# ⚡ Quick Start Guide - Primeiros Passos

> Guia rápido para começar a implementar a API Lacrei Saúde

## 🎯 Primeiro Passo (5 minutos)

### 1. Instale o Poetry
```powershell
# Windows PowerShell
pip install poetry
```

### 2. Verifique a instalação
```powershell
poetry --version
```

---

## 🚀 Setup Inicial (15 minutos)

### 1. Inicialize o projeto Poetry
```powershell
poetry init
```

**Responda as perguntas:**
- Package name: `lacrei-saude-api`
- Version: `0.1.0`
- Description: `API RESTful de Gerenciamento de Consultas Médicas`
- Author: `Seu Nome <seu.email@example.com>`
- License: `MIT`
- Python version: `^3.11`
- Aceite dependências interativas: `no` (vamos adicionar manualmente)

### 2. Adicione as dependências principais
```powershell
poetry add django djangorestframework psycopg2-binary python-decouple django-cors-headers djangorestframework-simplejwt gunicorn
```

### 3. Adicione as dependências de desenvolvimento
```powershell
poetry add --group dev pytest pytest-django pytest-cov black flake8 isort
```

---

## 🏗️ Criar Estrutura Django (10 minutos)

### 1. Ative o ambiente virtual do Poetry
```powershell
poetry shell
```

### 2. Crie o projeto Django
```powershell
poetry run django-admin startproject config .
```

### 3. Crie os apps
```powershell
poetry run python manage.py startapp professionals
poetry run python manage.py startapp appointments
```

### 4. Crie diretórios adicionais
```powershell
mkdir core
mkdir tests
mkdir docker
mkdir docs
mkdir scripts
mkdir .github
mkdir .github\workflows
```

---

## ⚙️ Configuração Básica (20 minutos)

### 1. Configure variáveis de ambiente

**Copie o .env.example:**
```powershell
Copy-Item .env.example .env
```

**Edite o .env com suas configurações:**
```env
DJANGO_SECRET_KEY=cole-aqui-uma-secret-key-gerada
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DB_NAME=lacrei_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
```

**Gere uma SECRET_KEY:**
```powershell
poetry run python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 2. Atualize config/settings.py

**Adicione no topo:**
```python
from decouple import config
import os
```

**Substitua:**
```python
SECRET_KEY = config('DJANGO_SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='').split(',')
```

**Adicione os apps:**
```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third party
    'rest_framework',
    'corsheaders',
    'rest_framework_simplejwt',
    
    # Local apps
    'professionals',
    'appointments',
]
```

**Configure o banco de dados:**
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

---

## 🗄️ Setup PostgreSQL (escolha uma opção)

### Opção A: PostgreSQL Local (Windows)

**1. Baixe e instale:**
- https://www.postgresql.org/download/windows/

**2. Crie o database:**
```powershell
# Abra o SQL Shell (psql)
CREATE DATABASE lacrei_db;
CREATE USER lacrei_user WITH PASSWORD 'lacrei_pass';
ALTER ROLE lacrei_user SET client_encoding TO 'utf8';
ALTER ROLE lacrei_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE lacrei_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE lacrei_db TO lacrei_user;
```

### Opção B: Docker (Recomendado)

**1. Crie docker-compose.yml temporário:**
```yaml
version: '3.9'

services:
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: lacrei_db
      POSTGRES_USER: lacrei_user
      POSTGRES_PASSWORD: lacrei_pass
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

**2. Suba o PostgreSQL:**
```powershell
docker-compose up -d db
```

---

## ✅ Primeiro Teste (5 minutos)

### 1. Execute as migrações iniciais
```powershell
poetry run python manage.py migrate
```

### 2. Crie um superusuário
```powershell
poetry run python manage.py createsuperuser
```

### 3. Inicie o servidor
```powershell
poetry run python manage.py runserver
```

### 4. Acesse no navegador
- API: http://localhost:8000
- Admin: http://localhost:8000/admin

**Se viu a página de boas-vindas do Django, funcionou! 🎉**

---

## 📋 Próximos Passos

Agora que o ambiente está configurado, siga a ordem:

1. **[CHECKLIST.md](CHECKLIST.md)** - Fase 2: Modelagem e Banco de Dados
2. Implementar o modelo `Professional`
3. Implementar o modelo `Appointment`
4. Criar migrations
5. Testar no Django Admin

---

## 🆘 Problemas Comuns

### "poetry: command not found"
```powershell
# Reinstale o Poetry
pip install --user poetry

# Adicione ao PATH (Windows)
# Geralmente em: C:\Users\SeuUsuario\AppData\Roaming\Python\Python311\Scripts
```

### "psycopg2 installation error"
```powershell
# Use psycopg2-binary em vez de psycopg2
poetry add psycopg2-binary
```

### "FATAL: database 'lacrei_db' does not exist"
```powershell
# Certifique-se de que criou o database
# Ou use Docker (opção mais fácil)
```

### "Could not find .env file"
```powershell
# Certifique-se de que copiou o .env.example
Copy-Item .env.example .env
```

---

## 📚 Documentação de Referência

Durante o desenvolvimento, consulte:

1. **[CHECKLIST.md](CHECKLIST.md)** - Para saber o que fazer
2. **[PLANO_IMPLEMENTACAO.md](PLANO_IMPLEMENTACAO.md)** - Para detalhes de implementação
3. **[COMANDOS_UTEIS.md](COMANDOS_UTEIS.md)** - Para comandos específicos
4. **[RESUMO_EXECUTIVO.md](RESUMO_EXECUTIVO.md)** - Para visão geral

---

## ⏱️ Tempo Investido Até Agora

- ✅ Instalação Poetry: 5 min
- ✅ Setup inicial: 15 min
- ✅ Estrutura Django: 10 min
- ✅ Configuração básica: 20 min
- ✅ Setup PostgreSQL: 10 min (Docker) ou 20 min (Local)
- ✅ Primeiro teste: 5 min

**Total: ~1 hora** ⏰

---

## 🎯 Checklist Rápido

- [ ] Poetry instalado e funcionando
- [ ] Projeto Django criado
- [ ] Apps professionals e appointments criados
- [ ] .env configurado
- [ ] PostgreSQL rodando
- [ ] Migrations executadas com sucesso
- [ ] Superusuário criado
- [ ] Servidor Django rodando
- [ ] Admin acessível

**Todos os itens marcados? Você está pronto para a Fase 2! 🚀**

---

## 💡 Dica Final

Mantenha uma janela com este arquivo aberto e outra com o CHECKLIST.md. Vá marcando os itens conforme completa e consultando o plano detalhado quando precisar de mais informações.

**Boa implementação! 💪**
