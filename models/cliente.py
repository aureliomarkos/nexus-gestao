from sqlalchemy import Column, String, DateTime, ForeignKey, text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
import uuid
from typing import Optional
from models.endereco import EnderecoBase, EnderecoRead
from database import Base

# --- MODELOS SQLALCHEMY (Mapeamento das Tabelas) ---
class ClienteModel(Base):
    __tablename__ = "clientes"
    id_cliente = Column(UUID(as_uuid=True), primary_key=True, default=text("gen_random_uuid()"))
    user_id = Column(UUID(as_uuid=True), nullable=False)
    id_endereco = Column(UUID(as_uuid=True), ForeignKey('enderecos.id_endereco'), nullable=True)
    nome = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    telefone = Column(String(50), nullable=True)
    pessoa_contato = Column(String(255), nullable=True)
    documento_fiscal = Column(String(50), nullable=True)
    segmento = Column(String(100), nullable=True)
    status_relacionamento = Column(String(50), nullable=False)
    origem = Column(String(100), nullable=True)
    observacoes = Column(String, nullable=True)
    data_criacao = Column(DateTime(timezone=True), default=datetime.now)
    data_ultimo_contato = Column(DateTime(timezone=True), nullable=True)
    
    # Relacionamentos
    endereco_obj = relationship("EnderecoModel", back_populates="clientes")
    projetos = relationship("ServicoProjetoModel", back_populates="cliente")
    infra = relationship("InfraestruturaItemModel", back_populates="cliente")


# --- ESQUEMAS PYDANTIC (Validação de Dados) ---
class ClienteBase(BaseModel):
    nome: str = Field(..., max_length=255)
    email: EmailStr = Field(..., max_length=255)
    telefone: Optional[str] = Field(None, max_length=50)
    pessoa_contato: Optional[str] = Field(None, max_length=255)
    documento_fiscal: Optional[str] = Field(None, max_length=50)
    segmento: Optional[str] = Field(None, max_length=100)
    status_relacionamento: Optional[str] = Field(None, max_length=50)
    origem: Optional[str] = Field(None, max_length=100)
    observacoes: Optional[str] = None
    data_ultimo_contato: Optional[datetime] = None

    # Adicionando Config para permitir o uso em ServicoProjetoRead
    class Config:
        from_attributes = True


class ClienteCreate(ClienteBase):
    endereco_obj: EnderecoBase 

class ClienteRead(ClienteBase):
    id_cliente: uuid.UUID
    id_endereco: Optional[uuid.UUID]
    data_criacao: datetime
    endereco_obj: EnderecoRead

    class Config:
        from_attributes = True
        populate_by_name = True # Essencial para o relacionamento endereco_obj
