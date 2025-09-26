
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from unittest.mock import patch
from app.config import TestingConfig
from app import create_app, db
from app.models import User, PasswordResetToken
from datetime import datetime, timedelta

@pytest.fixture(scope='module')
def test_app():
    """Cria uma instância do app para testes."""
    app = create_app(config_class=TestingConfig)
    yield app

@pytest.fixture(scope='module')
def test_client(test_app):
    """Cria um cliente de teste para fazer requisições."""
    return test_app.test_client()

@pytest.fixture(scope='function')
def init_database(test_app):
    """Limpa o banco de dados antes de cada teste."""
    with test_app.app_context():
        db.create_all()
        yield db
        db.session.remove()
        db.drop_all()

def test_register_success(test_client, init_database, test_app):
    """Testa o registro de um novo usuário com sucesso."""
    response = test_client.post('/api/register', json={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'password123'
    }, headers={'Content-Type': 'application/json'})
    assert response.status_code == 201
    assert response.json['success'] is True
    
    with test_app.app_context():
        user = User.query.filter_by(email='test@example.com').first()
        assert user is not None
        assert user.username == 'testuser'

def test_register_existing_user(test_client, init_database, test_app):
    """Testa o registro com um email que já existe."""
    # Cria um usuário primeiro
    with test_app.app_context():
        response = test_client.post('/api/register', json={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'password123'
        }, headers={'Content-Type': 'application/json'})
    # Tenta registrar de novo
    response = test_client.post('/api/register', json={
        'username': 'anotheruser',
        'email': 'test@example.com',
        'password': 'password456'
    }, headers={'Content-Type': 'application/json'})
    assert response.status_code == 409
    assert response.json['message'] == 'Usuário ou email já existente'

def test_login_success(test_client, init_database):
    """Testa o login com credenciais corretas."""
    # Registra um usuário para poder logar
    test_client.post('/api/register', json={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'password123'
    }, headers={'Content-Type': 'application/json'})
    
    response = test_client.post('/api/login', json={
        'email': 'test@example.com',
        'password': 'password123'
    }, headers={'Content-Type': 'application/json'})
    assert response.status_code == 200
    assert 'access_token' in response.json

def test_login_wrong_password(test_client, init_database):
    """Testa o login com a senha errada."""
    # Registra um usuário
    test_client.post('/api/register', json={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'password123'
    }, headers={'Content-Type': 'application/json'})
    
    response = test_client.post('/api/login', json={
        'email': 'test@example.com',
        'password': 'wrongpassword'
    }, headers={'Content-Type': 'application/json'})
    assert response.status_code == 401
    assert response.json['message'] == 'Credenciais inválidas'

def test_login_nonexistent_user(test_client, init_database):
    """Testa o login com um usuário que não existe."""
    response = test_client.post('/api/login', json={
        'email': 'nonexistent@example.com',
        'password': 'password123'
    }, headers={'Content-Type': 'application/json'})
    assert response.status_code == 401
    assert response.json['message'] == 'Credenciais inválidas'

@patch('app.routes.mail.send')
def test_request_password_reset_success(mock_mail_send, test_client, init_database, test_app):
    """Testa a solicitação de redefinição de senha com sucesso."""
    # Registra um usuário
    test_client.post('/api/register', json={
        'username': 'resetuser',
        'email': 'reset@example.com',
        'password': 'password123'
    }, headers={'Content-Type': 'application/json'})

    response = test_client.post('/api/request-password-reset', json={'email': 'reset@example.com'})
    assert response.status_code == 200
    assert response.json['message'] == 'Email de redefinição de senha enviado.'
    mock_mail_send.assert_called_once()

    with test_app.app_context():
        user = User.query.filter_by(email='reset@example.com').first()
        token_entry = PasswordResetToken.query.filter_by(user_id=user.id).first()
        assert token_entry is not None
        assert token_entry.token is not None

@patch('app.routes.mail.send')
def test_request_password_reset_nonexistent_email(mock_mail_send, test_client, init_database):
    """Testa a solicitação de redefinição de senha para um email não existente."""
    response = test_client.post('/api/request-password-reset', json={'email': 'nonexistent@example.com'})
    assert response.status_code == 404
    assert response.json['message'] == 'Email não encontrado.'
    mock_mail_send.assert_not_called()

@patch('app.routes.mail.send')
def test_reset_password_success(mock_mail_send, test_client, init_database, test_app):
    """Testa a redefinição de senha com um token válido."""
    # Registra um usuário
    test_client.post('/api/register', json={
        'username': 'resetuser2',
        'email': 'reset2@example.com',
        'password': 'oldpassword'
    }, headers={'Content-Type': 'application/json'})

    # Solicita a redefinição para gerar um token
    test_client.post('/api/request-password-reset', json={'email': 'reset2@example.com'})
    
    with test_app.app_context():
        user = User.query.filter_by(email='reset2@example.com').first()
        token_entry = PasswordResetToken.query.filter_by(user_id=user.id).first()
        token = token_entry.token

    response = test_client.post(f'/api/reset-password/{token}', json={'password': 'newpassword123'})
    assert response.status_code == 200
    assert response.json['message'] == 'Senha redefinida com sucesso.'

    # Verifica se a senha foi alterada
    login_response = test_client.post('/api/login', json={'email': 'reset2@example.com', 'password': 'newpassword123'})
    assert login_response.status_code == 200
    assert 'access_token' in login_response.json

    # Verifica se o token foi removido
    with test_app.app_context():
        token_entry_after_reset = PasswordResetToken.query.filter_by(token=token).first()
        assert token_entry_after_reset is None

@patch('app.routes.mail.send')
def test_reset_password_invalid_token(mock_mail_send, test_client, init_database):
    """Testa a redefinição de senha com um token inválido."""
    response = test_client.post('/api/reset-password/invalidtoken123', json={'password': 'newpassword'})
    assert response.status_code == 200  # A rota retorna 200 com mensagem de erro
    assert response.json['message'] == 'Token inválido ou expirado.'

@patch('app.routes.mail.send')
def test_reset_password_expired_token(mock_mail_send, test_client, init_database, test_app):
    """Testa a redefinição de senha com um token expirado."""
    # Registra um usuário
    test_client.post('/api/register', json={
        'username': 'resetuser3',
        'email': 'reset3@example.com',
        'password': 'oldpassword'
    }, headers={'Content-Type': 'application/json'})

    # Solicita a redefinição para gerar um token
    test_client.post('/api/request-password-reset', json={'email': 'reset3@example.com'})
    
    with test_app.app_context():
        user = User.query.filter_by(email='reset3@example.com').first()
        token_entry = PasswordResetToken.query.filter_by(user_id=user.id).first()
        token = token_entry.token
        # Manually expire the token
        token_entry.expires_at = datetime.utcnow() - timedelta(hours=1)
        db.session.add(token_entry)
        db.session.commit()

    response = test_client.post(f'/api/reset-password/{token}', json={'password': 'newpassword'})
    assert response.status_code == 200  # A rota retorna 200 com mensagem de erro
    assert response.json['message'] == 'Token inválido ou expirado.'
    
    # Tenta logar com a senha antiga (deve falhar)
    login_response = test_client.post('/api/login', json={'email': 'reset3@example.com', 'password': 'oldpassword'})
    assert login_response.status_code == 200
    
    # Tenta logar com a nova senha (deve falhar, pois a senha não foi redefinida)
    login_response = test_client.post('/api/login', json={'email': 'reset3@example.com', 'password': 'newpassword'})
    assert login_response.status_code == 401
