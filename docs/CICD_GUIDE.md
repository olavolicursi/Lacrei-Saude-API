# 🚀 CI/CD Pipeline - Guia Completo

## 📋 O que é CI/CD?

### CI - Continuous Integration (Integração Contínua)

Automatiza a **validação** do código sempre que você faz um commit:

- 🔍 **Lint** - Verifica formatação e estilo do código
- 🧪 **Tests** - Executa todos os testes automaticamente
- 📊 **Coverage** - Mede a cobertura de testes
- 🏗️ **Build** - Verifica se a aplicação compila/constrói

**Benefício:** Detecta problemas **imediatamente**, antes de chegar em produção.

### CD - Continuous Deployment/Delivery (Entrega Contínua)

Automatiza o **deploy** da aplicação:

- 📦 Constrói imagem Docker automaticamente
- 🚢 Faz deploy em staging (branch `develop`)
- 🌐 Faz deploy em produção (branch `main`)
- ✅ Valida a aplicação após deploy (smoke tests)

**Benefício:** Deploy **rápido, seguro e sem erros manuais**.

---

## 🏗️ Nossa Pipeline

```
┌─────────────┐
│  Git Push   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│    LINT     │ ← Black, Flake8, isort
└──────┬──────┘
       │
       ▼
┌─────────────┐
│    TESTS    │ ← Pytest + Coverage
└──────┬──────┘
       │
       ▼
┌─────────────┐
│    BUILD    │ ← Docker Image
└──────┬──────┘
       │
       ├──────────────┬──────────────┐
       ▼              ▼              ▼
┌──────────┐   ┌──────────┐   ┌──────────┐
│  Develop │   │   Main   │   │    PR    │
└────┬─────┘   └────┬─────┘   └──────────┘
     │              │
     ▼              ▼
┌─────────┐   ┌──────────┐
│ STAGING │   │   PROD   │
└─────────┘   └──────────┘
```

---

## 📁 Estrutura de Arquivos

```
.github/
└── workflows/
    ├── ci-cd.yml      # Pipeline principal (lint → test → build → deploy)
    └── tests.yml      # Apenas testes (para PRs rápidos)

scripts/
├── deploy-ecs.sh      # Deploy para AWS ECS
└── smoke-tests.sh     # Testes de sanidade pós-deploy

docs/
└── GITHUB_SECRETS.md  # Configuração de secrets
```

---

## 🔄 Fluxo de Trabalho

### 1️⃣ Desenvolvimento Local

```bash
# Criar feature branch
git checkout -b feature/nova-funcionalidade

# Desenvolver e testar localmente
poetry run pytest
poetry run black .
poetry run flake8 .

# Commit
git add .
git commit -m "feat: adiciona nova funcionalidade"
git push origin feature/nova-funcionalidade
```

### 2️⃣ Pull Request

```bash
# Criar PR no GitHub
# ✅ Workflow "tests.yml" roda automaticamente
# ✅ Verifica lint
# ✅ Executa testes
# ✅ Mostra cobertura
```

### 3️⃣ Merge para Develop (Staging)

```bash
git checkout develop
git merge feature/nova-funcionalidade
git push origin develop

# ✅ CI/CD completo roda
# ✅ Build da imagem Docker
# ✅ Push para Docker Hub (tag: develop-abc123)
# ✅ Deploy automático em STAGING
# ✅ Smoke tests
```

### 4️⃣ Release para Production

```bash
git checkout main
git merge develop
git push origin main

# ✅ CI/CD completo roda
# ✅ Build da imagem Docker
# ✅ Push para Docker Hub (tag: latest)
# ✅ Deploy automático em PRODUCTION (requer aprovação!)
# ✅ Smoke tests
# ✅ Notificação de sucesso
```

---

## 🎯 Workflows Disponíveis

### 1. `ci-cd.yml` - Pipeline Completo

**Triggers:**

- Push em `main` ou `develop`
- Pull Requests para `main` ou `develop`

**Jobs:**

#### Job 1: `lint` (Code Quality)

- ✅ Black - formatação de código
- ✅ Flake8 - linting (erros e warnings)
- ✅ isort - ordenação de imports

#### Job 2: `test` (Testes)

- ✅ Inicia PostgreSQL temporário
- ✅ Roda migrations
- ✅ Executa pytest com coverage
- ✅ Upload coverage para Codecov
- ✅ Gera relatório HTML

#### Job 3: `build` (Docker)

