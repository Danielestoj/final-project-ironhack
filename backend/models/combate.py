from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, JSON
from database import Base


class CombateDB(Base):
    __tablename__ = "combates"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    nombre = Column(String(100), default="Combate")
    ronda = Column(Integer, default=1)
    turno_actual = Column(Integer, default=0)
    activo = Column(Boolean, default=True)
    participantes = Column(JSON, default=list)
    fecha_creacion = Column(DateTime, default=lambda: datetime.now(timezone.utc))
