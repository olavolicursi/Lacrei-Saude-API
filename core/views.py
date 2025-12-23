from django.shortcuts import render
from django.http import JsonResponse
from django.db import connection
from django.conf import settings


def health_check(request):
    """
    Endpoint de health check para monitoramento e Docker healthcheck.
    Retorna o status da aplicação e conectividade do banco de dados.
    """
    status = {
        'status': 'healthy',
        'environment': settings.DEBUG and 'development' or 'production',
    }
    
    # Verificar conexão com o banco de dados
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        status['database'] = 'connected'
    except Exception as e:
        status['status'] = 'unhealthy'
        status['database'] = 'disconnected'
        status['error'] = str(e)
        return JsonResponse(status, status=503)
    
    return JsonResponse(status, status=200)

