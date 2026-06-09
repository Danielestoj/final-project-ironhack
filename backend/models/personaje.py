from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from sqlalchemy import Column, Integer, String, Boolean, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database import Base


class PersonajeDB(Base):
    __tablename__ = "personajes"
    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    # Basic
    nombre = Column(String(100), nullable=False)
    nombre_jugador = Column(String(100), default="")
    raza = Column(String(50), default="")
    clase = Column(String(50), default="")
    nivel = Column(Integer, default=1)
    trasfondo = Column(String(100), default="")
    experiencia = Column(Integer, default=0)
    alineamiento = Column(String(30), default="")
    # Stats
    fuerza = Column(Integer, default=10)
    destreza = Column(Integer, default=10)
    constitucion = Column(Integer, default=10)
    inteligencia = Column(Integer, default=10)
    sabiduria = Column(Integer, default=10)
    carisma = Column(Integer, default=10)
    # Combat
    clase_armadura = Column(Integer, default=10)
    iniciativa = Column(Integer, default=0)
    velocidad = Column(Integer, default=9)
    pg_max = Column(Integer, default=10)
    pg_actual = Column(Integer, default=10)
    pg_temporales = Column(Integer, default=0)
    dados_golpe = Column(String(10), default="1d10")
    muerte_exitos = Column(Integer, default=0)
    muerte_fallos = Column(Integer, default=0)
    inspiracion = Column(Boolean, default=False)
    bonif_competencia = Column(Integer, default=2)
    # Saving throws (proficiency)
    fuerza_salv_prof = Column(Boolean, default=False)
    destreza_salv_prof = Column(Boolean, default=False)
    constitucion_salv_prof = Column(Boolean, default=False)
    inteligencia_salv_prof = Column(Boolean, default=False)
    sabiduria_salv_prof = Column(Boolean, default=False)
    carisma_salv_prof = Column(Boolean, default=False)
    # Skills (0=none, 1=proficient, 2=expertise)
    acrobacias_prof = Column(Integer, default=0)
    arcanos_prof = Column(Integer, default=0)
    atletismo_prof = Column(Integer, default=0)
    engaño_prof = Column(Integer, default=0)
    historia_prof = Column(Integer, default=0)
    interpretacion_prof = Column(Integer, default=0)
    intimidacion_prof = Column(Integer, default=0)
    investigacion_prof = Column(Integer, default=0)
    juego_manos_prof = Column(Integer, default=0)
    medicina_prof = Column(Integer, default=0)
    naturaleza_prof = Column(Integer, default=0)
    percepcion_prof = Column(Integer, default=0)
    perspicacia_prof = Column(Integer, default=0)
    persuasion_prof = Column(Integer, default=0)
    religion_prof = Column(Integer, default=0)
    sigilo_prof = Column(Integer, default=0)
    supervivencia_prof = Column(Integer, default=0)
    trato_animales_prof = Column(Integer, default=0)
    # Competences & features
    competencias_idiomas = Column(Text, default="")
    rasgos_atributos = Column(Text, default="")
    rasgos_personalidad = Column(Text, default="")
    ideales = Column(Text, default="")
    vinculos = Column(Text, default="")
    defectos = Column(Text, default="")
    # Appearance
    edad = Column(String(20), default="")
    altura = Column(String(20), default="")
    peso = Column(String(20), default="")
    ojos = Column(String(20), default="")
    piel = Column(String(20), default="")
    cabello = Column(String(20), default="")
    # Backstory
    apariencia = Column(Text, default="")
    historia = Column(Text, default="")
    aliados_organizaciones = Column(Text, default="")
    tesoro = Column(Text, default="")
    rasgos_adicionales = Column(Text, default="")
    # Wealth
    pc = Column(Integer, default=0)
    pe = Column(Integer, default=0)
    ppt = Column(Integer, default=0)
    po = Column(Integer, default=0)
    pp = Column(Integer, default=0)
    # Spellcasting
    clase_lanzadora = Column(String(50), default="")
    carac_lanzamiento = Column(String(30), default="")
    salvacion_conjuro = Column(Integer, default=0)
    bonif_ataque_conjuro = Column(Integer, default=0)
    espacios_conjuros = Column(Text, default="{}")
    # Timestamps
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    fecha_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    # Relations
    usuario = relationship("UsuarioDB", back_populates="personajes")
    hechizos = relationship("PersonajeHechizo", back_populates="personaje", cascade="all, delete-orphan")
    objetos = relationship("PersonajeObjeto", back_populates="personaje", cascade="all, delete-orphan")
    ataques = relationship("PersonajeAtaque", back_populates="personaje", cascade="all, delete-orphan")


