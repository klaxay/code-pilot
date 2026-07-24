import ast
from pathlib import Path

from app.indexing.models import CodeChunk


def chunk_python_file(
    file_path: str | Path,
    relative_path: str,
) -> list[CodeChunk]:
    """
    Chunk a Python file into top-level functions and classes.

    file_path:
        Actual filesystem path used to read the file.

    relative_path:
        Repository-relative path stored in CodeChunk metadata.
    """

    path = Path(file_path)

    with path.open("r", encoding="utf-8") as f:
        source = f.read()

    tree = ast.parse(source)
    lines = source.splitlines()

    chunks: list[CodeChunk] = []

    for node in tree.body:
        if isinstance(
            node,
            (ast.FunctionDef, ast.AsyncFunctionDef),
        ):
            symbol_type = "function"

        elif isinstance(node, ast.ClassDef):
            symbol_type = "class"

        else:
            continue

        start_line = node.lineno
        end_line = node.end_lineno

        content = "\n".join(
            lines[start_line - 1:end_line]
        )

        chunks.append(
            CodeChunk(
                content=content,
                file_path=relative_path,
                symbol_type=symbol_type,
                symbol=node.name,
                start_line=start_line,
                end_line=end_line,
                language="python",
            )
        )

    return chunks


def chunk_text_file(
    file_path: str | Path,
    relative_path: str,
    chunk_size: int = 100,
    chunk_overlap: int = 20,
) -> list[CodeChunk]:
    """
    Chunk a non-Python text file using overlapping line windows.
    """

    if chunk_size <= 0:
        raise ValueError(
            "chunk_size must be greater than 0."
        )

    if chunk_overlap < 0 or chunk_overlap >= chunk_size:
        raise ValueError(
            "chunk_overlap must be >= 0 and smaller than chunk_size."
        )

    path = Path(file_path)

    with path.open("r", encoding="utf-8") as f:
        lines = f.read().splitlines()

    chunks: list[CodeChunk] = []

    start = 0

    while start < len(lines):
        end = min(
            start + chunk_size,
            len(lines),
        )

        content = "\n".join(
            lines[start:end]
        )

        if content.strip():
            chunks.append(
                CodeChunk(
                    content=content,
                    file_path=relative_path,
                    start_line=start + 1,
                    end_line=end,
                    symbol=None,
                    symbol_type="text",
                    language=None,
                )
            )

        if end >= len(lines):
            break

        start += chunk_size - chunk_overlap

    return chunks


def chunk_repository(
    repo_path: str,
    file_paths: list[str],
) -> list[CodeChunk]:
    """
    Chunk all indexable files in a repository.

    file_paths must contain paths relative to repo_path.
    """

    root = Path(repo_path).resolve()

    chunks: list[CodeChunk] = []

    for relative_path in file_paths:
        full_path = root / relative_path

        if not full_path.is_file():
            continue

        try:
            if full_path.suffix.lower() == ".py":
                file_chunks = chunk_python_file(
                    file_path=full_path,
                    relative_path=relative_path,
                )
            else:
                file_chunks = chunk_text_file(
                    file_path=full_path,
                    relative_path=relative_path,
                )

        except (
            UnicodeDecodeError,
            SyntaxError,
            OSError,
        ):
            # Skip files that cannot safely be parsed/read.
            continue

        chunks.extend(file_chunks)

    return chunks