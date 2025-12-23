# 🔒 Guia de Segurança - Lacrei Saúde API

Este documento descreve todas as configurações de segurança implementadas na API e como configurá-las corretamente para cada ambiente.

---

## 🎯 Visão Geral

A API implementa múltiplas camadas de segurança seguindo as melhores práticas recomendadas pela OWASP e Django Security Guidelines.

### Camadas de Segurança Implementadas:

1. **Autenticação JWT** - Tokens stateless com expiração
2. **HTTPS/SSL** - Criptografia em trânsito
3. **Headers de Segurança** - Proteção contra ataques comuns
4. **Detecção de Ameaças** - Middleware customizado
5. **Rate Limiting** - Proteção contra DDoS e força bruta
6. **Sanitização de Inputs** - Prevenção de SQL Injection e XSS
7. **Logging de Segurança** - Auditoria e monitoramento

---

## 🔐 Configurações por Ambiente

### Development (Desenvolvimento)

**Características:**

- DEBUG=True
- SSL opcional
- Cookies sem flag secure
- CORS permissivo
- Email no console

**Arquivo .env:**

```env
ENVIRONMENT=development
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
SECURE_SSL_REDIRECT=False
```

### Staging (Homologação)

**Características:**

- DEBUG=False
- SSL recomendado
- Cookies com flag secure
- CORS restrito
- Email real (opcional)

**Arquivo .env:**

```env
ENVIRONMENT=staging
DEBUG=False
ALLOWED_HOSTS=staging-api.lacrei.com
SECURE_SSL_REDIRECT=True
```

### Production (Produção)

**Características:**

- DEBUG=False (obrigatório)
- SSL obrigatório
- HSTS ativado
- Cookies secure
- CORS muito restrito
- Monitoramento ativo

**Arquivo .env:**

```env
ENVIRONMENT=production
DEBUG=False
ALLOWED_HOSTS=api.lacrei.com,www.api.lacrei.com
SECURE_SSL_REDIRECT=True
ADMIN_EMAIL=admin@lacrei.com
```

---

## 🛡️ Configurações de Segurança Detalhadas

### 1. Secret Key

**O que é:** Chave usada para criptografia, assinatura de tokens, cookies CSRF, etc.

**Configuração:**

```python
DJANGO_SECRET_KEY=<chave-aleatoria-de-50-caracteres>
```

**Como gerar:**

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

**⚠️ CRÍTICO:**

- NUNCA use a mesma chave em dev/staging/prod
- NUNCA commite a secret key no Git
- Mude imediatamente se comprometida

---

### 2. HTTPS/SSL

**Settings aplicados em produção:**

```python
SECURE_SSL_REDIRECT = True              # Redireciona HTTP → HTTPS
SECURE_HSTS_SECONDS = 31536000          # HSTS por 1 ano
SECURE_HSTS_INCLUDE_SUBDOMAINS = True   # HSTS em subdomínios
SECURE_HSTS_PRELOAD = True              # Permite HSTS preload list
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
```

**Checklist SSL:**

- [ ] Certificado SSL válido instalado
- [ ] Redirecionamento HTTP → HTTPS configurado
- [ ] HSTS headers configurados
- [ ] Teste em https://www.ssllabs.com/ssltest/

---

### 3. Cookies Seguros

**Configurações:**

```python
# Session Cookies
SESSION_COOKIE_SECURE = True          # Apenas HTTPS
SESSION_COOKIE_HTTPONLY = True        # Não acessível via JS
SESSION_COOKIE_SAMESITE = 'Lax'       # Proteção CSRF
SESSION_COOKIE_AGE = 86400            # Expira em 24h
SESSION_COOKIE_NAME = 'lacrei_sessionid'  # Nome customizado

# CSRF Cookies
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_NAME = 'lacrei_csrftoken'
```

**Por que customizar nomes?**
Nomes padrão revelam que o site usa Django, facilitando ataques direcionados.

---

### 4. Headers de Segurança

#### X-Content-Type-Options

