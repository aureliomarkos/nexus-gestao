from pydantic import BaseModel, Field
from cryptography.fernet import Fernet
import uuid
from config import ENCRYPTION_KEY


# Inicializa o objeto Fernet (Criptografia AES-128)
try:
    # A chave é passada como bytes para o Fernet (espera-se 44 chars base64-url)
    if not ENCRYPTION_KEY:
        raise Exception("ENCRYPTION_KEY não configurada. Verifique o arquivo .env")
    FERNET = Fernet(ENCRYPTION_KEY.encode()) 
except Exception as e:
    raise Exception(f"Erro ao inicializar Fernet. Verifique a chave no .env: {e}")


# --- FUNÇÕES DE CRIPTOGRAFIA ---
def encrypt_password(password: str) -> str:
    """Criptografa a string de senha usando Fernet."""
    # Como a inicialização já validou o FERNET, assumimos que ele está OK
    return FERNET.encrypt(password.encode()).decode()

def decrypt_password(encrypted_password: str) -> str:
    """Decifra a string de senha usando Fernet."""
    try:
        # Tenta decifrar.
        return FERNET.decrypt(encrypted_password.encode()).decode()
    except Exception:
        # Erro de decriptografia (chave incorreta ou dado corrompido)
        return "[ERRO DE DECRIPTOGRAFIA]"


# --- ESQUEMA PYDANTIC PARA SENHA DECIFRADA ---
class DecryptedSecret(BaseModel):
    id_item: uuid.UUID
    secret: str = Field(..., description="Senha decifrada em texto puro.")
