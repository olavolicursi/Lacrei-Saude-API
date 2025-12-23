"""
Middlewares customizados para segurança e logging.
"""

import logging
import time
import re
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponseForbidden
from django.core.cache import cache

logger = logging.getLogger('security')


class SecurityDetectionMiddleware(MiddlewareMixin):
    """
    Middleware que detecta e bloqueia requisições suspeitas.
    
    Detecta:
    - SQL Injection attempts
    - XSS (Cross-Site Scripting)
    - Path Traversal
    - User-Agents suspeitos
    - Rate limiting por IP
    - IPs em blacklist
    """
    
    # Padrões suspeitos para SQL Injection
    SQL_INJECTION_PATTERNS = [
        r"(\bUNION\b.*\bSELECT\b)",
        r"(\bSELECT\b.*\bFROM\b)",
        r"(\bINSERT\b.*\bINTO\b)",
        r"(\bUPDATE\b.*\bSET\b)",
        r"(\bDELETE\b.*\bFROM\b)",
        r"(\bDROP\b.*\bTABLE\b)",
        r"(--\s*$)",
        r"(;\s*DROP)",
        r"(\bOR\b\s+\d+\s*=\s*\d+)",
        r"('\s+OR\s+')",
        r"(xp_cmdshell)",
        r"(exec\s*\()",
    ]
    
    # Padrões suspeitos para XSS
    XSS_PATTERNS = [
        r"<script[^>]*>.*?</script>",
        r"javascript:",
        r"onerror\s*=",
        r"onload\s*=",
        r"onclick\s*=",
        r"<iframe",
        r"<embed",
        r"<object",
    ]
    
    # Padrões de Path Traversal
    PATH_TRAVERSAL_PATTERNS = [
        r"\.\./",
        r"\.\.\\"
        r"%2e%2e/",
        r"%2e%2e\\",
    ]
    
    # User-Agents suspeitos
    SUSPICIOUS_USER_AGENTS = [
        'sqlmap',
        'nikto',
        'nmap',
        'masscan',
        'burp',
        'metasploit',
        'havij',
        'acunetix',
    ]
    
    def __init__(self, get_response):
        super().__init__(get_response)
        self.get_response = get_response
        self.compiled_sql_patterns = [
            re.compile(pattern, re.IGNORECASE) 
            for pattern in self.SQL_INJECTION_PATTERNS
        ]
        self.compiled_xss_patterns = [
            re.compile(pattern, re.IGNORECASE) 
            for pattern in self.XSS_PATTERNS
        ]
        self.compiled_path_patterns = [
            re.compile(pattern, re.IGNORECASE) 
            for pattern in self.PATH_TRAVERSAL_PATTERNS
        ]
    
    def process_request(self, request):
        """Verifica requisição antes de processá-la."""
        
        # Obter IP do cliente
        ip = self._get_client_ip(request)
        
        # 1. Verificar blacklist
        if self._is_ip_blacklisted(ip):
            logger.error(f"Blocked request from blacklisted IP: {ip}")
            return HttpResponseForbidden("Access Denied")
        
        # 2. Rate limiting
        if self._is_rate_limited(ip):
            logger.warning(
                f"Rate limit exceeded for IP: {ip} | "
                f"Path: {request.path}"
            )
            return HttpResponseForbidden("Rate limit exceeded")
        
        # 3. Verificar User-Agent suspeito
        if self._has_suspicious_user_agent(request):
            user_agent = request.META.get('HTTP_USER_AGENT', 'unknown')
            logger.warning(
                f"Suspicious User-Agent detected | "
                f"IP: {ip} | "
                f"User-Agent: {user_agent} | "
                f"Path: {request.path}"
            )
            self._increment_threat_score(ip)
        
        # 4. Verificar SQL Injection
        if self._check_sql_injection(request):
            logger.error(
                f"SQL Injection attempt detected | "
                f"IP: {ip} | "
                f"Path: {request.path} | "
                f"Query: {request.META.get('QUERY_STRING', '')}"
            )
            self._increment_threat_score(ip, weight=5)
            return HttpResponseForbidden("Invalid request")
        
        # 5. Verificar XSS
        if self._check_xss(request):
            logger.error(
                f"XSS attempt detected | "
                f"IP: {ip} | "
                f"Path: {request.path}"
            )
            self._increment_threat_score(ip, weight=3)
            return HttpResponseForbidden("Invalid request")
        
        # 6. Verificar Path Traversal
        if self._check_path_traversal(request):
            logger.error(
                f"Path Traversal attempt detected | "
                f"IP: {ip} | "
                f"Path: {request.path}"
            )
            self._increment_threat_score(ip, weight=4)
            return HttpResponseForbidden("Invalid request")
        
        # 7. Auto-blacklist se score muito alto
        threat_score = self._get_threat_score(ip)
        if threat_score >= 10:
            self._blacklist_ip(ip, duration=3600)  # 1 hora
            logger.critical(
                f"IP auto-blacklisted due to high threat score | "
                f"IP: {ip} | "
                f"Score: {threat_score}"
            )
            return HttpResponseForbidden("Access Denied")
        
        return None
    
    def _get_client_ip(self, request):
        """Obtém o IP real do cliente."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', 'unknown')
        return ip
    
    def _is_ip_blacklisted(self, ip):
        """Verifica se IP está em blacklist."""
        return cache.get(f'blacklist:{ip}', False)
    
    def _blacklist_ip(self, ip, duration=3600):
        """Adiciona IP à blacklist temporária."""
        cache.set(f'blacklist:{ip}', True, duration)
    
    def _is_rate_limited(self, ip):
        """
        Rate limiting simples por IP.
        Máximo 100 requisições por minuto.
        """
        cache_key = f'rate_limit:{ip}'
        requests = cache.get(cache_key, 0)
        
        if requests >= 100:
            return True
        
        cache.set(cache_key, requests + 1, 60)  # 60 segundos
        return False
    
    def _has_suspicious_user_agent(self, request):
        """Verifica se User-Agent é suspeito."""
        user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
        
        if not user_agent:
            return True  # Sem User-Agent é suspeito
        
        for suspicious in self.SUSPICIOUS_USER_AGENTS:
            if suspicious in user_agent:
                return True
        
        return False
    
    def _check_sql_injection(self, request):
        """Verifica padrões de SQL Injection na requisição."""
        # Verificar query string
        query_string = request.META.get('QUERY_STRING', '')
        if self._matches_patterns(query_string, self.compiled_sql_patterns):
            return True
        
        # Verificar path
        if self._matches_patterns(request.path, self.compiled_sql_patterns):
            return True
        
        # Verificar POST data (se existir)
        if request.method == 'POST':
            try:
                body = request.body.decode('utf-8')
                if self._matches_patterns(body, self.compiled_sql_patterns):
                    return True
            except:
                pass
        
        return False
    
    def _check_xss(self, request):
        """Verifica padrões de XSS na requisição."""
        query_string = request.META.get('QUERY_STRING', '')
        if self._matches_patterns(query_string, self.compiled_xss_patterns):
            return True
        
        if request.method == 'POST':
            try:
                body = request.body.decode('utf-8')
                if self._matches_patterns(body, self.compiled_xss_patterns):
                    return True
            except:
                pass
        
        return False
    
    def _check_path_traversal(self, request):
        """Verifica padrões de Path Traversal."""
        path = request.path
        query_string = request.META.get('QUERY_STRING', '')
        
        if self._matches_patterns(path, self.compiled_path_patterns):
            return True
        
        if self._matches_patterns(query_string, self.compiled_path_patterns):
            return True
        
        return False
    
    def _matches_patterns(self, text, compiled_patterns):
        """Verifica se texto corresponde a algum padrão."""
        for pattern in compiled_patterns:
            if pattern.search(text):
                return True
        return False
    
    def _increment_threat_score(self, ip, weight=1):
        """Incrementa score de ameaça para um IP."""
        cache_key = f'threat_score:{ip}'
        score = cache.get(cache_key, 0)
        cache.set(cache_key, score + weight, 3600)  # 1 hora
    
    def _get_threat_score(self, ip):
        """Obtém score de ameaça atual do IP."""
        cache_key = f'threat_score:{ip}'
        return cache.get(cache_key, 0)


class SecurityLoggingMiddleware(MiddlewareMixin):
    """
    Middleware que registra todas as requisições HTTP para fins de segurança.
    
    Logs incluem:
    - Método HTTP
    - Path da requisição
    - Endereço IP do cliente
    - User agent
    - Status code da resposta
    - Tempo de processamento
    - Usuário autenticado (se houver)
    """
    
    def process_request(self, request):
        """Registra informações no início da requisição."""
        request.start_time = time.time()
        
        # Pegar IP real do cliente (considera proxies)
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', 'unknown')
        
        request.client_ip = ip
        
        # Log inicial da requisição
        logger.info(
            f"Request started: {request.method} {request.path} from {ip}"
        )
        
        return None
    
    def process_response(self, request, response):
        """Registra informações no fim da requisição."""
        # Calcular tempo de processamento
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            duration_ms = round(duration * 1000, 2)
        else:
            duration_ms = 0
        
        # Pegar informações do usuário
        user = 'anonymous'
        if hasattr(request, 'user') and request.user.is_authenticated:
            user = request.user.username or request.user.email or f'user_id_{request.user.id}'
        
        # Pegar IP
        ip = getattr(request, 'client_ip', 'unknown')
        
        # User agent
        user_agent = request.META.get('HTTP_USER_AGENT', 'unknown')
        
        # Log final da requisição
        log_message = (
            f"Request completed: {request.method} {request.path} | "
            f"Status: {response.status_code} | "
            f"User: {user} | "
            f"IP: {ip} | "
            f"Duration: {duration_ms}ms | "
            f"User-Agent: {user_agent[:100]}"
        )
        
        # Usar nível WARNING para status codes 4xx e 5xx
        if response.status_code >= 400:
            logger.warning(log_message)
        else:
            logger.info(log_message)
        
        return response
    
    def process_exception(self, request, exception):
        """Registra exceções não tratadas."""
        ip = getattr(request, 'client_ip', 'unknown')
        user = 'anonymous'
        
        if hasattr(request, 'user') and request.user.is_authenticated:
            user = request.user.username or request.user.email or f'user_id_{request.user.id}'
        
        logger.error(
            f"Exception in request: {request.method} {request.path} | "
            f"User: {user} | "
            f"IP: {ip} | "
            f"Exception: {exception.__class__.__name__}: {str(exception)}",
            exc_info=True
        )
        
        return None


class RequestResponseLoggingMiddleware(MiddlewareMixin):
    """
    Middleware que registra detalhes de requisições e respostas da API.
    
    Útil para debugging e monitoramento de performance.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.api_logger = logging.getLogger('appointments')
    
    def __call__(self, request):
        # Só logar rotas da API
        if request.path.startswith('/api/'):
            # Log da requisição
            self.log_request(request)
            
            # Processar requisição
            response = self.get_response(request)
            
            # Log da resposta
            self.log_response(request, response)
            
            return response
        
        return self.get_response(request)
    
    def log_request(self, request):
        """Loga detalhes da requisição."""
        user = 'anonymous'
        if hasattr(request, 'user') and request.user.is_authenticated:
            user = str(request.user)
        
        self.api_logger.info(
            f"API Request: {request.method} {request.path} | User: {user}"
        )
    
    def log_response(self, request, response):
        """Loga detalhes da resposta."""
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            duration_ms = round(duration * 1000, 2)
        else:
            duration_ms = 0
        
        self.api_logger.info(
            f"API Response: {request.method} {request.path} | "
            f"Status: {response.status_code} | "
            f"Duration: {duration_ms}ms"
        )
