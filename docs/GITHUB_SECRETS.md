# 🔐 GitHub Secrets - Configuração CI/CD

Este documento lista todos os **secrets** (segredos) que precisam ser configurados no GitHub para o pipeline CI/CD funcionar.

## 📍 Como Adicionar Secrets no GitHub

1. Acesse seu repositório no GitHub
2. Vá em **Settings** → **Secrets and variables** → **Actions**
3. Clique em **New repository secret**
4. Adicione cada secret listado abaixo

---

## 🔑 Secrets Obrigatórios

### 1. Docker Hub (Para Build e Push de Imagens)

#### `DOCKER_USERNAME`

- **Descrição:** Seu username do Docker Hub
- **Exemplo:** `seuusuario`
- **Como obter:** https://hub.docker.com/settings/general

#### `DOCKER_PASSWORD`

- **Descrição:** Token de acesso do Docker Hub (não usar senha!)
- **Como obter:**
  1. Acesse https://hub.docker.com/settings/security
  2. Clique em **New Access Token**
  3. Nome: `github-actions-lacrei`
  4. Copie o token gerado

---

## 🔑 Secrets Opcionais (Para Deploy AWS)

### 2. AWS Credentials (Para Deploy em ECS)

#### `AWS_ACCESS_KEY_ID`

- **Descrição:** ID da chave de acesso AWS
- **Como obter:**
  1. Console AWS → IAM → Users
  2. Selecione seu usuário (ou crie um para CI/CD)
  3. Security credentials → Create access key
  4. Escolha: "Application running outside AWS"

#### `AWS_SECRET_ACCESS_KEY`

- **Descrição:** Chave secreta da AWS
- **Como obter:** Será mostrada junto com o Access Key ID (copie imediatamente!)

**⚠️ Importante:** Crie um usuário IAM específico para CI/CD com permissões limitadas:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ecs:UpdateService",
        "ecs:DescribeServices",
        "ecs:DescribeTaskDefinition",
        "ecs:RegisterTaskDefinition"
      ],
      "Resource": "*"
    }
  ]
}
```

---

### 3. Django Secrets (Para Ambientes)

#### `DJANGO_SECRET_KEY`

- **Descrição:** Chave secreta do Django para produção
- **Como gerar:**
  ```bash
  python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
  ```

#### `DB_PASSWORD`

- **Descrição:** Senha do banco de dados de produção
- **Exemplo:** Senha segura do RDS PostgreSQL

---

## 🌍 Environments (Configuração por Ambiente)

### Configurar Staging Environment

1. **Settings** → **Environments** → **New environment**
2. Nome: `staging`
3. **Environment URL:** `https://staging-api.lacrei.com`
4. **Protection rules:**
   - ✅ Required reviewers (opcional)
   - ✅ Wait timer: 0 minutes

### Configurar Production Environment

1. **Settings** → **Environments** → **New environment**
2. Nome: `production`
3. **Environment URL:** `https://api.lacrei.com`
4. **Protection rules:**
   - ✅ **Required reviewers:** Adicione seu usuário
   - ✅ **Wait timer:** 5 minutes (segurança extra)
   - ✅ **Deployment branches:** Only main branch

---

## ✅ Checklist de Configuração

- [ ] `DOCKER_USERNAME` adicionado
- [ ] `DOCKER_PASSWORD` (token) adicionado
- [ ] `AWS_ACCESS_KEY_ID` adicionado (se usar AWS)
- [ ] `AWS_SECRET_ACCESS_KEY` adicionado (se usar AWS)
- [ ] `DJANGO_SECRET_KEY` adicionado (se necessário)
- [ ] Environment `staging` criado
- [ ] Environment `production` criado com proteção

---

## 🧪 Testando o Pipeline

### 1. Testar CI (Lint + Tests)

```bash
# Crie uma branch de teste
git checkout -b test/ci-pipeline

# Faça alguma alteração
echo "# Test" >> README.md

# Commit e push
git add .
git commit -m "test: CI pipeline"
git push origin test/ci-pipeline

# Crie um Pull Request no GitHub
# O workflow deve rodar automaticamente
```

### 2. Testar Build Docker

```bash
# Merge o PR na branch develop
# O workflow deve:
# 1. Rodar lint
# 2. Rodar testes
# 3. Fazer build da imagem Docker
# 4. Fazer push para Docker Hub
```

### 3. Verificar no Docker Hub

Acesse: `https://hub.docker.com/r/seuusuario/lacrei-api/tags`

Você deve ver tags como:

- `latest`
- `develop-abc123` (SHA do commit)

---

## 🔍 Monitorando Workflows

### Ver execuções:

1. GitHub → Seu repositório
2. Aba **Actions**
3. Clique em qualquer workflow para ver detalhes

### Ver logs:

1. Clique no workflow
2. Clique no job (lint, test, build, etc.)
3. Expanda os steps para ver logs detalhados

### Reexecutar workflow:

1. Abra o workflow que falhou
2. Clique em **Re-run jobs** → **Re-run all jobs**

---

## 🚨 Troubleshooting

### Erro: "Docker login failed"

- ✅ Verifique se `DOCKER_USERNAME` está correto
- ✅ Verifique se `DOCKER_PASSWORD` é um **token**, não sua senha
- ✅ Verifique se o token tem permissão de **Read, Write, Delete**

### Erro: "AWS credentials invalid"

- ✅ Verifique as credenciais no IAM
- ✅ Verifique se o usuário tem as permissões corretas
- ✅ Verifique se não tem espaços em branco nos secrets

### Erro: "Tests failed"

- ✅ Rode os testes localmente primeiro: `poetry run pytest`
- ✅ Verifique os logs do GitHub Actions
- ✅ Verifique se todas as dependências estão no `pyproject.toml`

### Workflow não está rodando

- ✅ Verifique se o arquivo está em `.github/workflows/`
- ✅ Verifique a sintaxe YAML (use um validator online)
- ✅ Verifique os triggers (`on:` section)

---

## 📚 Recursos Adicionais

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker Hub Access Tokens](https://docs.docker.com/docker-hub/access-tokens/)
- [AWS IAM Best Practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html)
- [GitHub Encrypted Secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)

---

## 🔐 Segurança

**NUNCA:**

- ❌ Commite secrets no código
- ❌ Coloque secrets em logs
- ❌ Compartilhe secrets em issues/PRs públicos
- ❌ Use a mesma senha em múltiplos ambientes

**SEMPRE:**

- ✅ Use secrets do GitHub para informações sensíveis
- ✅ Rotacione credenciais regularmente
- ✅ Use tokens com permissões mínimas necessárias
- ✅ Revogue tokens antigos/não utilizados
