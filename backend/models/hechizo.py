from sqlalchemy import Column, Integer, String, Text
from database import Base


class HechizoDB(Base):
    __tablename__ = "hechizos"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(Text, nullable=False, index=True)
    nivel = Column(Integer, default=0, index=True)
    escuela = Column(String(50), default="", index=True)
    tiempo = Column(String(100), default="")
    alcance = Column(String(100), default="")
    componentes = Column(Text, default="")
    duracion = Column(String(100), default="")
    descripcion = Column(Text, default="")
    clases = Column(Text, default="[]")
