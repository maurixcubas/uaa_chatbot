from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from app.config import Config
from dotenv import load_dotenv
import os

# Cargar variables desde .env
load_dotenv()

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)  # Configura Flask con la clase Config
    CORS(app)

    # Inicializar la base de datos
    db.init_app(app)

    # Registrar Blueprints
    from app.routes import api_bp
    from app.auth_routes import auth_bp
    app.register_blueprint(api_bp, url_prefix="/api")
    app.register_blueprint(auth_bp, url_prefix="/auth")

    # Verificación de claves (solo para asegurar que se cargan)
    print("OpenAI API Key:", os.getenv("OPENAI_API_KEY"))
    print("Assistant ID:", os.getenv("OPENAI_ASSISTANT_ID"))

    return app
