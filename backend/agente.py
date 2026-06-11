import os
import json
import random
import hashlib
import traceback
from datetime import datetime
from typing import TypedDict, Annotated, Sequence, Optional, Any

from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, AIMessage, ToolMessage
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from config import settings
from database import SessionLocal
from models.documento import DocumentoChunk
from sqlalchemy import text
from openai import OpenAI
import operator


# ─── OpenAI client (Groq backend) ───────────────────────────────────────

client = OpenAI(
    base_url=settings.LLM_BASE_URL,
    api_key=settings.LLM_API_KEY,
)


# ─── pgvector RAG (game‑aware) ────────────────────────────────────────────

EMBED_DIM = 384

_embedder = None


def _get_embedder():
    global _embedder
    if _embedder is None:
        from fastembed import TextEmbedding
        _embedder = TextEmbedding(model_name="all-MiniLM-L6-v2")
    return _embedder


def _embed_text(texto: str) -> list[float]:
    emb = list(_get_embedder().embed([texto]))[0]
    return list(emb)


def _embed_texts(textos: list[str]) -> list[list[float]]:
    return [list(e) for e in _get_embedder().embed(textos)]


def recuperar_docs(pregunta: str, n: int = 3, game_slug: str = "dnd") -> str:
    try:
        query_vec = _embed_text(pregunta)
        db = SessionLocal()
        try:
            rows = db.execute(
                text("""
                    SELECT content, filename
                    FROM document_chunks
                    WHERE game_slug = :slug
                    ORDER BY embedding <=> :query_vec
                    LIMIT :n
                """),
                {"slug": game_slug, "query_vec": str(query_vec), "n": n},
            ).fetchall()
            if not rows:
                return ""
            fragmentos = []
            for row in rows:
                fragmentos.append(f"[{row.filename}]\n{row.content}")
            return "\n\n".join(fragmentos)
        finally:
            db.close()
    except Exception:
        return ""


def get_collection_names() -> list[str]:
    db = SessionLocal()
    try:
        rows = db.execute(
            text("SELECT DISTINCT game_slug FROM document_chunks ORDER BY game_slug")
        ).fetchall()
        return [f"doc_{r[0]}" for r in rows]
    except Exception:
        return []
    finally:
        db.close()


# ─── Tools (Plain Python) ────────────────────────────────────────────────

TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "tirar_dado",
            "description": "Tira dados con notacion de D&D. Ejemplos: '1d20', '2d6', '1d20+5', '3d8+2'.",
            "parameters": {
                "type": "object",
                "properties": {
                    "formula": {
                        "type": "string",
                        "description": "Formula de dados, ej: 1d20, 2d6, 1d20+5",
                    }
                },
                "required": ["formula"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "buscar_hechizo",
            "description": "Busca informacion de un hechizo por nombre. Ejemplo: 'bola de fuego', 'curar heridas'.",
            "parameters": {
                "type": "object",
                "properties": {
                    "nombre": {
                        "type": "string",
                        "description": "Nombre del hechizo",
                    }
                },
                "required": ["nombre"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "buscar_condicion",
            "description": "Busca informacion de una condicion de D&D. Ejemplo: 'cegado', 'envenenado'.",
            "parameters": {
                "type": "object",
                "properties": {
                    "nombre": {
                        "type": "string",
                        "description": "Nombre de la condicion",
                    }
                },
                "required": ["nombre"],
            },
        },
    },
]


def tirar_dado(formula: str) -> str:
    import re
    match = re.match(r"^(\d+)d(\d+)(?:\s*([+-])\s*(\d+))?$", formula.strip().lower())
    if not match:
        return "Formato invalido. Usa notacion como '1d20', '2d6', '1d20+5'."
    cantidad = int(match.group(1))
    caras = int(match.group(2))
    if cantidad < 1 or caras < 2:
        return "La cantidad debe ser >= 1 y las caras >= 2."
    if cantidad > 100:
        return "Demasiados dados (maximo 100)."
    if caras > 1000:
        return "Demasiadas caras (maximo 1000)."
    tiradas = [random.randint(1, caras) for _ in range(cantidad)]
    total = sum(tiradas)
    if match.group(3) and match.group(4):
        mod = int(match.group(4))
        if match.group(3) == "+":
            total += mod
        else:
            total -= mod
        return f"Resultados: {tiradas} {'+' if match.group(3) == '+' else '-'} {mod} = **{total}**"
    return f"Resultados: {tiradas} = **{total}**"


def buscar_hechizo(nombre: str) -> str:
    hechizos = {
        "proyectil arcano": {"nivel": 0, "escuela": "Evocacion", "tiempo": "1 accion", "alcance": "120 pies", "duracion": "Instantanea", "descripcion": "Rayo de energia que impacta automaticamente."},
        "luz": {"nivel": 0, "escuela": "Evocacion", "tiempo": "1 accion", "alcance": "Toque", "duracion": "1 hora", "descripcion": "Ilumina un objeto durante una hora."},
        "armadura magica": {"nivel": 1, "escuela": "Abjuracion", "tiempo": "1 accion", "alcance": "Toque", "duracion": "8 horas", "descripcion": "Refuerza la defensa del objetivo."},
        "bola de fuego": {"nivel": 3, "escuela": "Evocacion", "tiempo": "1 accion", "alcance": "150 pies", "duracion": "Instantanea", "descripcion": "Explosion de fuego en area."},
        "curar heridas": {"nivel": 1, "escuela": "Abjuracion", "tiempo": "1 accion", "alcance": "Toque", "duracion": "Instantanea", "descripcion": "Restaura puntos de golpe."},
        "dormir": {"nivel": 1, "escuela": "Encantamiento", "tiempo": "1 accion", "alcance": "90 pies", "duracion": "1 minuto", "descripcion": "Sumerge criaturas en un sueno magico."},
        "telarana": {"nivel": 2, "escuela": "Conjuracion", "tiempo": "1 accion", "alcance": "60 pies", "duracion": "1 hora", "descripcion": "Cubre area con telaranas pegajosas."},
        "rayo": {"nivel": 0, "escuela": "Evocacion", "tiempo": "1 accion", "alcance": "100 pies", "duracion": "Instantanea", "descripcion": "Descarga electrica contra un objetivo."},
    }
    nl = nombre.lower().strip()
    if nl in hechizos:
        h = hechizos[nl]
        return f"**{nombre.title()}** - Nivel {h['nivel']}, {h['escuela']}\nTiempo: {h['tiempo']} | Alcance: {h['alcance']} | Duracion: {h['duracion']}\n{h['descripcion']}"
    similares = [k for k in hechizos if nl in k or any(w in k for w in nl.split())]
    if similares:
        return f"Hechizo no encontrado. Quizas quisiste decir: {', '.join(s.title() for s in similares)}"
    return f"Hechizo '{nombre}' no encontrado en el SRD basico."


def buscar_condicion(nombre: str) -> str:
    condiciones = {
        "cegado": "No puedes ver. Fallas pruebas que requieran vista. Ataques contra ti tienen ventaja, tus ataques tienen desventaja.",
        "hechizado": "No puedes atacar al hechizador. El tiene ventaja en pruebas sociales contra ti.",
        "ensordecido": "No puedes oir. Fallas pruebas que requieran oido.",
        "asustado": "Desventaja en pruebas y ataques mientras el origen del miedo este en linea de vision.",
        "agarrado": "Velocidad 0. No puedes beneficiarte de bonificaciones a la velocidad.",
        "inmovilizado": "Velocidad 0. Desventaja en salvaciones de Destreza. Ataques contra ti tienen ventaja.",
        "paralizado": "Incapacitado. No puedes moverte ni hablar. Fallas salvaciones de Fuerza y Destreza. Ataques cuerpo a cuerpo son criticos.",
        "petrificado": "Transformado en piedra. Incapacitado. Resistente a todo dano.",
        "envenenado": "Desventaja en tiradas de ataque y pruebas de habilidad.",
        "derribado": "Desventaja en ataques. Ataques cuerpo a cuerpo contra ti tienen ventaja, a distancia tienen desventaja.",
        "inconsciente": "Incapacitado. Sueltas lo que sostienes. Caes al suelo. Fallas salvaciones de Fuerza y Destreza. Ataques a 5 pies son criticos.",
    }
    nl = nombre.lower().strip()
    if nl in condiciones:
        return f"**{nombre.title()}**: {condiciones[nl]}"
    disponibles = ", ".join(c.title() for c in condiciones)
    return f"Condicion '{nombre}' no encontrada. Condiciones disponibles: {disponibles}"


TOOL_MAP = {
    "tirar_dado": tirar_dado,
    "buscar_hechizo": buscar_hechizo,
    "buscar_condicion": buscar_condicion,
}


# ─── Message conversion helpers ──────────────────────────────────────────

def _lc_to_openai(messages: list[BaseMessage]) -> list[dict]:
    result = []
    for m in messages:
        if isinstance(m, SystemMessage):
            result.append({"role": "system", "content": m.content})
        elif isinstance(m, HumanMessage):
            result.append({"role": "user", "content": m.content})
        elif isinstance(m, AIMessage):
            msg = {"role": "assistant", "content": m.content or ""}
            if hasattr(m, "tool_calls") and m.tool_calls:
                msg["tool_calls"] = [
                    {
                        "id": tc["id"],
                        "type": "function",
                        "function": {
                            "name": tc["name"],
                            "arguments": json.dumps(tc["args"]) if isinstance(tc["args"], dict) else tc["args"],
                        },
                    }
                    for tc in m.tool_calls
                ]
            result.append(msg)
        elif isinstance(m, ToolMessage):
            result.append({
                "role": "tool",
                "tool_call_id": m.tool_call_id,
                "content": m.content,
            })
        else:
            result.append({"role": "user", "content": str(m.content)})
    return result


def _openai_to_lc(msg: dict) -> BaseMessage:
    role = msg.get("role", "")
    content = msg.get("content", "") or ""
    if role == "assistant":
        tool_calls_data = msg.get("tool_calls")
        if tool_calls_data:
            lc_tool_calls = []
            for tc in tool_calls_data:
                fn = tc.get("function", {})
                args_str = fn.get("arguments", "{}")
                try:
                    args = json.loads(args_str) if isinstance(args_str, str) else args_str
                except json.JSONDecodeError:
                    args = {}
                lc_tool_calls.append({
                    "id": tc.get("id", ""),
                    "name": fn.get("name", ""),
                    "args": args,
                })
            return AIMessage(content=content, tool_calls=lc_tool_calls)
        return AIMessage(content=content)
    elif role == "tool":
        return ToolMessage(content=content, tool_call_id=msg.get("tool_call_id", ""))
    elif role == "system":
        return SystemMessage(content=content)
    else:
        return HumanMessage(content=content)


# ─── LangGraph Agent ─────────────────────────────────────────────────────

class EstadoDnD(TypedDict):
    mensajes: Annotated[Sequence[BaseMessage], operator.add]
    game_slug: str


def nodo_llm(estado: EstadoDnD) -> dict:
    ultimo_humano = next(
        (m.content for m in reversed(estado["mensajes"]) if isinstance(m, HumanMessage)),
        ""
    )
    slug = estado.get("game_slug", "dnd")
    contexto = recuperar_docs(ultimo_humano, game_slug=slug)

    system_text = f"""Eres un asistente experto en el juego de rol.
Responde preguntas sobre reglas, contenido y mecanicas usando el contexto proporcionado.
Usa las herramientas disponibles para tirar dados, buscar hechizos y consultar condiciones.

Contexto de reglas:
{contexto}

IMPORTANTE: Cuando uses informacion del contexto, DEBES citar la fuente entre corchetes al final de la frase. Ejemplo: "Segun las reglas de combate, una accion de ataque permite realizar un unico ataque [PHB - Acciones de Combate]".
Si no tienes informacion suficiente, dilo claramente. No inventes datos."""

    openai_messages = _lc_to_openai([SystemMessage(content=system_text)] + list(estado["mensajes"]))

    try:
        resp = client.chat.completions.create(
            model=settings.LLM_MODEL,
            messages=openai_messages,
            tools=TOOL_DEFINITIONS,
            temperature=0,
        )
    except Exception as e:
        error_msg = f"Error del LLM: {str(e)}\n{traceback.format_exc()}"
        return {"mensajes": [AIMessage(content=f"Lo siento, ocurrio un error al procesar tu solicitud. Detalle: {str(e)}")]}

    choice = resp.choices[0]
    msg = choice.message

    lc_msg = _openai_to_lc({
        "role": "assistant",
        "content": msg.content or "",
        "tool_calls": [
            {
                "id": tc.id,
                "function": {
                    "name": tc.function.name,
                    "arguments": tc.function.arguments,
                },
            }
            for tc in (msg.tool_calls or [])
        ],
    })

    return {"mensajes": [lc_msg]}


def debe_continuar(estado: EstadoDnD) -> str:
    ultimo = estado["mensajes"][-1]
    if isinstance(ultimo, AIMessage) and hasattr(ultimo, "tool_calls") and ultimo.tool_calls:
        return "usar_tool"
    return END


def nodo_tools(estado: EstadoDnD) -> dict:
    ultimo = estado["mensajes"][-1]
    if not isinstance(ultimo, AIMessage) or not hasattr(ultimo, "tool_calls") or not ultimo.tool_calls:
        return {"mensajes": []}

    nuevos = []
    for tc in ultimo.tool_calls:
        nombre = tc["name"]
        args = tc["args"]
        fn = TOOL_MAP.get(nombre)
        if fn:
            try:
                resultado = fn(**args)
            except Exception as e:
                resultado = f"Error al ejecutar {nombre}: {str(e)}"
        else:
            resultado = f"Herramienta '{nombre}' no encontrada."
        nuevos.append(ToolMessage(content=resultado, tool_call_id=tc["id"]))

    return {"mensajes": nuevos}


grafo = StateGraph(EstadoDnD)
grafo.add_node("llm", nodo_llm)
grafo.add_node("tools", nodo_tools)
grafo.set_entry_point("llm")
grafo.add_conditional_edges("llm", debe_continuar, {"usar_tool": "tools", END: END})
grafo.add_edge("tools", "llm")

checkpointer = MemorySaver()
agente = grafo.compile(checkpointer=checkpointer)


# ─── Simple RAG Chatbot (fallback) ────────────────────────────────────────

HISTORIAL = {}


def recuperar_fragmentos(pregunta: str, n_resultados: int = 5, game_slug: str = "dnd"):
    try:
        query_vec = _embed_text(pregunta)
        db = SessionLocal()
        try:
            rows = db.execute(
                text("""
                    SELECT content, filename, chunk_id
                    FROM document_chunks
                    WHERE game_slug = :slug
                    ORDER BY embedding <=> :query_vec
                    LIMIT :n
                """),
                {"slug": game_slug, "query_vec": str(query_vec), "n": n_resultados},
            ).fetchall()
            documentos = [r.content for r in rows]
            metadatos = [{"filename": r.filename, "chunk_id": r.chunk_id} for r in rows]
            return documentos, metadatos
        finally:
            db.close()
    except Exception:
        return [], []


class AgenteSimple:
    def chat(self, pregunta: str, session_id: str, game_slug: str = "dnd") -> dict:
        documentos, metadatos = recuperar_fragmentos(pregunta, game_slug=game_slug)
        if not documentos:
            respuesta = "No tengo informacion sobre eso en mis documentos."
            HISTORIAL.setdefault(session_id, []).append({"rol": "user", "contenido": pregunta})
            HISTORIAL[session_id].append({"rol": "assistant", "contenido": respuesta})
            return {"respuesta": respuesta, "fuentes": [], "session_id": session_id, "fragmentos_usados": 0}

        contexto = ""
        fuentes = set()
        for doc, meta in zip(documentos, metadatos):
            filename = meta.get("filename", "desconocido") if meta else "desconocido"
            chunk_id = meta.get("chunk_id", 0) if meta else 0
            contexto += f"[{filename} - chunk {chunk_id}]\n{doc}\n\n"
            fuentes.add(filename)

        hist_text = self._construir_historial(session_id)
        system_prompt = "Eres un asistente experto en juegos de rol. Responde EXCLUSIVAMENTE usando el contexto proporcionado. No inventes datos. IMPORTANTE: Cuando uses informacion del contexto, DEBES citar la fuente entre corchetes. Ejemplo: 'Segun el manual [PHB], el ataque de oportunidad...'. " + (f"Fuentes disponibles: {', '.join(fuentes)}." if fuentes else "")
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Contexto:\n{contexto}\n\nHistorial:\n{hist_text}\n\nPregunta:\n{pregunta}"},
        ]
        try:
            resp = client.chat.completions.create(
                model=settings.LLM_MODEL, messages=messages, temperature=0.2
            )
            respuesta = resp.choices[0].message.content.strip()
        except Exception:
            contexto_resumen = "\n".join(documentos)[:500]
            respuesta = f"Basado en los documentos:\n{contexto_resumen}\n\nFuentes: {', '.join(fuentes)}"

        HISTORIAL.setdefault(session_id, []).append({"rol": "user", "contenido": pregunta})
        HISTORIAL[session_id].append({"rol": "assistant", "contenido": respuesta})
        return {"respuesta": respuesta, "fuentes": list(fuentes), "session_id": session_id, "fragmentos_usados": len(documentos)}

    def _construir_historial(self, session_id: str) -> str:
        historial = HISTORIAL.get(session_id, [])
        return "\n".join(
            f"{'Usuario' if t['rol'] == 'user' else 'Asistente'}: {t['contenido'][:200]}"
            for t in historial[-6:]
        )


agente_simple = AgenteSimple()
