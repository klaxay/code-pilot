from app.indexing.vector_store import VectorStore
from app.retrieval.context_builder import (
    RetrievalContext,
    build_context,
)
from app.retrieval.semantic_search import semantic_search


class Retriever:
    def __init__(
        self,
        vector_store: VectorStore,
    ) -> None:
        self.vector_store = vector_store

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
    ) -> RetrievalContext:
        chunks = semantic_search(
            query=query,
            vector_store=self.vector_store,
            top_k=top_k,
        )

        return build_context(chunks)