class PersonajeHechizo(Base):
    __tablename__ = "personaje_hechizos"
    id = Column(Integer, primary_key=True)
    personaje_id = Column(Integer, ForeignKey("personajes.id", ondelete="CASCADE"), nullable=False)
    nombre_hechizo = Column(String(100), nullable=False)
    nivel = Column(Integer, default=0)
    preparado = Column(Boolean, default=False)
    es_truco = Column(Boolean, default=False)
    personaje = relationship("PersonajeDB", back_populates="hechizos")


class PersonajeObjeto(Base):
    __tablename__ = "personaje_objetos"
    id = Column(Integer, primary_key=True)
    personaje_id = Column(Integer, ForeignKey("personajes.id", ondelete="CASCADE"), nullable=False)
    nombre_objeto = Column(String(200), nullable=False)
    cantidad = Column(Integer, default=1)
    personaje = relationship("PersonajeDB", back_populates="objetos")


class PersonajeAtaque(Base):
    __tablename__ = "personaje_ataques"
    id = Column(Integer, primary_key=True)
    personaje_id = Column(Integer, ForeignKey("personajes.id", ondelete="CASCADE"), nullable=False)
    nombre = Column(String(100), default="")
    bonif_ataque = Column(String(20), default="")
    danio = Column(String(50), default="")
    tipo = Column(String(50), default="")
    personaje = relationship("PersonajeDB", back_populates="ataques")


# ── Pydantic schemas for API ──

class AtaqueSchema(BaseModel):
    nombre: str = ""
    bonif_ataque: str = ""
    danio: str = ""
    tipo: str = ""

    model_config = {"from_attributes": True}


class HechizoSchema(BaseModel):
    nombre_hechizo: str = ""
    nivel: int = 0
    preparado: bool = False
    es_truco: bool = False

    model_config = {"from_attributes": True}


class ObjetoSchema(BaseModel):
    nombre_objeto: str = ""
    cantidad: int = 1

    model_config = {"from_attributes": True}


