from pathlib import Path


def _resolve_safe_path(base_dir: str, relative_path: str) -> Path:
    """
    Resolve a generated relative file path inside base_dir and ensure
    it cannot escape the base directory.
    """
    base_path = Path(base_dir).resolve()
    target_path = (base_path / relative_path).resolve()

    if not str(target_path).startswith(str(base_path)):
        raise ValueError(f"Unsafe file path detected: {relative_path}")

    return target_path


def write_files(base_dir: str, files: list[dict]) -> list[str]:
    """
    Write generated files into base_dir safely.

    Args:
        base_dir: The root directory where files should be written.
        files: A list of dicts, each containing:
            - path: relative file path
            - content: file contents as a string

    Returns:
        A list of written file paths as strings.
    """
    base_path = Path(base_dir)
    base_path.mkdir(parents=True, exist_ok=True)

    written_files: list[str] = []

    for file_spec in files:
        if not isinstance(file_spec, dict):
            raise ValueError("Each file spec must be a dictionary.")

        relative_path = file_spec.get("path")
        content = file_spec.get("content")

        if not isinstance(relative_path, str) or not relative_path.strip():
            raise ValueError("Each file spec must contain a valid 'path' string.")

        if not isinstance(content, str):
            raise ValueError("Each file spec must contain a valid 'content' string.")

        safe_path = _resolve_safe_path(base_dir, relative_path)

        safe_path.parent.mkdir(parents=True, exist_ok=True)
        safe_path.write_text(content, encoding="utf-8")

        written_files.append(str(safe_path))

    return written_files