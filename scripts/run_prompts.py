import sys
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from services.scan import run_live_scan


def show_progress(
    completed: int,
    total: int,
    prompt_id: str,
    category: str,
    prompt_text: str,
) -> None:
    if completed < total:
        print(
            f"[{completed + 1}/{total}] "
            f"Running {prompt_id} — {category}..."
        )
    else:
        print(f"[{completed}/{total}] Complete.")


def main() -> None:
    scan = run_live_scan(
        progress_callback=show_progress
    )

    print()
    print(
        f"Done. Added {scan['responses']} live results. "
        f"Average score: {scan['avg_score']}. "
        f"Tokens used: {scan['total_tokens']:,}."
    )


if __name__ == "__main__":
    main()