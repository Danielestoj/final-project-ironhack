import json
from typing import Annotated, Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from auth.jwt import obtener_usuario_actual
from models.usuario import UsuarioDB
from models.hechizo import HechizoDB
from database import get_db

router = APIRouter(prefix="/hechizos", tags=["Hechizos"])
UsuarioActual = Annotated[UsuarioDB, Depends(obtener_usuario_actual)]
DbSession = Annotated[Session, Depends(get_db)]


def _hechizo_to_dict(h: HechizoDB) -> dict:
    return {
        "id": h.id,
        "nombre": h.nombre,
        "nivel": h.nivel,
        "escuela": h.escuela,
        "tiempo": h.tiempo,
        "alcance": h.alcance,
        "componentes": h.componentes,
        "duracion": h.duracion,
        "descripcion": h.descripcion,
        "clases": json.loads(h.clases or "[]"),
    }


@router.get("/")
def listar_hechizos(
    usuario: UsuarioActual,
    db: DbSession,
    nivel: Optional[int] = Query(None, ge=0, le=9),
    escuela: Optional[str] = None,
    clase: Optional[str] = None,
    q: Optional[str] = Query(None, min_length=1),
):
    query = db.query(HechizoDB)
    if nivel is not None:
        query = query.filter(HechizoDB.nivel == nivel)
    if escuela:
        query = query.filter(HechizoDB.escuela.ilike(escuela))
    if clase:
        query = query.filter(HechizoDB.clases.ilike(f"%{clase}%"))
    if q:
        ql = f"%{q.lower()}%"
        query = query.filter(
            HechizoDB.nombre.ilike(ql) | HechizoDB.descripcion.ilike(ql)
        )
    data = query.order_by(HechizoDB.nivel, HechizoDB.nombre).all()
    return [_hechizo_to_dict(h) for h in data]


@router.get("/{hechizo_id}")
def obtener_hechizo(hechizo_id: int, usuario: UsuarioActual, db: DbSession):
    h = db.query(HechizoDB).filter(HechizoDB.id == hechizo_id).first()
    if not h:
        raise HTTPException(status_code=404, detail="Hechizo no encontrado")
    return _hechizo_to_dict(h)
