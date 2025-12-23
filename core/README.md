# Core - Utilidades Compartilhadas

Este módulo contém utilidades compartilhadas entre os diferentes apps da aplicação, com foco em **segurança** e **validação de dados**.

## 📋 Conteúdo

### `validators.py` - Validadores de Segurança

Módulo com validadores customizados para proteger a aplicação contra ataques comuns:

#### 🛡️ Proteções Implementadas

1. **XSS (Cross-Site Scripting)**
   - Remoção de tags HTML perigosas
   - Detecção de tags `<script>`, `<iframe>`
   - Bloqueio de event handlers (onclick, onerror, etc.)
   - Bloqueio de protocolo `javascript:`

2. **SQL Injection**
   - Detecção de comandos SQL perigosos (DROP, DELETE, INSERT, etc.)
   - Bloqueio de comentários SQL (`--`, `/* */`)
   - Detecção de padrões de bypass (`OR 1=1`, `' OR '`)

3. **Path Traversal**
   - Validação de nomes de arquivo
   - Bloqueio de `../` e `..\`
   - Detecção de caracteres especiais perigosos

## 🔧 Funções Disponíveis

### `sanitize_html(value)`

Remove todas as tags HTML de uma string.

```python
from core.validators import sanitize_html

# Exemplo
texto = "<script>alert('XSS')</script>Texto limpo"
resultado = sanitize_html(texto)
# resultado = "Texto limpo"
```

**Uso:** Aplicado automaticamente nos campos de texto dos serializers.

---

### `validate_no_sql_injection(value)`

Valida que a string não contém padrões suspeitos de SQL Injection.

```python
from core.validators import validate_no_sql_injection

# Exemplo válido
validate_no_sql_injection("Dr. João Silva")  # OK

# Exemplo inválido - lança ValidationError
validate_no_sql_injection("'; DROP TABLE users; --")  # ❌ ValidationError
```

**Raises:** `ValidationError` se padrões suspeitos forem detectados.

---

### `validate_no_script_tags(value)`

Valida que a string não contém tags de script ou event handlers.

```python
from core.validators import validate_no_script_tags

# Exemplo inválido
validate_no_script_tags("<script>alert(1)</script>")  # ❌ ValidationError
validate_no_script_tags("<img onerror=alert(1)>")     # ❌ ValidationError
```

---

### `validate_safe_filename(value)`

Valida que o nome do arquivo não contém caracteres perigosos.

```python
from core.validators import validate_safe_filename

# Exemplo válido
validate_safe_filename("documento.pdf")  # OK

# Exemplo inválido
validate_safe_filename("../../etc/passwd")  # ❌ ValidationError
```

---

### `sanitize_and_validate(value)`

Função combinada que aplica sanitização e todas as validações.

```python
from core.validators import sanitize_and_validate

# Sanitiza e valida em uma única chamada
texto = sanitize_and_validate("<b>Texto</b>")
# texto = "Texto"
```

## 📝 Integração com Serializers

Os validadores são aplicados automaticamente nos serializers:

### Professional Serializer

```python
class ProfessionalSerializer(serializers.ModelSerializer):
    def validate_nome_social(self, value):
        """Sanitiza e valida nome social"""
        validate_no_sql_injection(value)
        return sanitize_html(value)
```

**Campos protegidos:**
- `nome_social`
- `logradouro`
- `complemento`
- `bairro`
- `cidade`
- `email`
- `telefone`

### Appointment Serializer

```python
class AppointmentSerializer(serializers.ModelSerializer):
    def validate_paciente_nome(self, value):
        """Sanitiza e valida nome do paciente"""
        validate_no_sql_injection(value)
        return sanitize_html(value)
```

**Campos protegidos:**
- `paciente_nome`
- `paciente_email`
- `paciente_telefone`
- `observacoes`

## 🧪 Testes

Os validadores possuem cobertura completa de testes em `core/tests.py`.

### Executar testes

```bash
# Todos os testes do módulo core
poetry run pytest core/tests.py -v

# Testes específicos
poetry run pytest core/tests.py::TestSanitizeHTML -v
poetry run pytest core/tests.py::TestValidateSQLInjection -v
```

### Exemplos de testes

```python
def test_remove_script_tags(self):
    """Deve remover tags de script"""
    input_str = "<script>alert('XSS')</script>Texto limpo"
    result = sanitize_html(input_str)
    assert result == "Texto limpo"

def test_detect_drop_table(self):
    """Deve detectar DROP TABLE"""
    with pytest.raises(ValidationError):
        validate_no_sql_injection("'; DROP TABLE users; --")
```

## 🔍 Padrões Detectados

### SQL Injection

```python
suspicious_patterns = [
    'DROP', 'DELETE', 'INSERT', 'UPDATE', 'TRUNCATE',
    'ALTER', 'CREATE', 'REPLACE', 'EXEC', 'EXECUTE',
    '--', ';--', 'xp_', 'sp_', '/*', '*/',
    'UNION', 'SELECT', 'WHERE', '1=1', '1 = 1',
    'OR 1', 'OR TRUE', "' OR '", '" OR "',
]
```

### XSS/Script Tags

```python
dangerous_tags = [
    '<script', '</script>', 
    '<iframe', '</iframe>',
    'javascript:', 
    'onerror=', 'onload=', 'onclick=',
]
```

## ⚠️ Importante

- **Validações são case-insensitive**: `DROP` e `drop` são detectados
- **Sanitização preserva texto**: apenas tags HTML são removidas
- **Valores não-string são ignorados**: validadores só processam strings
- **Erros são explícitos**: mensagens claras sobre o que foi bloqueado

## 🚀 Uso em Novos Campos

Para adicionar proteção em novos campos:

```python
from core.validators import sanitize_html, validate_no_sql_injection

class MeuSerializer(serializers.ModelSerializer):
    def validate_meu_campo(self, value):
        """Sanitiza e valida campo"""
        validate_no_sql_injection(value)
        return sanitize_html(value)
```

## 📚 Recursos Adicionais

- [OWASP - XSS Prevention](https://owasp.org/www-community/attacks/xss/)
- [OWASP - SQL Injection](https://owasp.org/www-community/attacks/SQL_Injection)
- [Bleach Documentation](https://bleach.readthedocs.io/)

---

**Status:** ✅ Implementado e testado  
**Última atualização:** Dezembro 2024
