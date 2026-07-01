import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("❌ [ERRO]: A variável GOOGLE_API_KEY não foi encontrada no arquivo .env")

gemini_client = genai.Client(api_key=GOOGLE_API_KEY)
MODEL_NAME = "gemini-2.5-flash"

DB_CONNECTION_STRING = "memoria_grafo.db"

# === Configurações de E-mail (IMAP / SMTP) ===
EMAIL_ACCOUNT = os.getenv("EMAIL_ACCOUNT")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

# Padrão para Gmail (se usar outro provedor, altere os hosts correspondentes)
IMAP_SERVER = "imap.gmail.com"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465  # Porta padrão para SSL