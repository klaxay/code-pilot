import json

from app.llm.client import get_llm
from app.models.state import CodePilotState


def build_review_prompt(task: str, plan: str, files_to_generate: list) -> str:
    return f"""
You are a senior software reviewer.

A coding agent generated files for the following task.

Task:
{task}

Implementation plan:
{plan}

Generated files:
{json.dumps(files_to_generate, indent=2)}

Your job is to review whether the generated files satisfy the task and are implementation-ready.

Evaluate for:
1. Correctness relative to the task
2. Missing files or missing required logic
3. Obvious syntax / structural issues
4. Whether the generated project is minimal but complete
5. Whether file contents match the purpose of the task

Return ONLY valid JSON in the following format:

{{
  "approved": true,
  "review_feedback": "Detailed feedback for the implementer. If approved, briefly explain why."
}}

Rules:
- Return only valid JSON.
- Do not wrap the JSON in markdown fences.
- Set "approved" to true only if the generated files are good enough to be written as the final result.
- Set "approved" to false if there are meaningful issues, omissions, incorrect file choices, or incomplete implementation details.
- If approved is false, review_feedback must be actionable and specific enough for the implementer to revise the files.
- Mention concrete missing files, missing logic, incorrect code structure, dependency issues, or task mismatches when relevant.
""".strip()


def review_agent(state: CodePilotState) -> dict:
    task = state["task"]
    plan = state["plan"]
    files_to_generate = state["files_to_generate"]

    llm = get_llm()
    prompt = build_review_prompt(task, plan, files_to_generate)

    response = llm.invoke(prompt)
    raw_output = response.content if hasattr(response, "content") else str(response)

    try:
        parsed = json.loads(raw_output)
    except json.JSONDecodeError as e:
        raise ValueError(f"Reviewer returned invalid JSON:\n{raw_output}") from e

    approved = parsed.get("approved")
    review_feedback = parsed.get("review_feedback")

    if not isinstance(approved, bool):
        raise ValueError("Reviewer output must contain 'approved' as a boolean.")

    if not isinstance(review_feedback, str) or not review_feedback.strip():
        raise ValueError(
            "Reviewer output must contain a non-empty 'review_feedback' string."
        )

    new_revision_count = state["revision_count"] + (0 if approved else 1)

    return {
        "approved": approved,
        "review_feedback": review_feedback,
        "revision_count": new_revision_count,
    }