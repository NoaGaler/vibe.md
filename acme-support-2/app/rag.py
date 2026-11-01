import chromadb

store = chromadb.PersistentClient(path="vectors")
docs = store.get_or_create_collection("customer_docs")


def ingest(doc_id: str, text: str, tenant_id: str):
    docs.add(ids=[doc_id], documents=[text], metadatas=[{"tenant_id": tenant_id}])


def search(question: str, tenant_id: str):
    result = docs.query(query_texts=[question], n_results=5, where={"tenant_id": tenant_id})
    return result["documents"][0]
