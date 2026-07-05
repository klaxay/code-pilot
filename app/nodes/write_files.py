from app.models.state import CodePilotState
from app.tools.file_tools import write_files


def write_files_node(state: CodePilotState) -> dict:
    output_dir = state["output_dir"]
    files_to_generate = state["files_to_generate"]

    written_files = write_files(output_dir, files_to_generate)

    return {
        "written_files": written_files
    }