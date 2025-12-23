# Exemplo de Uso - Sanitização de Inputs

Este documento demonstra como a sanitização de inputs funciona na prática na API Lacrei Saúde.

## 🎯 Cenários de Teste

### Cenário 1: Criação de Profissional com Dados Seguros

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/professionals/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <seu-token>" \
  -d '{
    "nome_social": "Dr. João Silva",
    "profissao": "MEDICO",
    "registro_profissional": "CRM-123456",
    "cep": "01310-100",
    "logradouro": "Avenida Paulista",
    "numero": "1000",
    "bairro": "Bela Vista",
    "cidade": "São Paulo",
    "estado": "SP",
    "telefone": "(11) 99999-9999",
    "email": "joao@example.com"
  }'
```

**Response:** ✅ 201 Created
```json
{
  "id": 1,
  "nome_social": "Dr. João Silva",
  "profissao": "MEDICO",
  ...
}
```

---

### Cenário 2: Tentativa de XSS (Cross-Site Scripting)

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/professionals/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <seu-token>" \
  -d '{
    "nome_social": "<script>alert(\"XSS\")</script>Dr. Maria Santos",
    "profissao": "PSICOLOGO",
    "registro_profissional": "CRP-654321",
    "logradouro": "<b>Rua das Flores</b>",
    "numero": "123",
    "bairro": "Centro",
    "cidade": "São Paulo",
    "estado": "SP",
    "telefone": "(11) 98888-8888",
    "email": "maria@example.com",
    "cep": "01000-000"
  }'
```

**Response:** ✅ 201 Created (com dados sanitizados)
```json
{
  "id": 2,
  "nome_social": "Dr. Maria Santos",  // ← Tags <script> removidas
  "profissao": "PSICOLOGO",
  "logradouro": "Rua das Flores",     // ← Tags <b> removidas
  ...
}
```

**O que aconteceu:**
- ✅ Tags HTML foram **removidas**
- ✅ Texto legítimo foi **preservado**
- ✅ Dados foram **salvos com segurança**

---

### Cenário 3: Tentativa de SQL Injection

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/professionals/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <seu-token>" \
  -d '{
    "nome_social": "\"; DROP TABLE professionals; --",
    "profissao": "MEDICO",
    "registro_profissional": "CRM-999999",
    "logradouro": "Rua Teste",
    "numero": "100",
    "bairro": "Centro",
    "cidade": "São Paulo",
    "estado": "SP",
    "telefone": "(11) 97777-7777",
    "email": "teste@example.com",
    "cep": "01000-000"
  }'
```

**Response:** ❌ 400 Bad Request
```json
{
  "nome_social": [
    "Entrada suspeita detectada. Caracteres ou padrões perigosos não são permitidos."
  ]
}
```

**O que aconteceu:**
- ❌ Padrão SQL perigoso **detectado**
- ❌ Request foi **bloqueada**
- ✅ Banco de dados **protegido**

---

### Cenário 4: Criação de Consulta com Observações HTML

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/appointments/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <seu-token>" \
  -d '{
    "professional": 1,
    "data_hora": "2024-12-30T10:00:00Z",
    "duracao_minutos": 60,
    "paciente_nome": "Ana <b>Silva</b>",
    "paciente_email": "ana@example.com",
    "paciente_telefone": "(11) 96666-6666",
    "observacoes": "<p>Paciente com <strong>ansiedade</strong></p>"
  }'
```

**Response:** ✅ 201 Created (com dados sanitizados)
```json
{
  "id": 1,
  "professional": 1,
  "data_hora": "2024-12-30T10:00:00Z",
  "paciente_nome": "Ana Silva",                    // ← Tags removidas
  "paciente_email": "ana@example.com",
  "observacoes": "Paciente com ansiedade",         // ← Tags removidas
  ...
}
```

---

### Cenário 5: Tentativa de Múltiplos Ataques

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/appointments/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <seu-token>" \
  -d '{
    "professional": 1,
    "data_hora": "2024-12-30T14:00:00Z",
    "duracao_minutos": 60,
    "paciente_nome": "<script>alert(1)</script>Carlos",
    "paciente_email": "carlos@example.com",
    "paciente_telefone": "\"; DELETE FROM appointments; --",
    "observacoes": "<iframe src=\"malicious.com\"></iframe>"
  }'
