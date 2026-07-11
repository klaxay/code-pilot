# we need three typed structures : 
# 1. FileSpec -> represents a file that the planner or implementer wants to create (pathL str, content: str)
# 2. PlannedFile -> represents a file before content is generated (path: str, purpose: str)
# 3. CodePilotState -> graph state (task: str, output_dir: str, plan: str, file_specs: list[PlannedFile], files_to_generate: list[FileSpec], written_files: list[str], explanation: str)

from pydantic import BaseModel, Field
from typing import TypedDict

class FileSpec(TypedDict):
    path: str
    content: str

class PlannedFile(TypedDict):
    path: str
    purpose: str

class CodePilotState(TypedDict):
    task: str
    output_dir: str
    plan: str
    file_specs: list[PlannedFile]
    files_to_generate: list[FileSpec]
    written_files: list[str]
    explanation: str
    review_feedback: str
    approved: bool
    revision_count: int
    max_revisions: int
    mode: str
    repo_path: str
    repo_tree: list[str]
    relevant_files: list[str]
    repo_context: list