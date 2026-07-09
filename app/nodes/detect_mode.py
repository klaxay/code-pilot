from app.models.state import CodePilotState

def detect_mode(state: CodePilotState) -> dict:
    repo_path = state["repo_path"]
    if(len(repo_path)==0):
        return{
            "mode" : "greenfield"
        }
    return{
        "mode" : "repo"
    }