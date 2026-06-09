from datetime import datetime
from pydantic import BaseModel, Field
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from database import Base


class UsuarioDB(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    nombre = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)
    rol = Column(String, default="usuario")
    fecha_registro = Column(DateTime, default=datetime.utcnow)
    personajes = relationship("PersonajeDB", back_populates="usuario", cascade="all, delete-orphan")


class UsuarioCrear(BaseModel):
    email: str = Field(..., max_length=255)
    nombre: str = Field(..., min_length=1, max_length=100)
    password: str = Field(..., min_length=6, max_length=128)


class UsuarioLogin(BaseModel):
    email: str
    password: str


class UsuarioPublico(BaseModel):
    id: int
    email: str
    nombre: str
    rol: str
    fecha_registro: datetime


class TokenRespuesta(BaseModel):
    access_token: str
    expira_en_segundos: int
    usuario: UsuarioPublico
