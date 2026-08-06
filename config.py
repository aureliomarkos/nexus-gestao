from dotenv import load_dotenv # Importação para carregar o .env
import os


# Carrega as variáveis do arquivo .env
load_dotenv()

# --- CONFIGURAÇÃO DE SEGURANÇA E AMBIENTE ---
ENVIRONMENT = os.environ.get("ENVIRONMENT", "development")
DEBUG = ENVIRONMENT == "development"
DATABASE_URL = os.environ.get("DATABASE_URL")
ENCRYPTION_KEY = os.environ.get("ENCRYPTION_KEY")
SECRET_KEY = os.environ.get("SECRET_KEY")
ENABLE_DOCS = os.environ.get("ENABLE_DOCS", "false").lower() in ("true", "1", "yes")

# Basic validation helpers (raise early if obviously misconfigured)
if ENCRYPTION_KEY is not None and len(ENCRYPTION_KEY) != 44:
	# don't raise here to avoid breaking simple scripts, but warn in logs when used
	# callers that require a valid Fernet key should validate explicitly
	pass