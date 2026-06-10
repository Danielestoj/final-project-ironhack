from typing import Annotated, Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from auth.jwt import obtener_usuario_actual
from models.usuario import UsuarioDB
from .data_loader import cargar_datos

router = APIRouter(prefix="/clases", tags=["Clases"])
UsuarioActual = Annotated[UsuarioDB, Depends(obtener_usuario_actual)]


def _datos():
    return cargar_datos("clases.json")


@router.get("/")
def listar_clases(
    usuario: UsuarioActual,
    q: Optional[str] = Query(None, min_length=1),
):
    data = _datos()
    if q:
        ql = q.lower()
        data = [c for c in data if ql in c.get("nombre", "").lower()]
    return data


@router.get("/{idx}")
def obtener_clase(idx: int, usuario: UsuarioActual):
    data = _datos()
    if 0 <= idx < len(data):
        return data[idx]
    raise HTTPException(status_code=404, detail="Clase no encontrada")
