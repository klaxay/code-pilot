from app.models.state import CodePilotState
from app.tools.repo_tools import list_repo_files


def discover_repo(state: CodePilotState) -> dict:
    repo_path = state["repo_path"].strip()

    if not repo_path:
        raise ValueError("discover_repo was called without a repo_path.")

    repo_files = list_repo_files(repo_path)

    return {
        "repo_tree": repo_files
    }