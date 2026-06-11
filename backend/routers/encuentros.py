import json
import random
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from auth.jwt import obtener_usuario_actual

router = APIRouter(prefix="/api/encuentros", tags=["Encuentros"])

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
ENEMIGOS_FILE = DATA_DIR / "enemigos.json"
CLASES_FILE = DATA_DIR / "clases.json"

UMBRALES = {"facil": 0.5, "medio": 1.0, "dificil": 1.5, "mortal": 2.0}
XP_POR_NIVEL = {1: 25, 2: 50, 3: 75, 4: 125, 5: 250, 6: 300, 7: 350, 8: 450, 9: 550, 10: 600,
                11: 800, 12: 1000, 13: 1100, 14: 1250, 15: 1400, 16: 1600, 17: 2000, 18: 2200, 19: 2500, 20: 3300}


def _cargar_enemigos():
    if ENEMIGOS_FILE.exists():
        return json.loads(ENEMIGOS_FILE.read_text(encoding="utf-8"))
    return []


class EncuentroRequest(BaseModel):
    jugadores: int = 4
    nivel: int = 3
    dificultad: str = "media"
    tipo: str = ""


@router.post("/generar")
def generar_encuentro(body: EncuentroRequest, user: dict = Depends(obtener_usuario_actual)):
    enemigos = _cargar_enemigos()
    if not enemigos:
        raise HTTPException(status_code=500, detail="No hay datos de enemigos")

    presupuesto_xp = UMBRALES.get(body.dificultad, 1.0) * XP_POR_NIVEL.get(body.nivel, 100) * body.jugadores
    candidatos = []

    for e in enemigos:
        cr = e.get("cr", e.get("CR", 1))
        xp = e.get("xp", cr * 100)
        if body.tipo and body.tipo.lower() not in e.get("tipo", "").lower() and body.tipo.lower() not in e.get("nombre", "").lower():
            continue
        candidatos.append({"nombre": e.get("nombre", "?"), "cr": cr, "xp": xp, "tipo": e.get("tipo", e.get("tipo_criatura", ""))})

    if not candidatos:
        candidatos = [{"nombre": e.get("nombre", "?"), "cr": e.get("cr", e.get("CR", 1)),
                       "xp": e.get("xp", e.get("cr", e.get("CR", 1)) * 100),
                       "tipo": e.get("tipo", e.get("tipo_criatura", ""))} for e in enemigos[:5]]

    seleccionados = []
    restante = presupuesto_xp
    intentos = 0
    while restante > 0 and candidatos and intentos < 20:
        elegible = [c for c in candidatos if c["xp"] <= restante]
        if not elegible:
            if seleccionados:
                break
            elegible = candidatos
        c = random.choice(elegible)
        seleccionados.append(c)
        restante -= c["xp"]
        intentos += 1

    return {
        "encuentro": seleccionados,
        "presupuesto_xp": presupuesto_xp,
        "total_xp": sum(s["xp"] for s in seleccionados),
        "dificultad": body.dificultad,
        "nivel_grupo": body.nivel,
        "num_jugadores": body.jugadores,
    }
