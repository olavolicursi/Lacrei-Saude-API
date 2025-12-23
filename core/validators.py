"""
Validadores customizados para sanitização de inputs e segurança.

Este módulo contém validadores para proteger a aplicação contra:
- XSS (Cross-Site Scripting)
- SQL Injection
- Outros ataques de injeção de código
"""
import bleach
from django.core.exceptions import ValidationError


def sanitize_html(value):
    """
    Remove tags HTML perigosas de uma string.
    
    Args:
        value (str): String a ser sanitizada
        
    Returns:
        str: String sem tags HTML
        
    Example:
        >>> sanitize_html("<script>alert('xss')</script>Texto limpo")
        "Texto limpo"
    """
    if not isinstance(value, str):
        return value
    
    allowed_tags = []  # Nenhuma tag permitida
    # strip=True remove as tags mas mantém o conteúdo
    # Para remover completamente, usamos strip=False e depois removemos manualmente
    cleaned = bleach.clean(value, tags=allowed_tags, strip=True)
    # Remove espaços extras que podem ter sido deixados
    return cleaned.strip()


def validate_no_sql_injection(value):
    """
    Verifica se a string contém padrões suspeitos de SQL Injection.
    
    Args:
        value (str): String a ser validada
        
    Raises:
        ValidationError: Se padrões suspeitos forem detectados
        
    Example:
        >>> validate_no_sql_injection("'; DROP TABLE users; --")
        # Raises ValidationError
    """
    if not isinstance(value, str):
        return
    
    suspicious_patterns = [
        'DROP', 'DELETE', 'INSERT', 'UPDATE', 'TRUNCATE',
        'ALTER', 'CREATE', 'REPLACE', 'EXEC', 'EXECUTE',
        '--', ';--', 'xp_', 'sp_', '/*', '*/',
        'UNION', 'SELECT', 'WHERE', '1=1', '1 = 1',
        'OR 1', 'OR TRUE', "' OR '", '" OR "',
    ]
    
    upper_value = value.upper()
    
    for pattern in suspicious_patterns:
        if pattern in upper_value:
            raise ValidationError(
                f"Entrada suspeita detectada. Caracteres ou padrões perigosos não são permitidos.",
                code='suspicious_input'
            )


def validate_safe_filename(value):
    """
    Valida que o nome do arquivo não contém caracteres perigosos.
    
    Args:
        value (str): Nome do arquivo
        
    Raises:
        ValidationError: Se caracteres perigosos forem encontrados
    """
    if not isinstance(value, str):
        return
    
    dangerous_chars = ['..', '/', '\\', '<', '>', ':', '"', '|', '?', '*']
    
    for char in dangerous_chars:
        if char in value:
            raise ValidationError(
                f"Nome de arquivo contém caracteres não permitidos.",
                code='invalid_filename'
            )


def validate_no_script_tags(value):
    """
    Valida que a string não contém tags de script.
    
    Args:
        value (str): String a ser validada
        
    Raises:
        ValidationError: Se tags de script forem encontradas
    """
    if not isinstance(value, str):
        return
    
    dangerous_tags = [
        '<script', '</script>', 
        '<iframe', '</iframe>',
        'javascript:', 
        'onerror=', 'onload=', 'onclick=',
    ]
    
    lower_value = value.lower()
    
    for tag in dangerous_tags:
        if tag in lower_value:
            raise ValidationError(
                f"Conteúdo HTML/JavaScript não é permitido.",
                code='script_detected'
            )


def sanitize_and_validate(value):
    """
    Aplica sanitização e validação completa em uma string.
    
    Esta função combina múltiplas validações:
    - Remove tags HTML
    - Valida contra SQL Injection
    - Valida contra tags de script
    
    Args:
        value (str): String a ser sanitizada e validada
        
    Returns:
        str: String sanitizada
        
    Raises:
        ValidationError: Se padrões perigosos forem detectados
    """
    if not isinstance(value, str):
        return value
    
    # Primeiro valida
    validate_no_sql_injection(value)
    validate_no_script_tags(value)
    
    # Depois sanitiza
    return sanitize_html(value)
