"""
Configurações de segurança customizadas.
"""

from django.core.cache import cache


class SecurityConfig:
    """Gerenciamento de configurações de segurança."""
    
    # Blacklist permanente de IPs conhecidos por ataques
    PERMANENT_BLACKLIST = [
        # Adicione IPs problemáticos aqui
        # '192.168.1.100',
    ]
    
    # Rate limits por endpoint (requisições por minuto)
    RATE_LIMITS = {
        '/api/v1/auth/': 10,      # Autenticação: 10 req/min
        '/api/v1/': 100,           # API geral: 100 req/min
        '/admin/': 20,             # Admin: 20 req/min
    }
    
    # Configurações de auto-ban
    AUTO_BAN_CONFIG = {
        'threat_score_threshold': 10,  # Score para ban automático
        'ban_duration': 3600,           # Duração do ban (segundos)
        'score_decay_time': 3600,       # Tempo para score expirar
    }
    
    @classmethod
    def is_ip_whitelisted(cls, ip):
        """
        Verifica se IP está em whitelist.
        IPs em whitelist nunca são bloqueados.
        """
        whitelist = cache.get('security:whitelist', set())
        return ip in whitelist
    
    @classmethod
    def add_to_whitelist(cls, ip):
        """Adiciona IP à whitelist."""
        whitelist = cache.get('security:whitelist', set())
        whitelist.add(ip)
        cache.set('security:whitelist', whitelist, None)  # Permanente
    
    @classmethod
    def remove_from_whitelist(cls, ip):
        """Remove IP da whitelist."""
        whitelist = cache.get('security:whitelist', set())
        whitelist.discard(ip)
        cache.set('security:whitelist', whitelist, None)
    
    @classmethod
    def get_permanent_blacklist(cls):
        """Retorna lista de IPs permanentemente bloqueados."""
        return cls.PERMANENT_BLACKLIST
    
    @classmethod
    def add_to_permanent_blacklist(cls, ip):
        """
        Adiciona IP à blacklist permanente.
        ATENÇÃO: Requer restart para tomar efeito.
        """
        if ip not in cls.PERMANENT_BLACKLIST:
            cls.PERMANENT_BLACKLIST.append(ip)
    
    @classmethod
    def get_rate_limit(cls, path):
        """
        Retorna o rate limit para um caminho específico.
        Usa o padrão mais específico que corresponder.
        """
        # Procura por match exato ou prefixo
        for pattern, limit in sorted(
            cls.RATE_LIMITS.items(),
            key=lambda x: len(x[0]),
            reverse=True
        ):
            if path.startswith(pattern):
                return limit
        
        # Rate limit padrão se não encontrar match
        return 200


class ThreatIntelligence:
    """Análise e inteligência de ameaças."""
    
    @staticmethod
    def get_threat_report(ip):
        """
        Gera relatório de ameaças para um IP.
        """
        cache_key_prefix = f'threat:'
        
        return {
            'ip': ip,
            'threat_score': cache.get(f'{cache_key_prefix}score:{ip}', 0),
            'total_requests': cache.get(f'{cache_key_prefix}requests:{ip}', 0),
            'blocked_attempts': cache.get(f'{cache_key_prefix}blocked:{ip}', 0),
            'sql_injection_attempts': cache.get(f'{cache_key_prefix}sql:{ip}', 0),
            'xss_attempts': cache.get(f'{cache_key_prefix}xss:{ip}', 0),
            'path_traversal_attempts': cache.get(f'{cache_key_prefix}path:{ip}', 0),
            'is_blacklisted': cache.get(f'blacklist:{ip}', False),
        }
    
    @staticmethod
    def record_attack(ip, attack_type):
        """Registra tentativa de ataque."""
        cache_key = f'threat:{attack_type}:{ip}'
        count = cache.get(cache_key, 0)
        cache.set(cache_key, count + 1, 86400)  # 24 horas
    
    @staticmethod
    def get_top_threats(limit=10):
        """
        Retorna os IPs com maiores scores de ameaça.
        Nota: Requer implementação de índice no cache.
        """
        # Implementação básica - pode ser melhorada com Redis sorted sets
        return []
    
    @staticmethod
    def clear_threat_data(ip):
        """Limpa dados de ameaça para um IP."""
        patterns = [
            f'threat:score:{ip}',
            f'threat:requests:{ip}',
            f'threat:blocked:{ip}',
            f'threat:sql:{ip}',
            f'threat:xss:{ip}',
            f'threat:path:{ip}',
            f'blacklist:{ip}',
        ]
        
        for pattern in patterns:
            cache.delete(pattern)


def get_security_headers():
    """
    Retorna headers de segurança recomendados.
    Para usar em middleware ou views.
    """
    return {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'Content-Security-Policy': "default-src 'self'",
        'Referrer-Policy': 'strict-origin-when-cross-origin',
        'Permissions-Policy': 'geolocation=(), microphone=(), camera=()',
    }
