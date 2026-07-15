from datetime import datetime
from pathlib import Path
from typing import Callable
from zoneinfo import ZoneInfo

import pandas as pd

from services.ai_client import run_prompt
from services.database import save_results
from services.evaluator import evaluate_response


BASE_DIR = Path(__file__).resolve().parent.parent
PROMPTS_FILE = BASE_DIR / "prompts" / "prompts.csv"

MODEL = "gpt-5"


def run_live_scan(
    progress_callback: Callable[
        [int, int, str, str, str],
        None,
    ]
    | None = None,
) -> dict:
    """
    Run all monitored prompts against OpenAI, save the results
    to SQLite, and return summary information.

    progress_callback receives:
        completed_count
        total_count
        prompt_id
        category
        prompt_text
    """

    if not PROMPTS_FILE.exists():
        raise FileNotFoundError(
            f"Prompt library not found: {PROMPTS_FILE}"
        )

    prompts = pd.read_csv(
        PROMPTS_FILE
    )

    required_columns = {
        "prompt_id",
        "category",
        "prompt",
    }

    missing_columns = (
        required_columns
        - set(prompts.columns)
    )

    if missing_columns:
        missing = ", ".join(
            sorted(missing_columns)
        )

        raise ValueError(
            "prompts.csv is missing required "
            f"columns: {missing}"
        )

    new_results = []

    run_started = datetime.now(
        ZoneInfo("America/New_York")
    )

    scan_id = run_started.strftime(
        "%Y%m%d%H%M%S"
    )

    run_date = run_started.strftime(
        "%Y-%m-%d"
    )

    run_timestamp = run_started.isoformat(
        timespec="seconds"
    )

    total_prompts = len(prompts)

    for prompt_number, (_, row) in enumerate(
        prompts.iterrows(),
        start=1,
    ):
        prompt_id = str(
            row["prompt_id"]
        )

        category = str(
            row["category"]
        )

        prompt_text = str(
            row["prompt"]
        )

        if progress_callback:
            progress_callback(
                prompt_number - 1,
                total_prompts,
                prompt_id,
                category,
                prompt_text,
            )

        ai_result = run_prompt(
            prompt=prompt_text,
            model=MODEL,
            instructions=(
                "Answer as an AI search assistant "
                "responding to a prospective student. "
                "Give a natural and useful answer. "
                "Mention institutions only when they "
                "genuinely belong in the response. "
                "Be concise, but include enough detail "
                "to help the user make a decision."
            ),
        )

        response_text = ai_result[
            "response"
        ]

        analysis = evaluate_response(
            prompt_text,
            response_text,
        )

        new_results.append(
            {
                "scan_id": scan_id,
                "run_date": run_date,
                "run_timestamp": run_timestamp,
                "platform": "ChatGPT",
                "provider": ai_result[
                    "provider"
                ],
                "model": ai_result[
                    "model"
                ],
                "prompt_id": prompt_id,
                "category": category,
                "prompt": prompt_text,
                "wake_tech_mentioned": (
                    "Yes"
                    if analysis["wake_mentioned"]
                    else "No"
                ),
                "position": analysis[
                    "wake_rank"
                ],
                "competitors": "|".join(
                    analysis["competitors"]
                ),
                "wake_tech_url": "",
                "competitor_urls": "",
                "score": analysis[
                    "score"
                ],
                "sentiment": analysis[
                    "sentiment"
                ],
                "strengths": "|".join(
                    analysis["strengths"]
                ),
                "weaknesses": "|".join(
                    analysis["weaknesses"]
                ),
                "recommendations": "|".join(
                    analysis[
                        "recommendations"
                    ]
                ),
                "notes": (
                    " | ".join(
                        analysis["weaknesses"]
                    )
                    if analysis["weaknesses"]
                    else (
                        "No major visibility "
                        "weaknesses identified."
                    )
                ),
                "response": response_text,
                "latency_seconds": ai_result[
                    "latency_seconds"
                ],
                "input_tokens": ai_result[
                    "input_tokens"
                ],
                "output_tokens": ai_result[
                    "output_tokens"
                ],
                "total_tokens": ai_result[
                    "total_tokens"
                ],
                "response_id": ai_result[
                    "response_id"
                ],
            }
        )

        if progress_callback:
            progress_callback(
                prompt_number,
                total_prompts,
                prompt_id,
                category,
                prompt_text,
            )

    if not new_results:
        return {
            "scan_id": scan_id,
            "responses": 0,
            "platforms": 0,
            "avg_score": 0,
            "total_tokens": 0,
        }

    saved_count = save_results(
        new_results
    )

    new_results_df = pd.DataFrame(
        new_results
    )

    return {
        "scan_id": scan_id,
        "responses": saved_count,
        "platforms": new_results_df[
            "platform"
        ].nunique(),
        "avg_score": round(
            new_results_df[
                "score"
            ].mean(),
            1,
        ),
        "total_tokens": int(
            new_results_df[
                "total_tokens"
            ].sum()
        ),
    }