```python
SECURE_CONTENT_TYPE_NOSNIFF = True
```

Previne que navegadores "adivinhem" o tipo MIME de arquivos.

#### X-Frame-Options

```python
X_FRAME_OPTIONS = 'DENY'
```

Previne clickjacking bloqueando iframes.

#### X-XSS-Protection

```python
SECURE_BROWSER_XSS_FILTER = True
```

Ativa filtro XSS do navegador.

**Verificar headers:**

```bash
curl -I https://api.lacrei.com
```

Deve retornar:

```
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
```

---

### 5. Content Security Policy (CSP)

**Status:** Preparado mas desabilitado por padrão

**Para ativar, adicione ao settings.py:**

```python
CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC = ("'self'",)
CSP_STYLE_SRC = ("'self'",)
CSP_IMG_SRC = ("'self'", "data:", "https:")
```

**Recomendação:** Configure CSP conforme necessidades do frontend.

---

### 6. Password Validation

**Validators ativos:**

1. **UserAttributeSimilarityValidator** - Senha não pode ser similar ao username/email
2. **MinimumLengthValidator** - Mínimo 8 caracteres
3. **CommonPasswordValidator** - Bloqueia senhas comuns (123456, password, etc)
4. **NumericPasswordValidator** - Senha não pode ser apenas números

**Customizar:**

```python
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': '...',
        'OPTIONS': {
            'min_length': 12,  # Aumentar para 12 caracteres
        }
    },
]
```

---

### 7. Rate Limiting

**Configurado no REST_FRAMEWORK:**

```python
'DEFAULT_THROTTLE_RATES': {
    'anon': '100/hour',    # Usuários não autenticados
    'user': '1000/hour',   # Usuários autenticados
}
```

**Middleware SecurityDetection:**

- 100 requisições/minuto por IP
- Auto-blacklist com score ≥ 10

**Customizar por endpoint:**

```python
from rest_framework.decorators import throttle_classes
from rest_framework.throttling import UserRateThrottle

class OncePerDayUserThrottle(UserRateThrottle):
    rate = '1/day'

@throttle_classes([OncePerDayUserThrottle])
def sensitive_endpoint(request):
    pass
```

---

### 8. CORS (Cross-Origin Resource Sharing)

**Development:**

```python
CORS_ALLOW_ALL_ORIGINS = True  # Permite qualquer origem
```

**Staging:**

```python
CORS_ALLOWED_ORIGINS = [
    "https://staging.lacrei.com",
    "http://localhost:3000",
]
```

**Production:**

```python
CORS_ALLOWED_ORIGINS = [
    "https://lacrei.com",
    "https://www.lacrei.com",
]
```

**Métodos permitidos:**

- GET, POST, PUT, PATCH, DELETE, OPTIONS

**Headers expostos:**

- Content-Type, X-CSRFToken

---

### 9. Upload Limits

**Proteção contra uploads grandes:**

```python
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5 MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5 MB
```

**Aumentar se necessário:**

- Para imagens de perfil: até 10 MB
- Para documentos: até 20 MB
- Para vídeos: considere upload direto para S3

---

### 10. Detecção de Ameaças

**Middleware SecurityDetection protege contra:**

✅ **SQL Injection**

- Padrões: UNION SELECT, DROP TABLE, OR 1=1, etc
- Bloqueio: Imediato com HTTP 403
- Score: +5 pontos

✅ **XSS (Cross-Site Scripting)**

- Padrões: `<script>`, `javascript:`, event handlers
- Bloqueio: Imediato com HTTP 403
- Score: +3 pontos

✅ **Path Traversal**

- Padrões: `../`, `..\\`, encoded variants
- Bloqueio: Imediato com HTTP 403
- Score: +4 pontos

✅ **User-Agents Suspeitos**

- Detecta: sqlmap, nikto, nmap, burp, metasploit
- Bloqueio: Não (apenas alerta)
- Score: +1 ponto

**Auto-blacklist:**

