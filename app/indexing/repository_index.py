from pathlib import Path

from app.indexing.chunker import chunk_repository
from app.indexing.embeddings import embed_chunks
from app.indexing.repo_tools import scan_indexable_files
from app.indexing.vector_store import VectorStore


class RepositoryIndex:
    def __init__(self, repo_path: str) -> None:
        self.repo_path = Path(repo_path).resolve()

        self.vector_store = VectorStore(
            collection_name=self.repo_path.name
        )

    def _validate_repo(self) -> None:
        if not self.repo_path.exists():
            raise ValueError(
                f"Repository does not exist: {self.repo_path}"
            )

        if not self.repo_path.is_dir():
            raise ValueError(
                f"Repository path is not a directory: {self.repo_path}"
            )

    def build(self) -> dict[str, int]:
        self._validate_repo()

        indexable_files = scan_indexable_files(
            str(self.repo_path)
        )

        chunks = chunk_repository(
            str(self.repo_path),
            indexable_files,
        )

        vectors = embed_chunks(chunks)

        self.vector_store.add_chunks(
            chunks,
            vectors,
        )

        return {
            "files": len(indexable_files),
            "chunks": len(chunks),
        }