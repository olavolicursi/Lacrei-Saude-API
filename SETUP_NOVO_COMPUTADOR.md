# 💻 Setup em Novo Computador

> Guia completo para configurar o projeto em uma nova máquina

## 🎯 Pré-requisitos

Certifique-se de ter instalado:
- ✅ Python 3.11+ ([Download](https://www.python.org/downloads/))
- ✅ Git ([Download](https://git-scm.com/downloads))
- ✅ Docker Desktop (opcional, mas recomendado) ([Download](https://www.docker.com/products/docker-desktop))
- ✅ PostgreSQL 15+ (se não usar Docker) ([Download](https://www.postgresql.org/download/))

---

## 🚀 Setup Completo (5 passos)

### 1️⃣ Clone o Repositório
```bash
git clone https://github.com/seu-usuario/Lacrei-Saude-API.git
cd Lacrei-Saude-API
```

### 2️⃣ Instale o Poetry
```bash
# Windows (PowerShell)
pip install poetry

# Verifique a instalação
poetry --version
```

### 3️⃣ Instale as Dependências
```bash
# Este comando instala TODAS as dependências do projeto
# Ele lê do pyproject.toml e poetry.lock
poetry install
```

**O que acontece aqui?**
- Poetry lê o `pyproject.toml` (lista de dependências)
- Poetry lê o `poetry.lock` (versões exatas)
- Cria um ambiente virtual automaticamente
- Instala todas as bibliotecas necessárias

### 4️⃣ Configure as Variáveis de Ambiente
```bash
# Copie o template
cp .env.example .env

# Edite o .env com um editor
notepad .env  # Windows
nano .env     # Linux/macOS
```

**Variáveis essenciais para configurar:**
```env
# Gere uma nova SECRET_KEY
DJANGO_SECRET_KEY=cole-aqui-uma-nova-secret-key

# Configurações locais
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (se usar Docker, deixe como está)
DB_NAME=lacrei_db
DB_USER=lacrei_user
DB_PASSWORD=lacrei_pass
DB_HOST=localhost  # ou 'db' se usar docker-compose
DB_PORT=5432
```

**Para gerar uma nova SECRET_KEY:**
```bash
poetry run python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 5️⃣ Suba o Banco de Dados

**Opção A: Com Docker (Recomendado) 🐳**
```bash
# Suba apenas o PostgreSQL
docker-compose up -d db

# Aguarde alguns segundos e verifique
docker-compose ps
```

**Opção B: PostgreSQL Local**
```bash
# Conecte ao PostgreSQL
psql -U postgres

# Crie o database e usuário
CREATE DATABASE lacrei_db;
CREATE USER lacrei_user WITH PASSWORD 'lacrei_pass';
GRANT ALL PRIVILEGES ON DATABASE lacrei_db TO lacrei_user;
\q
```

---

## ✅ Finalize a Configuração

### Execute as Migrations
```bash
poetry run python manage.py migrate
```

### Crie um Superusuário
```bash
poetry run python manage.py createsuperuser
```

### Inicie o Servidor
```bash
poetry run python manage.py runserver
```

### Acesse a Aplicação
- **API:** http://localhost:8000
- **Admin:** http://localhost:8000/admin
- **Docs:** http://localhost:8000/api/docs/

---

## 🐳 Alternativa: Setup 100% com Docker

Se preferir usar Docker para tudo (mais fácil):

```bash
# 1. Clone o repo
git clone https://github.com/seu-usuario/Lacrei-Saude-API.git
cd Lacrei-Saude-API

# 2. Configure o .env
cp .env.example .env
# Edite o .env: DB_HOST=db (importante!)

# 3. Suba tudo
docker-compose up --build

# Pronto! Acesse http://localhost:8000
```

**Para executar comandos no container:**
```bash
# Migrations
docker-compose exec web python manage.py migrate

# Criar superusuário
docker-compose exec web python manage.py createsuperuser

# Testes
docker-compose exec web pytest

# Shell
docker-compose exec web python manage.py shell
```

---

## 🔍 Verificação de Instalação

Execute este checklist para garantir que tudo está funcionando:

```bash
# 1. Poetry instalado?
poetry --version
# Deve mostrar: Poetry (version 1.7.1)

# 2. Dependências instaladas?
poetry show
# Deve listar todas as dependências

# 3. Django funcionando?
poetry run python manage.py --version
# Deve mostrar a versão do Django

# 4. Database conectando?
poetry run python manage.py check --database default
# Deve mostrar: System check identified no issues

# 5. Migrations aplicadas?
poetry run python manage.py showmigrations
# Deve mostrar [X] em todas as migrations

# 6. Testes passando?
poetry run pytest
# Deve mostrar todos os testes verdes
```

---

## 🆘 Problemas Comuns

### "poetry: command not found"
```bash
# Windows: Adicione Poetry ao PATH
# Geralmente em: C:\Users\SeuUsuario\AppData\Roaming\Python\Python311\Scripts

# Ou reinstale
pip install --user poetry
```

### "No module named 'django'"
```bash
# O ambiente virtual não está ativado
# Opção 1: Ative o ambiente
poetry shell

# Opção 2: Use 'poetry run' antes dos comandos
poetry run python manage.py runserver
```

### "FATAL: database does not exist"
```bash
# Certifique-se de que o PostgreSQL está rodando
# Docker:
docker-compose up -d db

# Local:
# Crie o database manualmente (veja passo 5️⃣)
```

### "poetry.lock is out of date"
```bash
# Atualize o lock file
poetry lock --no-update

# Ou reinstale tudo
poetry install
```

### Versões diferentes de dependências
```bash
# Force a instalação das versões exatas do poetry.lock
poetry install --sync

# Se ainda houver problemas, remova o ambiente e reinstale
poetry env remove python
poetry install
```

---

## 📦 Entendendo os Arquivos do Poetry

### pyproject.toml
- Lista de todas as dependências do projeto
- Configurações do projeto (nome, versão, autor)
- Configurações de ferramentas (black, pytest, etc)
- **Você edita este arquivo** quando adiciona/remove dependências

### poetry.lock
- Versões **exatas** de todas as dependências
- Inclui dependências indiretas (dependências das dependências)
- Garante que todos no time usem as mesmas versões
- **NÃO edite manualmente!** É gerado automaticamente

### Por que ambos?
- `pyproject.toml`: "Preciso do Django 5.0 ou maior"
- `poetry.lock`: "Use exatamente Django 5.0.1"
- Resultado: Todos têm o mesmo ambiente

---

## 🔄 Atualizando Dependências

```bash
# Ver dependências desatualizadas
poetry show --outdated

# Atualizar todas as dependências
poetry update

# Atualizar uma específica
poetry update django

# Atualizar e sincronizar
poetry update --sync
```

---

## 👥 Trabalhando em Equipe

### Quando você adiciona uma dependência:
```bash
# 1. Adicione a dependência
poetry add nome-do-pacote

# 2. Commit dos arquivos atualizados
git add pyproject.toml poetry.lock
git commit -m "build: adiciona nome-do-pacote"
git push
```

### Quando alguém adiciona uma dependência:
```bash
# 1. Puxe as mudanças
git pull

# 2. Instale as novas dependências
poetry install

# Pronto! Você tem as mesmas dependências
```

---

## 🎯 Comandos Essenciais do Poetry

```bash
# Instalar dependências do projeto
poetry install

# Ativar ambiente virtual
poetry shell

# Executar comando no ambiente
poetry run python manage.py comando

# Ver dependências instaladas
poetry show

# Adicionar dependência
poetry add pacote

# Remover dependência
poetry remove pacote

# Atualizar dependências
poetry update

# Sair do ambiente virtual
exit
```

---

## 📚 Próximos Passos

Após a instalação:

1. ✅ Leia o [README.md](README.md) para entender o projeto
2. ✅ Consulte [COMANDOS_UTEIS.md](COMANDOS_UTEIS.md) para referência
3. ✅ Execute os testes: `poetry run pytest`
4. ✅ Explore a API: http://localhost:8000/api/docs/
5. ✅ Comece a desenvolver! 🚀

---

## 💡 Dica Pro

Crie um alias para facilitar sua vida:

**Windows (PowerShell):**
```powershell
# Adicione ao seu perfil do PowerShell
function dj { poetry run python manage.py $args }

# Agora pode usar:
dj runserver
dj migrate
dj shell
```

**Linux/macOS (Bash/Zsh):**
```bash
# Adicione ao ~/.bashrc ou ~/.zshrc
alias dj='poetry run python manage.py'

# Agora pode usar:
dj runserver
dj migrate
dj shell
```

---

**Tudo configurado? Você está pronto para desenvolver! 🎉**
