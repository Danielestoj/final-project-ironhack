from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from services.metrics_service import metrics_service
from auth.jwt import obtener_usuario_actual as get_current_user

router = APIRouter(prefix="/api/metrics", tags=["metrics"])


class SpellView(BaseModel):
    nombre: str
    game_slug: str = "dnd"


class ChatQuery(BaseModel):
    texto: str
    game_slug: str = "dnd"


class SearchEvent(BaseModel):
    q: str = ""
    nivel: str = ""
    escuela: str = ""
    game_slug: str = "dnd"


@router.post("/spell-view")
def track_spell_view(data: SpellView, user: dict = Depends(get_current_user)):
    metrics_service.track_spell_view(data.nombre, data.game_slug)
    return {"ok": True}


@router.post("/chat-query")
def track_chat_query(data: ChatQuery, user: dict = Depends(get_current_user)):
    metrics_service.track_chat_query(data.texto, data.game_slug)
    return {"ok": True}


@router.post("/search")
def track_search(data: SearchEvent, user: dict = Depends(get_current_user)):
    metrics_service.track_search(data.q, data.nivel, data.escuela, data.game_slug)
    return {"ok": True}


@router.get("/dice-last-10")
def get_dice_rolls(user: dict = Depends(get_current_user)):
    return {"rolls": metrics_service.get_recent_dice_rolls(10)}


@router.get("/dashboard")
def get_dashboard(user: dict = Depends(get_current_user)):
    if user.rol != "admin":
        raise HTTPException(status_code=403, detail="Solo administradores")
    return metrics_service.get_dashboard()


@router.post("/save")
def save_metrics(user: dict = Depends(get_current_user)):
    if user.rol != "admin":
        raise HTTPException(status_code=403, detail="Solo administradores")
    return metrics_service.save_to_disk()
