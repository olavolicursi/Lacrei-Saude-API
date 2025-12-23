"""
Utilitário para gerenciar configurações de segurança.
"""
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.core.cache import cache
from core.security_config import SecurityConfig, ThreatIntelligence


def clear_ip_from_blacklist(ip):
    """Remove IP da blacklist."""
    cache.delete(f'blacklist:{ip}')
    print(f"✅ IP {ip} removido da blacklist")


def clear_threat_score(ip):
    """Limpa threat score de um IP."""
    ThreatIntelligence.clear_threat_data(ip)
    print(f"✅ Threat score limpo para IP {ip}")


def show_ip_status(ip):
    """Mostra status de segurança de um IP."""
    report = ThreatIntelligence.get_threat_report(ip)
    
    print(f"\n📊 Status de Segurança para IP: {ip}")
    print("=" * 60)
    print(f"  Threat Score: {report['threat_score']}")
    print(f"  Total de Requisições: {report['total_requests']}")
    print(f"  Tentativas Bloqueadas: {report['blocked_attempts']}")
    print(f"  SQL Injection: {report['sql_injection_attempts']}")
    print(f"  XSS: {report['xss_attempts']}")
    print(f"  Path Traversal: {report['path_traversal_attempts']}")
    print(f"  Blacklisted: {'Sim' if report['is_blacklisted'] else 'Não'}")
    print("=" * 60)


def clear_all_security_cache():
    """Limpa todo o cache de segurança."""
    cache.clear()
    print("✅ Todo o cache de segurança foi limpo")


def add_to_whitelist(ip):
    """Adiciona IP à whitelist."""
    SecurityConfig.add_to_whitelist(ip)
    print(f"✅ IP {ip} adicionado à whitelist")


def remove_from_whitelist(ip):
    """Remove IP da whitelist."""
    SecurityConfig.remove_from_whitelist(ip)
    print(f"✅ IP {ip} removido da whitelist")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Utilitário de gerenciamento de segurança'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Comandos disponíveis')
    
    # Comando: clear-blacklist
    clear_bl = subparsers.add_parser(
        'clear-blacklist',
        help='Remove IP da blacklist'
    )
    clear_bl.add_argument('ip', help='Endereço IP')
    
    # Comando: clear-threat
    clear_threat = subparsers.add_parser(
        'clear-threat',
        help='Limpa threat score de um IP'
    )
    clear_threat.add_argument('ip', help='Endereço IP')
    
    # Comando: status
    status = subparsers.add_parser(
        'status',
        help='Mostra status de segurança de um IP'
    )
    status.add_argument('ip', help='Endereço IP')
    
    # Comando: clear-all
    subparsers.add_parser(
        'clear-all',
        help='Limpa todo o cache de segurança'
    )
    
    # Comando: whitelist-add
    wl_add = subparsers.add_parser(
        'whitelist-add',
        help='Adiciona IP à whitelist'
    )
    wl_add.add_argument('ip', help='Endereço IP')
    
    # Comando: whitelist-remove
    wl_remove = subparsers.add_parser(
        'whitelist-remove',
        help='Remove IP da whitelist'
    )
    wl_remove.add_argument('ip', help='Endereço IP')
    
    args = parser.parse_args()
    
    if args.command == 'clear-blacklist':
        clear_ip_from_blacklist(args.ip)
    elif args.command == 'clear-threat':
        clear_threat_score(args.ip)
    elif args.command == 'status':
        show_ip_status(args.ip)
    elif args.command == 'clear-all':
        clear_all_security_cache()
    elif args.command == 'whitelist-add':
        add_to_whitelist(args.ip)
    elif args.command == 'whitelist-remove':
        remove_from_whitelist(args.ip)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
