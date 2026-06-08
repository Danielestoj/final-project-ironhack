from datetime import datetime, timedelta
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from config import settings
from auth.password import verificar_password
from services.usuario_service import usuario_service

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
EXPIRACION_MINUTOS = settings.ACCESS_TOKEN_EXPIRE_MINUTES

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def crear_token(datos: dict) -> str:
    payload = datos.copy()
    expira = datetime.utcnow() + timedelta(minutes=EXPIRACION_MINUTOS)
    payload["exp"] = expira
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decodificar_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")


def obtener_usuario_actual(token: str = Depends(oauth2_scheme)):
    payload = decodificar_token(token)
    email = payload.get("sub")
    if not email:
        raise HTTPException(status_code=401, detail="Token inválido")
    try:
        usuario = usuario_service.obtener_por_email(email)
    except KeyError:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")
    return usuario
