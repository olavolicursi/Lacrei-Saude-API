"""
Script para testar e validar configurações de segurança.
"""
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.conf import settings
from django.core.management import call_command
import warnings


def test_security_settings():
    """Testa configurações de segurança."""
    
    print("=" * 70)
    print("VALIDAÇÃO DE CONFIGURAÇÕES DE SEGURANÇA")
    print("=" * 70)
    
    issues = []
    warnings_list = []
    
    # 1. SECRET_KEY
    print("\n[1] SECRET_KEY")
    print("-" * 70)
    if not settings.SECRET_KEY:
        issues.append("❌ SECRET_KEY não está configurado!")
    elif settings.SECRET_KEY == 'django-insecure-change-this-in-production':
        warnings_list.append("⚠️  SECRET_KEY está usando valor padrão inseguro")
    else:
        print(f"✅ SECRET_KEY configurado ({len(settings.SECRET_KEY)} caracteres)")
    
    # 2. DEBUG
    print("\n[2] DEBUG Mode")
    print("-" * 70)
    if settings.DEBUG:
        if settings.ENVIRONMENT == 'production':
            issues.append("❌ DEBUG=True em ambiente de produção!")
        else:
            warnings_list.append(f"⚠️  DEBUG=True (OK para {settings.ENVIRONMENT})")
    else:
        print(f"✅ DEBUG=False")
    
    # 3. ALLOWED_HOSTS
    print("\n[3] ALLOWED_HOSTS")
    print("-" * 70)
    if not settings.ALLOWED_HOSTS or settings.ALLOWED_HOSTS == ['']:
        if settings.ENVIRONMENT == 'production':
            issues.append("❌ ALLOWED_HOSTS vazio em produção!")
        else:
            warnings_list.append("⚠️  ALLOWED_HOSTS vazio (OK para dev)")
    else:
        print(f"✅ ALLOWED_HOSTS: {', '.join(settings.ALLOWED_HOSTS)}")
    
    # 4. HTTPS/SSL Settings
    print("\n[4] HTTPS/SSL Settings")
    print("-" * 70)
    ssl_configs = [
        ('SECURE_SSL_REDIRECT', settings.SECURE_SSL_REDIRECT),
        ('SESSION_COOKIE_SECURE', settings.SESSION_COOKIE_SECURE),
        ('CSRF_COOKIE_SECURE', settings.CSRF_COOKIE_SECURE),
    ]
    
    for name, value in ssl_configs:
        status = "✅" if value else "⚠️ "
        print(f"  {status} {name}: {value}")
        
        if not value and settings.ENVIRONMENT == 'production':
            warnings_list.append(f"⚠️  {name}=False em produção")
    
    # 5. HSTS Settings
    print("\n[5] HSTS Settings")
    print("-" * 70)
    if hasattr(settings, 'SECURE_HSTS_SECONDS'):
        print(f"  ✅ SECURE_HSTS_SECONDS: {settings.SECURE_HSTS_SECONDS}")
        if settings.ENVIRONMENT == 'production' and settings.SECURE_HSTS_SECONDS < 31536000:
            warnings_list.append("⚠️  HSTS seconds menor que 1 ano em produção")
    else:
        print("  ⚠️  SECURE_HSTS_SECONDS não configurado")
    
    # 6. Security Headers
    print("\n[6] Security Headers")
    print("-" * 70)
    headers = [
        ('SECURE_CONTENT_TYPE_NOSNIFF', settings.SECURE_CONTENT_TYPE_NOSNIFF),
        ('SECURE_BROWSER_XSS_FILTER', settings.SECURE_BROWSER_XSS_FILTER),
        ('X_FRAME_OPTIONS', settings.X_FRAME_OPTIONS),
    ]
    
    for name, value in headers:
        print(f"  ✅ {name}: {value}")
    
    # 7. Cookie Settings
    print("\n[7] Cookie Settings")
    print("-" * 70)
    cookies = [
        ('SESSION_COOKIE_HTTPONLY', settings.SESSION_COOKIE_HTTPONLY),
        ('SESSION_COOKIE_SAMESITE', settings.SESSION_COOKIE_SAMESITE),
        ('CSRF_COOKIE_HTTPONLY', settings.CSRF_COOKIE_HTTPONLY),
        ('CSRF_COOKIE_SAMESITE', settings.CSRF_COOKIE_SAMESITE),
    ]
    
    for name, value in cookies:
        print(f"  ✅ {name}: {value}")
    
    # 8. Password Validators
    print("\n[8] Password Validators")
    print("-" * 70)
    validators = settings.AUTH_PASSWORD_VALIDATORS
    if len(validators) >= 4:
        print(f"  ✅ {len(validators)} validadores configurados")
        for v in validators:
            name = v['NAME'].split('.')[-1]
            print(f"     • {name}")
    else:
        warnings_list.append(f"⚠️  Apenas {len(validators)} password validators")
    
    # 9. Middleware de Segurança
    print("\n[9] Security Middleware")
    print("-" * 70)
    required_middleware = [
        'django.middleware.security.SecurityMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
        'core.middleware.SecurityDetectionMiddleware',
    ]
    
    for mw in required_middleware:
        if mw in settings.MIDDLEWARE:
            print(f"  ✅ {mw.split('.')[-1]}")
        else:
            issues.append(f"❌ Middleware ausente: {mw}")
    
    # 10. CORS Settings
    print("\n[10] CORS Settings")
    print("-" * 70)
    if hasattr(settings, 'CORS_ALLOW_ALL_ORIGINS') and settings.CORS_ALLOW_ALL_ORIGINS:
        if settings.ENVIRONMENT == 'production':
            issues.append("❌ CORS_ALLOW_ALL_ORIGINS=True em produção!")
        else:
            warnings_list.append("⚠️  CORS_ALLOW_ALL_ORIGINS=True (OK para dev)")
    else:
        origins = getattr(settings, 'CORS_ALLOWED_ORIGINS', [])
        print(f"  ✅ CORS restrito a {len(origins)} origens")
        for origin in origins:
            print(f"     • {origin}")
    
    # 11. Upload Limits
    print("\n[11] Upload Limits")
    print("-" * 70)
    print(f"  ✅ DATA_UPLOAD_MAX_MEMORY_SIZE: {settings.DATA_UPLOAD_MAX_MEMORY_SIZE / (1024*1024):.1f} MB")
    print(f"  ✅ FILE_UPLOAD_MAX_MEMORY_SIZE: {settings.FILE_UPLOAD_MAX_MEMORY_SIZE / (1024*1024):.1f} MB")
    
    # 12. Rate Limiting
    print("\n[12] Rate Limiting (REST Framework)")
    print("-" * 70)
    if 'DEFAULT_THROTTLE_CLASSES' in settings.REST_FRAMEWORK:
        print(f"  ✅ Throttle classes configuradas")
        rates = settings.REST_FRAMEWORK.get('DEFAULT_THROTTLE_RATES', {})
        for key, rate in rates.items():
            print(f"     • {key}: {rate}")
    else:
        warnings_list.append("⚠️  Rate limiting não configurado")
    
    # Resumo
    print("\n" + "=" * 70)
    print("RESUMO DA VALIDAÇÃO")
    print("=" * 70)
    
    print(f"\n✅ Ambiente: {settings.ENVIRONMENT}")
    print(f"✅ Debug: {settings.DEBUG}")
    
    if issues:
        print(f"\n❌ PROBLEMAS CRÍTICOS ({len(issues)}):")
        for issue in issues:
            print(f"   {issue}")
    
    if warnings_list:
        print(f"\n⚠️  AVISOS ({len(warnings_list)}):")
        for warning in warnings_list:
            print(f"   {warning}")
    
    if not issues and not warnings_list:
        print("\n🎉 TODAS AS CONFIGURAÇÕES DE SEGURANÇA ESTÃO OK!")
    elif not issues:
        print("\n✅ Nenhum problema crítico encontrado")
        print("   Revise os avisos acima")
    else:
        print("\n⚠️  AÇÃO NECESSÁRIA!")
        print("   Corrija os problemas críticos antes do deploy")
    
    print("\n" + "=" * 70)
    
    return len(issues) == 0


if __name__ == '__main__':
    success = test_security_settings()
    sys.exit(0 if success else 1)
