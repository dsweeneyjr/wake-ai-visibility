import altair as alt
import pandas as pd
import streamlit as st


def _prepare_history(df):
    if df.empty:
        return pd.DataFrame()

    history = df.copy()

    history["scan_id"] = history["scan_id"].astype(str)
    history["run_date"] = pd.to_datetime(
        history["run_date"],
        errors="coerce"
    )
    history["score"] = pd.to_numeric(
        history["score"],
        errors="coerce"
    )

    history = history.dropna(
        subset=["run_date", "scan_id", "score"]
    )

    return history


def get_latest_scan(df):
    history = _prepare_history(df)

    if history.empty:
        return pd.DataFrame()

    latest_scan_id = (
        history
        .sort_values(["run_date", "scan_id"])
        .iloc[-1]["scan_id"]
    )

    return history[
        history["scan_id"] == latest_scan_id
    ].copy()


def get_previous_scan(df):
    history = _prepare_history(df)

    if history.empty:
        return pd.DataFrame()

    scans = (
        history[["scan_id", "run_date"]]
        .drop_duplicates()
        .sort_values(["run_date", "scan_id"])
    )

    if len(scans) < 2:
        return pd.DataFrame()

    previous_scan_id = scans.iloc[-2]["scan_id"]

    return history[
        history["scan_id"] == previous_scan_id
    ].copy()


def get_category_trends(df):
    latest = get_latest_scan(df)
    previous = get_previous_scan(df)

    if latest.empty or previous.empty:
        return pd.DataFrame()

    latest_avg = (
        latest.groupby("category")["score"]
        .mean()
        .rename("latest")
    )

    previous_avg = (
        previous.groupby("category")["score"]
        .mean()
        .rename("previous")
    )

    trends = pd.concat(
        [latest_avg, previous_avg],
        axis=1
    ).dropna()

    trends["change"] = (
        trends["latest"] - trends["previous"]
    )

    return (
        trends
        .reset_index()
        .sort_values("change", ascending=False)
    )


def get_platform_trends(df):
    latest = get_latest_scan(df)
    previous = get_previous_scan(df)

    if latest.empty or previous.empty:
        return pd.DataFrame()

    latest_avg = (
        latest.groupby("platform")["score"]
        .mean()
        .rename("latest")
    )

    previous_avg = (
        previous.groupby("platform")["score"]
        .mean()
        .rename("previous")
    )

    trends = pd.concat(
        [latest_avg, previous_avg],
        axis=1
    ).dropna()

    trends["change"] = (
        trends["latest"] - trends["previous"]
    )

    return (
        trends
        .reset_index()
        .sort_values("change", ascending=False)
    )


def show_trends(df):
    st.subheader("Visibility Trend")

    history = _prepare_history(df)

    if history.empty:
        st.info("No historical scan data available yet.")
        return

    scan_trend = (
        history
        .groupby("scan_id", as_index=False)
        .agg(
            run_date=("run_date", "max"),
            average_visibility=("score", "mean")
        )
        .sort_values(["run_date", "scan_id"])
    )

    if len(scan_trend) < 2:
        st.info(
            "Run at least two scans to begin tracking visibility trends."
        )
        return

    scan_trend["average_visibility"] = (
        scan_trend["average_visibility"]
        .round(1)
        .astype(float)
    )

    scan_trend["scan_label"] = (
        scan_trend["run_date"]
        .dt.strftime("%b %d, %I:%M %p")
    )

    chart_data = scan_trend[
        [
            "scan_label",
            "average_visibility"
        ]
    ].copy()

    chart = (
        alt.Chart(chart_data)
        .mark_line(point=True)
        .encode(
            x=alt.X(
                "scan_label:N",
                title="Scan",
                sort=None
            ),
            y=alt.Y(
                "average_visibility:Q",
                title="Visibility Score",
                scale=alt.Scale(
                    domain=[
                        max(
                            0,
                            chart_data[
                                "average_visibility"
                            ].min() - 5
                        ),
                        min(
                            100,
                            chart_data[
                                "average_visibility"
                            ].max() + 5
                        )
                    ]
                )
            ),
            tooltip=[
                alt.Tooltip(
                    "scan_label:N",
                    title="Scan"
                ),
                alt.Tooltip(
                    "average_visibility:Q",
                    title="Avg Visibility",
                    format=".1f"
                ),
            ],
        )
        .properties(height=360)
    )

    st.altair_chart(
        chart,
        use_container_width=True
    )

    first_score = float(
        scan_trend.iloc[0]["average_visibility"]
    )
    latest_score = float(
        scan_trend.iloc[-1]["average_visibility"]
    )

    total_change = round(
        latest_score - first_score,
        1
    )

    if total_change > 0:
        st.success(
            f"Average AI visibility has improved by "
            f"{total_change} points since tracking began."
        )
    elif total_change < 0:
        st.warning(
            f"Average AI visibility has declined by "
            f"{abs(total_change)} points since tracking began."
        )
    else:
        st.info(
            "Average AI visibility is unchanged since tracking began."
        )