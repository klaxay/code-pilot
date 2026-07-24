from pathlib import Path

import chromadb
from chromadb.api.models.Collection import Collection

from app.indexing.embeddings import build_embedding_text
from app.indexing.models import CodeChunk


class VectorStore:
    def __init__(
        self,
        persist_directory: str = ".codepilot/chroma",
        collection_name: str = "repository",
    ) -> None:
        Path(persist_directory).mkdir(
            parents=True,
            exist_ok=True,
        )

        self.client = chromadb.PersistentClient(
            path=persist_directory,
        )

        self.collection: Collection = (
            self.client.get_or_create_collection(
                name=collection_name,
            )
        )

    def _chunk_id(
        self,
        chunk: CodeChunk,
    ) -> str:
        symbol = chunk.symbol or "global"

        return (
            f"{chunk.file_path}:"
            f"{symbol}:"
            f"{chunk.start_line}:"
            f"{chunk.end_line}"
        )

    def add_chunks(
        self,
        chunks: list[CodeChunk],
        vectors: list[list[float]],
    ) -> None:
        if not chunks:
            return

        ids: list[str] = []
        documents: list[str] = []
        metadatas: list[dict] = []

        for chunk in chunks:
            ids.append(self._chunk_id(chunk))

            documents.append(
                chunk.content
            )

            metadatas.append(
                {
                    "file_path": chunk.file_path,
                    "start_line": chunk.start_line,
                    "end_line": chunk.end_line,
                    "symbol": chunk.symbol,
                    "symbol_type": chunk.symbol_type,
                    "language": chunk.language,
                }
            )

        self.collection.upsert(
            ids=ids,
            embeddings=vectors,
            documents=documents,
            metadatas=metadatas,
        )

    def similarity_search(
        self,
        query_vector: list[float],
        k: int = 5,
    ) -> list[CodeChunk]:
        results = self.collection.query(
            query_embeddings=[query_vector],
            n_results=k,
        )

        chunks: list[CodeChunk] = []

        documents = results["documents"][0]
        metadatas = results["metadatas"][0]

        for document, metadata in zip(
            documents,
            metadatas,
        ):
            chunks.append(
                CodeChunk(
                    content=document,
                    file_path=metadata["file_path"],
                    start_line=metadata["start_line"],
                    end_line=metadata["end_line"],
                    symbol=metadata.get("symbol"),
                    symbol_type=metadata.get("symbol_type"),
                    language=metadata.get("language"),
                )
            )

        return chunks

    def clear(self) -> None:
        self.client.delete_collection(
            self.collection.name,
        )

        self.collection = (
            self.client.get_or_create_collection(
                name=self.collection.name,
            )
        )