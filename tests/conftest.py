import os
import sys
import tempfile
import pytest

# Añade el directorio principal al path de Python
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

# Importa después de ajustar el path
try:
    from app import app as flask_app
    from extensions import db
except ImportError as e:
    print(f"Error al importar: {e}")
    print("Asegúrate de haber instalado todas las dependencias necesarias:")
    print("pip install flask-login flask-wtf flask-sqlalchemy werkzeug")
    raise

@pytest.fixture
def app():
    # Crear un archivo temporal para la base de datos de pruebas
    db_fd, db_path = tempfile.mkstemp()
    
    # Configurar la aplicación para testing
    flask_app.config['TESTING'] = True
    flask_app.config['WTF_CSRF_ENABLED'] = False
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    
    # Crear el contexto de la aplicación
    with flask_app.app_context():
        # Crear todas las tablas
        db.create_all()
        
        # Aquí puedes cargar datos de prueba si necesitas
        yield flask_app
        
        # Limpiar después de las pruebas
        db.session.remove()
        db.drop_all()
    
    # Cerrar y eliminar el archivo temporal de la base de datos
    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()