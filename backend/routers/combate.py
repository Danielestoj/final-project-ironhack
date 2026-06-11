from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import get_db
from auth.jwt import obtener_usuario_actual
from models.usuario import UsuarioDB
from models.combate import CombateDB

router = APIRouter(prefix="/api/combate", tags=["Combate"])


class ParticipanteIn(BaseModel):
    nombre: str
    iniciativa: int
    pg: int = 1
    pg_max: int = 1
    tipo: str = "pj"
    condiciones: list = []


class CombateCrear(BaseModel):
    nombre: str = "Combate"
    participantes: list[ParticipanteIn]


@router.get("/")
def listar_combates(usuario: UsuarioDB = Depends(obtener_usuario_actual), db: Session = Depends(get_db)):
    combates = db.query(CombateDB).filter(
        CombateDB.usuario_id == usuario.id, CombateDB.activo == True
    ).all()
    return [{
        "id": c.id, "nombre": c.nombre, "ronda": c.ronda,
        "turno_actual": c.turno_actual, "participantes": c.participantes,
        "fecha_creacion": c.fecha_creacion.isoformat() if c.fecha_creacion else "",
    } for c in combates]


@router.post("/")
def crear_combate(body: CombateCrear, usuario: UsuarioDB = Depends(obtener_usuario_actual), db: Session = Depends(get_db)):
    participantes = [p.model_dump() for p in body.participantes]
    participantes.sort(key=lambda x: x["iniciativa"], reverse=True)
    c = CombateDB(
        usuario_id=usuario.id, nombre=body.nombre, participantes=participantes,
        turno_actual=0, ronda=1, activo=True,
        fecha_creacion=datetime.now(timezone.utc),
    )
    db.add(c)
    db.commit()
    db.refresh(c)
    return {"id": c.id, "nombre": c.nombre, "participantes": participantes, "ronda": 1, "turno_actual": 0, "activo": True}


@router.get("/{combate_id}")
def obtener_combate(combate_id: int, usuario: UsuarioDB = Depends(obtener_usuario_actual), db: Session = Depends(get_db)):
    c = db.query(CombateDB).filter(CombateDB.id == combate_id, CombateDB.usuario_id == usuario.id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Combate no encontrado")
    return {"id": c.id, "nombre": c.nombre, "ronda": c.ronda, "turno_actual": c.turno_actual,
            "participantes": c.participantes, "activo": c.activo}


@router.post("/{combate_id}/next")
def siguiente_turno(combate_id: int, usuario: UsuarioDB = Depends(obtener_usuario_actual), db: Session = Depends(get_db)):
    c = db.query(CombateDB).filter(CombateDB.id == combate_id, CombateDB.usuario_id == usuario.id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Combate no encontrado")
    if not c.activo:
        raise HTTPException(status_code=400, detail="Combate terminado")
    if c.turno_actual + 1 < len(c.participantes):
        c.turno_actual += 1
    else:
        c.turno_actual = 0
        c.ronda += 1
    db.commit()
    return {"ronda": c.ronda, "turno_actual": c.turno_actual, "participante": c.participantes[c.turno_actual]["nombre"]}


@router.post("/{combate_id}/damage")
def aplicar_dano(combate_id: int, idx: int, dano: int, usuario: UsuarioDB = Depends(obtener_usuario_actual), db: Session = Depends(get_db)):
    c = db.query(CombateDB).filter(CombateDB.id == combate_id, CombateDB.usuario_id == usuario.id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Combate no encontrado")
    if idx < 0 or idx >= len(c.participantes):
        raise HTTPException(status_code=400, detail="Índice inválido")
    p = c.participantes[idx]
    p["pg"] = max(0, p["pg"] - dano)
    c.participantes[idx] = p
    db.commit()
    return {"participante": p["nombre"], "pg_restantes": p["pg"], "pg_max": p["pg_max"]}


@router.post("/{combate_id}/heal")
def curar(combate_id: int, idx: int, curacion: int, usuario: UsuarioDB = Depends(obtener_usuario_actual), db: Session = Depends(get_db)):
    c = db.query(CombateDB).filter(CombateDB.id == combate_id, CombateDB.usuario_id == usuario.id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Combate no encontrado")
    if idx < 0 or idx >= len(c.participantes):
        raise HTTPException(status_code=400, detail="Índice inválido")
    p = c.participantes[idx]
    p["pg"] = min(p["pg_max"], p["pg"] + curacion)
    c.participantes[idx] = p
    db.commit()
    return {"participante": p["nombre"], "pg_restantes": p["pg"], "pg_max": p["pg_max"]}


@router.post("/{combate_id}/add-participant")
def agregar_participante(combate_id: int, body: ParticipanteIn, usuario: UsuarioDB = Depends(obtener_usuario_actual), db: Session = Depends(get_db)):
    c = db.query(CombateDB).filter(CombateDB.id == combate_id, CombateDB.usuario_id == usuario.id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Combate no encontrado")
    p = body.model_dump()
    c.participantes.append(p)
    c.participantes.sort(key=lambda x: x["iniciativa"], reverse=True)
    db.commit()
    return {"participantes": c.participantes}


@router.post("/{combate_id}/end")
def terminar_combate(combate_id: int, usuario: UsuarioDB = Depends(obtener_usuario_actual), db: Session = Depends(get_db)):
    c = db.query(CombateDB).filter(CombateDB.id == combate_id, CombateDB.usuario_id == usuario.id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Combate no encontrado")
    c.activo = False
    db.commit()
    return {"mensaje": "Combate terminado"}