- ✅ Constrói imagem Docker
- ✅ Push para Docker Hub
- ✅ Cache de layers para builds rápidos
- ✅ Tags: `latest`, `develop-SHA`, `main-SHA`

#### Job 4: `deploy-staging`

- ✅ Só roda em push para `develop`
- ✅ Deploy automático em staging
- ✅ Smoke tests
- ⚠️ (Requer AWS configurada)

#### Job 5: `deploy-production`

- ✅ Só roda em push para `main`
- ✅ Requer aprovação manual (proteção!)
- ✅ Deploy em produção
- ✅ Smoke tests completos
- ⚠️ (Requer AWS configurada)

---

### 2. `tests.yml` - Apenas Testes

**Triggers:**

- Pull Requests
- Execução manual (workflow_dispatch)

**Uso:** PRs rápidos, validação de código

---

## 🔐 Configuração de Secrets

Veja o arquivo completo: [`docs/GITHUB_SECRETS.md`](./GITHUB_SECRETS.md)

**Secrets obrigatórios:**

- `DOCKER_USERNAME` - Username do Docker Hub
- `DOCKER_PASSWORD` - Token do Docker Hub

**Secrets opcionais (AWS):**

- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`

---

## 🧪 Testando a Pipeline

### Teste 1: Verificar Lint

```bash
# Causa erro de formatação propositalmente
echo "x=1" >> test.py

git add test.py
git commit -m "test: lint"
git push

# Veja o workflow falhar no GitHub Actions
# Corrija com: poetry run black .
```

### Teste 2: Verificar Tests

```bash
# Adicione um teste que falha
# Veja no GitHub Actions
# Corrija o teste
```

### Teste 3: Build Docker

```bash
# Push para develop
git checkout develop
git push origin develop

# Verifique no Docker Hub:
# https://hub.docker.com/r/seuusuario/lacrei-api/tags
```

---

## 📊 Monitoramento

### Ver Status dos Workflows

1. GitHub → Seu repositório
2. Aba **Actions**
3. Lista de workflows executados

### Badges no README

Adicione badges para mostrar status:

```markdown
[![CI/CD](https://github.com/seu-usuario/Lacrei-Saude-API/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/seu-usuario/Lacrei-Saude-API/actions/workflows/ci-cd.yml)
[![Tests](https://github.com/seu-usuario/Lacrei-Saude-API/actions/workflows/tests.yml/badge.svg)](https://github.com/seu-usuario/Lacrei-Saude-API/actions/workflows/tests.yml)
[![codecov](https://codecov.io/gh/seu-usuario/Lacrei-Saude-API/branch/main/graph/badge.svg)](https://codecov.io/gh/seu-usuario/Lacrei-Saude-API)
```

---

## 🚨 Troubleshooting

### Pipeline falhando em "lint"

```bash
# Rode localmente
poetry run black --check .
poetry run flake8 .
poetry run isort --check-only .

# Corrija
poetry run black .
poetry run isort .
```

### Pipeline falhando em "test"

```bash
# Rode localmente
poetry run pytest -v

# Verifique logs detalhados no GitHub Actions
```

### Build Docker falhando

- Verifique se `DOCKER_USERNAME` e `DOCKER_PASSWORD` estão corretos
- Verifique se o Dockerfile está válido
- Teste build local: `docker build -t test .`

### Deploy não está rodando

- Verifique se está na branch correta (`develop` → staging, `main` → production)
- Verifique se os environments estão configurados no GitHub

---

## 🎓 Boas Práticas

### ✅ DO (Faça)

- Rode testes localmente antes de push
- Use commits semânticos: `feat:`, `fix:`, `test:`
- Mantenha PRs pequenos e focados
- Revise os logs dos workflows
- Configure proteção de branch em `main`

### ❌ DON'T (Não Faça)

- Push direto em `main` sem PR
- Ignorar falhas de lint
- Commitar código sem testes
- Pular code review
- Desabilitar proteções para "ir mais rápido"

---

## 📈 Próximos Passos

1. **Agora:** Configure os secrets no GitHub
2. **Depois:** Teste o pipeline com um PR
3. **Em seguida:** Configure AWS para deploy real
4. **Futuro:** Adicione testes de integração E2E

---

## 📚 Recursos

- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [Docker Hub](https://hub.docker.com)
- [Codecov](https://codecov.io)
- [AWS ECS](https://aws.amazon.com/ecs/)

---

**🎉 Pronto! Sua pipeline CI/CD está configurada!**
