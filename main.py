# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import DATABASE_URL, ENCRYPTION_KEY
from routers import (
    cliente,
    desenvolvedor,
    endereco,
    servicos_projeto,
    itens_infraestrutura
)
from routers import auth


# Validação Crítica
if not DATABASE_URL:
    raise ValueError("DATABASE_URL não configurada no arquivo .env ou contém o placeholder.")
if not ENCRYPTION_KEY or len(ENCRYPTION_KEY) != 44:
    raise ValueError("ENCRYPTION_KEY inválida ou não configurada corretamente (deve ter 44 caracteres Fernet).")


# --- INICIALIZAÇÃO DA API ---
app = FastAPI(
    title="Nexus - Gestão Centralizada de Infraestrutura",
    version="1.0.0",
    description="Backend completo para gerenciamento de Clientes, Desenvolvedores, Projetos e Infraestrutura, com criptografia de segredos."
)


# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],            # Lista de origens permitidas
    allow_credentials=True,         # Permite cookies de credenciais
    allow_methods=["*"],            # Permite todos os métodos (GET, POST, OPTIONS, etc.)
    allow_headers=["*"],            # Permite todos os cabeçalhos
)


# Incluir routers
app.include_router(cliente.router)
app.include_router(desenvolvedor.router)
app.include_router(endereco.router)
app.include_router(servicos_projeto.router)
app.include_router(itens_infraestrutura.router)
app.include_router(auth.router)


# Configuração OBRIGATÓRIA para permitir que o frontend acesse a API
"""
origins = [
    "http://127.0.0.1:8000",
    "http://localhost:8000",
    # Adicione a URL onde você está testando o arquivo HTML se for diferente
    "*"  # Permite todas as origens (ideal para desenvolvimento)
]
"""


@app.get("/", tags=["Saúde"], summary="Verifica a saúde da API")
def read_root():
    return {"status": "OK", "message": "API GCI (FastAPI) está em execução."}