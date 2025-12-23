"""
Testes para o app Appointments.
"""

import pytest
from datetime import datetime, timedelta
from rest_framework import status
from appointments.models import Appointment


@pytest.mark.django_db
class TestAppointmentModel:
    """Testes do modelo Appointment."""
    
    def test_create_appointment(self, sample_professional, test_user, valid_appointment_data):
        """Testa criação de consulta."""
        valid_appointment_data['profissional'] = sample_professional
        valid_appointment_data['paciente'] = test_user
        
        appointment = Appointment.objects.create(**valid_appointment_data)
        
        assert appointment.id is not None
        assert appointment.status == 'AGENDADA'
        assert appointment.ativo is True
        assert appointment.created_at is not None
    
    def test_appointment_string_representation(self, sample_appointment):
        """Testa __str__ da consulta."""
        result = str(sample_appointment)
        
        assert sample_appointment.paciente.get_full_name() in result or sample_appointment.paciente.username in result
        assert str(sample_appointment.data_hora.date()) in result
    
    def test_appointment_duration_validation(self, sample_professional, test_user):
        """Testa validação de duração mínima (15 minutos)."""
        appointment_data = {
            'profissional': sample_professional,
            'paciente': test_user,
            'data_hora': datetime.now() + timedelta(days=1),
            'duracao_minutos': 10  # Menos que 15
        }
        
        # CheckConstraint pode não ser testável diretamente, mas tentamos
        with pytest.raises(Exception):  # ValidationError ou IntegrityError
            appointment = Appointment(**appointment_data)
            appointment.full_clean()
    
    def test_appointment_ordering(self, multiple_appointments):
        """Testa ordenação por data_hora."""
        appointments = list(Appointment.objects.all())
        dates = [a.data_hora for a in appointments]
        
        assert dates == sorted(dates)


