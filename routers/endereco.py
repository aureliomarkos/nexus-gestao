# ------------------------------------------------------------------
# ROTAS CRUD: ENDERECOS (Read e Update)
# ------------------------------------------------------------------
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import uuid
from models.endereco import EnderecoModel
from models.endereco import EnderecoBase, EnderecoRead
from database import get_db
from models.usuario import UsuarioModel
from .auth import get_current_user


router = APIRouter(prefix="/enderecos", tags=["Enderecos"])

@router.get("/{endereco_id}", response_model=EnderecoRead, summary="Busca um Endereço por ID")
def read_endereco(endereco_id: uuid.UUID, db: Session = Depends(get_db), current_user: UsuarioModel = Depends(get_current_user)):
    endereco = db.query(EnderecoModel).filter(
        EnderecoModel.id_endereco == endereco_id,
        EnderecoModel.user_id == current_user.id_usuario
    ).first()
    
    if not endereco:
        raise HTTPException(status_code=404, detail="Endereço não encontrado ou inacessível.")
        
    return endereco


@router.put("/{endereco_id}", response_model=EnderecoRead, summary="Atualiza os detalhes de um Endereço por ID")
def update_endereco(endereco_id: uuid.UUID, endereco_update: EnderecoBase, db: Session = Depends(get_db), current_user: UsuarioModel = Depends(get_current_user)):
    endereco = db.query(EnderecoModel).filter(
        EnderecoModel.id_endereco == endereco_id,
        EnderecoModel.user_id == current_user.id_usuario
    ).first()
    
    if not endereco:
        raise HTTPException(status_code=404, detail="Endereço não encontrado ou inacessível.")

    try:
        update_data = endereco_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(endereco, key, value)
            
        db.commit()
        db.refresh(endereco)
        return endereco
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro interno ao atualizar endereço: {e}")