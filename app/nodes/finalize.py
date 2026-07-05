from app.models.state import CodePilotState


def finalize(state: CodePilotState) -> dict:
    task = state["task"]
    written_files = state["written_files"]
    explanation = state["explanation"]

    summary = (
        f"Task completed successfully.\n"
        f"Task: {task}\n"
        f"Files written: {len(written_files)}"
    )

    return {
        "explanation": explanation if explanation.strip() else summary
    }