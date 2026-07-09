from app.models.state import CodePilotState


def intake_task(state: CodePilotState) -> dict:
    task = state["task"].strip()
    output_dir = state.get("output_dir", "").strip()
    repo_path = state.get("repo_path", "").strip()

    if not task:
        raise ValueError("Task cannot be empty.")

    return {
        "task": task,
        "output_dir": output_dir,

        "mode": state.get("mode", ""),
        "repo_path": repo_path,
        "repo_tree": state.get("repo_tree", []),
        "relevant_files": state.get("relevant_files", []),
        "repo_context": state.get("repo_context", []),

        "plan": state.get("plan", ""),
        "file_specs": state.get("file_specs", []),
        "files_to_generate": state.get("files_to_generate", []),
        "written_files": state.get("written_files", []),
        "explanation": state.get("explanation", ""),

        "review_feedback": state.get("review_feedback", ""),
        "approved": state.get("approved", False),
        "revision_count": state.get("revision_count", 0),
        "max_revisions": state.get("max_revisions", 2),
    }