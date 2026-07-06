from datetime import datetime
from pathlib import Path

import pandas as pd


RESULTS_FILE = Path("data/results.csv")


def run_demo_scan():
    df = pd.read_csv(RESULTS_FILE)

    now = datetime.now()
    scan_id = now.strftime("%Y%m%d%H%M%S%f")
    today = now.strftime("%Y-%m-%d")

    if "scan_id" not in df.columns:
        df["scan_id"] = df["run_date"].astype(str)

    latest_rows = (
        df.sort_values(["run_date", "scan_id"])
        .drop_duplicates(
            subset=["platform", "prompt_id"],
            keep="last"
        )
        .copy()
    )

    latest_rows["scan_id"] = scan_id
    latest_rows["run_date"] = today
    latest_rows["score"] = latest_rows["score"].apply(
        lambda x: min(100, max(0, int(x) + 3))
    )

    updated = pd.concat([df, latest_rows], ignore_index=True)
    updated.to_csv(RESULTS_FILE, index=False)

    return {
        "scan_id": scan_id,
        "scan_date": today,
        "platforms": latest_rows["platform"].nunique(),
        "responses": len(latest_rows),
        "avg_score": round(latest_rows["score"].mean(), 1),
    }