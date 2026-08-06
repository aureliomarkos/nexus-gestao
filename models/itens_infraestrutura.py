from pydantic import BaseModel, Field
from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from database_types import UUIDType
from datetime import datetime
from typing import Optional
import uuid
from database import Base

# --- MODELOS SQLALCHEMY (Mapeamento das Tabelas) ---
class InfraestruturaItemModel(Base):
    __tablename__ = "itens_infraestrutura"
    id_item = Column(UUIDType(), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUIDType(), nullable=False)
    id_cliente = Column(UUIDType(), ForeignKey('clientes.id_cliente'), nullable=False)
    id_servico = Column(UUIDType(), ForeignKey('servicos_projetos.id_servico'), nullable=True)
    id_desenvolvedor = Column(UUIDType(), ForeignKey('desenvolvedores.id_desenvolvedor'), nullable=False)
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

    @property
    def projeto_titulo(self) -> Optional[str]:
        return self.projeto.titulo if self.projeto else "N/A"


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
    projeto_titulo: Optional[str] = None
    # O Pydantic irá substituir este valor mascarado antes de enviar para o cliente
    referencia_senha: Optional[str] = Field(..., description="Senha criptografada ou Mascarada ('***')")
    
    class Config:
        from_attributes = True