class PersonajeCrear(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=100)
    nombre_jugador: str = ""
    raza: str = ""
    clase: str = ""
    nivel: int = 1
    trasfondo: str = ""
    experiencia: int = 0
    alineamiento: str = ""
    fuerza: int = 10
    destreza: int = 10
    constitucion: int = 10
    inteligencia: int = 10
    sabiduria: int = 10
    carisma: int = 10
    clase_armadura: int = 10
    iniciativa: int = 0
    velocidad: int = 9
    pg_max: int = 10
    pg_actual: int = 10
    pg_temporales: int = 0
    dados_golpe: str = "1d10"
    muerte_exitos: int = 0
    muerte_fallos: int = 0
    inspiracion: bool = False
    bonif_competencia: int = 2
    fuerza_salv_prof: bool = False
    destreza_salv_prof: bool = False
    constitucion_salv_prof: bool = False
    inteligencia_salv_prof: bool = False
    sabiduria_salv_prof: bool = False
    carisma_salv_prof: bool = False
    acrobacias_prof: int = 0
    arcanos_prof: int = 0
    atletismo_prof: int = 0
    engaño_prof: int = 0
    historia_prof: int = 0
    interpretacion_prof: int = 0
    intimidacion_prof: int = 0
    investigacion_prof: int = 0
    juego_manos_prof: int = 0
    medicina_prof: int = 0
    naturaleza_prof: int = 0
    percepcion_prof: int = 0
    perspicacia_prof: int = 0
    persuasion_prof: int = 0
    religion_prof: int = 0
    sigilo_prof: int = 0
    supervivencia_prof: int = 0
    trato_animales_prof: int = 0
    competencias_idiomas: str = ""
    rasgos_atributos: str = ""
    rasgos_personalidad: str = ""
    ideales: str = ""
    vinculos: str = ""
    defectos: str = ""
    edad: str = ""
    altura: str = ""
    peso: str = ""
    ojos: str = ""
    piel: str = ""
    cabello: str = ""
    apariencia: str = ""
    historia: str = ""
    aliados_organizaciones: str = ""
    tesoro: str = ""
    rasgos_adicionales: str = ""
    pc: int = 0
    pe: int = 0
    ppt: int = 0
    po: int = 0
    pp: int = 0
    clase_lanzadora: str = ""
    carac_lanzamiento: str = ""
    salvacion_conjuro: int = 0
    bonif_ataque_conjuro: int = 0
    espacios_conjuros: str = "{}"
    hechizos: list[HechizoSchema] = Field(default_factory=list)
    objetos: list[ObjetoSchema] = Field(default_factory=list)
    ataques: list[AtaqueSchema] = Field(default_factory=list)
    hechizos_favoritos: list[str] = Field(default_factory=list)

    model_config = {"populate_by_name": True}


class PersonajeActualizar(BaseModel):
    nombre: Optional[str] = Field(None, min_length=1, max_length=100)
    nombre_jugador: Optional[str] = None
    raza: Optional[str] = None
    clase: Optional[str] = None
    nivel: Optional[int] = Field(None, ge=1, le=20)
    trasfondo: Optional[str] = None
    experiencia: Optional[int] = None
    alineamiento: Optional[str] = None
    fuerza: Optional[int] = None
    destreza: Optional[int] = None
    constitucion: Optional[int] = None
    inteligencia: Optional[int] = None
    sabiduria: Optional[int] = None
    carisma: Optional[int] = None
    clase_armadura: Optional[int] = None
    iniciativa: Optional[int] = None
    velocidad: Optional[int] = None
    pg_max: Optional[int] = None
    pg_actual: Optional[int] = None
    pg_temporales: Optional[int] = None
    dados_golpe: Optional[str] = None
    muerte_exitos: Optional[int] = None
    muerte_fallos: Optional[int] = None
    inspiracion: Optional[bool] = None
    bonif_competencia: Optional[int] = None
    fuerza_salv_prof: Optional[bool] = None
    destreza_salv_prof: Optional[bool] = None
    constitucion_salv_prof: Optional[bool] = None
    inteligencia_salv_prof: Optional[bool] = None
    sabiduria_salv_prof: Optional[bool] = None
    carisma_salv_prof: Optional[bool] = None
    acrobacias_prof: Optional[int] = None
    arcanos_prof: Optional[int] = None
    atletismo_prof: Optional[int] = None
    engaño_prof: Optional[int] = None
    historia_prof: Optional[int] = None
    interpretacion_prof: Optional[int] = None
    intimidacion_prof: Optional[int] = None
    investigacion_prof: Optional[int] = None
    juego_manos_prof: Optional[int] = None
    medicina_prof: Optional[int] = None
    naturaleza_prof: Optional[int] = None
    percepcion_prof: Optional[int] = None
    perspicacia_prof: Optional[int] = None
    persuasion_prof: Optional[int] = None
    religion_prof: Optional[int] = None
    sigilo_prof: Optional[int] = None
    supervivencia_prof: Optional[int] = None
    trato_animales_prof: Optional[int] = None
    competencias_idiomas: Optional[str] = None
    rasgos_atributos: Optional[str] = None
    rasgos_personalidad: Optional[str] = None
    ideales: Optional[str] = None
    vinculos: Optional[str] = None
    defectos: Optional[str] = None
    edad: Optional[str] = None
    altura: Optional[str] = None
    peso: Optional[str] = None
    ojos: Optional[str] = None
    piel: Optional[str] = None
    cabello: Optional[str] = None
    apariencia: Optional[str] = None
    historia: Optional[str] = None
    aliados_organizaciones: Optional[str] = None
    tesoro: Optional[str] = None
    rasgos_adicionales: Optional[str] = None
    pc: Optional[int] = None
    pe: Optional[int] = None
    ppt: Optional[int] = None
    po: Optional[int] = None
    pp: Optional[int] = None
    clase_lanzadora: Optional[str] = None
    carac_lanzamiento: Optional[str] = None
    salvacion_conjuro: Optional[int] = None
    bonif_ataque_conjuro: Optional[int] = None
    espacios_conjuros: Optional[str] = None
    hechizos: Optional[list[HechizoSchema]] = None
    objetos: Optional[list[ObjetoSchema]] = None
    ataques: Optional[list[AtaqueSchema]] = None
    hechizos_favoritos: Optional[list[str]] = None


