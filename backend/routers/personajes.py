from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from auth.jwt import obtener_usuario_actual
from models.personaje import PersonajeCrear, PersonajeActualizar, PersonajeOut
from models.usuario import UsuarioDB
from services.personaje_service import personaje_service

router = APIRouter(prefix="/personajes", tags=["Personajes"])
UsuarioActual = Annotated[UsuarioDB, Depends(obtener_usuario_actual)]
DBSession = Annotated[Session, Depends(get_db)]


@router.get("/", response_model=List[PersonajeOut])
def listar_personajes(usuario: UsuarioActual, db: DBSession):
    return personaje_service.listar(db, usuario.id)


@router.get("/{personaje_id}", response_model=PersonajeOut)
def obtener_personaje(personaje_id: int, usuario: UsuarioActual, db: DBSession):
    try:
        pj = personaje_service.obtener(db, personaje_id)
        if pj.usuario_id != usuario.id:
            raise HTTPException(status_code=403, detail="No tienes acceso a este personaje")
        return pj
    except KeyError:
        raise HTTPException(status_code=404, detail="Personaje no encontrado")


@router.post("/", response_model=PersonajeOut, status_code=status.HTTP_201_CREATED)
def crear_personaje(datos: PersonajeCrear, usuario: UsuarioActual, db: DBSession):
    return personaje_service.crear(db, datos, usuario.id)


@router.put("/{personaje_id}", response_model=PersonajeOut)
def actualizar_personaje(personaje_id: int, datos: PersonajeActualizar, usuario: UsuarioActual, db: DBSession):
    try:
        return personaje_service.actualizar(db, personaje_id, datos, usuario.id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Personaje no encontrado")
    except ValueError as exc:
        raise HTTPException(status_code=403, detail=str(exc))


@router.delete("/{personaje_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_personaje(personaje_id: int, usuario: UsuarioActual, db: DBSession):
    try:
        personaje_service.eliminar(db, personaje_id, usuario.id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Personaje no encontrado")
    except ValueError as exc:
        raise HTTPException(status_code=403, detail=str(exc))
