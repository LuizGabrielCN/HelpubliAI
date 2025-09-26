import os
import google.generativeai as genai
from flask import current_app

# --- Configuração do Modelo Generativo ---

# Cache para o modelo generativo para evitar reinicialização
generative_model_cache = None
GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')

def get_generative_model():
    """
    Retorna uma instância cacheada do modelo generativo.
    Inicializa o modelo se ainda não estiver em cache.
    """
    global generative_model_cache
    if generative_model_cache is None:
        try:
            if not GOOGLE_API_KEY:
                raise ValueError("A chave da API do Google não foi configurada.")
            
            genai.configure(api_key=GOOGLE_API_KEY)
            generative_model_cache = genai.GenerativeModel('gemini-pro')
            current_app.logger.info("Modelo Generativo 'gemini-pro' inicializado com sucesso.")
        except Exception as e:
            current_app.logger.error(f"Falha ao inicializar o modelo generativo: {e}")
            # Propaga o erro para que a rota que o chamou possa lidar com ele
            raise
            
    return generative_model_cache

def clear_generative_model_cache():
    """
    Limpa o cache do modelo generativo.
    """
    global generative_model_cache
    generative_model_cache = None
    current_app.logger.info("Cache do modelo generativo foi limpo.")

