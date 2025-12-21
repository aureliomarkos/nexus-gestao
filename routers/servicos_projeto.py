# ------------------------------------------------------------------
# ROTAS CRUD: SERVICOS_PROJETOS
# ------------------------------------------------------------------
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
import uuid
from sqlalchemy.orm import Session
from models.servico_projeto import ServicoProjetoModel
from models.servico_projeto import ServicoProjetoCreate, ServicoProjetoRead
from models.cliente import ClienteModel
from models.desenvolvedor import DesenvolvedorModel
from database import get_db
from models.usuario import UsuarioModel
from .auth import get_current_user

router = APIRouter(prefix="/projetos", tags=["Projetos"])


@router.post("/", response_model=ServicoProjetoRead, status_code=status.HTTP_201_CREATED, summary="Cria um novo Serviço ou Projeto")
def create_projeto(projeto: ServicoProjetoCreate, db: Session = Depends(get_db), current_user: UsuarioModel = Depends(get_current_user)):
    """Cria um novo Serviço ou Projeto"""
    try:
        # 1. Validação de FKs: Garante que o Cliente existe e pertence ao usuário
        cliente = db.query(ClienteModel).filter(
            ClienteModel.id_cliente == projeto.id_cliente, 
            ClienteModel.user_id == current_user.id_usuario
        ).first()
        if not cliente:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cliente não encontrado ou inacessível.")

        # 2. Validação de FKs: Garante que o Desenvolvedor existe e pertence ao usuário (se fornecido)
        if projeto.id_desenvolvedor:
             desenvolvedor = db.query(DesenvolvedorModel).filter(
                DesenvolvedorModel.id_desenvolvedor == projeto.id_desenvolvedor, 
                DesenvolvedorModel.user_id == current_user.id_usuario
            ).first()
             if not desenvolvedor:
                 raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Desenvolvedor não encontrado ou inacessível.")


        # 3. Cria o Projeto
        projeto_data = projeto.model_dump()
        novo_projeto = ServicoProjetoModel(
            **projeto_data,
            user_id=current_user.id_usuario
        )
        db.add(novo_projeto)
        db.commit()
        db.refresh(novo_projeto)

        return novo_projeto

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro interno: {e}")


@router.get("/", response_model=List[ServicoProjetoRead], summary="Lista todos os Serviços e Projetos")
def read_projetos(db: Session = Depends(get_db), current_user: UsuarioModel = Depends(get_current_user)):
    """Lista todos os Serviços e Projetos do usuário"""
    projetos = db.query(ServicoProjetoModel).filter(ServicoProjetoModel.user_id == current_user.id_usuario).all()
    return projetos


@router.get("/{projeto_id}", response_model=ServicoProjetoRead, summary="Busca um Serviço ou Projeto por ID")
def read_projeto(projeto_id: uuid.UUID, db: Session = Depends(get_db), current_user: UsuarioModel = Depends(get_current_user)):
    """Busca um Serviço ou Projeto pelo ID"""
    projeto = db.query(ServicoProjetoModel).filter(
        ServicoProjetoModel.id_servico == projeto_id,
        ServicoProjetoModel.user_id == current_user.id_usuario
    ).first()
    if not projeto:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Serviço ou Projeto não encontrado ou inacessível.")
    return projeto


@router.put("/{projeto_id}", response_model=ServicoProjetoRead, summary="Atualiza um Serviço ou Projeto existente")
def update_projeto(projeto_id: uuid.UUID, projeto: ServicoProjetoCreate, db: Session = Depends(get_db), current_user: UsuarioModel = Depends(get_current_user)):
    """Atualiza um Serviço ou Projeto existente pelo ID"""
    existing_projeto = db.query(ServicoProjetoModel).filter(
        ServicoProjetoModel.id_servico == projeto_id,
        ServicoProjetoModel.user_id == current_user.id_usuario
    ).first()
    if not existing_projeto:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Serviço ou Projeto não encontrado ou inacessível.")

    try:
        # Atualiza os campos do projeto
        for key, value in projeto.model_dump().items():
            setattr(existing_projeto, key, value)

        db.commit()
        db.refresh(existing_projeto)
        return existing_projeto

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro interno: {e}")