"""Tests para la API del Asistente D&D."""

import models.personaje  # noqa: F401 — register models for Base
import models.usuario  # noqa: F401
import models.combate  # noqa: F401
import models.hechizo  # noqa: F401
import models.objeto  # noqa: F401

from fastapi.testclient import TestClient
from database import engine, Base
from sqlalchemy import text

# Ensure fresh schema for hechizos/objetos (column type may have changed)
with engine.connect() as conn:
    conn.execute(text("DROP TABLE IF EXISTS hechizos CASCADE"))
    conn.execute(text("DROP TABLE IF EXISTS objetos CASCADE"))
    conn.commit()
Base.metadata.create_all(bind=engine)

from seed_db import seed_all
seed_all()

from main import app
client = TestClient(app)

TEST_EMAIL = "test_integration@test.com"
TEST_PASS = "testpass123"
_token = None


def _get_token():
    global _token
    if _token:
        return _token
    resp = client.post("/auth/login", json={
        "email": TEST_EMAIL, "password": TEST_PASS,
    })
    if resp.status_code == 200:
        _token = resp.json()["access_token"]
        return _token
    resp = client.post("/auth/registro", json={
        "email": TEST_EMAIL, "password": TEST_PASS, "nombre": "Test",
    })
    if resp.status_code == 201:
        _token = resp.json()["access_token"]
        return _token
    resp = client.post("/auth/login", json={
        "email": "admin@admin.com", "password": "12345678",
    })
    if resp.status_code == 200:
        _token = resp.json()["access_token"]
        return _token
    return None


def _auth_headers():
    t = _get_token()
    return {"Authorization": f"Bearer {t}"} if t else {}


# ─── Health & Root ───

def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_root():
    resp = client.get("/")
    assert resp.status_code == 200
    data = resp.json()
    assert "nombre" in data
    assert "endpoints" in data


# ─── Auth ───

def test_login():
    resp = client.post("/auth/login", json={
        "email": "admin@admin.com", "password": "12345678",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data


def test_auth_required():
    assert client.get("/personajes/").status_code == 401
    assert client.post("/api/chat", json={"session_id": "t", "message": "t"}).status_code == 401


# ─── Validation errors ───

def test_validation_error():
    resp = client.post("/auth/registro", json={"email": "bad"})
    assert resp.status_code == 422
    data = resp.json()
    assert "error" in data
    assert "detalle" in data


# ─── Data endpoints ───

def test_hechizos():
    resp = client.get("/hechizos/", headers=_auth_headers())
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_not_found():
    resp = client.get("/personajes/99999", headers=_auth_headers())
    assert resp.status_code == 404


# ─── Dice rolls ───

def test_dice_roll_endpoint():
    resp = client.get("/api/metrics/dice-last-10", headers=_auth_headers())
    assert resp.status_code == 200
    assert "rolls" in resp.json()


# ─── Random character ───

def test_random_character():
    resp = client.post("/personajes/random", headers=_auth_headers())
    assert resp.status_code == 201
    data = resp.json()
    assert "nombre" in data
    assert "raza" in data
    assert "clase" in data


# ─── Encuentro generator ───

def test_encuentro_generator():
    resp = client.post("/api/encuentros/generar", headers=_auth_headers(), json={
        "jugadores": 4, "nivel": 3, "dificultad": "media",
    })
    assert resp.status_code == 200
    assert len(resp.json()["encuentro"]) > 0


# ─── Combate (create table first) ───

def _ensure_combate_table():
    from models.combate import CombateDB
    from database import Base, engine
    Base.metadata.create_all(bind=engine, tables=[CombateDB.__table__])


def _create_test_combate():
    _ensure_combate_table()
    return client.post("/api/combate/", headers=_auth_headers(), json={
        "nombre": "Test Combat",
        "participantes": [
            {"nombre": "Hero", "iniciativa": 18, "pg": 20, "pg_max": 20, "tipo": "pj", "condiciones": []},
            {"nombre": "Goblin", "iniciativa": 12, "pg": 7, "pg_max": 7, "tipo": "enemigo", "condiciones": []},
        ],
    })


def test_combate_crear():
    resp = _create_test_combate()
    assert resp.status_code == 200
    data = resp.json()
    assert data["ronda"] == 1
    assert len(data["participantes"]) == 2


def test_combate_next_turn():
    resp = _create_test_combate()
    cid = resp.json()["id"]
    resp = client.post(f"/api/combate/{cid}/next", headers=_auth_headers())
    assert resp.status_code == 200
    assert resp.json()["turno_actual"] == 1


def test_combate_damage():
    resp = _create_test_combate()
    cid = resp.json()["id"]
    resp = client.post(f"/api/combate/{cid}/damage?idx=0&dano=5", headers=_auth_headers())
    assert resp.status_code == 200
    assert resp.json()["pg_restantes"] == 15
