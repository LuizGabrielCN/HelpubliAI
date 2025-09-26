import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from app.config import TestingConfig
from app import create_app, db
from app.models import User, Collection

# Re-usando as fixtures do conftest ou definindo-as aqui se necessário
# Por simplicidade, vamos assumir que as fixtures de test_auth.py estão disponíveis
# ou vamos recriá-las.

@pytest.fixture(scope='module')
def test_app():
    app = create_app(config_class=TestingConfig)
    with app.app_context():
        yield app

@pytest.fixture(scope='module')
def test_client(test_app):
    return test_app.test_client()

@pytest.fixture(scope='function')
def init_database(test_app):
    with test_app.app_context():
        db.create_all()
        yield db
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope='function')
def auth_headers(test_client, init_database):
    """Cria um usuário, faz login e retorna os headers de autorização."""
    test_client.post('/api/register', json={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'password123'
    }, headers={'Content-Type': 'application/json'})
    response = test_client.post('/api/login', json={
        'email': 'test@example.com',
        'password': 'password123'
    }, headers={'Content-Type': 'application/json'})
    assert response.status_code == 200, f"Login failed with status {response.status_code} and response {response.json}"
    print(f"Login Status Code: {response.status_code}")
    print(f"Login Response JSON: {response.json}")
    token = response.json['access_token']
    return {
        'Authorization': f'Bearer {token}'
    }

def test_create_collection_success(test_client, init_database, auth_headers, test_app):
    """Testa a criação de uma coleção com sucesso por um usuário autenticado."""
    import json
    response = test_client.post('/api/collections', data=json.dumps({
        'name': 'Minha Primeira Coleção'
    }), headers=auth_headers, mimetype='application/json')
    print(f"[DEBUG] create_collection_success response.status_code: {response.status_code}")
    print(f"[DEBUG] create_collection_success response.data: {response.data}")
    try:
        response_json = response.json
        print(f"[DEBUG] create_collection_success response.json: {response_json}")
    except Exception as e:
        print(f"[DEBUG] Error parsing JSON from response: {e}")
    
    assert response.status_code == 201
    assert response.json['name'] == 'Minha Primeira Coleção'
    assert 'id' in response.json

    # Verifica se foi salvo no banco
    with test_app.app_context():
        collection = Collection.query.first()
        assert collection is not None
        assert collection.name == 'Minha Primeira Coleção'

def test_create_collection_unauthorized(test_client, init_database):
    """Testa a criação de uma coleção sem autenticação."""
    response = test_client.post('/api/collections', json={
        'name': 'Coleção Fantasma'
    }, headers={'Content-Type': 'application/json'})
    assert response.status_code == 401 # JWT Extended retorna 401 para token faltando

def test_get_collections_success(test_client, init_database, auth_headers):
    """Testa se um usuário pode listar suas próprias coleções."""
    # Cria duas coleções para o usuário
    test_client.post('/api/collections', json={'name': 'Viagem'}, headers=auth_headers, mimetype='application/json')
    test_client.post('/api/collections', json={'name': 'Trabalho'}, headers=auth_headers, mimetype='application/json')

    # Pega a lista de coleções
    response = test_client.get('/api/collections', headers=auth_headers)

    assert response.status_code == 200
    assert isinstance(response.json, list)
    assert len(response.json) == 2
    
    collection_names = {c['name'] for c in response.json}
    assert collection_names == {'Viagem', 'Trabalho'}

def test_get_collections_is_isolated(test_client, init_database):
    """Testa se um usuário não pode ver as coleções de outro usuário."""
    # Cria e loga o Usuário 1
    reg_res1 = test_client.post('/api/register', json={'username': 'user1', 'email': 'user1@test.com', 'password': 'password'}, headers={'Content-Type': 'application/json'})
    assert reg_res1.status_code == 201, f"User1 Registration failed with status {reg_res1.status_code} and response {reg_res1.json}"
    res1 = test_client.post('/api/login', json={'email': 'user1@test.com', 'password': 'password'}, headers={'Content-Type': 'application/json'})
    assert res1.status_code == 200, f"User1 Login failed with status {res1.status_code} and response {res1.json}"
    headers1 = {'Authorization': f'Bearer {res1.json["access_token"]}'}

    # Cria e loga o Usuário 2
    test_client.post('/api/register', json={'username': 'user2', 'email': 'user2@test.com', 'password': 'password2'}, headers={'Content-Type': 'application/json'})
    res2 = test_client.post('/api/login', json={'email': 'user2@test.com', 'password': 'password2'}, headers={'Content-Type': 'application/json'})
    assert res2.status_code == 200, f"User2 Login failed with status {res2.status_code} and response {res2.json}"
    headers2 = {'Authorization': f'Bearer {res2.json["access_token"]}'}

    # Usuário 1 cria uma coleção
    test_client.post('/api/collections', json={'name': 'Coleção do User1'}, headers=headers1, mimetype='application/json')
    # Usuário 2 busca suas coleções
    response = test_client.get('/api/collections', headers=headers2)

    assert response.status_code == 200
    assert isinstance(response.json, list)
    assert len(response.json) == 0 # A lista do usuário 2 deve estar vazia

