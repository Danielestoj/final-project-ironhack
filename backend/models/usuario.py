from datetime import datetime, timezone
from typing import Literal
from pydantic import BaseModel, Field


class UsuarioCrear(BaseModel):
    email: str = Field(..., description="Email único del usuario")
    password: str = Field(..., min_length=8, description="Contraseña (mínimo 8 caracteres)")
    nombre: str = Field(..., min_length=2, max_length=100)


class UsuarioLogin(BaseModel):
    email: str
    password: str


class UsuarioPublico(BaseModel):
    id: int
    email: str
    nombre: str
    rol: str = "usuario"
    fecha_registro: datetime

    model_config = {"from_attributes": True}


class UsuarioDB(UsuarioPublico):
    password_hash: str


class TokenRespuesta(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expira_en_segundos: int = 3600
    usuario: UsuarioPublico
