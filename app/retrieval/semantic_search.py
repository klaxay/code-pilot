from app.indexing.embeddings import embed_query
from app.indexing.vector_store import VectorStore
from app.indexing.models import CodeChunk

def semantic_search(
    query: str,
    vector_store: VectorStore,
    top_k: int = 5
) -> list[CodeChunk]:
    query_vector = embed_query(query)
    return vector_store.similarity_search(query_vector=query_vector, k=top_k)