def test_get_single_collection_success(test_client, init_database, auth_headers):
    """Testa se um usuário pode obter uma única coleção pelo ID."""
    # Cria uma coleção
    create_response = test_client.post('/api/collections', json={'name': 'Coleção de Teste'}, headers=auth_headers, mimetype='application/json')
    assert create_response.status_code == 201
    collection_id = create_response.json['id']

    # Busca a coleção pelo ID
    response = test_client.get(f'/api/collections/{collection_id}', headers=auth_headers)

    assert response.status_code == 200
    assert response.json['name'] == 'Coleção de Teste'
    assert response.json['id'] == collection_id

def test_get_single_collection_forbidden(test_client, init_database):
    """Testa se um usuário não pode ver a coleção de outro usuário."""
    # Cria e loga o Usuário 1
    test_client.post('/api/register', json={'username': 'user1', 'email': 'user1@test.com', 'password': 'password'}, headers={'Content-Type': 'application/json'})
    res1 = test_client.post('/api/login', json={'email': 'user1@test.com', 'password': 'password'}, headers={'Content-Type': 'application/json'})
    headers1 = {'Authorization': f'Bearer {res1.json["access_token"]}'}

    # Cria e loga o Usuário 2
    test_client.post('/api/register', json={'username': 'user2', 'email': 'user2@test.com', 'password': 'password2'}, headers={'Content-Type': 'application/json'})
    res2 = test_client.post('/api/login', json={'email': 'user2@test.com', 'password': 'password2'}, headers={'Content-Type': 'application/json'})
    headers2 = {'Authorization': f'Bearer {res2.json["access_token"]}'}

    # Usuário 1 cria uma coleção
    create_res = test_client.post('/api/collections', json={'name': 'Coleção do User1'}, headers=headers1, mimetype='application/json')
    collection_id = create_res.json['id']

    # Usuário 2 tenta buscar a coleção do usuário 1
    response = test_client.get(f'/api/collections/{collection_id}', headers=headers2)

    assert response.status_code == 404

def test_update_collection_success(test_client, init_database, auth_headers):
    """Testa se um usuário pode atualizar sua própria coleção."""
    # Cria uma coleção
    create_response = test_client.post('/api/collections', json={'name': 'Nome Antigo'}, headers=auth_headers, mimetype='application/json')
    collection_id = create_response.json['id']

    # Atualiza a coleção
    update_response = test_client.put(f'/api/collections/{collection_id}', json={'name': 'Nome Novo'}, headers=auth_headers, mimetype='application/json')

    assert update_response.status_code == 200
    assert update_response.json['name'] == 'Nome Novo'

    # Verifica no GET
    get_response = test_client.get(f'/api/collections/{collection_id}', headers=auth_headers)
    assert get_response.json['name'] == 'Nome Novo'

def test_update_collection_forbidden(test_client, init_database):
    """Testa que um usuário não pode atualizar a coleção de outro."""
    # User 1 cria a coleção
    test_client.post('/api/register', json={'username': 'user1', 'email': 'user1@test.com', 'password': 'password'})
    res1 = test_client.post('/api/login', json={'email': 'user1@test.com', 'password': 'password'})
    headers1 = {'Authorization': f'Bearer {res1.json["access_token"]}'}
    create_res = test_client.post('/api/collections', json={'name': 'Coleção Original'}, headers=headers1, mimetype='application/json')
    collection_id = create_res.json['id']

    # User 2 tenta atualizar
    test_client.post('/api/register', json={'username': 'user2', 'email': 'user2@test.com', 'password': 'password2'})
    res2 = test_client.post('/api/login', json={'email': 'user2@test.com', 'password': 'password2'})
    headers2 = {'Authorization': f'Bearer {res2.json["access_token"]}'}
    update_response = test_client.put(f'/api/collections/{collection_id}', json={'name': 'Nome Hackeado'}, headers=headers2, mimetype='application/json')

    assert update_response.status_code == 404

