import pandas as pd
import streamlit as st


def show_metrics(df, historical_df=None):

    col1, col2, col3, col4 = st.columns(4)

    avg_score = round(df["score"].mean(), 1) if not df.empty else 0

    mention_rate = (
        round((df["wake_tech_mentioned"] == "Yes").mean() * 100, 1)
        if not df.empty
        else 0
    )

    prompts = df["prompt_id"].nunique()
    platforms = df["platform"].nunique()

    score_delta = None
    mention_delta = None

    if historical_df is not None and not historical_df.empty:

        history = historical_df.copy()

        history["run_date"] = pd.to_datetime(
            history["run_date"],
            errors="coerce"
        )

        scan_summary = (
            history
            .groupby("scan_id")
            .agg(
                run_date=("run_date", "max"),
                avg_score=("score", "mean"),
                mention_rate=(
                    "wake_tech_mentioned",
                    lambda x: (x == "Yes").mean() * 100
                )
            )
            .sort_values("run_date")
        )

        if len(scan_summary) >= 2:
            current_scan = scan_summary.iloc[-1]
            previous_scan = scan_summary.iloc[-2]

            score_delta = round(
                current_scan["avg_score"] - previous_scan["avg_score"],
                1
            )

            mention_delta = round(
                current_scan["mention_rate"] - previous_scan["mention_rate"],
                1
            )

    col1.metric(
        "Average Visibility",
        avg_score,
        delta=score_delta
    )

    col2.metric(
        "Mention Rate",
        f"{mention_rate}%",
        delta=f"{mention_delta} pts" if mention_delta is not None else None
    )

    col3.metric(
        "Prompts",
        prompts
    )

    col4.metric(
        "AI Platforms",
        platforms
    )