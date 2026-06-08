from typing import Annotated, Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from auth.jwt import obtener_usuario_actual
from models.usuario import UsuarioDB
from .data_loader import cargar_datos

router = APIRouter(prefix="/objetos", tags=["Objetos y Equipo"])
UsuarioActual = Annotated[UsuarioDB, Depends(obtener_usuario_actual)]


def _datos():
    return cargar_datos("objetos_equipo.json")


@router.get("/")
def listar_objetos(
    usuario: UsuarioActual,
    tipo: Optional[str] = None,
    q: Optional[str] = Query(None, min_length=1),
):
    data = _datos()
    if tipo:
        data = [o for o in data if o.get("tipo") == tipo]
    if q:
        ql = q.lower()
        data = [o for o in data if ql in o.get("nombre", "").lower()]
    return data


@router.get("/{idx}")
def obtener_objeto(idx: int, usuario: UsuarioActual):
    data = _datos()
    if 0 <= idx < len(data):
        return data[idx]
    raise HTTPException(status_code=404, detail="Objeto no encontrado")
