import chromadb

store = chromadb.PersistentClient(path="vectors")
docs = store.get_or_create_collection("customer_docs")


def ingest(doc_id: str, text: str, tenant_id: str):
    docs.add(ids=[doc_id], documents=[text])


def search(question: str):
    result = docs.query(query_texts=[question], n_results=5)
    return result["documents"][0]
