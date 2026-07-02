from datetime import datetime
import pandas as pd


def run_demo_scan():

    df = pd.read_csv("data/results.csv")

    now = datetime.now().strftime("%Y-%m-%d")

    df["run_date"] = now

    df.to_csv("data/results.csv", index=False)

    return {
        "scan_time": datetime.now().strftime("%I:%M %p"),
        "platforms": df["platform"].nunique(),
        "responses": len(df),
        "avg_score": round(df["score"].mean(), 1)
    }