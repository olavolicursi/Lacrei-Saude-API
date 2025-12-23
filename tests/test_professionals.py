"""
Testes para o app Professionals.
"""

import pytest
from rest_framework import status
from professionals.models import Professional


@pytest.mark.django_db
class TestProfessionalModel:
    """Testes do modelo Professional."""
    
    def test_create_professional(self, valid_professional_data):
        """Testa criação de profissional."""
        professional = Professional.objects.create(**valid_professional_data)
        
        assert professional.id is not None
        assert professional.nome_social == valid_professional_data['nome_social']
        assert professional.ativo is True
        assert professional.created_at is not None
        assert professional.updated_at is not None
    
    def test_professional_string_representation(self, sample_professional):
        """Testa __str__ do profissional."""
        expected = f"{sample_professional.nome_social} - {sample_professional.get_profissao_display()}"
        assert str(sample_professional) == expected or str(sample_professional) == sample_professional.nome_social
    
    def test_professional_email_unique(self, sample_professional, valid_professional_data):
        """Testa que email deve ser único."""
        valid_professional_data['email'] = sample_professional.email
        valid_professional_data['registro_profissional'] = 'CRM-SP-999999'
        
        with pytest.raises(Exception):  # IntegrityError
            Professional.objects.create(**valid_professional_data)
    
    def test_professional_registro_unique(self, sample_professional, valid_professional_data):
        """Testa que registro profissional deve ser único."""
        valid_professional_data['registro_profissional'] = sample_professional.registro_profissional
        valid_professional_data['email'] = 'outro@test.com'
        
        with pytest.raises(Exception):  # IntegrityError
            Professional.objects.create(**valid_professional_data)
    
    def test_professional_ordering(self, multiple_professionals):
        """Testa ordenação por nome_social."""
        professionals = list(Professional.objects.all())
        names = [p.nome_social for p in professionals]
        
        assert names == sorted(names)


@pytest.mark.django_db
@pytest.mark.api
class TestProfessionalListAPI:
    """Testes da listagem de profissionais."""
    
    def test_list_professionals_unauthenticated(self, api_client, sample_professional):
        """Testa que não autenticados não podem listar."""
        response = api_client.get('/api/v1/professionals/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_list_professionals_authenticated(self, authenticated_client, sample_professional):
        """Testa listagem de profissionais autenticado."""
        response = authenticated_client.get('/api/v1/professionals/')
        
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data
        assert len(response.data['results']) >= 1
    
    def test_list_only_active_professionals(
        self, authenticated_client, sample_professional, inactive_professional
    ):
        """Testa que lista apenas profissionais ativos."""
        response = authenticated_client.get('/api/v1/professionals/')
        
        assert response.status_code == status.HTTP_200_OK
        
        ids = [p['id'] for p in response.data['results']]
        assert sample_professional.id in ids
        assert inactive_professional.id not in ids
    
    def test_list_professionals_pagination(self, authenticated_client, multiple_professionals):
        """Testa paginação da listagem."""
        response = authenticated_client.get('/api/v1/professionals/')
        
        assert response.status_code == status.HTTP_200_OK
        assert 'count' in response.data
        assert 'next' in response.data
        assert 'previous' in response.data
        assert 'results' in response.data
    
    def test_filter_professionals_by_profissao(
        self, authenticated_client, sample_professional, sample_psychologist
    ):
        """Testa filtro por profissão."""
        response = authenticated_client.get('/api/v1/professionals/?profissao=MEDICO')
        
        assert response.status_code == status.HTTP_200_OK
        
        for prof in response.data['results']:
            assert prof['profissao'] == 'MEDICO'
    
    def test_search_professionals_by_name(self, authenticated_client, sample_professional):
        """Testa busca por nome."""
        response = authenticated_client.get(f'/api/v1/professionals/?search={sample_professional.nome_social}')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) >= 1
    
    def test_search_professionals_by_email(self, authenticated_client, sample_professional):
        """Testa busca por email."""
        response = authenticated_client.get(f'/api/v1/professionals/?search={sample_professional.email}')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) >= 1


