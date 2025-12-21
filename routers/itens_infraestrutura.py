# ------------------------------------------------------------------
# ROTAS CRUD: ITENS_INFRAESTRUTURA (AGORA COM CRIPTOGRAFIA)
# ------------------------------------------------------------------
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.orm import Session
import uuid
from models.itens_infraestrutura import InfraestruturaItemModel
from models.itens_infraestrutura import InfraestruturaCreate, InfraestruturaRead
from models.servico_projeto import ServicoProjetoModel
from models.cliente import ClienteModel
from database import get_db
from models.usuario import UsuarioModel
from .auth import get_current_user
from models.descriptar_senha import DecryptedSecret
from models.descriptar_senha import encrypt_password, decrypt_password

router = APIRouter(prefix="/infra", tags=["Infraestrutura"])


@router.post("/", response_model=InfraestruturaRead, status_code=status.HTTP_201_CREATED, summary="Cria um novo Item de Infraestrutura (Criptografa a senha)")
def create_infra_item(item: InfraestruturaCreate, db: Session = Depends(get_db), current_user: UsuarioModel = Depends(get_current_user)):
    """Cria um novo Item de Infraestrutura"""
    try:
        # 1. Validação de FKs: Cliente
        cliente = db.query(ClienteModel).filter(
            ClienteModel.id_cliente == item.id_cliente, 
            ClienteModel.user_id == current_user.id_usuario
        ).first()
        if not cliente:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cliente não encontrado ou inacessível.")
        
        # 2. Validação de FKs: Projeto (se fornecido)
        if item.id_servico:
             projeto = db.query(ServicoProjetoModel).filter(
                ServicoProjetoModel.id_servico == item.id_servico, 
                ServicoProjetoModel.user_id == current_user.id_usuario
            ).first()
             if not projeto:
                 raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Projeto não encontrado ou inacessível.")

        # 3. Criptografa a Senha ANTES de salvar
        item_data = item.model_dump()
        raw_password = item_data.pop("referencia_senha", None)
        
        encrypted_password = None
        if raw_password:
            encrypted_password = encrypt_password(raw_password)
            
        # 4. Cria o Item com a senha criptografada
        novo_item = InfraestruturaItemModel(
            **item_data,
            referencia_senha=encrypted_password,
            user_id=current_user.id_usuario
        )
        db.add(novo_item)
        db.commit()
        db.refresh(novo_item)
        
        # Mascara a senha no retorno para o cliente
        novo_item.referencia_senha = "*** CRIPTOGRAFADO ***"
        return novo_item

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro interno: {e}")


@router.get("/", response_model=List[InfraestruturaRead], summary="Lista todos os Itens de Infraestrutura (Senha Mascarada)")
def read_infra_items(db: Session = Depends(get_db), current_user: UsuarioModel = Depends(get_current_user)):
    """Lista todos os Itens de Infraestrutura do usuário"""
    items = db.query(InfraestruturaItemModel).filter(InfraestruturaItemModel.user_id == current_user.id_usuario).all()
    
    # Mascara a senha para a lista de leitura
    for item in items:
        item.referencia_senha = "*** CRIPTOGRAFADO ***"
    return items


@router.get("/{item_id}", response_model=InfraestruturaRead, summary="Busca um Item de Infraestrutura por ID (Senha Mascarada)")
def read_infra_item(item_id: uuid.UUID, db: Session = Depends(get_db), current_user: UsuarioModel = Depends(get_current_user)):
    """Busca um Item de Infraestrutura pelo ID"""
    item = db.query(InfraestruturaItemModel).filter(
        InfraestruturaItemModel.id_item == item_id,
        InfraestruturaItemModel.user_id == current_user.id_usuario
    ).first()
    
    if not item:
        raise HTTPException(status_code=404, detail="Item de Infraestrutura não encontrado.")
    
    # Mascara a senha no retorno
    item.referencia_senha = "*** CRIPTOGRAFADO ***"
    return item


