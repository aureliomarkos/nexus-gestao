# ------------------------------------------------------------------
# ROTAS CRUD: DESENVOLVEDORES (Inclui Endereço)
# ------------------------------------------------------------------
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.orm import Session
import uuid
from models.desenvolvedor import DesenvolvedorModel
from models.desenvolvedor import DesenvolvedorCreate, DesenvolvedorRead
from models.endereco import EnderecoModel
from database import get_db
from models.usuario import UsuarioModel
from .auth import get_current_user

router = APIRouter(prefix="/desenvolvedores", tags=["Desenvolvedores"])

@router.get("/", response_model=List[DesenvolvedorRead], summary="Lista todos os Desenvolvedores")
def listar_desenvolvedores(db: Session = Depends(get_db), current_user: UsuarioModel = Depends(get_current_user)):
    """ Lista todos os desenvolvedores """
    desenvolvedores = db.query(DesenvolvedorModel).filter(DesenvolvedorModel.user_id == current_user.id_usuario).all()
    return desenvolvedores


@router.get("/{dev_id}", response_model=DesenvolvedorRead, summary="Busca um Desenvolvedor por ID")
def read_desenvolvedor(dev_id: uuid.UUID, db: Session = Depends(get_db), current_user: UsuarioModel = Depends(get_current_user)):
    """ Busca um desenvolvedor pelo ID """
    
    desenvolvedor = db.query(DesenvolvedorModel).filter(
        DesenvolvedorModel.id_desenvolvedor == dev_id,
        DesenvolvedorModel.user_id == current_user.id_usuario
    ).first()
    if not desenvolvedor:
        raise HTTPException(status_code=404, detail="Desenvolvedor não encontrado ou inacessível.")
    return desenvolvedor


@router.post("/", response_model=DesenvolvedorRead, status_code=status.HTTP_201_CREATED, summary="Cria um novo Desenvolvedor e seu Endereço Legal")
def create_desenvolvedor(dev: DesenvolvedorCreate, db: Session = Depends(get_db), current_user: UsuarioModel = Depends(get_current_user)):

    try:
        # 1. Cria o Endereço
        endereco_data = dev.endereco_obj.model_dump()
        novo_endereco = EnderecoModel(
            **endereco_data,
            user_id=current_user.id_usuario
        )
        db.add(novo_endereco)
        db.flush() 

        # 2. Cria o Desenvolvedor
        dev_data = dev.model_dump(exclude={"endereco_obj"})
        novo_desenvolvedor = DesenvolvedorModel(
            **dev_data,
            user_id=current_user.id_usuario,
            id_endereco=novo_endereco.id_endereco
        )
        db.add(novo_desenvolvedor)
        db.commit()
        db.refresh(novo_desenvolvedor)

        return novo_desenvolvedor

    except Exception as e:
        db.rollback()
        if "duplicate key value violates unique constraint" in str(e):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Erro: O email fornecido já está cadastrado.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro interno: {e}")


@router.put("/{dev_id}", response_model=DesenvolvedorRead, summary="Atualiza um Desenvolvedor existente")
def update_desenvolvedor(dev_id: uuid.UUID, dev: DesenvolvedorCreate, db: Session = Depends(get_db), current_user: UsuarioModel = Depends(get_current_user)):
    """ Atualiza um desenvolvedor existente """
    desenvolvedor = db.query(DesenvolvedorModel).filter(
        DesenvolvedorModel.id_desenvolvedor == dev_id,
        DesenvolvedorModel.user_id == current_user.id_usuario
    ).first()
    if not desenvolvedor:
        raise HTTPException(status_code=404, detail="Desenvolvedor não encontrado ou inacessível.")

    try:
        # Atualiza o Endereço
        endereco_data = dev.endereco_obj.model_dump()
        db.query(EnderecoModel).filter(
            EnderecoModel.id_endereco == desenvolvedor.id_endereco,
            EnderecoModel.user_id == current_user.id_usuario
        ).update(endereco_data)

        # Atualiza o Desenvolvedor
        dev_data = dev.model_dump(exclude={"endereco_obj"})
        db.query(DesenvolvedorModel).filter(
            DesenvolvedorModel.id_desenvolvedor == dev_id,
            DesenvolvedorModel.user_id == current_user.id_usuario
        ).update(dev_data)

        db.commit()

        atualizado_desenvolvedor = db.query(DesenvolvedorModel).filter(
            DesenvolvedorModel.id_desenvolvedor == dev_id,
            DesenvolvedorModel.user_id == current_user.id_usuario
        ).first()

        return atualizado_desenvolvedor

    except Exception as e:
        db.rollback()
        if "duplicate key value violates unique constraint" in str(e):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Erro: O email fornecido já está cadastrado.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro ao alterar Desenvolvedor: {e}")
    

@router.delete("/{dev_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Deleta um Desenvolvedor existente")
def delete_desenvolvedor(dev_id: uuid.UUID, db: Session = Depends(get_db), current_user: UsuarioModel = Depends(get_current_user)):
    """ Deleta um desenvolvedor existente """
    desenvolvedor = db.query(DesenvolvedorModel).filter(
        DesenvolvedorModel.id_desenvolvedor == dev_id,
        DesenvolvedorModel.user_id == current_user.id_usuario
    ).first()
    if not desenvolvedor:
        raise HTTPException(status_code=404, detail="Desenvolvedor não encontrado ou inacessível.")

    try:
        # Deleta o Desenvolvedor
        db.delete(desenvolvedor)

        # Opcional: Deleta o Endereço associado
        endereco = db.query(EnderecoModel).filter(
            EnderecoModel.id_endereco == desenvolvedor.id_endereco,
            EnderecoModel.user_id == current_user.id_usuario
        ).first()
        if endereco:
            db.delete(endereco)

        db.commit()
        return

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro ao Deletar Desenvolvedor: {e}")


