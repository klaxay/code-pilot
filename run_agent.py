from app.graph.workflow import build_graph


def main():
    task = input("Enter coding task: ").strip()
    output_dir = input("Enter output directory: ").strip()

    graph = build_graph()

    initial_state = {
        "task": task,
        "output_dir": output_dir,
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
    print(f"\nPlan:\n{result['plan']}")

    print("\nGenerated Files:")
    for file_spec in result["files_to_generate"]:
        print(f"- {file_spec['path']}")

    print("\nWritten Files:")
    for path in result["written_files"]:
        print(f"- {path}")

    print(f"\nExplanation:\n{result['explanation']}")
    print(f"\nApproved: {result['approved']}")
    print(f"Revision Count: {result['revision_count']}")
    print(f"Review Feedback:\n{result['review_feedback']}")


if __name__ == "__main__":
    main()