class PersonajeOut(BaseModel):
    id: int
    usuario_id: int
    nombre: str
    nombre_jugador: str = ""
    raza: str = ""
    clase: str = ""
    nivel: int = 1
    trasfondo: str = ""
    experiencia: int = 0
    alineamiento: str = ""
    fuerza: int = 10
    destreza: int = 10
    constitucion: int = 10
    inteligencia: int = 10
    sabiduria: int = 10
    carisma: int = 10
    clase_armadura: int = 10
    iniciativa: int = 0
    velocidad: int = 9
    pg_max: int = 10
    pg_actual: int = 10
    pg_temporales: int = 0
    dados_golpe: str = "1d10"
    muerte_exitos: int = 0
    muerte_fallos: int = 0
    inspiracion: bool = False
    bonif_competencia: int = 2
    fuerza_salv_prof: bool = False
    destreza_salv_prof: bool = False
    constitucion_salv_prof: bool = False
    inteligencia_salv_prof: bool = False
    sabiduria_salv_prof: bool = False
    carisma_salv_prof: bool = False
    acrobacias_prof: int = 0
    arcanos_prof: int = 0
    atletismo_prof: int = 0
    engaño_prof: int = 0
    historia_prof: int = 0
    interpretacion_prof: int = 0
    intimidacion_prof: int = 0
    investigacion_prof: int = 0
    juego_manos_prof: int = 0
    medicina_prof: int = 0
    naturaleza_prof: int = 0
    percepcion_prof: int = 0
    perspicacia_prof: int = 0
    persuasion_prof: int = 0
    religion_prof: int = 0
    sigilo_prof: int = 0
    supervivencia_prof: int = 0
    trato_animales_prof: int = 0
    competencias_idiomas: str = ""
    rasgos_atributos: str = ""
    rasgos_personalidad: str = ""
    ideales: str = ""
    vinculos: str = ""
    defectos: str = ""
    edad: str = ""
    altura: str = ""
    peso: str = ""
    ojos: str = ""
    piel: str = ""
    cabello: str = ""
    apariencia: str = ""
    historia: str = ""
    aliados_organizaciones: str = ""
    tesoro: str = ""
    rasgos_adicionales: str = ""
    pc: int = 0
    pe: int = 0
    ppt: int = 0
    po: int = 0
    pp: int = 0
    clase_lanzadora: str = ""
    carac_lanzamiento: str = ""
    salvacion_conjuro: int = 0
    bonif_ataque_conjuro: int = 0
    espacios_conjuros: str = "{}"
    hechizos: list[HechizoSchema] = Field(default_factory=list)
    objetos: list[ObjetoSchema] = Field(default_factory=list)
    ataques: list[AtaqueSchema] = Field(default_factory=list)
    hechizos_favoritos: list[str] = Field(default_factory=list)
    fecha_creacion: datetime
    fecha_actualizacion: datetime

    model_config = {"from_attributes": True}
