from app.indexing.models import CodeChunk
from functools import lru_cache
from langchain_huggingface import HuggingFaceEmbeddings

@lru_cache(maxsize=1)
def get_embedding_model() -> HuggingFaceEmbeddings:
    return HuggingFaceEmbeddings(
        model_name = "sentence-transformers/all-MiniLM-L6-v2"
    )

def build_embedding_text(chunk: CodeChunk) -> str:
    parts: list[str] = [
        f"File: {chunk.file_path}",
    ]

    if chunk.symbol:
        parts.append(f"Symbol: {chunk.symbol}")

    if chunk.symbol_type:
        parts.append(f"Type: {chunk.symbol_type}")

    if chunk.language:
        parts.append(f"Language: {chunk.language}")

    parts.append("")
    parts.append(chunk.content)

    return "\n".join(parts)
    
def embed_chunks(chunks: list[CodeChunk]) -> list[list[float]]:
    embedding_model = get_embedding_model()

    chunk_documents = []

    for chunk in chunks:
        chunk_text = build_embedding_text(chunk)
        chunk_documents.append(chunk_text)
    
    vectors = embedding_model.embed_documents(chunk_documents)
    
    return vectors


def embed_query(query: str) -> list[float]:
    if not query.strip():
        raise ValueError("Query cannot be empty.")

    embedding_model = get_embedding_model()
    return embedding_model.embed_query(query)