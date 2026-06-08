from typing import Annotated, Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from auth.jwt import obtener_usuario_actual
from models.usuario import UsuarioDB
from .data_loader import cargar_datos

router = APIRouter(prefix="/hechizos", tags=["Hechizos"])
UsuarioActual = Annotated[UsuarioDB, Depends(obtener_usuario_actual)]


def _datos():
    return cargar_datos("hechizos.json")


@router.get("/")
def listar_hechizos(
    usuario: UsuarioActual,
    nivel: Optional[int] = Query(None, ge=0, le=9),
    escuela: Optional[str] = None,
    q: Optional[str] = Query(None, min_length=1),
):
    data = _datos()
    if nivel is not None:
        data = [h for h in data if h.get("nivel") == nivel]
    if escuela:
        data = [h for h in data if h.get("escuela", "").lower() == escuela.lower()]
    if q:
        ql = q.lower()
        data = [h for h in data if ql in h.get("nombre", "").lower() or ql in h.get("descripcion", "").lower()]
    return data


@router.get("/{hechizo_id}")
def obtener_hechizo(hechizo_id: int, usuario: UsuarioActual):
    data = _datos()
    if 0 <= hechizo_id < len(data):
        return data[hechizo_id]
    raise HTTPException(status_code=404, detail="Hechizo no encontrado")
