from app.models.state import CodePilotState


def intake_task(state: CodePilotState) -> dict:
    """
    Normalize the initial user input and ensure downstream state keys exist.
    """

    task = state["task"].strip()
    output_dir = state["output_dir"].strip()

    if not task:
        raise ValueError("Task cannot be empty.")

    if not output_dir:
        raise ValueError("Output directory cannot be empty.")

    return {
        "task": task,
        "output_dir": output_dir,
        "plan": state.get("plan", ""),
        "file_specs": state.get("file_specs", []),
        "files_to_generate": state.get("files_to_generate", []),
        "written_files": state.get("written_files", []),
        "explanation": state.get("explanation", ""),
    }