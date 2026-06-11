from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from dotenv import load_dotenv
import os

from database import engine, Base, SessionLocal
from passlib.context import CryptContext


def _init_db_and_seed():
    import models.personaje  # noqa: F401 — register model for Base
    import models.usuario  # noqa: F401
    import models.combate  # noqa: F401
    import models.hechizo  # noqa: F401
    import models.objeto  # noqa: F401
    import models.documento  # noqa: F401
    from sqlalchemy import text
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        conn.commit()
    Base.metadata.create_all(bind=engine)
    from models.usuario import UsuarioDB
    db = SessionLocal()
    try:
        if not db.query(UsuarioDB).filter(UsuarioDB.email == "admin@admin.com").first():
            pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")
            db.add(UsuarioDB(
                id=1, email="admin@admin.com", nombre="Administrador",
                password_hash=pwd.hash("12345678"), rol="admin",
            ))
            db.commit()
    finally:
        db.close()
    from seed_db import seed_all
    seed_all()

    # Auto-ingestar documentos RAG si la tabla está vacía
    try:
        from models.documento import DocumentoChunk
        db2 = SessionLocal()
        try:
            if not db2.query(DocumentoChunk).filter(DocumentoChunk.game_slug == "dnd").first():
                from ingestar import ingestar_game
                print("  -> Ingestando documentos RAG para game dnd...")
                ingestar_game("dnd")
        finally:
            db2.close()
    except Exception as e:
        print(f"  -> Skip auto-ingest (pgvector no disponible): {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    _init_db_and_seed()
    yield


from routers import auth as auth_router
from routers import personajes as personajes_router
from routers import hechizos as hechizos_router
from routers import ia as ia_router
from routers import pdf as pdf_router
from routers import condiciones as condiciones_router
from routers import clases as clases_router
from routers import razas as razas_router
from routers import enemigos as enemigos_router
from routers import objetos as objetos_router
from routers import sync as sync_router
from routers import games as games_router
from routers import encuentros as encuentros_router
from routers import combate as combate_router
from routers import cleanup as cleanup_router
from routers import metrics as metrics_router

load_dotenv()

app = FastAPI(
    title="Asistente D&D",
    description="API del asistente inteligente para Dungeons & Dragons con IA integrada (LangGraph + RAG)",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail or "Error HTTP", "status_code": exc.status_code},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    errores = [
        {"campo": " → ".join(str(x) for x in e["loc"]), "mensaje": e["msg"]}
        for e in exc.errors()
    ]
    return JSONResponse(
        status_code=422,
        content={"error": "Error de validación", "detalle": errores},
    )


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"error": "Error interno del servidor", "detalle": str(exc)},
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
app.include_router(clases_router.router)
app.include_router(razas_router.router)
app.include_router(enemigos_router.router)
app.include_router(objetos_router.router)
app.include_router(sync_router.router)
app.include_router(games_router.router)
app.include_router(cleanup_router.router)
app.include_router(metrics_router.router)
app.include_router(encuentros_router.router)
app.include_router(combate_router.router)


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
            "clases": "/clases (GET)",
            "razas": "/razas (GET)",
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