@router.put("/{item_id}", response_model=InfraestruturaRead, summary="Atualiza um Item de Infraestrutura (Re-criptografa a senha se alterada)")
def update_infra_item(item_id: uuid.UUID, item: InfraestruturaCreate, db: Session = Depends(get_db), current_user: UsuarioModel = Depends(get_current_user)):
    """Atualiza um Item de Infraestrutura existente pelo ID"""
    existing_item = db.query(InfraestruturaItemModel).filter(
        InfraestruturaItemModel.id_item == item_id,
        InfraestruturaItemModel.user_id == current_user.id_usuario
    ).first()
    
    if not existing_item:
        raise HTTPException(status_code=404, detail="Item de Infraestrutura não encontrado.")
    
    try:
        # 1. Validação de FKs: Cliente
        cliente = db.query(ClienteModel).filter(
            ClienteModel.id_cliente == item.id_cliente, 
            ClienteModel.user_id == current_user.id_usuario
        ).first()
        if not cliente:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cliente não encontrado ou inacessível.")
        
        # 2. Validação de FKs: Projeto (se fornecido)
        if item.id_servico:
             projeto = db.query(ServicoProjetoModel).filter(
                ServicoProjetoModel.id_servico == item.id_servico, 
                ServicoProjetoModel.user_id == current_user.id_usuario
            ).first()
             if not projeto:
                 raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Projeto não encontrado ou inacessível.")
        
        # 3. Atualiza os campos do item
        item_data = item.model_dump()
        raw_password = item_data.pop("referencia_senha", None)
        
        if raw_password is not None:
            # Re-criptografa a senha se foi alterada
            encrypted_password = encrypt_password(raw_password)
            existing_item.referencia_senha = encrypted_password
        
        for key, value in item_data.items():
            setattr(existing_item, key, value)
        
        db.commit()
        db.refresh(existing_item)
        
        # Mascara a senha no retorno
        existing_item.referencia_senha = "*** CRIPTOGRAFADO ***"
        return existing_item

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro interno: {e}") 


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Deleta um Item de Infraestrutura existente")
def delete_infra_item(item_id: uuid.UUID, db: Session = Depends(get_db), current_user: UsuarioModel = Depends(get_current_user)):
    """Deleta um Item de Infraestrutura existente pelo ID"""
    item = db.query(InfraestruturaItemModel).filter(
        InfraestruturaItemModel.id_item == item_id,
        InfraestruturaItemModel.user_id == current_user.id_usuario
    ).first()
    
    if not item:
        raise HTTPException(status_code=404, detail="Item de Infraestrutura não encontrado.")
    
    try:
        db.delete(item)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro interno: {e}")


@router.get("/decrypt/{item_id}", response_model=DecryptedSecret, summary="DECIFRA E RETORNA a senha de um item (Acesso Restrito!)")
def decrypt_infra_secret(item_id: uuid.UUID, db: Session = Depends(get_db), current_user: UsuarioModel = Depends(get_current_user)):
    """Decifra e retorna a senha de um Item de Infraestrutura pelo ID"""
    item = db.query(InfraestruturaItemModel).filter(
        InfraestruturaItemModel.id_item == item_id,
        InfraestruturaItemModel.user_id == current_user.id_usuario
    ).first()
    
    if not item:
        raise HTTPException(status_code=404, detail="Item de Infraestrutura não encontrado.")
    
    if not item.referencia_senha:
        raise HTTPException(status_code=404, detail="Item não possui senha registrada.")
        
    decrypted_secret = decrypt_password(item.referencia_senha)
    
    if decrypted_secret == "[ERRO DE DECRIPTOGRAFIA]":
        raise HTTPException(status_code=500, detail="Não foi possível decifrar o segredo. Verifique a ENCRYPTION_KEY.")
    
    return DecryptedSecret(
        id_item=item_id,
        secret=decrypted_secret
    )