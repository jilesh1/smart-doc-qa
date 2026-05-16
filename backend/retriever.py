import chromadb
from embedder import embed_texts

CHROMA_DIR = "chroma_db"
_client = chromadb.PersistentClient(path=CHROMA_DIR)


def _collection_name(doc_id: str) -> str:
    return f"doc_{doc_id}"[:63].replace(".", "_")


def retrieve_chunks(doc_id: str, question: str, top_k: int = 5):
    collection = _client.get_or_create_collection(name=_collection_name(doc_id))
    query_embedding = embed_texts([question])[0]
    result = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    docs = result.get("documents", [[]])[0]
    metas = result.get("metadatas", [[]])[0]
    distances = result.get("distances", [[]])[0]

    chunks = []
    for doc, meta, distance in zip(docs, metas, distances):
        chunks.append({
            "text": doc,
            "source": meta.get("source"),
            "chunk_index": meta.get("chunk_index"),
            "citation": f"{meta.get('source')} - chunk {meta.get('chunk_index')}",
            "distance": distance,
        })
    return chunks


def list_documents():
    docs = []
    for col in _client.list_collections():
        name = col.name
        if name.startswith("doc_"):
            doc_id = name[4:]
            try:
                collection = _client.get_collection(name=name)
                data = collection.get(limit=1, include=["metadatas"])
                source = data.get("metadatas", [{}])[0].get("source", doc_id)
                count = collection.count()
            except Exception:
                source = doc_id
                count = 0
            docs.append({"doc_id": doc_id, "filename": source, "chunks": count})
    return docs
