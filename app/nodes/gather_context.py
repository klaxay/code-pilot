import json

from app.llm.client import get_llm
from app.models.state import CodePilotState
from app.tools.repo_tools import read_repo_files


def build_gather_context_prompt(task: str, repo_tree: list[str]) -> str:
    return f"""
    You are a senior software engineer.

    Task:
    {task}

    Repository files:
    {json.dumps(repo_tree, indent=2)}

    Your job is to determine which files should be READ before implementing the task.

    Rules:
    - Return ONLY valid JSON.
    - Do not wrap the JSON in markdown.
    - Select only the files necessary to understand and implement the task.
    - Prefer 3-8 files unless more are clearly required.

    Return JSON in this format:

    {{
        "relevant_files": [
            "app/main.py",
            "app/routes/auth.py",
            "requirements.txt"
        ]
    }}
    """.strip()


def gather_context(state: CodePilotState) -> dict:
    task = state["task"]
    repo_tree = state["repo_tree"]
    repo_path = state["repo_path"]

    llm = get_llm()

    prompt = build_gather_context_prompt(task, repo_tree)

    response = llm.invoke(prompt)

    raw_output = (
        response.content
        if hasattr(response, "content")
        else str(response)
    )

    try:
        parsed = json.loads(raw_output)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"Context selector returned invalid JSON:\n{raw_output}"
        ) from e

    relevant_files = parsed.get("relevant_files")

    if not isinstance(relevant_files, list):
        raise ValueError(
            "Missing or invalid 'relevant_files' list."
        )

    repo_context = read_repo_files(
        repo_path,
        relevant_files,
    )

    return {
        "relevant_files": relevant_files,
        "repo_context": repo_context,
    }