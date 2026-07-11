import json

from app.llm.client import get_llm
from app.models.state import CodePilotState


def build_greenfield_planner_prompt(task: str) -> str:
    return f"""
You are a senior software planning assistant.

A user has given the following coding task:

{task}

Your responsibilities are:

1. Produce a concise implementation strategy.
2. Identify the minimum set of files required.
3. Avoid unnecessary files.
4. Do NOT generate code.

Return ONLY valid JSON in the following format:

{{
    "plan": "1. ...\\n2. ...\\n3. ...",
    "file_specs": [
        {{
            "path": "main.py",
            "purpose": "Application entry point"
        }}
    ]
}}

Rules:
- Return only valid JSON.
- Do not wrap the response in markdown.
- Use only relative file paths.
- Keep the design minimal.
- Do not generate implementation code.
""".strip()


def build_repo_planner_prompt(
    task: str,
    repo_context: list,
) -> str:
    return f"""
You are a senior software architect.

Your job is to plan modifications to an EXISTING software project.

User Task:

{task}

Repository Context:

{json.dumps(repo_context, indent=2)}

Your responsibilities are:

1. Understand the existing implementation.
2. Determine which existing files should be modified.
3. Determine whether any new files need to be created.
4. Produce a step-by-step implementation strategy.
5. Reuse existing code whenever possible.
6. Avoid creating duplicate or unnecessary files.

Return ONLY valid JSON in the following format:

{{
    "plan": "1. ...\\n2. ...\\n3. ...",
    "file_specs": [
        {{
            "path": "app/main.py",
            "purpose": "Register authentication router"
        }}
    ]
}}

Rules:
- Return only valid JSON.
- Do not wrap the response in markdown.
- Use relative file paths only.
- Prefer modifying existing files over creating new ones.
- Only create new files when absolutely necessary.
- Do not generate implementation code.
""".strip()


def build_planner_prompt(
    task: str,
    mode: str,
    repo_context: list,
) -> str:
    if mode == "greenfield":
        return build_greenfield_planner_prompt(task)

    if mode == "repo":
        return build_repo_planner_prompt(
            task,
            repo_context,
        )

    raise ValueError(f"Unknown planner mode: {mode}")


def planner_agent(state: CodePilotState) -> dict:
    task = state["task"]
    mode = state["mode"]
    repo_context = state.get("repo_context", [])

    llm = get_llm()

    prompt = build_planner_prompt(
        task=task,
        mode=mode,
        repo_context=repo_context,
    )

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
            f"Planner returned invalid JSON:\n{raw_output}"
        ) from e

    plan = parsed.get("plan")
    file_specs = parsed.get("file_specs")

    if not isinstance(plan, str) or not plan.strip():
        raise ValueError(
            "Planner output is missing a valid 'plan'."
        )

    if not isinstance(file_specs, list):
        raise ValueError(
            "Planner output is missing a valid 'file_specs' list."
        )

    for file_spec in file_specs:
        if not isinstance(file_spec, dict):
            raise ValueError(
                "Each file spec must be a dictionary."
            )

        if "path" not in file_spec:
            raise ValueError(
                "Missing 'path' in file spec."
            )

        if "purpose" not in file_spec:
            raise ValueError(
                "Missing 'purpose' in file spec."
            )

    return {
        "plan": plan,
        "file_specs": file_specs,
    }