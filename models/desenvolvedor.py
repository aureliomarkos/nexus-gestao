from sqlalchemy import Column, String, DateTime, ForeignKey, text, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr
from typing import Optional
import uuid
from models.endereco import EnderecoBase, EnderecoRead
from database import Base

# --- MODELOS SQLALCHEMY (Mapeamento das Tabelas) ---
class DesenvolvedorModel(Base):
    __tablename__ = "desenvolvedores"
    id_desenvolvedor = Column(UUID(as_uuid=True), primary_key=True, default=text("gen_random_uuid()"))
    user_id = Column(UUID(as_uuid=True), nullable=False)
    id_endereco = Column(UUID(as_uuid=True), ForeignKey('enderecos.id_endereco'), nullable=False)
    nome = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    telefone = Column(String(50), nullable=True)
    documento_fiscal = Column(String(50), nullable=False)
    tipo_contrato = Column(String(50), nullable=True)
    taxa_horaria = Column(Numeric(10, 2), nullable=True)
    data_criacao = Column(DateTime(timezone=True), default=datetime.now)
    
    # Relacionamentos
    endereco_obj = relationship("EnderecoModel", back_populates="desenvolvedores")
    projetos = relationship("ServicoProjetoModel", back_populates="desenvolvedores")

# --- ESQUEMAS PYDANTIC (Validação de Dados) ---
class DesenvolvedorBase(BaseModel):
    nome: str = Field(..., max_length=255)
    email: EmailStr = Field(..., max_length=255)
    telefone: Optional[str] = Field(None, max_length=50)
    documento_fiscal: str = Field(..., max_length=50)
    tipo_contrato: Optional[str] = Field(None, max_length=50)
    taxa_horaria: Optional[float] = Field(None, ge=0)
    
    # Adicionando Config para permitir o uso em ServicoProjetoRead
    class Config:
        from_attributes = True

class DesenvolvedorCreate(DesenvolvedorBase):
    endereco_obj: EnderecoBase 

class DesenvolvedorRead(DesenvolvedorBase):
    id_desenvolvedor: uuid.UUID
    id_endereco: uuid.UUID
    data_criacao: datetime
    endereco_obj: EnderecoRead 

    class Config:
        from_attributes = True
        populate_by_name = True # Essencial para o relacionamento endereco_obj
