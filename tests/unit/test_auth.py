import pytest
from flask import url_for
from models import User
from werkzeug.security import generate_password_hash
from flask_login import current_user
from extensions import db

@pytest.fixture
def test_user(app):
    """Fixture para crear un usuario de prueba."""
    with app.app_context():
        user = User(
            username='testuser',
            email='test@example.com',
            password_hash=generate_password_hash('password123'),
            is_admin=False
        )
        db.session.add(user)
        db.session.commit()
        
        yield user
        
        # Limpiar después de la prueba
        db.session.delete(user)
        db.session.commit()

def test_login_success(client, test_user):
    """Prueba un login exitoso."""
    response = client.post('/login', data={
        'username': 'testuser',
        'password': 'password123',
        'remember': False
    }, follow_redirects=True)
    
    assert response.status_code == 200
    # Verificar redirección exitosa a la página de inicio
    assert b'La Mejor Compra' in response.data

def test_login_invalid_credentials(client, test_user):
    """Prueba un login con credenciales inválidas."""
    response = client.post('/login', data={
        'username': 'testuser',
        'password': 'wrongpassword',
        'remember': False
    }, follow_redirects=True)
    
    assert response.status_code == 200
    # Verificar mensaje de error
    assert b'Usuario o contrase' in response.data

def test_register_user(client, app):
    """Prueba el registro de un nuevo usuario."""
    response = client.post('/register', data={
        'username': 'newuser',
        'email': 'new@example.com',
        'password': 'password123',
        'confirm': 'password123'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    
    # Verificar que el usuario fue creado en la base de datos
    with app.app_context():
        assert User.query.filter_by(username='newuser').first() is not None