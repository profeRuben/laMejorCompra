import pytest
from flask import url_for
from models import User, Product
from werkzeug.security import generate_password_hash

def test_home_page(client):
    """Prueba que la página principal carga correctamente."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'La Mejor Compra' in response.data

def test_login_page(client):
    """Prueba que la página de login carga correctamente."""
    response = client.get('/login')
    assert response.status_code == 200
    assert b'Iniciar Sesi' in response.data  # Busca parte de "Iniciar Sesión"

def test_catalog_page(client):
    """Prueba que la página de catálogo carga correctamente."""
    response = client.get('/catalog')
    assert response.status_code == 200
    assert b'Productos' in response.data