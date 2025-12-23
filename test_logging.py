"""
Script para testar o sistema de logging fazendo uma requisição à API.
"""
import logging
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

# Agora podemos importar os módulos do Django
from django.test import RequestFactory
from appointments.views import AppointmentViewSet

# Criar um logger para este script
logger = logging.getLogger('appointments')

def test_logging():
    """Testa o sistema de logging fazendo uma chamada simulada."""
    
    print("=" * 60)
    print("TESTANDO SISTEMA DE LOGGING")
    print("=" * 60)
    
    # Criar uma requisição fake
    factory = RequestFactory()
    request = factory.get('/api/v1/appointments/')
    
    # Adicionar um usuário fake à requisição
    from django.contrib.auth.models import AnonymousUser
    request.user = AnonymousUser()
    
    # Log de teste
    logger.info("Iniciando teste de logging...")
    logger.info(f"Requisição: GET {request.path}")
    
    # Tentar listar appointments (vai falhar porque não está autenticado, mas vai gerar logs)
    try:
        view = AppointmentViewSet.as_view({'get': 'list'})
        response = view(request)
        logger.info(f"Resposta recebida com status: {response.status_code}")
    except Exception as e:
        logger.error(f"Erro ao processar requisição: {e}", exc_info=True)
    
    # Logs de diferentes níveis
    logger.debug("Este é um log de DEBUG (não deve aparecer)")
    logger.info("Este é um log de INFO")
    logger.warning("Este é um log de WARNING")
    logger.error("Este é um log de ERROR")
    
    print("\n" + "=" * 60)
    print("TESTE CONCLUÍDO!")
    print("=" * 60)
    print("\nVerifique os arquivos de log em:")
    print("  - logs/api.log (todos os logs)")
    print("  - logs/errors.log (apenas erros)")
    print("  - logs/security.log (logs de segurança)")
    print()

if __name__ == '__main__':
    test_logging()
