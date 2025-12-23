"""
Script para testar o sistema de detecção de ameaças.
"""
import sys
from pathlib import Path

# Adicionar o diretório raiz ao path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# Configurar Django
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import RequestFactory
from core.middleware import SecurityDetectionMiddleware


def test_security_detection():
    """Testa a detecção de ameaças."""
    
    print("=" * 70)
    print("TESTANDO SISTEMA DE DETECÇÃO DE AMEAÇAS DE SEGURANÇA")
    print("=" * 70)
    
    factory = RequestFactory()
    middleware = SecurityDetectionMiddleware(lambda r: None)
    
    # Lista de testes
    tests = []
    
    # 1. Teste SQL Injection
    print("\n[TEST 1] SQL Injection Detection")
    print("-" * 70)
    
    sql_tests = [
        "/api/v1/professionals/?id=1' OR '1'='1",
        "/api/v1/appointments/?search='; DROP TABLE appointments; --",
        "/api/v1/professionals/?name=admin' UNION SELECT * FROM users--",
    ]
    
    for sql_path in sql_tests:
        request = factory.get(sql_path)
        result = middleware.process_request(request)
        status = "🔴 BLOCKED" if result is not None else "🟢 ALLOWED"
        print(f"  {status} - {sql_path}")
        tests.append(("SQL Injection", sql_path, result is not None))
    
    # 2. Teste XSS
    print("\n[TEST 2] XSS (Cross-Site Scripting) Detection")
    print("-" * 70)
    
    xss_tests = [
        "/api/v1/professionals/?name=<script>alert('XSS')</script>",
        "/api/v1/appointments/?search=<img src=x onerror=alert('XSS')>",
        "/api/v1/professionals/?query=javascript:alert(1)",
    ]
    
    for xss_path in xss_tests:
        request = factory.get(xss_path)
        result = middleware.process_request(request)
        status = "🔴 BLOCKED" if result is not None else "🟢 ALLOWED"
        print(f"  {status} - {xss_path}")
        tests.append(("XSS", xss_path, result is not None))
    
    # 3. Teste Path Traversal
    print("\n[TEST 3] Path Traversal Detection")
    print("-" * 70)
    
    path_tests = [
        "/api/v1/../../../etc/passwd",
        "/api/v1/professionals/?file=../../config/settings.py",
        "/api/v1/appointments/?path=..\\..\\windows\\system32",
    ]
    
    for path in path_tests:
        request = factory.get(path)
        result = middleware.process_request(request)
        status = "🔴 BLOCKED" if result is not None else "🟢 ALLOWED"
        print(f"  {status} - {path}")
        tests.append(("Path Traversal", path, result is not None))
    
    # 4. Teste User-Agent suspeito
    print("\n[TEST 4] Suspicious User-Agent Detection")
    print("-" * 70)
    
    ua_tests = [
        "sqlmap/1.0",
        "Nikto/2.1.6",
        "Nmap Scripting Engine",
        "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)",  # Normal
    ]
    
    for user_agent in ua_tests:
        request = factory.get("/api/v1/professionals/")
        request.META['HTTP_USER_AGENT'] = user_agent
        result = middleware.process_request(request)
        
        # User-agent suspeito não bloqueia, mas incrementa score
        is_suspicious = middleware._has_suspicious_user_agent(request)
        status = "⚠️  SUSPICIOUS" if is_suspicious else "🟢 NORMAL"
        print(f"  {status} - {user_agent[:50]}")
        tests.append(("User-Agent", user_agent, is_suspicious))
    
    # 5. Teste requisição normal (não deve ser bloqueada)
    print("\n[TEST 5] Normal Requests (should NOT be blocked)")
    print("-" * 70)
    
    normal_tests = [
        "/api/v1/professionals/",
        "/api/v1/appointments/?professional_id=1",
        "/api/v1/professionals/?search=João Silva",
    ]
    
    for normal_path in normal_tests:
        request = factory.get(normal_path)
        request.META['HTTP_USER_AGENT'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
        result = middleware.process_request(request)
        status = "🟢 ALLOWED" if result is None else "🔴 BLOCKED (ERROR!)"
        print(f"  {status} - {normal_path}")
        tests.append(("Normal Request", normal_path, result is None))
    
    # Estatísticas
    print("\n" + "=" * 70)
    print("RESUMO DOS TESTES")
    print("=" * 70)
    
    total = len(tests)
    
    # Contar testes de ameaças bloqueadas
    threat_tests = [t for t in tests if t[0] != "Normal Request"]
    threats_blocked = sum(1 for t in threat_tests if t[2])
    
    # Contar requisições normais permitidas
    normal_tests_list = [t for t in tests if t[0] == "Normal Request"]
    normal_allowed = sum(1 for t in normal_tests_list if t[2])
    
    print(f"\nAmeaças Detectadas: {threats_blocked}/{len(threat_tests)}")
    print(f"Requisições Normais Permitidas: {normal_allowed}/{len(normal_tests_list)}")
    print(f"\nTotal de Testes: {total}")
    
    # Verificação final
    print("\n" + "=" * 70)
    if threats_blocked == len(threat_tests) and normal_allowed == len(normal_tests_list):
        print("✅ TODOS OS TESTES PASSARAM!")
        print("   Sistema de segurança funcionando corretamente.")
    else:
        print("⚠️  ALGUNS TESTES FALHARAM")
        print("   Verifique a configuração do middleware.")
    print("=" * 70)
    
    print("\n📝 Arquivos de log gerados:")
    print("   - logs/security.log (logs de segurança)")
    print("   - logs/api.log (logs gerais)")
    print()


if __name__ == '__main__':
    test_security_detection()
