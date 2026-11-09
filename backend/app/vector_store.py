from pathlib import Path
import chromadb
from app.ingest import load_pdfs, chunk_pages

print("vector_store.py is running")

VECTOR_DIR=Path(__file__).resolve().parents[2]/"data"/"vector_store"

def get_collection():
    client=chromadb.PersistentClient(path=str(VECTOR_DIR))
    return client.get_or_create_collection(name="course_docs")

def build_index():
    collection=get_collection()
    chunks=chunk_pages(load_pdfs())
    collection.upsert(
        ids=[c["chunk_id"] for c in chunks],
        documents=[c["text"] for c in chunks],
        metadatas=[{"source":c["source"], "page":c["page"]} for c in chunks],

    )

    print(f"Indexed {len(chunks)} chunks. Collection now holds {collection.count()}.")

if __name__=="__main__":
    build_index()
    collection=get_collection()
    results=collection.query(
        query_texts=["What is AI?"],
        n_results=3
    )
    for doc, meta, dist in zip(
        results["documents"][0], results["metadatas"][0], results["distances"][0]
    ):
        print(f"\n{dist:.3f}  {meta['source']} (page {meta['page']})")
        print(doc[:200])