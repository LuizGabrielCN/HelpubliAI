import os
import threading
import time
from flask import Blueprint, request, jsonify, current_app
from . import db, bcrypt, jwt, mail, socketio
from .models import User, Collection, Content, GenerationHistory, PasswordResetToken
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from sqlalchemy.exc import IntegrityError
from flask_mail import Message
from datetime import datetime, timedelta
import secrets
from pydantic import ValidationError
from .services.ai_service import get_generative_model, GOOGLE_API_KEY
from . import schemas

from .services.ai_service import clear_generative_model_cache

main_bp = Blueprint('main', __name__)

def _clean_cache_periodically():
    """Função que roda em background para limpar o cache."""
    while True:
        # Limpa o cache a cada 2 horas (7200 segundos)
        time.sleep(7200)
        # O app_context é necessário para acessar o logger e outras configs do Flask
        # Como não temos o `app` aqui, usamos um truque para pegá-lo do blueprint
        if main_bp.app_context():
             with main_bp.app_context():
                current_app.logger.info("Limpando o cache do modelo de IA...")
                clear_generative_model_cache()

def init_cache_cleaner(app):
    """Inicia a thread de limpeza de cache em background."""
    # Usamos o contexto da aplicação para garantir que tudo esteja carregado
    with app.app_context():
        current_app.logger.info("Iniciando a thread de limpeza de cache do modelo de IA.")
        cache_cleaner_thread = threading.Thread(target=_clean_cache_periodically, daemon=True)
        cache_cleaner_thread.start()


# ... (outros imports)

# --- Rotas de Autenticação ---

@main_bp.route('/api/register', methods=['POST'])
def register():
    try:
        validated_data = schemas.UserRegisterSchema(**request.get_json())
    except ValidationError as err:
        return jsonify(err.errors()), 400

    if User.query.filter_by(username=validated_data.username).first() or User.query.filter_by(email=validated_data.email).first():
        return jsonify({"message": "Usuário ou email já existente"}), 409

    new_user = User(username=validated_data.username, email=validated_data.email)
    new_user.set_password(validated_data.password)
    
    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"success": True, "message": "Usuário registrado com sucesso"}), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({"message": "Erro de banco de dados ao registrar"}), 500
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erro ao registrar usuário: {e}")
        return jsonify({"message": "Erro interno do servidor"}), 500


@main_bp.route('/api/login', methods=['POST'])
def login():
    try:
        validated_data = schemas.UserLoginSchema(**request.get_json())
    except ValidationError as err:
        return jsonify(err.errors()), 400

    user = User.query.filter_by(email=validated_data.email).first()

    if user and user.check_password(validated_data.password):
        access_token = create_access_token(identity=str(user.id))
        return jsonify(access_token=access_token)

    return jsonify({"message": "Credenciais inválidas"}), 401

@main_bp.route('/api/request-password-reset', methods=['POST'])
def request_password_reset():
    data = request.get_json()
    email = data.get('email')
    user = User.query.filter_by(email=email).first()

    if user:
        # Remove tokens antigos para este usuário
        PasswordResetToken.query.filter_by(user_id=user.id).delete()

        # Cria novo token
        token = secrets.token_urlsafe(20)
        expires_at = datetime.utcnow() + timedelta(hours=1)
        new_token = PasswordResetToken(user_id=user.id, token=token, expires_at=expires_at)
        db.session.add(new_token)
        db.session.commit()

        # Envia o email
        reset_url = f"{request.host_url}reset-password/{token}"
        msg = Message("Redefinição de Senha - HelpubliAI",
                      recipients=[user.email])
        msg.body = f"Para redefinir sua senha, clique no link: {reset_url}\n\nSe você não solicitou isso, ignore este email."
        try:
            mail.send(msg)
            return jsonify({"message": "Email de redefinição de senha enviado."}) 
        except Exception as e:
            current_app.logger.error(f"Falha ao enviar email: {e}")
            return jsonify({"message": "Não foi possível enviar o email de redefinição."}), 500

    return jsonify({"message": "Email não encontrado."}), 404


@main_bp.route('/api/reset-password/<token>', methods=['POST'])
def reset_password_with_token(token):
    data = request.get_json()
    new_password = data.get('password')

    reset_token = PasswordResetToken.query.filter_by(token=token).first()

    if not reset_token or reset_token.expires_at < datetime.utcnow():
        return jsonify({"message": "Token inválido ou expirado."}) 

    user = User.query.get(reset_token.user_id)
    if user:
        user.set_password(new_password)
        db.session.delete(reset_token)  # Token usado
        db.session.commit()
        return jsonify({"message": "Senha redefinida com sucesso."}) 

    return jsonify({"message": "Usuário não encontrado."}), 404


