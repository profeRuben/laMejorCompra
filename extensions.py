from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Inicializar extensiones
db = SQLAlchemy()
login_manager = LoginManager()

# Configurar login manager
login_manager.login_view = 'login'
login_manager.login_message = 'Por favor inicia sesión para acceder a esta página.'
login_manager.login_message_category = 'warning'