- Threshold: 10 pontos
- Duração: 1 hora
- Log: `logs/security.log`

**Gerenciar IPs:**

```bash
# Ver status de um IP
poetry run python manage_security.py status 192.168.1.100

# Remover da blacklist
poetry run python manage_security.py clear-blacklist 192.168.1.100

# Adicionar à whitelist
poetry run python manage_security.py whitelist-add 192.168.1.50

# Limpar todo cache
poetry run python manage_security.py clear-all
```

---

## 📊 Monitoramento de Segurança

### Logs

**Arquivos:**

- `logs/api.log` - Logs gerais
- `logs/errors.log` - Apenas erros
- `logs/security.log` - Eventos de segurança

**Rotação:**

- Tamanho máximo: 10 MB
- Backups: 5 arquivos

**Monitorar em produção:**

```bash
# Acompanhar security.log em tempo real
tail -f logs/security.log

# Ver últimas ameaças detectadas
grep "attempt detected" logs/security.log | tail -20

# IPs bloqueados hoje
grep "blacklisted" logs/security.log | grep "$(date +%Y-%m-%d)"
```

### Métricas Importantes

**Monitorar:**

1. Taxa de requisições bloqueadas
2. IPs em blacklist
3. Tentativas de SQL Injection
4. Tentativas de XSS
5. Rate limit exceeded

**Alertas recomendados:**

- \> 10 ameaças/minuto
- \> 50 IPs bloqueados/hora
- Spike de 403 errors

---

## 🚨 Incidentes de Segurança

### Checklist de Resposta

1. **Identificar o problema**

   - Checar logs: `logs/security.log`
   - Identificar padrão de ataque
   - Listar IPs maliciosos

2. **Conter a ameaça**

   ```bash
   # Bloquear IP permanentemente
   poetry run python manage_security.py blacklist-add <IP>

   # Limpar tokens comprometidos
   poetry run python manage.py cleartokens
   ```

3. **Analisar impacto**

   - Dados acessados?
   - Sistemas comprometidos?
   - Usuários afetados?

4. **Remediar**

   - Corrigir vulnerabilidade
   - Atualizar SECRET_KEY se necessário
   - Forçar logout de todos usuários
   - Notificar usuários afetados

5. **Documentar**
   - Registrar incidente
   - Ações tomadas
   - Lições aprendidas

---

## ✅ Checklist de Segurança para Deploy

### Pre-Deploy

- [ ] SECRET_KEY única e forte
- [ ] DEBUG=False
- [ ] ALLOWED_HOSTS configurado
- [ ] SSL/HTTPS ativo
- [ ] Variáveis sensíveis em .env (não no código)
- [ ] Dependências atualizadas
- [ ] Testes de segurança passando

### Post-Deploy

- [ ] Verificar headers de segurança
- [ ] Testar HTTPS redirect
- [ ] Confirmar rate limiting funcionando
- [ ] Logs de segurança sendo gerados
- [ ] Monitoramento ativo
- [ ] Backup configurado

### Auditoria Regular

- [ ] Revisar logs semanalmente
- [ ] Atualizar dependências mensalmente
- [ ] Testar backup/restore mensalmente
- [ ] Audit de segurança trimestral
- [ ] Penetration test anual

---

## 🔗 Recursos e Referências

### Documentação Oficial

- [Django Security](https://docs.djangoproject.com/en/stable/topics/security/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Mozilla Web Security](https://infosec.mozilla.org/guidelines/web_security)

### Ferramentas de Teste

- [SSL Labs Test](https://www.ssllabs.com/ssltest/)
- [Security Headers](https://securityheaders.com/)
- [OWASP ZAP](https://www.zaproxy.org/)

### Comunidade

- Django Security Mailing List
- Python Security Response Team

---

## 📞 Suporte

Para questões de segurança urgentes:

- Email: security@lacrei.com
- Não divulgue vulnerabilidades publicamente
- Use Responsible Disclosure

---

**Última atualização:** 2025-12-23
**Versão:** 1.0
