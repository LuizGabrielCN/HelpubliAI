import os
import sys
from dotenv import load_dotenv
from flask import send_from_directory, current_app

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

# Adiciona o diretório do backend ao path do Python para importações corretas
BACKEND_DIR = os.path.dirname(__file__)
sys.path.insert(0, BACKEND_DIR)

# Importa a factory e a configuração DEPOIS de configurar o path
from app import create_app, socketio, models
from app.config import Config
from app.routes import init_cache_cleaner

app = create_app(Config)
init_cache_cleaner(app) # Inicia a limpeza de cache em background

# Rota "catch-all" para servir o frontend (Single Page Application)
# Esta rota garante que o React/Vue/Angular router funcione corretamente
# ao recarregar a página em rotas como /admin, /login, etc.
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    # A pasta estática é definida em create_app() como 'frontend'
    static_folder = current_app.static_folder
    
    # Se o caminho solicitado existir como um arquivo estático (css, js, img), sirva-o.
    if path != "" and os.path.exists(os.path.join(static_folder, path)):
        return send_from_directory(static_folder, path)
    else:
        # Caso contrário, sirva o index.html para que o roteador do frontend assuma.
        return send_from_directory(static_folder, 'index.html')

if __name__ == '__main__':
    # A porta é definida pelo ambiente (para deploy) ou 5000 como padrão
    port = int(os.environ.get('PORT', 5000))
    # debug=False é mais seguro para produção. Para desenvolvimento, pode ser True.
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() in ['true', '1']
    
    try:
        print(f"Servidor ContentAI iniciando em http://0.0.0.0:{port} (Debug: {debug_mode})")
        # ATENÇÃO: allow_unsafe_werkzeug=True é usado aqui para compatibilidade com o modo de desenvolvimento do Flask.
        # Em um ambiente de produção, considere usar um servidor WSGI como Gunicorn ou uWSGI com eventlet ou gevent,
        # e remova 'allow_unsafe_werkzeug=True'.
        socketio.run(app, host='0.0.0.0', port=port, debug=debug_mode, allow_unsafe_werkzeug=True)
    except Exception as e:
        print(f"Erro ao iniciar servidor: {e}")
        print(f"💡 Verifique se a porta {port} não está sendo usada por outro processo.")

