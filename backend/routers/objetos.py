import json
from typing import Annotated, Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from auth.jwt import obtener_usuario_actual
from models.usuario import UsuarioDB
from models.objeto import ObjetoDB
from database import get_db

router = APIRouter(prefix="/objetos", tags=["Objetos y Equipo"])
UsuarioActual = Annotated[UsuarioDB, Depends(obtener_usuario_actual)]
DbSession = Annotated[Session, Depends(get_db)]

SECCION_LABELS = {
    "armaduras": "Armaduras",
    "armas": "Armas",
    "equipo": "Equipo",
    "herramientas": "Herramientas",
    "objetos_magicos": "Objetos Mágicos",
}


def _objeto_to_dict(o: ObjetoDB) -> dict:
    datos = json.loads(o.datos or "{}")
    return {
        "id": o.id,
        "nombre": o.nombre,
        "seccion": o.seccion,
        **datos,
    }


@router.get("/")
def listar_objetos(
    usuario: UsuarioActual,
    db: DbSession,
    seccion: Optional[str] = None,
    q: Optional[str] = Query(None, min_length=1),
):
    query = db.query(ObjetoDB)
    if seccion:
        query = query.filter(ObjetoDB.seccion == seccion)
    if q:
        ql = f"%{q.lower()}%"
        query = query.filter(ObjetoDB.nombre.ilike(ql))
    data = query.order_by(ObjetoDB.nombre).all()
    return [_objeto_to_dict(o) for o in data]


@router.get("/{objeto_id}")
def obtener_objeto(objeto_id: int, usuario: UsuarioActual, db: DbSession):
    o = db.query(ObjetoDB).filter(ObjetoDB.id == objeto_id).first()
    if not o:
        raise HTTPException(status_code=404, detail="Objeto no encontrado")
    return _objeto_to_dict(o)