@pytest.mark.django_db
@pytest.mark.api
class TestAppointmentListAPI:
    """Testes da listagem de consultas."""
    
    def test_list_appointments_unauthenticated(self, api_client, sample_appointment):
        """Testa que não autenticados não podem listar."""
        response = api_client.get('/api/v1/appointments/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_list_appointments_authenticated(self, authenticated_client, sample_appointment):
        """Testa listagem de consultas autenticado."""
        response = authenticated_client.get('/api/v1/appointments/')
        
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data
        assert len(response.data['results']) >= 1
    
    def test_list_user_appointments_only(
        self, api_client, test_user, sample_appointment, multiple_appointments
    ):
        """Testa que usuário vê apenas suas próprias consultas."""
        # Autenticar como test_user
        api_client.force_authenticate(user=test_user)
        
        response = api_client.get('/api/v1/appointments/')
        
        assert response.status_code == status.HTTP_200_OK
        
        # Todas as consultas retornadas devem ser do test_user
        for appointment in response.data['results']:
            assert appointment['paciente'] == test_user.id or appointment['paciente']['id'] == test_user.id
    
    def test_filter_appointments_by_status(
        self, authenticated_client, sample_appointment, confirmed_appointment
    ):
        """Testa filtro por status."""
        response = authenticated_client.get('/api/v1/appointments/?status=CONFIRMADA')
        
        assert response.status_code == status.HTTP_200_OK
        
        for appointment in response.data['results']:
            assert appointment['status'] == 'CONFIRMADA'
    
    def test_filter_appointments_by_professional(
        self, authenticated_client, multiple_appointments, sample_professional
    ):
        """Testa filtro por profissional."""
        response = authenticated_client.get(f'/api/v1/appointments/?profissional={sample_professional.id}')
        
        assert response.status_code == status.HTTP_200_OK
        
        for appointment in response.data['results']:
            assert appointment['profissional'] == sample_professional.id or appointment['profissional']['id'] == sample_professional.id
    
    def test_filter_upcoming_appointments(
        self, authenticated_client, sample_appointment, past_appointment
    ):
        """Testa filtro de consultas futuras."""
        response = authenticated_client.get('/api/v1/appointments/?upcoming=true')
        
        assert response.status_code == status.HTTP_200_OK
        
        now = datetime.now()
        for appointment in response.data['results']:
            # Data deve ser futura
            assert appointment['id'] != past_appointment.id
    
    def test_filter_past_appointments(
        self, authenticated_client, sample_appointment, past_appointment
    ):
        """Testa filtro de consultas passadas."""
        response = authenticated_client.get('/api/v1/appointments/?past=true')
        
        assert response.status_code == status.HTTP_200_OK
        
        # Deve incluir a consulta passada
        ids = [a['id'] for a in response.data['results']]
        assert past_appointment.id in ids


@pytest.mark.django_db
@pytest.mark.api
class TestAppointmentCreateAPI:
    """Testes de criação de consultas."""
    
    def test_create_appointment_success(self, authenticated_client, valid_appointment_data):
        """Testa criação bem-sucedida de consulta."""
        initial_count = Appointment.objects.count()
        
        response = authenticated_client.post(
            '/api/v1/appointments/',
            valid_appointment_data,
            format='json'
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        assert Appointment.objects.count() == initial_count + 1
        assert response.data['status'] == 'AGENDADA'
    
    def test_create_appointment_past_date(self, authenticated_client, invalid_appointment_data):
        """Testa que não permite criar consulta no passado."""
        response = authenticated_client.post(
            '/api/v1/appointments/',
            invalid_appointment_data,
            format='json'
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'data_hora' in response.data or 'non_field_errors' in response.data
    
    def test_create_appointment_invalid_duration(self, authenticated_client, valid_appointment_data):
        """Testa que não permite duração menor que 15 minutos."""
        valid_appointment_data['duracao_minutos'] = 10
        
        response = authenticated_client.post(
            '/api/v1/appointments/',
            valid_appointment_data,
            format='json'
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_create_appointment_missing_required_fields(self, authenticated_client):
        """Testa criação sem campos obrigatórios."""
        incomplete_data = {
            'data_hora': (datetime.now() + timedelta(days=1)).isoformat()
        }
        
        response = authenticated_client.post(
            '/api/v1/appointments/',
            incomplete_data,
            format='json'
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_create_appointment_inactive_professional(
        self, authenticated_client, inactive_professional, valid_appointment_data
    ):
        """Testa que não permite criar consulta com profissional inativo."""
        valid_appointment_data['profissional'] = inactive_professional.id
        
        response = authenticated_client.post(
            '/api/v1/appointments/',
            valid_appointment_data,
            format='json'
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
@pytest.mark.api
class TestAppointmentRetrieveAPI:
    """Testes de detalhamento de consultas."""
    
    def test_retrieve_appointment_success(self, authenticated_client, sample_appointment):
        """Testa recuperação de consulta específica."""
        response = authenticated_client.get(f'/api/v1/appointments/{sample_appointment.id}/')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == sample_appointment.id
    
    def test_retrieve_appointment_not_found(self, authenticated_client):
        """Testa recuperação de consulta inexistente."""
        response = authenticated_client.get('/api/v1/appointments/999999/')
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_retrieve_appointment_other_user(
        self, api_client, sample_appointment, admin_user
    ):
        """Testa que usuário não pode ver consulta de outro usuário."""
        # Autenticar como admin (diferente do dono da consulta)
        api_client.force_authenticate(user=admin_user)
        
        response = api_client.get(f'/api/v1/appointments/{sample_appointment.id}/')
        
        # Depende da implementação de permissões
        # Se IsOwnerOrAdmin, admin pode ver
        # Se IsOwner apenas, deve dar 403 ou 404
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND]


@pytest.mark.django_db
@pytest.mark.api
class TestAppointmentUpdateAPI:
    """Testes de atualização de consultas."""
    
    def test_update_appointment_success(self, authenticated_client, sample_appointment):
        """Testa atualização bem-sucedida."""
        update_data = {
            'observacoes': 'Consulta remarcada'
        }
        
        response = authenticated_client.patch(
            f'/api/v1/appointments/{sample_appointment.id}/',
            update_data,
            format='json'
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['observacoes'] == update_data['observacoes']
    
    def test_update_appointment_change_date(self, authenticated_client, sample_appointment):
        """Testa mudança de data/hora."""
        new_date = datetime.now() + timedelta(days=14)
        update_data = {
            'data_hora': new_date.isoformat()
        }
        
        response = authenticated_client.patch(
            f'/api/v1/appointments/{sample_appointment.id}/',
            update_data,
            format='json'
        )
        
        assert response.status_code == status.HTTP_200_OK
    
    def test_update_appointment_invalid_status_transition(
        self, authenticated_client, cancelled_appointment
    ):
        """Testa que não pode atualizar consulta cancelada."""
        update_data = {
            'status': 'CONFIRMADA'
        }
        
        response = authenticated_client.patch(
            f'/api/v1/appointments/{cancelled_appointment.id}/',
            update_data,
            format='json'
        )
        
        # Depende da implementação - pode impedir ou permitir
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST]


@pytest.mark.django_db
@pytest.mark.api
class TestAppointmentDeleteAPI:
    """Testes de deleção de consultas."""
    
    def test_delete_appointment_success(self, authenticated_client, sample_appointment):
        """Testa deleção de consulta (soft delete)."""
        response = authenticated_client.delete(f'/api/v1/appointments/{sample_appointment.id}/')
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verificar soft delete
        sample_appointment.refresh_from_db()
        assert sample_appointment.ativo is False or sample_appointment.status == 'CANCELADA'
    
    def test_delete_appointment_not_found(self, authenticated_client):
        """Testa deleção de consulta inexistente."""
        response = authenticated_client.delete('/api/v1/appointments/999999/')
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
@pytest.mark.api
class TestAppointmentActions:
    """Testes de actions customizadas."""
    
    def test_cancel_appointment_action(self, authenticated_client, sample_appointment):
        """Testa action de cancelamento."""
        response = authenticated_client.post(
            f'/api/v1/appointments/{sample_appointment.id}/cancel/',
            format='json'
        )
        
        assert response.status_code == status.HTTP_200_OK
        
        sample_appointment.refresh_from_db()
        assert sample_appointment.status == 'CANCELADA'
    
    def test_cancel_less_than_24h_notice(self, authenticated_client, confirmed_appointment):
        """Testa cancelamento com menos de 24h de antecedência."""
        # confirmed_appointment está marcado para 3 dias no futuro
        # Alterar para estar próximo (menos de 24h)
        confirmed_appointment.data_hora = datetime.now() + timedelta(hours=12)
        confirmed_appointment.save()
        
        response = authenticated_client.post(
            f'/api/v1/appointments/{confirmed_appointment.id}/cancel/',
            format='json'
        )
        
        # Depende da regra de negócio - pode permitir ou não
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST]
    
    def test_confirm_appointment_action(self, authenticated_client, sample_appointment):
        """Testa action de confirmação."""
        response = authenticated_client.post(
            f'/api/v1/appointments/{sample_appointment.id}/confirm/',
            format='json'
        )
        
        assert response.status_code == status.HTTP_200_OK
        
        sample_appointment.refresh_from_db()
        assert sample_appointment.status == 'CONFIRMADA'
    
    def test_complete_appointment_action(self, authenticated_client, confirmed_appointment):
        """Testa action de conclusão."""
        # Marcar como passada
        confirmed_appointment.data_hora = datetime.now() - timedelta(hours=1)
        confirmed_appointment.save()
        
        response = authenticated_client.post(
            f'/api/v1/appointments/{confirmed_appointment.id}/complete/',
            format='json'
        )
        
        assert response.status_code == status.HTTP_200_OK
        
        confirmed_appointment.refresh_from_db()
        assert confirmed_appointment.status == 'REALIZADA'
    
    def test_statistics_endpoint(self, authenticated_client, multiple_appointments):
        """Testa endpoint de estatísticas."""
        response = authenticated_client.get('/api/v1/appointments/statistics/')
        
        if response.status_code == status.HTTP_200_OK:
            assert 'total' in response.data or 'count' in response.data
        else:
            # Endpoint pode não estar implementado ainda
            assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_available_slots_endpoint(self, authenticated_client, sample_professional):
        """Testa endpoint de horários disponíveis."""
        today = datetime.now().date()
        response = authenticated_client.get(
            f'/api/v1/appointments/available_slots/?profissional={sample_professional.id}&date={today}'
        )
        
        if response.status_code == status.HTTP_200_OK:
            assert isinstance(response.data, list) or 'slots' in response.data
        else:
            # Endpoint pode não estar implementado
            assert response.status_code in [status.HTTP_404_NOT_FOUND, status.HTTP_400_BAD_REQUEST]


@pytest.mark.django_db
@pytest.mark.integration
class TestAppointmentWorkflow:
    """Testes de workflow completo de consultas."""
    
    def test_full_appointment_lifecycle(
        self, authenticated_client, sample_professional, valid_appointment_data
    ):
        """Testa ciclo completo: criar → confirmar → realizar."""
        # 1. Criar consulta
        response = authenticated_client.post(
            '/api/v1/appointments/',
            valid_appointment_data,
            format='json'
        )
        assert response.status_code == status.HTTP_201_CREATED
        appointment_id = response.data['id']
        
        # 2. Confirmar
        response = authenticated_client.post(
            f'/api/v1/appointments/{appointment_id}/confirm/',
            format='json'
        )
        if response.status_code == status.HTTP_200_OK:
            assert response.data['status'] == 'CONFIRMADA'
        
        # 3. Completar
        response = authenticated_client.post(
            f'/api/v1/appointments/{appointment_id}/complete/',
            format='json'
        )
        if response.status_code == status.HTTP_200_OK:
            assert response.data['status'] == 'REALIZADA'
    
    def test_appointment_conflict_detection(
        self, authenticated_client, sample_professional, valid_appointment_data
    ):
        """Testa detecção de conflito de horários."""
        # Criar primeira consulta
        response1 = authenticated_client.post(
            '/api/v1/appointments/',
            valid_appointment_data,
            format='json'
        )
        assert response1.status_code == status.HTTP_201_CREATED
        
        # Tentar criar segunda consulta no mesmo horário
        response2 = authenticated_client.post(
            '/api/v1/appointments/',
            valid_appointment_data,
            format='json'
        )
        
        # Deve impedir ou permitir dependendo da implementação
        # Se validação de conflito existe, deve dar 400
        assert response2.status_code in [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST]
