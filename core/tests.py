"""
Testes para os validadores de sanitização.

Verifica proteção contra:
- XSS (Cross-Site Scripting)
- SQL Injection
- Outros ataques de injeção
"""
import pytest
from django.core.exceptions import ValidationError
from core.validators import (
    sanitize_html,
    validate_no_sql_injection,
    validate_safe_filename,
    validate_no_script_tags,
    sanitize_and_validate
)


class TestSanitizeHTML:
    """Testes de sanitização de HTML"""
    
    def test_remove_script_tags(self):
        """Deve remover tags de script mas manter texto"""
        input_str = "<script>alert('XSS')</script>Texto limpo"
        result = sanitize_html(input_str)
        # Tags removidas, conteúdo preservado
        assert "<script>" not in result
        assert "Texto limpo" in result
    
    def test_remove_all_html_tags(self):
        """Deve remover todas as tags HTML mas manter texto"""
        input_str = "<div><p>Texto</p></div>"
        result = sanitize_html(input_str)
        assert "Texto" in result
        assert "<" not in result
        assert ">" not in result
    
    def test_preserve_plain_text(self):
        """Deve preservar texto sem tags"""
        input_str = "Texto normal sem tags"
        result = sanitize_html(input_str)
        assert result == input_str
    
    def test_handle_non_string(self):
        """Deve retornar valores não-string sem modificação"""
        assert sanitize_html(123) == 123
        assert sanitize_html(None) is None


class TestValidateSQLInjection:
    """Testes de validação contra SQL Injection"""
    
    def test_detect_drop_table(self):
        """Deve detectar DROP TABLE"""
        with pytest.raises(ValidationError):
            validate_no_sql_injection("'; DROP TABLE users; --")
    
    def test_detect_delete(self):
        """Deve detectar DELETE"""
        with pytest.raises(ValidationError):
            validate_no_sql_injection("admin' OR '1'='1'; DELETE FROM users WHERE '1'='1")
    
    def test_detect_union_select(self):
        """Deve detectar UNION SELECT"""
        with pytest.raises(ValidationError):
            validate_no_sql_injection("1' UNION SELECT * FROM users--")
    
    def test_detect_comment(self):
        """Deve detectar comentários SQL"""
        with pytest.raises(ValidationError):
            validate_no_sql_injection("admin'--")
    
    def test_detect_or_true(self):
        """Deve detectar padrão OR TRUE"""
        with pytest.raises(ValidationError):
            validate_no_sql_injection("' OR TRUE --")
    
    def test_allow_safe_text(self):
        """Deve permitir texto seguro"""
        # Não deve lançar exceção
        validate_no_sql_injection("Texto normal e seguro")
        validate_no_sql_injection("Dr. João Silva")
        validate_no_sql_injection("Rua das Flores, 123")
    
    def test_handle_non_string(self):
        """Deve ignorar valores não-string"""
        # Não deve lançar exceção
        validate_no_sql_injection(123)
        validate_no_sql_injection(None)


class TestValidateSafeFilename:
    """Testes de validação de nomes de arquivo"""
    
    def test_detect_path_traversal(self):
        """Deve detectar tentativa de path traversal"""
        with pytest.raises(ValidationError):
            validate_safe_filename("../../etc/passwd")
    
    def test_detect_backslash(self):
        """Deve detectar barras invertidas"""
        with pytest.raises(ValidationError):
            validate_safe_filename("..\\..\\windows\\system32")
    
    def test_detect_special_chars(self):
        """Deve detectar caracteres especiais perigosos"""
        dangerous_chars = ['<', '>', ':', '"', '|', '?', '*']
        for char in dangerous_chars:
            with pytest.raises(ValidationError):
                validate_safe_filename(f"arquivo{char}.txt")
    
    def test_allow_safe_filename(self):
        """Deve permitir nomes de arquivo seguros"""
        # Não deve lançar exceção
        validate_safe_filename("documento.pdf")
        validate_safe_filename("imagem_2024.jpg")
        validate_safe_filename("relatorio-final.xlsx")


