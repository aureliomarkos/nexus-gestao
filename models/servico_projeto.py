from pydantic import BaseModel, Field
from sqlalchemy import Column, String, DateTime, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from database_types import UUIDType
from datetime import datetime
from typing import Optional
import uuid
from models.cliente import ClienteBase
from models.desenvolvedor import DesenvolvedorRead
from database import Base

# --- MODELOS SQLALCHEMY (Mapeamento das Tabelas) ---
class ServicoProjetoModel(Base):
    __tablename__ = "servicos_projetos"
    id_servico = Column(UUIDType(), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUIDType(), nullable=False)
    id_cliente = Column(UUIDType(), ForeignKey('clientes.id_cliente'), nullable=False)
    id_desenvolvedor = Column(UUIDType(), ForeignKey('desenvolvedores.id_desenvolvedor'), nullable=True)
    titulo = Column(String(255), nullable=False)
    escopo = Column(String, nullable=False)
    status_projeto = Column(String(50), nullable=False)
    data_inicio = Column(DateTime(timezone=True), nullable=True)
    data_limite = Column(DateTime(timezone=True), nullable=True)
    orcamento = Column(Numeric(10, 2), nullable=True)
    notas_internas = Column(String, nullable=True)
    
    # Relacionamentos
    cliente = relationship("ClienteModel", back_populates="projetos")
    desenvolvedor = relationship("DesenvolvedorModel", back_populates="projetos")
    infra = relationship("InfraestruturaItemModel", back_populates="projeto")


# --- ESQUEMAS PYDANTIC (Validação de Dados) ---
class ServicoProjetoBase(BaseModel):
    titulo: str = Field(..., max_length=255)
    escopo: str
    status_projeto: str = Field(..., max_length=50)
    data_inicio: Optional[datetime] = None
    data_limite: Optional[datetime] = None
    orcamento: Optional[float] = Field(None, ge=0)
    notas_internas: Optional[str] = None

class ServicoProjetoCreate(ServicoProjetoBase):
    id_cliente: uuid.UUID
    id_desenvolvedor: Optional[uuid.UUID] = None

class ServicoProjetoRead(ServicoProjetoBase):
    id_servico: uuid.UUID
    id_cliente: uuid.UUID
    id_desenvolvedor: Optional[uuid.UUID]
    
    # Inclusão dos objetos de relacionamento para leitura
    cliente: Optional[ClienteBase] = None
    # Usamos o DesenvolvedorRead para ter a informação completa do desenvolvedor
    desenvolvedor: Optional[DesenvolvedorRead] = None 

    class Config:
        from_attributes = True
