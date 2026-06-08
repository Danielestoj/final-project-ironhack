from typing import Annotated, Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from auth.jwt import obtener_usuario_actual
from models.usuario import UsuarioDB
from .data_loader import cargar_datos

router = APIRouter(prefix="/enemigos", tags=["Enemigos"])
UsuarioActual = Annotated[UsuarioDB, Depends(obtener_usuario_actual)]


def _datos():
    return cargar_datos("enemigos.json")


@router.get("/")
def listar_enemigos(
    usuario: UsuarioActual,
    q: Optional[str] = Query(None, min_length=1),
):
    data = _datos()
    if q:
        ql = q.lower()
        data = [e for e in data if ql in e.get("nombre", "").lower()]
    return data


@router.get("/{idx}")
def obtener_enemigo(idx: int, usuario: UsuarioActual):
    data = _datos()
    if 0 <= idx < len(data):
        return data[idx]
    raise HTTPException(status_code=404, detail="Enemigo no encontrado")