class TestValidateScriptTags:
    """Testes de validação contra tags de script"""
    
    def test_detect_script_tag(self):
        """Deve detectar tag script"""
        with pytest.raises(ValidationError):
            validate_no_script_tags("<script>alert('XSS')</script>")
    
    def test_detect_iframe(self):
        """Deve detectar iframe"""
        with pytest.raises(ValidationError):
            validate_no_script_tags("<iframe src='malicious.com'></iframe>")
    
    def test_detect_javascript_protocol(self):
        """Deve detectar protocolo javascript:"""
        with pytest.raises(ValidationError):
            validate_no_script_tags("<a href='javascript:alert(1)'>Click</a>")
    
    def test_detect_event_handlers(self):
        """Deve detectar event handlers"""
        handlers = ['onerror=', 'onload=', 'onclick=']
        for handler in handlers:
            with pytest.raises(ValidationError):
                validate_no_script_tags(f"<img {handler}alert(1)>")
    
    def test_case_insensitive(self):
        """Deve detectar independente de maiúsculas/minúsculas"""
        with pytest.raises(ValidationError):
            validate_no_script_tags("<SCRIPT>alert(1)</SCRIPT>")
        with pytest.raises(ValidationError):
            validate_no_script_tags("<Script>alert(1)</Script>")
    
    def test_allow_safe_text(self):
        """Deve permitir texto seguro"""
        # Não deve lançar exceção
        validate_no_script_tags("Texto normal")
        validate_no_script_tags("Consulta sobre javascript como linguagem")


class TestSanitizeAndValidate:
    """Testes da função combinada"""
    
    def test_sanitize_and_validate_safe_text(self):
        """Deve processar texto seguro normalmente"""
        input_str = "Dr. João Silva"
        result = sanitize_and_validate(input_str)
        assert result == input_str
    
    def test_block_sql_injection(self):
        """Deve bloquear SQL injection"""
        with pytest.raises(ValidationError):
            sanitize_and_validate("'; DROP TABLE users; --")
    
    def test_block_xss(self):
        """Deve bloquear XSS"""
        with pytest.raises(ValidationError):
            sanitize_and_validate("<script>alert('XSS')</script>")
    
    def test_sanitize_html_tags(self):
        """Deve sanitizar tags HTML simples"""
        input_str = "<b>Texto em negrito</b>"
        result = sanitize_and_validate(input_str)
        assert "Texto em negrito" in result
        assert "<b>" not in result
    
    def test_handle_non_string(self):
        """Deve retornar valores não-string sem modificação"""
        assert sanitize_and_validate(123) == 123
        assert sanitize_and_validate(None) is None


class TestIntegrationWithSerializers:
    """Testes de integração com serializers"""
    
    def test_example_safe_professional_data(self):
        """Exemplo de dados seguros de profissional"""
        safe_data = {
            'nome_social': 'Dr. João Silva',
            'profissao': 'MEDICO',
            'email': 'joao@example.com',
            'logradouro': 'Rua das Flores',
            'cidade': 'São Paulo',
            'bairro': 'Centro'
        }
        
        # Aplicar validações
        for key, value in safe_data.items():
            if isinstance(value, str) and key not in ['email', 'profissao']:
                result = sanitize_and_validate(value)
                assert result == value
    
    def test_example_malicious_professional_data(self):
        """Exemplo de dados maliciosos de profissional"""
        malicious_data = {
            'nome_social': "'; DROP TABLE professionals; --",
            'logradouro': "<script>alert('XSS')</script>",
        }
        
        # Deve bloquear dados maliciosos
        with pytest.raises(ValidationError):
            validate_no_sql_injection(malicious_data['nome_social'])
        
        with pytest.raises(ValidationError):
            validate_no_script_tags(malicious_data['logradouro'])

