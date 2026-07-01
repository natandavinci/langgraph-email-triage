import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("❌ [ERRO]: A variável GEMINI_API_KEY não foi encontrada no arquivo .env")

gemini_client = genai.Client(api_key=GEMINI_API_KEY)

DB_CONNECTION_STRING = "memoria_grafo.db"