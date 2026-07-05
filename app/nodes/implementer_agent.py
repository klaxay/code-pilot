import json

from app.llm.client import get_llm
from app.models.state import CodePilotState


def build_implementer_prompt(task: str, plan: str, file_specs: list) -> str:
    return f"""
You are a software implementation assistant.

A user has given the following coding task:

{task}

Implementation plan:
{plan}

Files to generate:
{json.dumps(file_specs, indent=2)}

Your job is to generate the complete contents for each planned file.

Return ONLY valid JSON in the following format:

{{
  "files_to_generate": [
    {{
      "path": "main.py",
      "content": "print('hello world')"
    }}
  ],
  "explanation": "A short explanation of what was generated."
}}

Rules:
- Return only valid JSON. Do not include markdown code fences or extra commentary.
- Respect the provided file paths from file_specs.
- Generate complete file contents for each file.
- Do not leave placeholders like TODO unless absolutely necessary.
- File paths must remain relative.
""".strip()


def implementer_agent(state: CodePilotState) -> dict:
    task = state["task"]
    plan = state["plan"]
    file_specs = state["file_specs"]

    llm = get_llm()
    prompt = build_implementer_prompt(task, plan, file_specs)

    response = llm.invoke(prompt)
    raw_output = response.content if hasattr(response, "content") else str(response)

    try:
        parsed = json.loads(raw_output)
    except json.JSONDecodeError as e:
        raise ValueError(f"Implementer returned invalid JSON:\n{raw_output}") from e

    files_to_generate = parsed.get("files_to_generate")
    explanation = parsed.get("explanation")

    if not isinstance(files_to_generate, list):
        raise ValueError("Implementer output is missing a valid 'files_to_generate' list.")

    for file_spec in files_to_generate:
        if not isinstance(file_spec, dict):
            raise ValueError("Each item in 'files_to_generate' must be a dictionary.")
        if "path" not in file_spec or "content" not in file_spec:
            raise ValueError("Each generated file must contain 'path' and 'content'.")

    if not isinstance(explanation, str) or not explanation.strip():
        raise ValueError("Implementer output is missing a valid 'explanation' string.")

    return {
        "files_to_generate": files_to_generate,
        "explanation": explanation,
    }