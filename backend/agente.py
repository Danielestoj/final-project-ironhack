import os
import json
import random
import hashlib
from datetime import datetime
from typing import TypedDict, Annotated, Sequence, Optional

from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver
import chromadb
from chromadb.utils import embedding_functions
from config import settings
import operator


# ─── ChromaDB RAG ──────────────────────────────────────────────────────────

chroma_client = chromadb.PersistentClient(path="./chroma_db")
try:
    collection = chroma_client.get_collection(name="documentos")
except Exception:
    collection = None

embedding_fn = embedding_functions.DefaultEmbeddingFunction()


def recuperar_docs(pregunta: str, n: int = 3) -> str:
    if collection is None:
        return ""
    try:
        resultados = collection.query(query_texts=[pregunta], n_results=n)
        if not resultados["documents"] or not resultados["documents"][0]:
            return ""
        fragmentos = []
        for doc, meta in zip(resultados["documents"][0], resultados["metadatas"][0]):
            source = meta.get("filename", "desconocido") if meta else "desconocido"
            fragmentos.append(f"[{source}]\n{doc}")
        return "\n\n".join(fragmentos)
    except Exception:
        return ""


# ─── LangGraph Agent ───────────────────────────────────────────────────────

class EstadoDnD(TypedDict):
    mensajes: Annotated[Sequence[BaseMessage], operator.add]


@tool
def tirar_dado(formula: str) -> str:
    """Tira dados con notación de D&D. Ejemplos: '1d20', '2d6', '1d20+5', '3d8+2'."""
    import re
    match = re.match(r"^(\d+)d(\d+)(?:\s*([+-])\s*(\d+))?$", formula.strip().lower())
    if not match:
        return "Formato inválido. Usa notación como '1d20', '2d6', '1d20+5'."
    cantidad = int(match.group(1))
    caras = int(match.group(2))
    if cantidad < 1 or caras < 2:
        return "La cantidad debe ser >= 1 y las caras >= 2."
    if cantidad > 100:
        return "Demasiados dados (máximo 100)."
    if caras > 1000:
        return "Demasiadas caras (máximo 1000)."
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


@tool
def buscar_hechizo(nombre: str) -> str:
    """Busca información de un hechizo por nombre. Ejemplo: 'bola de fuego', 'curar heridas'."""
    hechizos = {
        "proyectil arcano": {"nivel": 0, "escuela": "Evocación", "tiempo": "1 acción", "alcance": "120 pies", "duracion": "Instantánea", "descripcion": "Rayo de energía que impacta automáticamente."},
        "luz": {"nivel": 0, "escuela": "Evocación", "tiempo": "1 acción", "alcance": "Toque", "duracion": "1 hora", "descripcion": "Ilumina un objeto durante una hora."},
        "armadura mágica": {"nivel": 1, "escuela": "Abjuración", "tiempo": "1 acción", "alcance": "Toque", "duracion": "8 horas", "descripcion": "Refuerza la defensa del objetivo."},
        "bola de fuego": {"nivel": 3, "escuela": "Evocación", "tiempo": "1 acción", "alcance": "150 pies", "duracion": "Instantánea", "descripcion": "Explosión de fuego en área."},
        "curar heridas": {"nivel": 1, "escuela": "Abjuración", "tiempo": "1 acción", "alcance": "Toque", "duracion": "Instantánea", "descripcion": "Restaura puntos de golpe."},
        "dormir": {"nivel": 1, "escuela": "Encantamiento", "tiempo": "1 acción", "alcance": "90 pies", "duracion": "1 minuto", "descripcion": "Sumerge criaturas en un sueño mágico."},
        "telaraña": {"nivel": 2, "escuela": "Conjuración", "tiempo": "1 acción", "alcance": "60 pies", "duracion": "1 hora", "descripcion": "Cubre área con telarañas pegajosas."},
        "rayo": {"nivel": 0, "escuela": "Evocación", "tiempo": "1 acción", "alcance": "100 pies", "duracion": "Instantánea", "descripcion": "Descarga eléctrica contra un objetivo."},
    }
    nl = nombre.lower().strip()
    if nl in hechizos:
        h = hechizos[nl]
        return f"**{nombre.title()}** — Nivel {h['nivel']}, {h['escuela']}\nTiempo: {h['tiempo']} | Alcance: {h['alcance']} | Duración: {h['duracion']}\n{h['descripcion']}"
    similares = [k for k in hechizos if nl in k or any(w in k for w in nl.split())]
    if similares:
        return f"Hechizo no encontrado. Quizás quisiste decir: {', '.join(s.title() for s in similares)}"
    return f"Hechizo '{nombre}' no encontrado en el SRD básico."


