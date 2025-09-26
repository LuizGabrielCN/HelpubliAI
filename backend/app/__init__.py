import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO
from flask_mail import Mail
from flask_bcrypt import Bcrypt
from .config import Config

from flask_marshmallow import Marshmallow

# Inicialização das extensões
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
socketio = SocketIO()
mail = Mail()
bcrypt = Bcrypt()
ma = Marshmallow()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Inicializar extensões com o app
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    socketio.init_app(app, cors_allowed_origins="*", manage_session=False)
    mail.init_app(app)
    bcrypt.init_app(app)
    ma.init_app(app)

    with app.app_context():
        # Import models so that Alembic can detect them
        from . import models

        # Registro dos Blueprints (rotas)
        from .routes import main_bp
        app.register_blueprint(main_bp)

    return app
