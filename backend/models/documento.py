from sqlalchemy import Column, Integer, String, Text, Index
from pgvector.sqlalchemy import Vector
from database import Base


class DocumentoChunk(Base):
    __tablename__ = "document_chunks"
    id = Column(Integer, primary_key=True, index=True)
    chunk_id = Column(String(200), unique=True, index=True, nullable=False)
    game_slug = Column(String(50), index=True, nullable=False)
    filename = Column(String(200), default="")
    content = Column(Text, default="")
    embedding = Column(Vector(384))
    hash = Column(String(64), default="")

    __table_args__ = (
        Index("ix_docs_slug_file", "game_slug", "filename"),
    )
