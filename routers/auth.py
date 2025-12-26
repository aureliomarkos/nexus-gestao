from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from datetime import timedelta

from database import get_db
from models.usuario import UsuarioModel, UsuarioCreate, UsuarioRead
from auth.utils import verify_password, hash_password, create_access_token, ALGORITHM
from config import SECRET_KEY

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")
router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/users/", response_model=UsuarioRead, status_code=status.HTTP_201_CREATED)
def create_user(user_in: UsuarioCreate, db: Session = Depends(get_db)):
    # Verifica usuario existente por nome ou email
    exists = db.query(UsuarioModel).filter((UsuarioModel.nome == user_in.nome) | (UsuarioModel.email == user_in.email)).first()
    if exists:
        raise HTTPException(status_code=400, detail="Usuário ou email já cadastrado")

    hashed = hash_password(user_in.password)
    user = UsuarioModel(
        nome=user_in.nome,
        email=user_in.email,
        hashed_password=hashed
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/token")
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    remember: str | None = Form(None),
    db: Session = Depends(get_db)
):
    # form_data.username corresponde ao campo `nome` no model
    user = db.query(UsuarioModel).filter((UsuarioModel.nome == form_data.username) | (UsuarioModel.email == form_data.username)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciais inválidas")
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciais inválidas")

    # Se o usuário marcou "Lembrar", aumenta a validade do token (ex.: 30 dias)
    remember_flag = False
    if remember:
        try:
            if str(remember).lower() in ("true", "on", "1", "yes"):
                remember_flag = True
        except Exception:
            remember_flag = False

    access_token_expires = timedelta(days=7) if remember_flag else timedelta(minutes=60 * 24)
    token = create_access_token(data={"sub": str(user.id_usuario)}, expires_delta=access_token_expires)
    return {"access_token": token, "token_type": "bearer"}


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> UsuarioModel:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        sub: str | None = payload.get("sub")
        if sub is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(UsuarioModel).filter(UsuarioModel.id_usuario == sub).first()
    if not user:
        raise credentials_exception
    return user


@router.get("/me", response_model=UsuarioRead)
def read_me(current_user: UsuarioModel = Depends(get_current_user)):
    return current_user
