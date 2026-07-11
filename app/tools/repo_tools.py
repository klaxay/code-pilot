from pathlib import Path
from app.models.state import FileSpec

IGNORED_DIRS = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "dist",
    "build",
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
    ".idea",
    ".vscode",
}

IGNORED_FILE_SUFFIXES = {
    ".pyc",
}

IGNORED_FILE_NAMES = {
    ".DS_Store",
}


def list_repo_files(repo_path: str) -> list[str]:
    """
    Recursively list relevant files in a repository, returning paths
    relative to repo_path.
    """
    root = Path(repo_path).resolve()

    if not root.exists():
        raise ValueError(f"Repository path does not exist: {repo_path}")

    if not root.is_dir():
        raise ValueError(f"Repository path is not a directory: {repo_path}")

    repo_files: list[str] = []

    for path in root.rglob("*"):
        if path.is_dir():
            continue

        # Skip ignored directories anywhere in the path
        if any(part in IGNORED_DIRS for part in path.parts):
            continue

        if path.name in IGNORED_FILE_NAMES:
            continue

        if path.suffix in IGNORED_FILE_SUFFIXES:
            continue

        relative_path = path.relative_to(root).as_posix()
        repo_files.append(relative_path)

    repo_files.sort()
    return repo_files

def read_repo_files(
    repo_path: str,
    file_paths: list[str],
) -> list[FileSpec]:
    """
    Reads the selected repository files and returns
    their contents.
    """

    root = Path(repo_path).resolve()

    repo_context: list[FileSpec] = []

    for relative_path in file_paths:
        full_path = root / relative_path

        if not full_path.exists():
            continue

        if not full_path.is_file():
            continue

        try:
            content = full_path.read_text(
                encoding="utf-8",
                errors="ignore",
            )
        except Exception:
            continue

        repo_context.append(
            {
                "path": relative_path,
                "content": content,
            }
        )

    return repo_context