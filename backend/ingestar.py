import os
import hashlib
from database import SessionLocal
from models.documento import DocumentoChunk
from sqlalchemy import text

GAMES_DIR = "games"


def chunk_text(texto, size=500):
    parrafos = texto.split("\n\n")
    chunks = []
    actual = ""
    for p in parrafos:
        if len(actual) + len(p) < size:
            actual += p + "\n\n"
        else:
            chunks.append(actual.strip())
            actual = p + "\n\n"
    if actual:
        chunks.append(actual.strip())
    return chunks


def hash_texto(texto):
    return hashlib.md5(texto.encode()).hexdigest()


_embedder = None


def _get_embedder():
    global _embedder
    if _embedder is None:
        from fastembed import TextEmbedding
        _embedder = TextEmbedding(model_name="all-MiniLM-L6-v2")
    return _embedder


def _embed_texts(textos: list[str]) -> list[list[float]]:
    return [list(e) for e in _get_embedder().embed(textos)]


def ingestar_game(slug: str):
    """Ingest docs from games/{slug}/docs/*.txt into pgvector (document_chunks)."""
    docs_dir = os.path.join(GAMES_DIR, slug, "docs")
    if not os.path.isdir(docs_dir):
        print(f"  -> No docs dir for {slug}, skipping")
        return

    db = SessionLocal()
    try:
        documentos = []
        for filename in sorted(os.listdir(docs_dir)):
            if filename.endswith(".txt") and not filename.startswith("processing"):
                filepath = os.path.join(docs_dir, filename)
                with open(filepath, "r", encoding="utf-8") as f:
                    contenido = f.read()
                    documentos.append((filename, contenido))
                print(f"    -> {filename}")

        print(f"  Indexing {len(documentos)} documents for [{slug}]...")
        total_chunks = 0
        new_chunks = []
        for filename, contenido in documentos:
            chunks = chunk_text(contenido)
            for i, ct in enumerate(chunks):
                chunk_id = f"{slug}_{filename}_chunk_{i}"
                h = hash_texto(ct)

                existing = db.query(DocumentoChunk).filter(
                    DocumentoChunk.chunk_id == chunk_id
                ).first()
                if existing:
                    if existing.hash == h:
                        continue
                    else:
                        db.delete(existing)

                new_chunks.append({
                    "chunk_id": chunk_id,
                    "game_slug": slug,
                    "filename": filename,
                    "content": ct,
                    "hash": h,
                })
                total_chunks += 1

        if new_chunks:
            texts = [c["content"] for c in new_chunks]
            embeddings = _embed_texts(texts)
            for chunk_data, emb in zip(new_chunks, embeddings):
                db.add(DocumentoChunk(
                    chunk_id=chunk_data["chunk_id"],
                    game_slug=chunk_data["game_slug"],
                    filename=chunk_data["filename"],
                    content=chunk_data["content"],
                    hash=chunk_data["hash"],
                    embedding=emb,
                ))
            db.commit()

        print(f"  -> {total_chunks} chunks indexed for [{slug}]")
    finally:
        db.close()


def ingestar_todo():
    """Legacy: ingest docs/ into doc_dnd collection for backward compat."""
    ingestar_game("dnd")


if __name__ == "__main__":
    print("Ingesting all games...")
    for entry in os.listdir(GAMES_DIR):
        if os.path.isdir(os.path.join(GAMES_DIR, entry)):
            print(f"  Game: {entry}")
            ingestar_game(entry)
