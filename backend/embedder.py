import chromadb
from sentence_transformers import SentenceTransformer

CHROMA_DIR = "chroma_db"
MODEL_NAME = "all-MiniLM-L6-v2"

_client = chromadb.PersistentClient(path=CHROMA_DIR)
_model = SentenceTransformer(MODEL_NAME)


def _collection_name(doc_id: str) -> str:
    return f"doc_{doc_id}"[:63].replace(".", "_")


def embed_texts(texts):
    return _model.encode(texts, normalize_embeddings=True).tolist()


def add_chunks_to_chroma(doc_id: str, chunks, source_name: str):
    collection = _client.get_or_create_collection(name=_collection_name(doc_id))
    ids = [f"{doc_id}_{i}" for i in range(len(chunks))]
    embeddings = embed_texts(chunks)
    metadatas = [
        {"doc_id": doc_id, "source": source_name, "chunk_index": i}
        for i in range(len(chunks))
    ]

    # Replace old indexed copy of same document if re-uploaded
    try:
        collection.delete(where={"doc_id": doc_id})
    except Exception:
        pass

    collection.add(
        ids=ids,
        documents=chunks,
        embeddings=embeddings,
        metadatas=metadatas,
    )
