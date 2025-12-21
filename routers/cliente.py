# ------------------------------------------------------------------
# ROTAS CRUD: CLIENTES (Inclui Endereço)
# ------------------------------------------------------------------
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from models.cliente import ClienteModel
from models.cliente import ClienteCreate, ClienteRead
from models.endereco import EnderecoModel
from database import get_db
from models.usuario import UsuarioModel
from .auth import get_current_user
import uuid


router = APIRouter(prefix="/clientes", tags=["Clientes"])

@router.get("/", response_model=List[ClienteRead], summary="Lista todos os Clientes")
def read_clientes(db: Session = Depends(get_db), current_user: UsuarioModel = Depends(get_current_user)):
    """ Lista todos os clientes """
    clientes = db.query(ClienteModel).filter(ClienteModel.user_id == current_user.id_usuario).all()
    return clientes


@router.get("/{cliente_id}", response_model=ClienteRead, summary="Busca um Cliente por ID")
def read_cliente(cliente_id: uuid.UUID, db: Session = Depends(get_db), current_user: UsuarioModel = Depends(get_current_user)):
    """ Busca um cliente pelo ID """
    
    cliente = db.query(ClienteModel).filter(
        ClienteModel.id_cliente == cliente_id,
        ClienteModel.user_id == current_user.id_usuario
    ).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado ou inacessível.")
    return cliente


@router.post("/", response_model=ClienteRead, status_code=status.HTTP_201_CREATED, summary="Cria um novo Cliente e seu Endereço Principal")
def create_cliente(cliente: ClienteCreate, db: Session = Depends(get_db), current_user: UsuarioModel = Depends(get_current_user)):
    """ Cria um novo cliente junto com seu endereço principal """
    try:
        # 1. Cria o Endereço (se fornecido)
        endereco_data = cliente.endereco_obj.model_dump()
        novo_endereco = EnderecoModel(
            **endereco_data,
            user_id=current_user.id_usuario
        )
        db.add(novo_endereco)
        db.flush() 

        # 2. Cria o Cliente
        cliente_data = cliente.model_dump(exclude={"endereco_obj"})
        novo_cliente = ClienteModel(
            **cliente_data,
            user_id=current_user.id_usuario,
            id_endereco=novo_endereco.id_endereco
        )
        db.add(novo_cliente)
        db.commit()
        db.refresh(novo_cliente)

        return novo_cliente

    except Exception as e:
        db.rollback()
        if "duplicate key value violates unique constraint" in str(e):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Erro: O email fornecido já está cadastrado.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro ao adicionar cliente: {e}")


@router.put("/{cliente_id}", response_model=ClienteRead, summary="Atualiza um Cliente existente")
def update_cliente(cliente_id: uuid.UUID, cliente: ClienteCreate, db: Session = Depends (get_db), current_user: UsuarioModel = Depends(get_current_user)):
    """ Atualiza os dados de um cliente existente, incluindo seu endereço principal """
    
    cliente_db = db.query(ClienteModel).filter(
        ClienteModel.id_cliente == cliente_id,
        ClienteModel.user_id == current_user.id_usuario
    ).first()
    
    if not cliente_db:
        raise HTTPException(status_code=404, detail="Cliente não encontrado ou inacessível.")
    
    try:
        # 1. Atualiza o Endereço (se fornecido)
        if cliente.endereco_obj:
            endereco_data = cliente.endereco_obj.model_dump()
            endereco_db = db.query(EnderecoModel).filter(
                EnderecoModel.id_endereco == cliente_db.id_endereco,
                EnderecoModel.user_id == current_user.id_usuario
            ).first()
            for key, value in endereco_data.items():
                setattr(endereco_db, key, value)
            db.add(endereco_db)

        # 2. Atualiza o Cliente
        cliente_data = cliente.model_dump(exclude={"endereco_obj"})
        for key, value in cliente_data.items():
            setattr(cliente_db, key, value)
        db.add(cliente_db)

        db.commit()
        db.refresh(cliente_db)

        return cliente_db

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro ao atualizar cliente: {e}")


@router.delete("/{cliente_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Deleta um Cliente existente")
def delete_cliente(cliente_id: uuid.UUID, db: Session = Depends (get_db), current_user: UsuarioModel = Depends(get_current_user)):
    """ Deleta um cliente existente """
    
    cliente_db = db.query(ClienteModel).filter(
        ClienteModel.id_cliente == cliente_id,
        ClienteModel.user_id == current_user.id_usuario
    ).first()
    
    if not cliente_db:
        raise HTTPException(status_code=404, detail="Cliente não encontrado ou inacessível.")
    
    try:
        db.delete(cliente_db)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro ao deletar cliente: {e}")