@tool
def buscar_condicion(nombre: str) -> str:
    """Busca información de una condición de D&D. Ejemplo: 'cegado', 'envenenado'."""
    condiciones = {
        "cegado": "No puedes ver. Fallas pruebas que requieran vista. Ataques contra ti tienen ventaja, tus ataques tienen desventaja.",
        "hechizado": "No puedes atacar al hechizador. Él tiene ventaja en pruebas sociales contra ti.",
        "ensordecido": "No puedes oír. Fallas pruebas que requieran oído.",
        "asustado": "Desventaja en pruebas y ataques mientras el origen del miedo esté en línea de visión.",
        "agarrado": "Velocidad 0. No puedes beneficiarte de bonificaciones a la velocidad.",
        "inmovilizado": "Velocidad 0. Desventaja en salvaciones de Destreza. Ataques contra ti tienen ventaja.",
        "paralizado": "Incapacitado. No puedes moverte ni hablar. Fallas salvaciones de Fuerza y Destreza. Ataques cuerpo a cuerpo son críticos.",
        "petrificado": "Transformado en piedra. Incapacitado. Resistente a todo daño.",
        "envenenado": "Desventaja en tiradas de ataque y pruebas de habilidad.",
        "derribado": "Desventaja en ataques. Ataques cuerpo a cuerpo contra ti tienen ventaja, a distancia tienen desventaja.",
        "inconsciente": "Incapacitado. Sueltas lo que sostienes. Caes al suelo. Fallas salvaciones de Fuerza y Destreza. Ataques a 5 pies son críticos.",
    }
    nl = nombre.lower().strip()
    if nl in condiciones:
        return f"**{nombre.title()}**: {condiciones[nl]}"
    disponibles = ", ".join(c.title() for c in condiciones)
    return f"Condición '{nombre}' no encontrada. Condiciones disponibles: {disponibles}"


tools = [tirar_dado, buscar_hechizo, buscar_condicion]

modelo = ChatOpenAI(
    model=settings.LLM_MODEL,
    base_url=settings.LLM_BASE_URL,
    api_key=settings.LLM_API_KEY,
    temperature=0
)
modelo_con_tools = modelo.bind_tools(tools)


def nodo_llm(estado: EstadoDnD) -> dict:
    ultimo_humano = next(
        (m.content for m in reversed(estado["mensajes"]) if isinstance(m, HumanMessage)),
        ""
    )
    contexto = recuperar_docs(ultimo_humano)

    system = SystemMessage(content=f"""Eres un asistente experto en Dungeons & Dragons 5e (SRD 5.1).
Responde preguntas sobre reglas, hechizos, condiciones, clases y enemigos usando el contexto proporcionado.
Usa las herramientas disponibles para tirar dados, buscar hechizos y consultar condiciones.

Contexto de reglas:
{contexto}

Si no tienes información suficiente, dilo claramente. No inventes datos.""")

    mensajes_con_system = [system] + list(estado["mensajes"])
    respuesta = modelo_con_tools.invoke(mensajes_con_system)
    return {"mensajes": [respuesta]}


def debe_continuar(estado: EstadoDnD) -> str:
    ultimo = estado["mensajes"][-1]
    if hasattr(ultimo, "tool_calls") and ultimo.tool_calls:
        return "usar_tool"
    return END


nodo_tools = ToolNode(tools)

grafo = StateGraph(EstadoDnD)
grafo.add_node("llm", nodo_llm)
grafo.add_node("tools", nodo_tools)
grafo.set_entry_point("llm")
grafo.add_conditional_edges("llm", debe_continuar, {"usar_tool": "tools", END: END})
grafo.add_edge("tools", "llm")

checkpointer = MemorySaver()
agente = grafo.compile(checkpointer=checkpointer)


# ─── Simple RAG Chatbot (fallback sin LLM local) ──────────────────────────────

from openai import OpenAI

client_openai = OpenAI(
    base_url=settings.LLM_BASE_URL,
    api_key=settings.LLM_API_KEY
)

HISTORIAL = {}


def recuperar_fragmentos(pregunta: str, n_resultados: int = 5):
    if collection is None:
        return [], []
    try:
        resultados = collection.query(query_texts=[pregunta], n_results=n_resultados)
        documentos = resultados["documents"][0] if resultados["documents"] else []
        metadatos = resultados["metadatas"][0] if resultados["metadatas"] else []
        return documentos, metadatos
    except Exception:
        return [], []


class AgenteSimple:
    def chat(self, pregunta: str, session_id: str) -> dict:
        documentos, metadatos = recuperar_fragmentos(pregunta)
        if not documentos:
            respuesta = "No tengo información sobre eso en mis documentos."
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
        system_prompt = "Eres un asistente experto en Dragones y Mazmorras. Responde EXCLUSIVAMENTE usando el contexto proporcionado. No inventes datos."
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Contexto:\n{contexto}\n\nHistorial:\n{hist_text}\n\nPregunta:\n{pregunta}"},
        ]
        try:
            resp = client_openai.chat.completions.create(
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
