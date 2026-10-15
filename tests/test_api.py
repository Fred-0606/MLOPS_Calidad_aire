from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_health():
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json() == {'status': 'ok'}


def test_pagina_inicio():
    response = client.get('/')
    assert response.status_code == 200
    assert 'API_URL' in response.text
