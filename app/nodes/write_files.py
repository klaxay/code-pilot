from app.models.state import CodePilotState
from app.tools.file_tools import (
    prepare_output_directory,
    write_files,
)


def write_files_node(state: CodePilotState) -> dict:
    output_dir = state["output_dir"]
    repo_path = state.get("repo_path", "")

    prepare_output_directory(
        output_dir=output_dir,
        repo_path=repo_path if repo_path else None,
        overwrite=True,
    )

    written_files = write_files(
        output_dir=output_dir,
        files_to_generate=state["files_to_generate"],
    )

    return {
        "written_files": written_files,
    }