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


def init_db():
    """Importa os módulos de modelos e cria as tabelas no banco se não existirem.

    Ao importar explicitamente os módulos que definem os modelos, garantimos que
    as classes estão registradas em `Base.metadata` antes de chamar
    `create_all`.
    """
    # Importar módulos que declaram modelos para registrá-los em Base.metadata
    try:
        import models.cliente
        import models.desenvolvedor
        import models.endereco
        import models.itens_infraestrutura
        import models.servico_projeto
        import models.usuario
    except Exception:
        # Import silencioso: se algum modelo não existir, ainda tentamos criar o restante
        pass

    # Cria as tabelas declarativas que ainda não existem
    Base.metadata.create_all(bind=engine)
