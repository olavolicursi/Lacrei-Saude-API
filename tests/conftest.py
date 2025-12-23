"""
Configurações e fixtures compartilhadas para testes pytest.
"""

import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from datetime import datetime, timedelta
from professionals.models import Professional
from appointments.models import Appointment


# ==============================================================================
# Fixtures de Clientes API
# ==============================================================================

@pytest.fixture
def api_client():
    """Cliente API não autenticado."""
    return APIClient()


@pytest.fixture
def authenticated_client(db, test_user):
    """Cliente API autenticado."""
    client = APIClient()
    client.force_authenticate(user=test_user)
    return client


@pytest.fixture
def admin_client(db, admin_user):
    """Cliente API autenticado como admin."""
    client = APIClient()
    client.force_authenticate(user=admin_user)
    return client


# ==============================================================================
# Fixtures de Usuários
# ==============================================================================

@pytest.fixture
def test_user(db):
    """Usuário de teste padrão."""
    return User.objects.create_user(
        username='testuser',
        email='testuser@test.com',
        password='testpass123'
    )


@pytest.fixture
def admin_user(db):
    """Usuário administrador."""
    return User.objects.create_superuser(
        username='admin',
        email='admin@test.com',
        password='adminpass123'
    )


@pytest.fixture
def multiple_users(db):
    """Cria múltiplos usuários para testes."""
    users = []
    for i in range(3):
        user = User.objects.create_user(
            username=f'user{i}',
            email=f'user{i}@test.com',
            password='testpass123'
        )
        users.append(user)
    return users


# ==============================================================================
# Fixtures de Profissionais
# ==============================================================================

@pytest.fixture
def sample_professional(db):
    """Profissional de teste padrão."""
    return Professional.objects.create(
        nome_social="Dr. João Silva",
        profissao="MEDICO",
        registro_profissional="CRM-SP-123456",
        cep="01310-100",
        logradouro="Av. Paulista",
        numero="1000",
        bairro="Bela Vista",
        cidade="São Paulo",
        estado="SP",
        telefone="(11) 98765-4321",
        email="joao.silva@test.com",
        ativo=True
    )


@pytest.fixture
def sample_psychologist(db):
    """Psicólogo de teste."""
    return Professional.objects.create(
        nome_social="Dra. Maria Santos",
        profissao="PSICOLOGO",
        registro_profissional="CRP-SP-654321",
        cep="04567-890",
        logradouro="Rua Augusta",
        numero="2000",
        bairro="Consolação",
        cidade="São Paulo",
        estado="SP",
        telefone="(11) 91234-5678",
        email="maria.santos@test.com",
        ativo=True
    )


@pytest.fixture
def sample_nutritionist(db):
    """Nutricionista de teste."""
    return Professional.objects.create(
        nome_social="Dr. Carlos Oliveira",
        profissao="NUTRICIONISTA",
        registro_profissional="CRN-SP-789012",
        cep="05678-123",
        logradouro="Rua Oscar Freire",
        numero="500",
        bairro="Jardins",
        cidade="São Paulo",
        estado="SP",
        telefone="(11) 99876-5432",
        email="carlos.oliveira@test.com",
        ativo=True
    )


@pytest.fixture
def inactive_professional(db):
    """Profissional inativo."""
    return Professional.objects.create(
        nome_social="Dr. Pedro Inativo",
        profissao="MEDICO",
        registro_profissional="CRM-SP-999999",
        cep="01234-567",
        logradouro="Rua Teste",
        numero="100",
        bairro="Centro",
        cidade="São Paulo",
        estado="SP",
        telefone="(11) 91111-2222",
        email="pedro.inativo@test.com",
        ativo=False
    )


@pytest.fixture
def multiple_professionals(db):
    """Cria múltiplos profissionais para testes."""
    professionals = []
    professions = ['MEDICO', 'PSICOLOGO', 'NUTRICIONISTA']
    
    for i, prof in enumerate(professions):
        professional = Professional.objects.create(
            nome_social=f"Dr. Teste {i}",
            profissao=prof,
            registro_profissional=f"REG-{i}-{prof}",
            cep=f"0{i}000-000",
            logradouro=f"Rua Teste {i}",
            numero=str(i * 100),
            bairro="Bairro Teste",
            cidade="São Paulo",
            estado="SP",
            telefone=f"(11) 9000{i}-000{i}",
            email=f"teste{i}@test.com",
            ativo=True
        )
        professionals.append(professional)
    
    return professionals


# ==============================================================================
# Fixtures de Consultas (Appointments)
# ==============================================================================

@pytest.fixture
def sample_appointment(db, sample_professional):
    """Consulta de teste padrão (futura)."""
    future_date = datetime.now() + timedelta(days=7)
    return Appointment.objects.create(
        professional=sample_professional,
        data_hora=future_date,
        duracao_minutos=60,
        status='AGENDADA',
        paciente_nome="João Paciente",
        paciente_email="joao.paciente@test.com",
        paciente_telefone="(11) 98888-7777",
        observacoes="Consulta de rotina"
    )


@pytest.fixture
def confirmed_appointment(db, sample_professional):
    """Consulta confirmada."""
    future_date = datetime.now() + timedelta(days=3)
    return Appointment.objects.create(
        professional=sample_professional,
        data_hora=future_date,
        duracao_minutos=45,
        status='CONFIRMADA',
        paciente_nome="Maria Paciente",
        paciente_email="maria.paciente@test.com",
        paciente_telefone="(11) 97777-6666"
    )


