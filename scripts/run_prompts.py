import os
import re
from datetime import datetime
from pathlib import Path

import pandas as pd
from openai import OpenAI
from openai import OpenAI, RateLimitError


BASE_DIR = Path(__file__).resolve().parent.parent
PROMPTS_FILE = BASE_DIR / "prompts" / "prompts.csv"
RESULTS_FILE = BASE_DIR / "data" / "results.csv"

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


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


def ask_openai(prompt):
    try:
        response = client.responses.create(
            model="gpt-4.1-mini",
            input=f"""
You are answering as an AI search assistant.

Question:
{prompt}
"""
        )

        return response.output_text

    except RateLimitError as e:
        if "insufficient_quota" in str(e):
            print("OpenAI API quota unavailable. Check API billing and credits.")
            return None

        raise

def analyze_response(response_text):
    text = response_text.lower()

    wake_mentioned = "wake tech" in text or "wake technical" in text

    competitors = [
        competitor
        for competitor in KNOWN_COMPETITORS
        if competitor.lower() in text
    ]

    urls = re.findall(r"https?://\\S+", response_text)

    wake_urls = [
        url for url in urls
        if "waketech.edu" in url.lower()
    ]

    competitor_urls = [
        url for url in urls
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


def main():
    prompts = pd.read_csv(PROMPTS_FILE)
    existing_results = pd.read_csv(RESULTS_FILE)

    new_results = []

    for _, row in prompts.iterrows():
        print(f"Running {row['prompt_id']} — {row['category']}...")

        response = ask_openai(row["prompt"])
        if response is None:
            print(f"Skipping {row['prompt_id']} because the API is unavailable.")
            continue
        analysis = analyze_response(response)

        new_results.append({
            "run_date": datetime.now().strftime("%Y-%m-%d"),
            "platform": "ChatGPT",
            "prompt_id": row["prompt_id"],
            "category": row["category"],
            "prompt": row["prompt"],
            "wake_tech_mentioned": analysis["wake_tech_mentioned"],
            "position": analysis["position"],
            "competitors": analysis["competitors"],
            "wake_tech_url": analysis["wake_tech_url"],
            "competitor_urls": analysis["competitor_urls"],
            "score": analysis["score"],
            "notes": analysis["notes"],
            "response": response,
        })

    updated_results = pd.concat(
        [existing_results, pd.DataFrame(new_results)],
        ignore_index=True
    )

    updated_results.to_csv(RESULTS_FILE, index=False)

    print(f"Done. Added {len(new_results)} new results to {RESULTS_FILE}")


if __name__ == "__main__":
    main()