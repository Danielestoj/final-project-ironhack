from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, status

from auth.jwt import obtener_usuario_actual
from models.personaje import PersonajeCrear, PersonajeActualizar, PersonajeDB
from models.usuario import UsuarioDB
from services.personaje_service import personaje_service

router = APIRouter(prefix="/personajes", tags=["Personajes"])
UsuarioActual = Annotated[UsuarioDB, Depends(obtener_usuario_actual)]


@router.get("/", response_model=List[PersonajeDB])
def listar_personajes(usuario: UsuarioActual):
    return personaje_service.listar(usuario.id)


@router.get("/{personaje_id}", response_model=PersonajeDB)
def obtener_personaje(personaje_id: int, usuario: UsuarioActual):
    try:
        pj = personaje_service.obtener(personaje_id)
        if pj.usuario_id != usuario.id:
            raise HTTPException(status_code=403, detail="No tienes acceso a este personaje")
        return pj
    except KeyError:
        raise HTTPException(status_code=404, detail="Personaje no encontrado")


@router.post("/", response_model=PersonajeDB, status_code=status.HTTP_201_CREATED)
def crear_personaje(datos: PersonajeCrear, usuario: UsuarioActual):
    return personaje_service.crear(datos, usuario.id)


@router.put("/{personaje_id}", response_model=PersonajeDB)
def actualizar_personaje(personaje_id: int, datos: PersonajeActualizar, usuario: UsuarioActual):
    try:
        return personaje_service.actualizar(personaje_id, datos, usuario.id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Personaje no encontrado")
    except ValueError as exc:
        raise HTTPException(status_code=403, detail=str(exc))


@router.delete("/{personaje_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_personaje(personaje_id: int, usuario: UsuarioActual):
    try:
        personaje_service.eliminar(personaje_id, usuario.id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Personaje no encontrado")
    except ValueError as exc:
        raise HTTPException(status_code=403, detail=str(exc))
