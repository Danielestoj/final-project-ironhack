from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class PersonajeCrear(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=100)
    raza: str = Field(..., description="Humano, Elfo, Enano, etc.")
    clase: str = Field(..., description="Guerrero, Mago, Pícaro, etc.")
    nivel: int = Field(default=1, ge=1, le=20)
    fuerza: int = Field(default=10, ge=1, le=20)
    destreza: int = Field(default=10, ge=1, le=20)
    constitucion: int = Field(default=10, ge=1, le=20)
    inteligencia: int = Field(default=10, ge=1, le=20)
    sabiduria: int = Field(default=10, ge=1, le=20)
    carisma: int = Field(default=10, ge=1, le=20)
    puntos_golpe: int = Field(default=10, ge=1)
    hechizos_favoritos: list[str] = Field(default_factory=list)


class PersonajeActualizar(BaseModel):
    nombre: Optional[str] = Field(None, min_length=1, max_length=100)
    nivel: Optional[int] = Field(None, ge=1, le=20)
    puntos_golpe: Optional[int] = Field(None, ge=1)
    hechizos_favoritos: Optional[list[str]] = None


class PersonajeDB(BaseModel):
    id: int
    nombre: str
    raza: str
    clase: str
    nivel: int
    fuerza: int
    destreza: int
    constitucion: int
    inteligencia: int
    sabiduria: int
    carisma: int
    puntos_golpe: int
    hechizos_favoritos: list[str]
    usuario_id: int
    fecha_creacion: datetime
    fecha_actualizacion: datetime

    model_config = {"from_attributes": True}
