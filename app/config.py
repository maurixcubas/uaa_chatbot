from dotenv import load_dotenv
import os

# Cargar las variables de entorno desde .env
load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "default_secret_key")  # Clave secreta
    SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI", "sqlite:///combined.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # Clave para OpenAI
    ASSISTANT_ID = os.getenv("ASSISTANT_ID")      # ID del asistente de OpenAI
