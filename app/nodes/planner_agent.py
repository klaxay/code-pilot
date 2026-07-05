import json

from app.llm.client import get_llm
from app.models.state import CodePilotState


def build_planner_prompt(task: str) -> str:
    return f"""
You are a software planning assistant.

A user has given the following coding task:

{task}

Your job is to:
1. Create a concise implementation plan.
2. Identify the minimal set of files required to complete the task.

Return ONLY valid JSON in the following format:

{{
  "plan": "1. ...\\n2. ...\\n3. ...",
  "file_specs": [
    {{
      "path": "main.py",
      "purpose": "Main application entrypoint"
    }}
  ]
}}

Rules:
- Return only valid JSON. Do not include markdown code fences or extra commentary.
- Use only relative file paths, never absolute paths.
- Keep the file list minimal and practical for the task.
- Do not generate file contents.
""".strip()


def planner_agent(state: CodePilotState) -> dict:
    task = state["task"]

    llm = get_llm()
    prompt = build_planner_prompt(task)

    response = llm.invoke(prompt)

    raw_output = response.content if hasattr(response, "content") else str(response)

    try:
        parsed = json.loads(raw_output)
    except json.JSONDecodeError as e:
        raise ValueError(f"Planner returned invalid JSON:\n{raw_output}") from e

    plan = parsed.get("plan")
    file_specs = parsed.get("file_specs")

    if not isinstance(plan, str) or not plan.strip():
        raise ValueError("Planner output is missing a valid 'plan' string.")

    if not isinstance(file_specs, list):
        raise ValueError("Planner output is missing a valid 'file_specs' list.")

    for file_spec in file_specs:
        if not isinstance(file_spec, dict):
            raise ValueError("Each item in 'file_specs' must be a dictionary.")
        if "path" not in file_spec or "purpose" not in file_spec:
            raise ValueError("Each file spec must contain 'path' and 'purpose'.")

    return {
        "plan": plan,
        "file_specs": file_specs,
    }