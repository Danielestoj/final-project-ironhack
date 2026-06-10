from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException
from langchain_core.messages import HumanMessage
from pydantic import BaseModel

from auth.jwt import obtener_usuario_actual
from models.usuario import UsuarioDB
from agente import agente, agente_simple, get_collection_names

router = APIRouter(prefix="/api", tags=["IA"])
UsuarioActual = Annotated[UsuarioDB, Depends(obtener_usuario_actual)]


class MensajeRequest(BaseModel):
    session_id: str
    message: str
    game_slug: str = "dnd"


class ChatInput(BaseModel):
    message: str
    session_id: str = "default"
    game_slug: str = "dnd"


class ChatResponse(BaseModel):
    response: str
    session_id: str
    sources: list[str] = []


@router.post("/chat", response_model=ChatResponse)
def chat(body: MensajeRequest, usuario: UsuarioActual):
    config = {"configurable": {"thread_id": body.session_id}}
    try:
        resultado = agente.invoke(
            {"mensajes": [HumanMessage(content=body.message)], "game_slug": body.game_slug},
            config=config
        )
        return ChatResponse(
            response=resultado["mensajes"][-1].content,
            session_id=body.session_id,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error del agente: {str(e)}")


@router.post("/chat/simple")
def chat_simple(body: ChatInput, usuario: UsuarioActual):
    respuesta = agente_simple.chat(
        pregunta=body.message,
        session_id=body.session_id,
        game_slug=body.game_slug,
    )
    return ChatResponse(
        response=respuesta["respuesta"],
        session_id=body.session_id,
        sources=respuesta.get("fuentes", []),
    )


@router.get("/chat/history/{session_id}")
def historial(session_id: str, usuario: UsuarioActual):
    from agente import HISTORIAL
    historial_data = HISTORIAL.get(session_id, [])
    return {"session_id": session_id, "historial": historial_data}


@router.delete("/chat/{session_id}")
def limpiar_sesion(session_id: str, usuario: UsuarioActual):
    from agente import HISTORIAL
    if session_id in HISTORIAL:
        del HISTORIAL[session_id]
    return {"mensaje": f"Sesión {session_id} cerrada"}
