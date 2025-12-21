from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, text
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from database import Base
from pydantic import BaseModel, EmailStr
import uuid
from datetime import datetime
from typing import Optional

# --- MODELOS SQLALCHEMY (Mapeamento das Tabelas) ---
class UsuarioModel(Base):
    __tablename__ = "usuarios"
    id_usuario = Column(UUID(as_uuid=True), primary_key=True, default=text("gen_random_uuid()"))
    nome = Column(String(150), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    id_desenvolvedor = Column(UUID(as_uuid=True), ForeignKey('desenvolvedores.id_desenvolvedor'), nullable=True)


# --- ESQUEMAS PYDANTIC (Validação de Dados) ---
class UsuarioCreate(BaseModel):
    nome: str
    email: Optional[EmailStr]
    password: str

class UsuarioRead(BaseModel):
    id_usuario: uuid.UUID
    nome: str
    email: Optional[EmailStr]
    is_active: bool
    is_admin: bool
    created_at: datetime

    class Config:
        from_attributes = True