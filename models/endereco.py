from sqlalchemy import Column, String, DateTime, text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional
import uuid
from database import Base


class EnderecoModel(Base):
    __tablename__ = "enderecos"
    id_endereco = Column(UUID(as_uuid=True), primary_key=True, default=text("gen_random_uuid()"))
    user_id = Column(UUID(as_uuid=True), nullable=False)
    rua = Column(String(255), nullable=False)
    numero = Column(String(50), nullable=False)
    complemento = Column(String(100), nullable=True)
    bairro = Column(String(100), nullable=True)
    cidade = Column(String(100), nullable=False)
    estado = Column(String(50), nullable=False)
    cep = Column(String(20), nullable=False)
    data_criacao = Column(DateTime(timezone=True), default=datetime.now)
    
    # Relacionamentos
    desenvolvedores = relationship("DesenvolvedorModel", back_populates="endereco_obj")
    clientes = relationship("ClienteModel", back_populates="endereco_obj")

# Esquemas Pydantic
class EnderecoBase(BaseModel):
    rua: str = Field(..., max_length=255)
    numero: str = Field(..., max_length=50)
    complemento: Optional[str] = Field(None, max_length=100)
    bairro: str = Field(..., max_length=100)
    cidade: str = Field(..., max_length=100)
    estado: str = Field(..., max_length=50)
    cep: str = Field(..., max_length=20)

class EnderecoRead(EnderecoBase):
    id_endereco: uuid.UUID
    class Config:
        from_attributes = True
