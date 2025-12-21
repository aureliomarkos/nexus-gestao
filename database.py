from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.orm import DeclarativeBase
from config import DATABASE_URL

# --- CONFIGURAÇÃO SQLALCHEMY ---
class Base(DeclarativeBase):
    """Base para as classes declarativas do SQLAlchemy."""
    pass


# Engine de conexão (Sincrona)
engine = create_engine(DATABASE_URL, echo=False)

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    class_=Session
)

def get_db():
    """Fornece uma sessão do banco de dados para as rotas do FastAPI."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
