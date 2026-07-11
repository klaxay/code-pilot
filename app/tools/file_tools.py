from pathlib import Path
import shutil

from app.models.state import FileSpec


IGNORED_PATTERNS = shutil.ignore_patterns(
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    "node_modules",
    "dist",
    "build",
    ".pytest_cache",
    ".mypy_cache",
    ".idea",
    ".vscode",
)


def prepare_output_directory(
    output_dir: str,
    repo_path: str | None = None,
    overwrite: bool = False,
) -> None:
    """
    Prepare the output directory.

    Greenfield mode:
        - Create an empty output directory.

    Repo mode:
        - Copy the repository into the output directory.
    """

    output = Path(output_dir)

    if output.exists():
        if not overwrite:
            raise ValueError(
                f"Output directory '{output_dir}' already exists."
            )

        shutil.rmtree(output)

    if repo_path:
        repo = Path(repo_path)

        if not repo.exists():
            raise ValueError(
                f"Repository path '{repo_path}' does not exist."
            )

        if not repo.is_dir():
            raise ValueError(
                f"Repository path '{repo_path}' is not a directory."
            )

        shutil.copytree(
            repo,
            output,
            ignore=IGNORED_PATTERNS,
        )

    else:
        output.mkdir(
            parents=True,
            exist_ok=True,
        )


def write_files(
    output_dir: str,
    files_to_generate: list[FileSpec],
) -> list[str]:
    """
    Write generated files into the prepared output directory.
    """

    output = Path(output_dir)

    written_files: list[str] = []

    for file in files_to_generate:
        file_path = output / file["path"]

        file_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        file_path.write_text(
            file["content"],
            encoding="utf-8",
        )

        written_files.append(file["path"])

    return written_files