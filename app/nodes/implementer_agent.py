import json

from app.llm.client import get_llm
from app.models.state import CodePilotState


def build_greenfield_implementer_prompt(
    task: str,
    plan: str,
    file_specs: list,
    existing_files: list | None = None,
    review_feedback: str | None = None,
    is_revision: bool = False,
) -> str:
    prompt = f"""
You are a senior software engineer.

A user has given the following coding task:

{task}

Implementation Plan:

{plan}

Planned Files:

{json.dumps(file_specs, indent=2)}

Your job is to generate the complete contents for every planned file.

"""

    if is_revision:
        prompt += f"""
This is a revision of a previous implementation.

Previously Generated Files:

{json.dumps(existing_files, indent=2)}

Reviewer Feedback:

{review_feedback}

Your responsibilities are:

- Preserve all correct functionality.
- Address every issue raised by the reviewer.
- Modify existing generated files instead of unnecessarily rewriting everything.
- Introduce new files only if absolutely necessary.
- Ensure the implementation fully satisfies the original task.

"""

    prompt += """
Return ONLY valid JSON in the following format:

{
    "files_to_generate": [
        {
            "path": "main.py",
            "content": "..."
        }
    ],
    "explanation": "Brief explanation of what was generated."
}

Rules:
- Return only valid JSON.
- Do not wrap the response in markdown.
- Respect the planned file paths.
- Generate complete file contents.
- Do not leave TODO placeholders unless absolutely necessary.
- File paths must remain relative.
"""

    return prompt.strip()


def build_repo_implementer_prompt(
    task: str,
    plan: str,
    file_specs: list,
    repo_context: list,
    existing_files: list | None = None,
    review_feedback: str | None = None,
    is_revision: bool = False,
) -> str:
    prompt = f"""
You are a senior software engineer modifying an EXISTING software project.

User Task:

{task}

Implementation Plan:

{plan}

Planned Files:

{json.dumps(file_specs, indent=2)}

Repository Context:

{json.dumps(repo_context, indent=2)}

Your responsibilities are:

- Reuse the existing implementation wherever possible.
- Preserve the current project architecture.
- Follow the existing coding style and conventions.
- Avoid modifying unrelated code.
- Modify existing files instead of creating duplicate files whenever possible.

"""

    if is_revision:
        prompt += f"""
This is a revision of a previous implementation.

Previously Generated Files:

{json.dumps(existing_files, indent=2)}

Reviewer Feedback:

{review_feedback}

Your responsibilities are:

- Address every issue raised by the reviewer.
- Preserve all correct functionality.
- Continue following the repository's existing architecture.
- Return complete updated file contents.
"""

    prompt += """
Return ONLY valid JSON in the following format:

{
    "files_to_generate": [
        {
            "path": "app/main.py",
            "content": "..."
        }
    ],
    "explanation": "Brief explanation of what was implemented."
}

Rules:
- Return only valid JSON.
- Do not wrap the response in markdown.
- Return complete contents for every modified/generated file.
- Respect relative file paths.
- Do not leave TODO placeholders unless absolutely necessary.
"""

    return prompt.strip()


def build_implementer_prompt(
    mode: str,
    task: str,
    plan: str,
    file_specs: list,
    repo_context: list | None = None,
    existing_files: list | None = None,
    review_feedback: str | None = None,
    is_revision: bool = False,
) -> str:
    if mode == "greenfield":
        return build_greenfield_implementer_prompt(
            task=task,
            plan=plan,
            file_specs=file_specs,
            existing_files=existing_files,
            review_feedback=review_feedback,
            is_revision=is_revision,
        )

    if mode == "repo":
        return build_repo_implementer_prompt(
            task=task,
            plan=plan,
            file_specs=file_specs,
            repo_context=repo_context or [],
            existing_files=existing_files,
            review_feedback=review_feedback,
            is_revision=is_revision,
        )

    raise ValueError(f"Unknown implementation mode: {mode}")


def implementer_agent(state: CodePilotState) -> dict:
    task = state["task"]
    mode = state["mode"]
    plan = state["plan"]
    file_specs = state["file_specs"]

    repo_context = state.get("repo_context", [])

    review_feedback = state.get("review_feedback", "")
    approved = state.get("approved", False)
    existing_files = state.get("files_to_generate", [])

    is_revision = (
        bool(review_feedback.strip())
        and not approved
        and len(existing_files) > 0
    )

    llm = get_llm()

    prompt = build_implementer_prompt(
        mode=mode,
        task=task,
        plan=plan,
        file_specs=file_specs,
        repo_context=repo_context,
        existing_files=existing_files,
        review_feedback=review_feedback,
        is_revision=is_revision,
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
            f"Implementer returned invalid JSON:\n{raw_output}"
        ) from e

    files_to_generate = parsed.get("files_to_generate")
    explanation = parsed.get("explanation")

    if not isinstance(files_to_generate, list):
        raise ValueError(
            "Implementer output is missing a valid 'files_to_generate' list."
        )

    for file_spec in files_to_generate:
        if not isinstance(file_spec, dict):
            raise ValueError(
                "Each generated file must be a dictionary."
            )

        if "path" not in file_spec:
            raise ValueError(
                "Generated file missing 'path'."
            )

        if "content" not in file_spec:
            raise ValueError(
                "Generated file missing 'content'."
            )

    if not isinstance(explanation, str) or not explanation.strip():
        raise ValueError(
            "Implementer output is missing a valid 'explanation'."
        )

    return {
        "files_to_generate": files_to_generate,
        "explanation": explanation,
    }