@pytest.fixture
def past_appointment(db, sample_professional):
    """Consulta passada (realizada)."""
    past_date = datetime.now() - timedelta(days=7)
    return Appointment.objects.create(
        professional=sample_professional,
        data_hora=past_date,
        duracao_minutos=60,
        status='REALIZADA',
        paciente_nome="Carlos Paciente",
        paciente_email="carlos.paciente@test.com",
        paciente_telefone="(11) 96666-5555"
    )


@pytest.fixture
def cancelled_appointment(db, sample_professional):
    """Consulta cancelada."""
    future_date = datetime.now() + timedelta(days=5)
    return Appointment.objects.create(
        professional=sample_professional,
        data_hora=future_date,
        duracao_minutos=30,
        status='CANCELADA',
        paciente_nome="Ana Paciente",
        paciente_email="ana.paciente@test.com",
        paciente_telefone="(11) 95555-4444",
        observacoes="Paciente cancelou com antecedência"
    )


@pytest.fixture
def multiple_appointments(db, sample_professional, sample_psychologist):
    """Cria múltiplas consultas para diferentes profissionais."""
    appointments = []
    
    # 3 consultas futuras para o médico
    for i in range(3):
        future_date = datetime.now() + timedelta(days=i+1)
        appointment = Appointment.objects.create(
            professional=sample_professional,
            data_hora=future_date,
            duracao_minutos=60,
            status='AGENDADA',
            paciente_nome=f"Paciente {i}",
            paciente_email=f"paciente{i}@test.com",
            paciente_telefone=f"(11) 9000{i}-000{i}"
        )
        appointments.append(appointment)
    
    # 2 consultas futuras para o psicólogo
    for i in range(2):
        future_date = datetime.now() + timedelta(days=i+5)
        appointment = Appointment.objects.create(
            professional=sample_psychologist,
            data_hora=future_date,
            duracao_minutos=45,
            status='AGENDADA',
            paciente_nome=f"Paciente Psi {i}",
            paciente_email=f"paciente.psi{i}@test.com",
            paciente_telefone=f"(11) 9100{i}-100{i}"
        )
        appointments.append(appointment)
    
    return appointments


# ==============================================================================
# Fixtures de Dados de Teste
# ==============================================================================

@pytest.fixture
def valid_professional_data():
    """Dados válidos para criar um profissional."""
    return {
        'nome_social': 'Dr. Novo Profissional',
        'profissao': 'MEDICO',
        'registro_profissional': 'CRM-RJ-111111',
        'cep': '20000-000',
        'logradouro': 'Rua Nova',
        'numero': '123',
        'complemento': 'Sala 101',
        'bairro': 'Centro',
        'cidade': 'Rio de Janeiro',
        'estado': 'RJ',
        'telefone': '(21) 98888-9999',
        'email': 'novo.profissional@test.com'
    }


@pytest.fixture
def invalid_professional_data():
    """Dados inválidos para criar um profissional."""
    return {
        'nome_social': '',  # Vazio
        'profissao': 'INVALIDO',  # Profissão inválida
        'registro_profissional': '',
        'email': 'email-invalido'  # Email inválido
    }


@pytest.fixture
def valid_appointment_data(sample_professional):
    """Dados válidos para criar uma consulta."""
    future_date = datetime.now() + timedelta(days=10)
    return {
        'professional': sample_professional.id,
        'data_hora': future_date.isoformat(),
        'duracao_minutos': 60,
        'paciente_nome': 'Paciente Novo',
        'paciente_email': 'paciente.novo@test.com',
        'paciente_telefone': '(11) 99999-8888',
        'observacoes': 'Primeira consulta'
    }


@pytest.fixture
def invalid_appointment_data():
    """Dados inválidos para criar uma consulta."""
    past_date = datetime.now() - timedelta(days=1)
    return {
        'professional': 999999,  # ID inexistente
        'data_hora': past_date.isoformat(),  # Data no passado
        'duracao_minutos': 10,  # Duração menor que mínimo
        'paciente_nome': '',  # Vazio
        'paciente_email': 'email-invalido',
        'paciente_telefone': '123'  # Telefone inválido
    }


# ==============================================================================
# Fixtures de Configuração
# ==============================================================================

@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    """Habilita acesso ao banco de dados para todos os testes."""
    pass


@pytest.fixture
def clear_cache():
    """Limpa o cache antes/depois do teste."""
    from django.core.cache import cache
    cache.clear()
    yield
    cache.clear()


@pytest.fixture
def mock_datetime_now():
    """Mock para datetime.now() em testes."""
    from unittest.mock import patch
    from datetime import datetime
    
    fixed_time = datetime(2025, 12, 23, 12, 0, 0)
    
    with patch('datetime.datetime') as mock_datetime:
        mock_datetime.now.return_value = fixed_time
        mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)
        yield fixed_time


# ==============================================================================
# Fixtures de Ambiente de Teste
# ==============================================================================

@pytest.fixture(scope='session')
def django_db_setup():
    """Configuração do banco de dados de teste."""
    from django.conf import settings
    
    # Garantir que estamos em modo de teste
    settings.DEBUG = False
    settings.TESTING = True


@pytest.fixture
def capture_logs():
    """Captura logs durante o teste."""
    import logging
    from io import StringIO
    
    log_stream = StringIO()
    handler = logging.StreamHandler(log_stream)
    handler.setLevel(logging.INFO)
    
    logger = logging.getLogger()
    logger.addHandler(handler)
    
    yield log_stream
    
    logger.removeHandler(handler)


# ==============================================================================
# Markers e Helpers
# ==============================================================================

def pytest_configure(config):
    """Configuração customizada do pytest."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "security: marks tests as security tests"
    )
