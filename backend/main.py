from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

from routers import auth as auth_router
from routers import personajes as personajes_router
from routers import hechizos as hechizos_router
from routers import ia as ia_router
from routers import pdf as pdf_router
from routers import condiciones as condiciones_router
from routers import clases_razas as clases_razas_router
from routers import enemigos as enemigos_router
from routers import objetos as objetos_router
from routers import sync as sync_router
from routers import games as games_router
from routers import cleanup as cleanup_router
from routers import metrics as metrics_router

load_dotenv()

app = FastAPI(
    title="Asistente D&D",
    description="API del asistente inteligente para Dungeons & Dragons con IA integrada (LangGraph + RAG)",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router)
app.include_router(personajes_router.router)
app.include_router(hechizos_router.router)
app.include_router(ia_router.router)
app.include_router(pdf_router.router)
app.include_router(condiciones_router.router)
app.include_router(clases_razas_router.router)
app.include_router(enemigos_router.router)
app.include_router(objetos_router.router)
app.include_router(sync_router.router)
app.include_router(games_router.router)
app.include_router(cleanup_router.router)
app.include_router(metrics_router.router)


@app.get("/")
def raiz():
    return {
        "nombre": "Asistente D&D",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "auth": "/auth/registro | /auth/login | /auth/perfil",
            "personajes": "/personajes (GET, POST, PUT, DELETE)",
            "hechizos": "/hechizos (GET)",
            "condiciones": "/condiciones (GET)",
            "clases_razas": "/clases-razas (GET)",
            "enemigos": "/enemigos (GET)",
            "objetos": "/objetos (GET)",
            "ia": "/api/chat | /api/chat/simple | /api/chat/history/{id}",
            "pdf_processor": "/api/pdf/check-pending | /api/pdf/process | /api/pdf/sync-to-db",
            "games": "/api/games (GET, POST)",
            "data_cleanup": "/api/data/cleanup (POST)",
            "metrics": "/api/metrics/dashboard (GET) | /api/metrics/save (POST)",
            "webhook": "/webhook/n8n",
        },
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/webhook/n8n")
def webhook_n8n(data: dict):
    return {
        "received": True,
        "data": data,
        "message": "Evento registrado para N8N",
    }