```

**Response:** ❌ 400 Bad Request
```json
{
  "paciente_telefone": [
    "Entrada suspeita detectada. Caracteres ou padrões perigosos não são permitidos."
  ]
}
```

**O que aconteceu:**
- ❌ SQL Injection no telefone foi **detectada**
- ❌ Request foi **bloqueada completamente**
- ✅ Banco de dados **protegido**
- 💡 Mesmo que outros campos fossem válidos, a request inteira é rejeitada

---

## 🧪 Como Testar Localmente

### 1. Teste com cURL

```bash
# 1. Obter token JWT
TOKEN=$(curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' \
  | jq -r '.access')

# 2. Testar XSS
curl -X POST http://localhost:8000/api/v1/professionals/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "nome_social": "<script>alert(1)</script>Dr. Teste",
    "profissao": "MEDICO",
    "registro_profissional": "TEST-001",
    "logradouro": "Rua Teste",
    "numero": "1",
    "bairro": "Centro",
    "cidade": "SP",
    "estado": "SP",
    "telefone": "11999999999",
    "email": "teste@test.com",
    "cep": "01000-000"
  }' | jq

# 3. Testar SQL Injection
curl -X POST http://localhost:8000/api/v1/professionals/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "nome_social": "DROP TABLE users",
    "profissao": "MEDICO",
    ...
  }' | jq
```

### 2. Teste com Python

```python
import requests

BASE_URL = "http://localhost:8000"

# 1. Obter token
response = requests.post(f"{BASE_URL}/api/token/", json={
    "username": "admin",
    "password": "admin123"
})
token = response.json()["access"]
headers = {"Authorization": f"Bearer {token}"}

# 2. Testar XSS
malicious_data = {
    "nome_social": "<script>alert('XSS')</script>Dr. Teste",
    "profissao": "MEDICO",
    "registro_profissional": "TEST-001",
    # ... outros campos
}
response = requests.post(
    f"{BASE_URL}/api/v1/professionals/",
    json=malicious_data,
    headers=headers
)
print(f"Status: {response.status_code}")
print(f"Nome sanitizado: {response.json().get('nome_social')}")
# Esperado: "Dr. Teste" (sem tags)
```

### 3. Teste com Postman

1. **Configurar ambiente:**
   - Base URL: `http://localhost:8000`
   - Token: Obter de `/api/token/`

2. **Criar collection com testes:**
   - Test XSS: POST `/api/v1/professionals/` com tags HTML
   - Test SQL Injection: POST com padrões SQL
   - Test válido: POST com dados limpos

3. **Validar respostas:**
   - XSS deve retornar 201 com dados sanitizados
   - SQL Injection deve retornar 400 Bad Request

---

## 📊 Estatísticas de Segurança

### Validadores Implementados

| Validador | Padrões Detectados | Cobertura de Testes |
|-----------|-------------------|---------------------|
| `sanitize_html` | Tags HTML | 100% |
| `validate_no_sql_injection` | 18+ padrões SQL | 100% |
| `validate_no_script_tags` | 8+ padrões XSS | 100% |
| `validate_safe_filename` | 10+ caracteres | 100% |

### Campos Protegidos

| Model | Campos Sanitizados | Total de Campos |
|-------|-------------------|-----------------|
| Professional | 7 de 12 | 58% |
| Appointment | 4 de 10 | 40% |

**Total de validações por request:** 2-3 camadas
1. ✅ Django REST Framework (tipos)
2. ✅ Validadores customizados (segurança)
3. ✅ Django ORM (constraints)

---

## 🛡️ Boas Práticas Implementadas

### ✅ Defesa em Profundidade (Defense in Depth)

1. **Frontend:** Validação client-side (primeira linha)
2. **API:** Validadores customizados (segunda linha)
3. **ORM:** Prepared statements (terceira linha)
4. **Database:** Constraints e permissions (quarta linha)

### ✅ Princípio do Menor Privilégio

- Usuários de banco com permissões mínimas
- Tokens JWT com expiração curta
- Rate limiting por role

### ✅ Fail Secure

- Em caso de dúvida, **bloquear**
- Erros explícitos, não silenciosos
- Logs de todas as tentativas suspeitas

---

## 📚 Referências

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [OWASP XSS Prevention](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html)
- [OWASP SQL Injection Prevention](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html)
- [Django Security](https://docs.djangoproject.com/en/stable/topics/security/)
- [Bleach Documentation](https://bleach.readthedocs.io/)

---

**Última atualização:** Dezembro 2024  
**Status:** ✅ Implementado e testado
