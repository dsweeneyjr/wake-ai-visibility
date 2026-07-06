from datetime import datetime
from pathlib import Path

import pandas as pd


RESULTS_FILE = Path("data/results.csv")
PROMPTS_FILE = Path("prompts/prompts.csv")

PLATFORMS = ["ChatGPT", "Gemini", "Perplexity"]


def demo_score(platform, category):
    base_scores = {
        "ChatGPT": 68,
        "Gemini": 74,
        "Perplexity": 48,
    }

    category_adjustments = {
        "Nursing": 12,
        "Admissions": 8,
        "Cybersecurity": -6,
        "Transfer": 4,
        "Financial Aid": -3,
    }

    return max(
        0,
        min(
            100,
            base_scores.get(platform, 60) + category_adjustments.get(category, 0)
        )
    )


def demo_competitors(category):
    competitors = {
        "Nursing": "UNC|Durham Tech",
        "Admissions": "Durham Tech",
        "Cybersecurity": "NC State|Durham Tech",
        "Transfer": "NC State|UNC",
        "Financial Aid": "Central Piedmont|Durham Tech",
    }

    return competitors.get(category, "Durham Tech")


def run_demo_scan():
    prompts = pd.read_csv(PROMPTS_FILE)
    existing_results = pd.read_csv(RESULTS_FILE)

    now = datetime.now()
    scan_id = now.strftime("%Y%m%d%H%M%S%f")
    today = now.strftime("%Y-%m-%d")

    new_rows = []

    for _, prompt_row in prompts.iterrows():
        for platform in PLATFORMS:
            score = demo_score(platform, prompt_row["category"])
            mentioned = "Yes" if score >= 55 else "No"

            new_rows.append({
                "scan_id": scan_id,
                "run_date": today,
                "platform": platform,
                "prompt_id": prompt_row["prompt_id"],
                "category": prompt_row["category"],
                "prompt": prompt_row["prompt"],
                "wake_tech_mentioned": mentioned,
                "position": 1 if score >= 70 else 2 if score >= 55 else 0,
                "competitors": demo_competitors(prompt_row["category"]),
                "wake_tech_url": "https://www.waketech.edu" if mentioned == "Yes" else "",
                "competitor_urls": "",
                "score": score,
                "notes": "Demo result generated from Prompt Library.",
            })

    new_results = pd.DataFrame(new_rows)

    updated = pd.concat([existing_results, new_results], ignore_index=True)
    updated.to_csv(RESULTS_FILE, index=False)

    return {
        "scan_id": scan_id,
        "scan_date": today,
        "platforms": new_results["platform"].nunique(),
        "responses": len(new_results),
        "avg_score": round(new_results["score"].mean(), 1),
    }