def test_delete_collection_success(test_client, init_database, auth_headers):
    """Testa se um usuário pode deletar sua própria coleção."""
    # Cria uma coleção
    create_response = test_client.post('/api/collections', json={'name': 'Para Deletar'}, headers=auth_headers, mimetype='application/json')
    collection_id = create_response.json['id']

    # Deleta a coleção
    delete_response = test_client.delete(f'/api/collections/{collection_id}', headers=auth_headers)
    assert delete_response.status_code == 200
    assert delete_response.json['message'] == 'Coleção deletada com sucesso'
    # Verifica que a coleção não existe mais
    get_response = test_client.get(f'/api/collections/{collection_id}', headers=auth_headers)
    assert get_response.status_code == 404

def test_delete_collection_forbidden(test_client, init_database):
    """Testa que um usuário não pode deletar a coleção de outro."""
    # User 1 cria a coleção
    test_client.post('/api/register', json={'username': 'user1', 'email': 'user1@test.com', 'password': 'password'})
    res1 = test_client.post('/api/login', json={'email': 'user1@test.com', 'password': 'password'})
    headers1 = {'Authorization': f'Bearer {res1.json["access_token"]}'}
    create_res = test_client.post('/api/collections', json={'name': 'Coleção Protegida'}, headers=headers1, mimetype='application/json')
    collection_id = create_res.json['id']

    # User 2 tenta deletar
    test_client.post('/api/register', json={'username': 'user2', 'email': 'user2@test.com', 'password': 'password2'})
    res2 = test_client.post('/api/login', json={'email': 'user2@test.com', 'password': 'password2'})
    headers2 = {'Authorization': f'Bearer {res2.json["access_token"]}'}
    delete_response = test_client.delete(f'/api/collections/{collection_id}', headers=headers2)

    assert delete_response.status_code == 404

def test_delete_nonexistent_collection(test_client, init_database, auth_headers):
    """Testa deletar uma coleção que não existe."""
    delete_response = test_client.delete('/api/collections/9999', headers=auth_headers)
    assert delete_response.status_code == 404

# --- Testes de Conteúdo da Coleção ---

def test_add_content_to_collection_success(test_client, init_database, auth_headers):
    """Testa adicionar conteúdo a uma coleção com sucesso."""
    # Cria uma coleção
    create_res = test_client.post('/api/collections', json={'name': 'Coleção com Conteúdo'}, headers=auth_headers, mimetype='application/json')
    collection_id = create_res.json['id']

    # Adiciona conteúdo a ela
    add_content_res = test_client.post(f'/api/collections/{collection_id}/contents', json={
        'title': 'Meu primeiro conteúdo',
        'body': 'Este é o corpo do meu conteúdo.'
    }, headers=auth_headers, mimetype='application/json')

    assert add_content_res.status_code == 201
    assert add_content_res.json['title'] == 'Meu primeiro conteúdo'

    # Verifica se o conteúdo foi adicionado
    get_res = test_client.get(f'/api/collections/{collection_id}', headers=auth_headers)
    assert len(get_res.json['contents']) == 1
    assert get_res.json['contents'][0]['title'] == 'Meu primeiro conteúdo'

def test_add_content_to_collection_forbidden(test_client, init_database):
    """Testa que um usuário não pode adicionar conteúdo na coleção de outro."""
    # User 1 cria a coleção
    test_client.post('/api/register', json={'username': 'user1', 'email': 'user1@test.com', 'password': 'password'})
    res1 = test_client.post('/api/login', json={'email': 'user1@test.com', 'password': 'password'})
    headers1 = {'Authorization': f'Bearer {res1.json["access_token"]}'}
    create_res = test_client.post('/api/collections', json={'name': 'Coleção do User1'}, headers=headers1, mimetype='application/json')
    collection_id = create_res.json['id']

    # User 2 tenta adicionar conteúdo
    test_client.post('/api/register', json={'username': 'user2', 'email': 'user2@test.com', 'password': 'password2'})
    res2 = test_client.post('/api/login', json={'email': 'user2@test.com', 'password': 'password2'})
    headers2 = {'Authorization': f'Bearer {res2.json["access_token"]}'}
    add_content_res = test_client.post(f'/api/collections/{collection_id}/contents', json={
        'title': 'Conteúdo Malicioso',
        'body': 'Corpo'
    }, headers=headers2, mimetype='application/json')

    assert add_content_res.status_code == 404

