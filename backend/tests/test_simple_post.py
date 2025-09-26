import pytest
from app import create_app, db
from app.config import TestingConfig

@pytest.fixture(scope='module')
def test_app():
    app = create_app(config_class=TestingConfig)
    yield app

@pytest.fixture(scope='module')
def test_client(test_app):
    return test_app.test_client()

def test_simple_post(test_client):
    response = test_client.post('/api/test_post', json={'key': 'value'})
    assert response.status_code == 200
    assert response.json == {'message': 'Test POST successful'}
