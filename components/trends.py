import altair as alt
import pandas as pd
import streamlit as st


def show_trends(df):
    st.subheader("Visibility Trend")

    if df.empty:
        st.info("No historical scan data available yet.")
        return

    history = df.copy()
    history["run_date"] = pd.to_datetime(history["run_date"], errors="coerce")

    history = history.dropna(subset=["run_date", "scan_id", "score"])

    scan_trend = (
        history
        .groupby("scan_id")
        .agg(
            run_date=("run_date", "max"),
            average_visibility=("score", "mean")
        )
        .reset_index()
        .sort_values("run_date")
    )

    if len(scan_trend) < 2:
        st.info("Run at least two scans to begin tracking visibility trends.")
        return

    scan_trend["average_visibility"] = scan_trend["average_visibility"].round(1)

    scan_trend["scan_label"] = (
        scan_trend["run_date"].dt.strftime("%b %d, %I:%M %p")
    )

    chart = (
        alt.Chart(scan_trend)
        .mark_line(point=True)
        .encode(
            x=alt.X("scan_label:N", title="Scan"),
            y=alt.Y("average_visibility:Q", title="Visibility Score"),
            tooltip=[
                alt.Tooltip("scan_label:N", title="Scan"),
                alt.Tooltip("average_visibility:Q", title="Avg Visibility"),
            ],
        )
        .properties(height=360)
    )

    st.altair_chart(chart, use_container_width=True)

    first_score = scan_trend.iloc[0]["average_visibility"]
    latest_score = scan_trend.iloc[-1]["average_visibility"]

    total_change = round(latest_score - first_score, 1)

    if total_change > 0:
        st.success(f"Average AI visibility has improved by {total_change} points since tracking began.")
    elif total_change < 0:
        st.warning(f"Average AI visibility has declined by {abs(total_change)} points since tracking began.")
    else:
        st.info("Average AI visibility is unchanged since tracking began.")