import os

# Define o diretório base do projeto (a pasta que contém 'run.py')
basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a-secret-key'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'another-secret-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Adicione outras configurações gerais aqui

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  # Banco de dados em memória
    WTF_CSRF_ENABLED = False  # Desabilita CSRF para testes
