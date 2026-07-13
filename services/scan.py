import re
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path
from typing import Callable

import pandas as pd

from services.ai_client import run_prompt


BASE_DIR = Path(__file__).resolve().parent.parent
PROMPTS_FILE = BASE_DIR / "prompts" / "prompts.csv"
RESULTS_FILE = BASE_DIR / "data" / "results.csv"

MODEL = "gpt-5"

KNOWN_COMPETITORS = [
    "Durham Tech",
    "Central Piedmont",
    "CPCC",
    "NC State",
    "UNC",
    "ECU",
    "Fayetteville Tech",
    "Johnston Community College",
    "Wake Forest",
    "Campbell University",
    "Pitt Community College",
]


def analyze_response(response_text: str) -> dict:
    text = response_text.lower()

    wake_mentioned = (
        "wake tech" in text
        or "wake technical" in text
        or "wake technical community college" in text
    )

    competitors = [
        competitor
        for competitor in KNOWN_COMPETITORS
        if competitor.lower() in text
    ]

    urls = re.findall(r"https?://\S+", response_text)

    urls = [
        url.rstrip(".,;:!?)]}\"'")
        for url in urls
    ]

    wake_urls = [
        url
        for url in urls
        if "waketech.edu" in url.lower()
    ]

    competitor_urls = [
        url
        for url in urls
        if "waketech.edu" not in url.lower()
    ]

    score = 0

    if wake_mentioned:
        score += 60

    if wake_urls:
        score += 25

    if competitors:
        score -= min(len(competitors) * 5, 20)

    score = max(0, min(score, 100))

    if not wake_mentioned:
        notes = "Wake Tech was not mentioned."
        position = 0
    elif score < 70:
        notes = "Wake Tech was mentioned, but visibility appears weak."
        position = 2
    else:
        notes = "Wake Tech has strong visibility."
        position = 1

    return {
        "wake_tech_mentioned": "Yes" if wake_mentioned else "No",
        "position": position,
        "competitors": "|".join(competitors),
        "wake_tech_url": "|".join(wake_urls),
        "competitor_urls": "|".join(competitor_urls),
        "score": score,
        "notes": notes,
    }


def load_existing_results() -> pd.DataFrame:
    if not RESULTS_FILE.exists():
        return pd.DataFrame()

    try:
        return pd.read_csv(RESULTS_FILE)
    except pd.errors.EmptyDataError:
        return pd.DataFrame()


def run_live_scan(
    progress_callback: Callable[[int, int, str, str, str], None] | None = None,
) -> dict:
    """
    Run all monitored prompts against OpenAI, append the results,
    and return summary information.

    progress_callback receives:
        completed_count
        total_count
        prompt_id
        category
    """

    if not PROMPTS_FILE.exists():
        raise FileNotFoundError(
            f"Prompt library not found: {PROMPTS_FILE}"
        )

    prompts = pd.read_csv(PROMPTS_FILE)

    required_columns = {"prompt_id", "category", "prompt"}
    missing_columns = required_columns - set(prompts.columns)

    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(
            f"prompts.csv is missing required columns: {missing}"
        )

    existing_results = load_existing_results()
    new_results = []

    run_started = datetime.now(
        ZoneInfo("America/New_York")
    )

    scan_id = run_started.strftime("%Y%m%d%H%M%S")
    run_date = run_started.strftime("%Y-%m-%d")
    run_timestamp = run_started.isoformat(timespec="seconds")

    total_prompts = len(prompts)

    for prompt_number, (_, row) in enumerate(
        prompts.iterrows(),
        start=1,
    ):
        prompt_id = str(row["prompt_id"])
        category = str(row["category"])
        prompt_text = str(row["prompt"])

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
                "Answer as an AI search assistant responding to a prospective "
                "student. Give a natural and useful answer. Mention institutions "
                "only when they genuinely belong in the response. Be concise, "
                "but include enough detail to help the user make a decision."
            ),
        )

        response_text = ai_result["response"]
        analysis = analyze_response(response_text)

        new_results.append({
            "scan_id": scan_id,
            "run_date": run_date,
            "run_timestamp": run_timestamp,
            "platform": "ChatGPT",
            "provider": ai_result["provider"],
            "model": ai_result["model"],
            "prompt_id": prompt_id,
            "category": category,
            "prompt": prompt_text,
            "wake_tech_mentioned": analysis["wake_tech_mentioned"],
            "position": analysis["position"],
            "competitors": analysis["competitors"],
            "wake_tech_url": analysis["wake_tech_url"],
            "competitor_urls": analysis["competitor_urls"],
            "score": analysis["score"],
            "notes": analysis["notes"],
            "response": response_text,
            "latency_seconds": ai_result["latency_seconds"],
            "input_tokens": ai_result["input_tokens"],
            "output_tokens": ai_result["output_tokens"],
            "total_tokens": ai_result["total_tokens"],
            "response_id": ai_result["response_id"],
        })

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

    new_results_df = pd.DataFrame(new_results)

    updated_results = pd.concat(
        [existing_results, new_results_df],
        ignore_index=True,
        sort=False,
    )

    RESULTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    updated_results.to_csv(RESULTS_FILE, index=False)

    return {
        "scan_id": scan_id,
        "responses": len(new_results_df),
        "platforms": new_results_df["platform"].nunique(),
        "avg_score": round(new_results_df["score"].mean(), 1),
        "total_tokens": int(new_results_df["total_tokens"].sum()),
    }