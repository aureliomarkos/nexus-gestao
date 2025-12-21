from pydantic import BaseModel, Field
from sqlalchemy import Column, String, DateTime, ForeignKey, text, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from typing import Optional
import uuid
from database import Base

# --- MODELOS SQLALCHEMY (Mapeamento das Tabelas) ---
class InfraestruturaItemModel(Base):
    __tablename__ = "itens_infraestrutura"
    id_item = Column(UUID(as_uuid=True), primary_key=True, default=text("gen_random_uuid()"))
    user_id = Column(UUID(as_uuid=True), nullable=False)
    id_cliente = Column(UUID(as_uuid=True), ForeignKey('clientes.id_cliente'), nullable=False)
    id_servico = Column(UUID(as_uuid=True), ForeignKey('servicos_projetos.id_servico'), nullable=True)
    id_desenvolvedor = Column(UUID(as_uuid=True), ForeignKey('desenvolvedores.id_desenvolvedor'), nullable=False)
    tipo_item = Column(String(50), nullable=False)
    descricao = Column(String(255), nullable=False)
    url_acesso = Column(String(512), nullable=True)
    usuario = Column(String(100), nullable=True)
    referencia_senha = Column(String(512), nullable=True) 
    is_critico = Column(Boolean, nullable=False, default=False)
    data_expiracao = Column(DateTime(timezone=True), nullable=True)
    notas_acesso = Column(String, nullable=True)
    
    # Relacionamentos
    cliente = relationship("ClienteModel", back_populates="infra")
    projeto = relationship("ServicoProjetoModel", back_populates="infra")


# --- ESQUEMAS PYDANTIC (Validação de Dados) ---
class InfraestruturaBase(BaseModel):
    tipo_item: str = Field(..., max_length=50)
    descricao: str = Field(..., max_length=255)
    url_acesso: Optional[str] = Field(None, max_length=512)
    usuario: Optional[str] = Field(None, max_length=100)
    referencia_senha: Optional[str] = Field(None, max_length=512)
    is_critico: bool = False
    data_expiracao: Optional[datetime] = None
    notas_acesso: Optional[str] = None

class InfraestruturaCreate(InfraestruturaBase):
    id_cliente: uuid.UUID
    id_desenvolvedor: uuid.UUID
    id_servico: Optional[uuid.UUID] = None

class InfraestruturaRead(InfraestruturaBase):
    id_item: uuid.UUID
    id_cliente: uuid.UUID
    id_desenvolvedor: uuid.UUID
    id_servico: Optional[uuid.UUID]
    # O Pydantic irá substituir este valor mascarado antes de enviar para o cliente
    referencia_senha: Optional[str] = Field(..., description="Senha criptografada ou Mascarada ('***')")
    
    class Config:
        from_attributes = True
