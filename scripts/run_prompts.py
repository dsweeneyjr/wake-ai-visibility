import os
from datetime import datetime
from pathlib import Path

import pandas as pd
from openai import OpenAI


BASE_DIR = Path(__file__).resolve().parent.parent
PROMPTS_FILE = BASE_DIR / "prompts" / "prompts.csv"
OUTPUT_FILE = BASE_DIR / "output" / "results.csv"

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def ask_openai(prompt):
    response = client.responses.create(
        model="gpt-4.1-mini",
        input=f"""
You are answering as an AI search assistant.

Question:
{prompt}
"""
    )
    return response.output_text


def main():
    prompts = pd.read_csv(PROMPTS_FILE)
    results = []

    for _, row in prompts.iterrows():
        print(f"Running {row['prompt_id']}...")

        answer = ask_openai(row["prompt"])

        results.append({
            "run_date": datetime.now().strftime("%Y-%m-%d"),
            "model": "gpt-4.1-mini",
            "prompt_id": row["prompt_id"],
            "category": row["category"],
            "priority": row["priority"],
            "prompt": row["prompt"],
            "response": answer
        })

    df = pd.DataFrame(results)
    df.to_csv(OUTPUT_FILE, index=False)

    print(f"Done. Saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()