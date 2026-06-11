from sqlalchemy import Column, Integer, String, Text
from database import Base


class ObjetoDB(Base):
    __tablename__ = "objetos"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(200), nullable=False, index=True)
    seccion = Column(String(50), default="", index=True)
    datos = Column(Text, default="{}")
