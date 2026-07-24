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

# Files that are generally not useful for code retrieval.
NON_INDEXABLE_SUFFIXES = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".ico",
    ".pdf",
    ".zip",
    ".tar",
    ".gz",
    ".exe",
    ".dll",
    ".so",
    ".woff",
    ".woff2",
    ".ttf",
}

MAX_INDEXABLE_FILE_SIZE = 1_000_000


def _get_repo_files(repo_path: str) -> tuple[Path, list[Path]]:
    root = Path(repo_path).resolve()

    if not root.exists():
        raise ValueError(
            f"Repository path does not exist: {repo_path}"
        )

    if not root.is_dir():
        raise ValueError(
            f"Repository path is not a directory: {repo_path}"
        )

    files: list[Path] = []

    for path in root.rglob("*"):
        if not path.is_file():
            continue

        relative_path = path.relative_to(root)

        if any(
            part in IGNORED_DIRS
            for part in relative_path.parts
        ):
            continue

        if path.name in IGNORED_FILE_NAMES:
            continue

        if path.suffix.lower() in IGNORED_FILE_SUFFIXES:
            continue

        files.append(path)

    return root, files


def list_repo_files(repo_path: str) -> list[str]:
    """
    Return repository files for repository discovery.
    """

    root, files = _get_repo_files(repo_path)

    repo_files = [
        path.relative_to(root).as_posix()
        for path in files
    ]

    return sorted(repo_files)


def scan_indexable_files(repo_path: str) -> list[str]:
    """
    Return repository files suitable for indexing.
    """

    root, files = _get_repo_files(repo_path)

    indexable_files: list[str] = []

    for path in files:

        if path.suffix.lower() in NON_INDEXABLE_SUFFIXES:
            continue

        try:
            if path.stat().st_size > MAX_INDEXABLE_FILE_SIZE:
                continue
        except OSError:
            continue

        indexable_files.append(
            path.relative_to(root).as_posix()
        )

    return sorted(indexable_files)


def read_repo_files(
    repo_path: str,
    file_paths: list[str],
) -> list[FileSpec]:

    root = Path(repo_path).resolve()

    repo_context: list[FileSpec] = []

    for relative_path in file_paths:
        full_path = root / relative_path

        if not full_path.is_file():
            continue

        try:
            content = full_path.read_text(
                encoding="utf-8",
                errors="ignore",
            )
        except OSError:
            continue

        repo_context.append(
            {
                "path": relative_path,
                "content": content,
            }
        )

    return repo_context