def test_update_collection_content_success(test_client, init_database, auth_headers):
    """Testa a atualização de um conteúdo em uma coleção."""
    # Cria coleção e conteúdo
    create_res = test_client.post('/api/collections', json={'name': 'Coleção'}, headers=auth_headers, mimetype='application/json')
    collection_id = create_res.json['id']
    add_content_res = test_client.post(f'/api/collections/{collection_id}/contents', json={'title': 'Título Antigo', 'body': 'Corpo Antigo'}, headers=auth_headers, mimetype='application/json')
    content_id = add_content_res.json['id']

    # Atualiza o conteúdo
    update_res = test_client.put(f'/api/collections/{collection_id}/contents/{content_id}', json={'title': 'Título Novo', 'body': 'Corpo Novo'}, headers=auth_headers, mimetype='application/json')

    assert update_res.status_code == 200
    assert update_res.json['title'] == 'Título Novo'

    # Verifica se a atualização persistiu
    get_res = test_client.get(f'/api/collections/{collection_id}', headers=auth_headers)
    assert get_res.json['contents'][0]['title'] == 'Título Novo'

def test_update_collection_content_forbidden(test_client, init_database):
    """Testa que um usuário não pode editar o conteúdo da coleção de outro."""
    # User 1 cria coleção e conteúdo
    test_client.post('/api/register', json={'username': 'user1', 'email': 'user1@test.com', 'password': 'password'})
    res1 = test_client.post('/api/login', json={'email': 'user1@test.com', 'password': 'password'})
    headers1 = {'Authorization': f'Bearer {res1.json["access_token"]}'}
    create_res = test_client.post('/api/collections', json={'name': 'Coleção'}, headers=headers1, mimetype='application/json')
    collection_id = create_res.json['id']
    add_content_res = test_client.post(f'/api/collections/{collection_id}/contents', json={'title': 'Título', 'body': 'Corpo'}, headers=headers1, mimetype='application/json')
    content_id = add_content_res.json['id']

    # User 2 tenta atualizar
    test_client.post('/api/register', json={'username': 'user2', 'email': 'user2@test.com', 'password': 'password2'})
    res2 = test_client.post('/api/login', json={'email': 'user2@test.com', 'password': 'password2'})
    headers2 = {'Authorization': f'Bearer {res2.json["access_token"]}'}
    update_res = test_client.put(f'/api/collections/{collection_id}/contents/{content_id}', json={'title': 'Título Hackeado'}, headers=headers2, mimetype='application/json')

    assert update_res.status_code == 404

def test_delete_collection_content_success(test_client, init_database, auth_headers):
    """Testa a exclusão de um conteúdo de uma coleção."""
    # Cria coleção e conteúdo
    create_res = test_client.post('/api/collections', json={'name': 'Coleção'}, headers=auth_headers, mimetype='application/json')
    collection_id = create_res.json['id']
    add_content_res = test_client.post(f'/api/collections/{collection_id}/contents', json={'title': 'Para Deletar', 'body': 'Corpo'}, headers=auth_headers, mimetype='application/json')
    content_id = add_content_res.json['id']

    # Deleta o conteúdo
    delete_res = test_client.delete(f'/api/collections/{collection_id}/contents/{content_id}', headers=auth_headers)
    assert delete_res.status_code == 200
    assert delete_res.json['message'] == 'Conteúdo deletado com sucesso'
    # Verifica se o conteúdo foi removido
    get_res = test_client.get(f'/api/collections/{collection_id}', headers=auth_headers)
    assert len(get_res.json['contents']) == 0

def test_delete_collection_content_forbidden(test_client, init_database):
    """Testa que um usuário não pode deletar o conteúdo da coleção de outro."""
    # User 1 cria coleção e conteúdo
    test_client.post('/api/register', json={'username': 'user1', 'email': 'user1@test.com', 'password': 'password'})
    res1 = test_client.post('/api/login', json={'email': 'user1@test.com', 'password': 'password'})
    headers1 = {'Authorization': f'Bearer {res1.json["access_token"]}'}
    create_res = test_client.post('/api/collections', json={'name': 'Coleção'}, headers=headers1, mimetype='application/json')
    collection_id = create_res.json['id']
    add_content_res = test_client.post(f'/api/collections/{collection_id}/contents', json={'title': 'Título', 'body': 'Corpo'}, headers=headers1, mimetype='application/json')
    content_id = add_content_res.json['id']

    # User 2 tenta deletar
    test_client.post('/api/register', json={'username': 'user2', 'email': 'user2@test.com', 'password': 'password2'})
    res2 = test_client.post('/api/login', json={'email': 'user2@test.com', 'password': 'password2'})
    headers2 = {'Authorization': f'Bearer {res2.json["access_token"]}'}
    delete_res = test_client.delete(f'/api/collections/{collection_id}/contents/{content_id}', headers=headers2)

    assert delete_res.status_code == 404
