import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

if os.path.exists(".env"):
    load_dotenv()

_DATABASE_URL = os.getenv("DATABASE_URL")

# Railway inyecta PG* individuales si no hay DATABASE_URL
if not _DATABASE_URL:
    pg_host = os.getenv("PGHOST") or os.getenv("PGHOSTADDR")
    pg_port = os.getenv("PGPORT", "5432")
    pg_user = os.getenv("PGUSER", "postgres")
    pg_pass = os.getenv("PGPASSWORD", "")
    pg_db = os.getenv("PGDATABASE", "postgres")
    if pg_host:
        _DATABASE_URL = f"postgresql://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_db}"

if not _DATABASE_URL:
    _DATABASE_URL = "postgresql://postgres:ironhack@localhost:5432/rol_app"

DATABASE_URL = _DATABASE_URL
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