# --- Rotas Protegidas ---

@main_bp.route('/api/profile')
@jwt_required()
def profile():
    current_user_identity = get_jwt_identity()
    user_id = int(current_user_identity)
    user = User.query.get(user_id)
    if user:
        return jsonify({"username": user.username, "email": user.email, "is_admin": user.is_admin})
    return jsonify({"message": "Usuário não encontrado"}), 404

@main_bp.route('/api/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    if not user:
        return jsonify({"message": "Usuário não encontrado"}), 404

    data = request.get_json()
    username = data.get('username')
    email = data.get('email')

    if not username or not email:
        return jsonify({"message": "Nome de usuário e email são obrigatórios"}), 400

    # Check for username/email conflicts if they are being changed
    if username != user.username and User.query.filter_by(username=username).first():
        return jsonify({"message": "Nome de usuário já existe"}), 409
    if email != user.email and User.query.filter_by(email=email).first():
        return jsonify({"message": "Email já existe"}), 409

    user.username = username
    user.email = email
    db.session.commit()

    return jsonify({"username": user.username, "email": user.email, "is_admin": user.is_admin}), 200

# --- Rotas de Coleções ---

@main_bp.route('/api/collections', methods=['GET'])
@jwt_required()
def get_collections():
    current_user_identity = get_jwt_identity()
    user_id = int(current_user_identity)
    collections = Collection.query.filter_by(user_id=user_id).order_by(Collection.created_at.desc()).all()
    collections_data = [{'id': c.id, 'name': c.name} for c in collections]
    return jsonify(collections_data)

@main_bp.route('/api/collections', methods=['POST'])
@jwt_required()
def create_collection():
    try:
        validated_data = schemas.CollectionSchema(**request.get_json())
    except ValidationError as err:
        return jsonify(err.errors()), 422

    user_id = int(get_jwt_identity())

    new_collection = Collection(name=validated_data.name, user_id=user_id)
    db.session.add(new_collection)
    db.session.commit()

    return jsonify({"id": new_collection.id, "name": new_collection.name}), 201

@main_bp.route('/api/collections/<int:collection_id>', methods=['GET', 'PUT', 'DELETE'])
@jwt_required()
def handle_collection_details(collection_id):
    user_id = int(get_jwt_identity())
    # Garante que a coleção existe e pertence ao usuário
    collection = Collection.query.filter_by(id=collection_id, user_id=user_id).first_or_404()

    if request.method == 'GET':
        contents = Content.query.filter_by(collection_id=collection.id).order_by(Content.created_at.desc()).all()
        contents_data = [{'id': c.id, 'title': c.title, 'body': c.body} for c in contents]
        return jsonify({'id': collection.id, 'name': collection.name, 'contents': contents_data})

    elif request.method == 'PUT':
        data = request.get_json()
        if not data or 'name' not in data:
            return jsonify({"message": "O nome da coleção é obrigatório"}), 400
        
        collection.name = data['name']
        db.session.commit()
        return jsonify({"id": collection.id, "name": collection.name})

    elif request.method == 'DELETE':
        db.session.delete(collection)
        db.session.commit()
        return jsonify({"message": "Coleção deletada com sucesso"}), 200

@main_bp.route('/api/collections/<int:collection_id>/contents', methods=['POST'])
@jwt_required()
def add_content_to_collection(collection_id):
    current_user_identity = get_jwt_identity()
    user_id = int(current_user_identity)

    collection = Collection.query.filter_by(id=collection_id, user_id=user_id).first_or_404()
    
    data = request.get_json()
    title = data.get('title')
    body = data.get('body')

    if not title or not body:
        return jsonify({"message": "Título e corpo do conteúdo são obrigatórios"}), 400

    new_content = Content(title=title, body=body, collection_id=collection.id)
    db.session.add(new_content)
    db.session.commit()

    return jsonify({'id': new_content.id, 'title': new_content.title}), 201


@main_bp.route('/api/collections/<int:collection_id>/contents/<int:content_id>', methods=['PUT', 'DELETE'])
@jwt_required()
def handle_collection_content(collection_id, content_id):
    user_id = int(get_jwt_identity())
    
    # Verifica a posse da coleção
    collection = Collection.query.filter_by(id=collection_id, user_id=user_id).first_or_404()
    
    # Verifica se o conteúdo existe e está na coleção correta
    content = Content.query.filter_by(id=content_id, collection_id=collection.id).first_or_404()

    if request.method == 'PUT':
        data = request.get_json()
        title = data.get('title')
        body = data.get('body')

        if not title or not body:
            return jsonify({"message": "Título e corpo são obrigatórios"}), 400

        content.title = title
        content.body = body
        db.session.commit()
        return jsonify({"id": content.id, "title": content.title, "body": content.body}), 200

    elif request.method == 'DELETE':
        db.session.delete(content)
        db.session.commit()
        return jsonify({"message": "Conteúdo deletado com sucesso"}), 200

# --- Rota de Histórico ---
@main_bp.route('/api/history', methods=['GET'])
@jwt_required()
def get_history():
    current_user_identity = get_jwt_identity()
    user_id = int(current_user_identity)
    history_entries = GenerationHistory.query.filter_by(user_id=user_id).order_by(GenerationHistory.timestamp.desc()).all()
    history_data = [
        {
            'id': h.id, 
            'prompt': h.prompt, 
            'generated_content': h.generated_content, 
            'timestamp': h.timestamp.isoformat()
        } for h in history_entries
    ]
    return jsonify(history_data)


# --- Rotas de Geração de Conteúdo ---

@main_bp.route('/api/generate', methods=['POST'])
@jwt_required()
def generate_content():
    if not GOOGLE_API_KEY:
        return jsonify({"error": "API Key do Google não configurada no servidor."}), 500

    data = request.get_json()
    prompt = data.get('prompt')
    if not prompt:
        return jsonify({"error": "O prompt é obrigatório."}), 400

    current_user_identity = get_jwt_identity()
    user_id = int(current_user_identity)
    client_sid = request.sid # Captura o SID do cliente para respostas diretas

    try:
        model = get_generative_model()
        full_generated_text = ""
        
        # Geração de conteúdo em streaming
        for chunk in model.generate_content(prompt, stream=True):
            if chunk.text:
                full_generated_text += chunk.text
                socketio.emit('generated_content_chunk', {'chunk': chunk.text}, room=client_sid)
                socketio.sleep(0) # Força o envio imediato

        # Salva no histórico após a geração completa
        history_entry = GenerationHistory(
            user_id=user_id,
            prompt=prompt,
            generated_content=full_generated_text
        )
        db.session.add(history_entry)
        db.session.commit()

        socketio.emit('generated_content_complete', {'full_content': full_generated_text}, room=client_sid)
        # A resposta HTTP pode ser simples, já que o conteúdo foi enviado via WebSocket
        return jsonify({"message": "Geração de conteúdo concluída e enviada via WebSocket."}), 200

    except Exception as e:
        current_app.logger.error(f"Erro na geração de conteúdo: {e}")
        error_message = str(e)
        # Emite um evento de erro para o cliente
        socketio.emit('generated_content_error', {'error': "Falha ao gerar conteúdo.", 'details': error_message}, room=client_sid)
        return jsonify({"error": "Falha ao gerar conteúdo.", "details": error_message}), 500


# --- Rotas para o SocketIO ---

@socketio.on('connect')
@jwt_required(optional=True) # Permite conexões sem token, mas o contexto de identidade não estará disponível
def handle_connect():
    # Opcional: verificar a identidade do usuário se o token for fornecido
    current_user_id = get_jwt_identity()
    if current_user_id:
        user = User.query.get(int(current_user_id))
        if user:
            current_app.logger.info(f"Cliente conectado ao WebSocket: {user.username} (SID: {request.sid})")
        else:
            current_app.logger.info(f"Cliente com token inválido conectado ao WebSocket (SID: {request.sid})")
    else:
        current_app.logger.info(f"Cliente anônimo conectado ao WebSocket (SID: {request.sid})")


@socketio.on('disconnect')
def handle_disconnect():
    current_app.logger.info(f"Cliente desconectado do WebSocket (SID: {request.sid})")


# --- Rotas de Admin ---

@main_bp.route('/api/admin/users', methods=['GET'])
@jwt_required()
def get_all_users():
    user_id = int(get_jwt_identity())
    current_user = User.query.get(user_id)
    if not current_user or not current_user.is_admin:
        return jsonify({"message": "Acesso negado: requer privilégios de administrador"}), 403

    users = User.query.all()
    users_data = [{
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "is_admin": user.is_admin,
        "created_at": user.created_at.isoformat()
    } for user in users]
    
    return jsonify(users_data)

@main_bp.route('/api/admin/users/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user_role(user_id):
    admin_user_id = int(get_jwt_identity())
    admin_user = User.query.get(admin_user_id)
    if not admin_user or not admin_user.is_admin:
        return jsonify({"message": "Acesso negado"}), 403

    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "Usuário não encontrado"}), 404

    data = request.get_json()
    if 'is_admin' in data and isinstance(data['is_admin'], bool):
        user.is_admin = data['is_admin']
        db.session.commit()
        return jsonify({"success": True, "message": f"Permissões do usuário {user.username} atualizadas."})
    
    return jsonify({"message": "Payload inválido"}), 400