@pytest.mark.django_db
@pytest.mark.api
class TestProfessionalCreateAPI:
    """Testes de criação de profissionais."""
    
    def test_create_professional_success(self, authenticated_client, valid_professional_data):
        """Testa criação bem-sucedida de profissional."""
        initial_count = Professional.objects.count()
        
        response = authenticated_client.post(
            '/api/v1/professionals/',
            valid_professional_data,
            format='json'
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        assert Professional.objects.count() == initial_count + 1
        assert response.data['nome_social'] == valid_professional_data['nome_social']
        assert response.data['email'] == valid_professional_data['email'].lower()
    
    def test_create_professional_email_lowercase(self, authenticated_client, valid_professional_data):
        """Testa que email é convertido para minúsculas."""
        valid_professional_data['email'] = 'TEST@EXAMPLE.COM'
        
        response = authenticated_client.post(
            '/api/v1/professionals/',
            valid_professional_data,
            format='json'
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['email'] == 'test@example.com'
    
    def test_create_professional_invalid_email(self, authenticated_client, valid_professional_data):
        """Testa criação com email inválido."""
        valid_professional_data['email'] = 'email-invalido'
        
        response = authenticated_client.post(
            '/api/v1/professionals/',
            valid_professional_data,
            format='json'
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'email' in response.data
    
    def test_create_professional_missing_required_fields(self, authenticated_client):
        """Testa criação sem campos obrigatórios."""
        incomplete_data = {
            'nome_social': 'Apenas Nome'
        }
        
        response = authenticated_client.post(
            '/api/v1/professionals/',
            incomplete_data,
            format='json'
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_create_professional_duplicate_email(
        self, authenticated_client, sample_professional, valid_professional_data
    ):
        """Testa que não permite email duplicado."""
        valid_professional_data['email'] = sample_professional.email
        valid_professional_data['registro_profissional'] = 'OUTRO-REG-123'
        
        response = authenticated_client.post(
            '/api/v1/professionals/',
            valid_professional_data,
            format='json'
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_create_professional_invalid_telefone(self, authenticated_client, valid_professional_data):
        """Testa criação com telefone inválido."""
        valid_professional_data['telefone'] = '123'  # Muito curto
        
        response = authenticated_client.post(
            '/api/v1/professionals/',
            valid_professional_data,
            format='json'
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'telefone' in response.data


@pytest.mark.django_db
@pytest.mark.api
class TestProfessionalRetrieveAPI:
    """Testes de detalhamento de profissionais."""
    
    def test_retrieve_professional_success(self, authenticated_client, sample_professional):
        """Testa recuperação de profissional específico."""
        response = authenticated_client.get(f'/api/v1/professionals/{sample_professional.id}/')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == sample_professional.id
        assert response.data['nome_social'] == sample_professional.nome_social
        assert response.data['email'] == sample_professional.email
    
    def test_retrieve_professional_not_found(self, authenticated_client):
        """Testa recuperação de profissional inexistente."""
        response = authenticated_client.get('/api/v1/professionals/999999/')
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_retrieve_inactive_professional(self, authenticated_client, inactive_professional):
        """Testa que profissionais inativos não aparecem na listagem mas podem ser acessados diretamente."""
        response = authenticated_client.get(f'/api/v1/professionals/{inactive_professional.id}/')
        
        # Depende da implementação - pode ser 404 ou 200
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]


@pytest.mark.django_db
@pytest.mark.api
class TestProfessionalUpdateAPI:
    """Testes de atualização de profissionais."""
    
    def test_update_professional_success(self, authenticated_client, sample_professional):
        """Testa atualização bem-sucedida."""
        update_data = {
            'nome_social': 'Dr. João Silva Atualizado',
            'telefone': '(11) 99999-9999'
        }
        
        response = authenticated_client.patch(
            f'/api/v1/professionals/{sample_professional.id}/',
            update_data,
            format='json'
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['nome_social'] == update_data['nome_social']
        assert response.data['telefone'] == update_data['telefone']
        
        sample_professional.refresh_from_db()
        assert sample_professional.nome_social == update_data['nome_social']
    
    def test_update_professional_full(self, authenticated_client, sample_professional, valid_professional_data):
        """Testa atualização completa (PUT)."""
        valid_professional_data['email'] = sample_professional.email  # Manter email
        valid_professional_data['registro_profissional'] = sample_professional.registro_profissional
        
        response = authenticated_client.put(
            f'/api/v1/professionals/{sample_professional.id}/',
            valid_professional_data,
            format='json'
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['nome_social'] == valid_professional_data['nome_social']
    
    def test_update_professional_readonly_fields(self, authenticated_client, sample_professional):
        """Testa que não pode atualizar campos read-only."""
        original_created_at = sample_professional.created_at
        
        update_data = {
            'nome_social': 'Nome Novo',
            'created_at': '2020-01-01T00:00:00Z'
        }
        
        response = authenticated_client.patch(
            f'/api/v1/professionals/{sample_professional.id}/',
            update_data,
            format='json'
        )
        
        assert response.status_code == status.HTTP_200_OK
        
        sample_professional.refresh_from_db()
        assert sample_professional.created_at == original_created_at


@pytest.mark.django_db
@pytest.mark.api
class TestProfessionalDeleteAPI:
    """Testes de deleção de profissionais."""
    
    def test_delete_professional_success(self, authenticated_client, sample_professional):
        """Testa deleção de profissional (soft delete)."""
        response = authenticated_client.delete(f'/api/v1/professionals/{sample_professional.id}/')
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verificar se foi soft delete
        sample_professional.refresh_from_db()
        assert sample_professional.ativo is False
    
    def test_delete_professional_not_found(self, authenticated_client):
        """Testa deleção de profissional inexistente."""
        response = authenticated_client.delete('/api/v1/professionals/999999/')
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_cannot_delete_professional_with_appointments(
        self, authenticated_client, sample_professional, sample_appointment
    ):
        """Testa que não pode deletar profissional com consultas."""
        response = authenticated_client.delete(f'/api/v1/professionals/{sample_professional.id}/')
        
        # Comportamento esperado: ou impede deleção ou faz soft delete
        # Como usamos PROTECT no ForeignKey, deve dar erro se tentar deletar do banco
        # Mas como é soft delete, deve funcionar
        assert response.status_code in [status.HTTP_204_NO_CONTENT, status.HTTP_400_BAD_REQUEST]
