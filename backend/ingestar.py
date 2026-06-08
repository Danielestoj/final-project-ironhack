import os
import hashlib
import chromadb
from chromadb.utils import embedding_functions

RUTA_DOCS = "docs/"
PERSIST_DIR = "./chroma_db"

print("Conectando a ChromaDB...")
chroma_client = chromadb.PersistentClient(path=PERSIST_DIR)
collection = chroma_client.get_or_create_collection(
    name="documentos",
    embedding_function=embedding_functions.DefaultEmbeddingFunction(),
)


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


print("Leyendo documentos de docs/ ...")
documentos = []
for filename in os.listdir(RUTA_DOCS):
    if filename.endswith(".txt"):
        filepath = os.path.join(RUTA_DOCS, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            contenido = f.read()
            documentos.append((filename, contenido))
        print(f"  → {filename}")

print(f"Indexando {len(documentos)} documentos en ChromaDB...")
total_chunks = 0

for filename, contenido in documentos:
    chunks = chunk_text(contenido)
    for i, chunk in enumerate(chunks):
        chunk_id = f"{filename}_chunk_{i}"
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
            metadatas=[{"filename": filename, "chunk_id": i, "hash": h}],
        )
        total_chunks += 1

print(f"Indexación completada: {total_chunks} chunks en {len(documentos)} documentos")
