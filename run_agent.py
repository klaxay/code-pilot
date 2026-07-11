from app.graph.workflow import build_graph
from IPython.display import Image, display


def main():
    task = input("Enter coding task: ").strip()
    output_dir = input("Enter output directory: ").strip()
    repo_path = input("Enter repo path (leave blank to build from scratch): ").strip()

    graph = build_graph()
    graph_image = graph.get_graph().draw_mermaid_png()
    display(Image(graph_image))
    initial_state = {
        "task": task,
        "output_dir": output_dir,

        "mode": "",
        "repo_path": repo_path,
        "repo_tree": [],
        "relevant_files": [],
        "repo_context": [],

        "plan": "",
        "file_specs": [],
        "files_to_generate": [],
        "written_files": [],
        "explanation": "",

        "review_feedback": "",
        "approved": False,
        "revision_count": 0,
        "max_revisions": 2,
    }

    result = graph.invoke(initial_state)

    print("\n=== CODE PILOT RESULT ===")
    print(f"\nTask:\n{result['task']}")
    print(f"\nMode: {result['mode']}")
    print(f"Repo Path: {result['repo_path'] or '(none)'}")
    print(f"\nPlan:\n{result['plan']}")

    print("\nGenerated Files:")
    for file_spec in result["files_to_generate"]:
        print(f"- {file_spec['path']}")

    print("\nWritten Files:")
    for path in result["written_files"]:
        print(f"- {path}")

    print(f"\nApproved: {result['approved']}")
    print(f"Revision Count: {result['revision_count']}")
    print(f"\nReview Feedback:\n{result['review_feedback']}")
    print(f"\nExplanation:\n{result['explanation']}")


if __name__ == "__main__":
    main()