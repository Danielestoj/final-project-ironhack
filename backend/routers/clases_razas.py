from typing import Annotated, Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from auth.jwt import obtener_usuario_actual
from models.usuario import UsuarioDB
from .data_loader import cargar_datos

router = APIRouter(prefix="/clases-razas", tags=["Clases y Razas"])
UsuarioActual = Annotated[UsuarioDB, Depends(obtener_usuario_actual)]


def _datos():
    return cargar_datos("clases_razas.json")


@router.get("/")
def listar_clases_razas(
    usuario: UsuarioActual,
    tipo: Optional[str] = None,
    q: Optional[str] = Query(None, min_length=1),
):
    data = _datos()
    if tipo:
        data = [c for c in data if c.get("tipo") == tipo]
    if q:
        ql = q.lower()
        data = [c for c in data if ql in c.get("nombre", "").lower()]
    return data


@router.get("/{idx}")
def obtener_clase_raza(idx: int, usuario: UsuarioActual):
    data = _datos()
    if 0 <= idx < len(data):
        return data[idx]
    raise HTTPException(status_code=404, detail="Entrada no encontrada")
