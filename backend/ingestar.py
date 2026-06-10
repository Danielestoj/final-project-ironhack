import os
import hashlib
import chromadb
from chromadb.utils import embedding_functions

PERSIST_DIR = "./chroma_db"
GAMES_DIR = "games"

chroma_client = chromadb.PersistentClient(path=PERSIST_DIR)


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


def ingestar_game(slug: str):
    """Ingest docs from games/{slug}/docs/*.txt into ChromaDB collection doc_{slug}."""
    docs_dir = os.path.join(GAMES_DIR, slug, "docs")
    if not os.path.isdir(docs_dir):
        print(f"  -> No docs dir for {slug}, skipping")
        return

    collection = chroma_client.get_or_create_collection(
        name=f"doc_{slug}",
        embedding_function=embedding_functions.DefaultEmbeddingFunction(),
    )

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
    for filename, contenido in documentos:
        chunks = chunk_text(contenido)
        for i, chunk in enumerate(chunks):
            chunk_id = f"{slug}_{filename}_chunk_{i}"
            h = hash_texto(chunk)

            existente = collection.get(ids=[chunk_id])
            if existente["ids"]:
                if existente["metadatas"][0].get("hash") == h:
                    continue
                else:
                    collection.delete(ids=[chunk_id])

            collection.add(
                ids=[chunk_id],
                documents=[chunk],
                metadatas=[{"filename": filename, "chunk_id": i, "hash": h, "game_slug": slug}],
            )
            total_chunks += 1
    print(f"  -> {total_chunks} chunks indexed for [{slug}]")


def ingestar_todo():
    """Legacy: ingest docs/ into doc_dnd collection for backward compat."""
    ingestar_game("dnd")


if __name__ == "__main__":
    print("Ingesting all games...")
    for entry in os.listdir(GAMES_DIR):
        if os.path.isdir(os.path.join(GAMES_DIR, entry)):
            print(f"  Game: {entry}")
            ingestar_game(entry)
