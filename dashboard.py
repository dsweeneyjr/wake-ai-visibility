import time
from pathlib import Path

import pandas as pd
import streamlit as st

from services.scan import run_live_scan
from components.executive_summary import show_executive_summary
from components.metrics import show_metrics
from components.charts import show_charts
from components.prompt_explorer import show_prompt_explorer
from components.insights import show_competitors, show_insights
from components.trends import show_trends
from components.styles import apply_wake_tech_style

st.set_page_config(
    page_title="Wake Tech AI Search Intelligence",
    layout="wide"
)
apply_wake_tech_style()

RESULTS_FILE = Path("data/results.csv")
df = pd.read_csv(RESULTS_FILE)
df["scan_id"] = df["scan_id"].astype(str)
df["_row_order"] = range(len(df))

df["run_date"] = pd.to_datetime(
    df["run_date"],
    errors="coerce",
)

if "run_timestamp" in df.columns:
    df["scan_sort_date"] = (
        pd.to_datetime(
            df["run_timestamp"],
            errors="coerce",
            utc=True,
        )
        .dt.tz_convert("America/New_York")
    )
else:
    df["scan_sort_date"] = df["run_date"]

missing_scan_dates = df["scan_sort_date"].isna()

fallback_dates = pd.to_datetime(
    df.loc[missing_scan_dates, "scan_id"]
    .astype(str)
    .str.replace("-", "", regex=False)
    .str[:14],
    format="%Y%m%d%H%M%S",
    errors="coerce",
)

df.loc[missing_scan_dates, "scan_sort_date"] = (
    fallback_dates
    .dt.tz_localize("America/New_York")
)

df["run_date"] = pd.to_datetime(
    df["run_date"],
    errors="coerce",
)

if "run_timestamp" in df.columns:
    df["scan_sort_date"] = (
        pd.to_datetime(
            df["run_timestamp"],
            errors="coerce",
            utc=True,
        )
        .dt.tz_convert("America/New_York")
    )
else:
    df["scan_sort_date"] = df["run_date"]

st.title("Wake Tech AI Search Intelligence")
st.caption(
    "Monitor how leading AI platforms recommend Wake Tech, "
    "identify visibility gaps, and track performance over time."
)
if "scan_message" in st.session_state:
    st.success(st.session_state["scan_message"])
    del st.session_state["scan_message"]

with st.sidebar:
    st.header("Filters")

    selected_platforms = st.multiselect(
        "AI Platforms",
        sorted(df["platform"].dropna().unique()),
        default=sorted(df["platform"].dropna().unique())
    )

    selected_categories = st.multiselect(
        "Categories",
        sorted(df["category"].dropna().unique()),
        default=sorted(df["category"].dropna().unique())
    )

filtered_all = df[
    df["platform"].isin(selected_platforms) &
    df["category"].isin(selected_categories)
]

with st.sidebar:
    show_history = st.checkbox("Show all historical runs", value=False)

if show_history:
    filtered = filtered_all
else:
    filtered = (
        filtered_all
        .sort_values("_row_order")
        .drop_duplicates(
            subset=["platform", "prompt_id"],
            keep="last"
        )
    )

valid_filtered_all = filtered_all[
    filtered_all["scan_sort_date"].notna()
].copy()

latest_scan_id = (
    valid_filtered_all
    .sort_values("_row_order")
    ["scan_id"]
    .iloc[-1]
    if not valid_filtered_all.empty
    else None
)

latest_scan = (
    valid_filtered_all[valid_filtered_all["scan_id"] == latest_scan_id]
    if latest_scan_id is not None
    else pd.DataFrame()
)

latest_date = (
    latest_scan["scan_sort_date"].max()
    if not latest_scan.empty
    else None
)

with st.container(border=True):
    st.markdown("### Executive Summary")
    st.write(
        "Track how AI platforms recommend Wake Tech, compare competitor visibility, "
        "identify content opportunities, and measure changes across repeated scans."
    )

    st.info(
        "Run a live visibility scan to ask OpenAI the monitored student questions "
        "and immediately analyze the results."
    )
    if latest_date is not None and pd.notna(latest_date):
        st.caption(f"Last scan: {latest_date.strftime('%b %d, %Y at %I:%M %p')}")
    else:
        st.caption("Last scan: Not available yet")

    scan_area = st.empty()

if st.button(
    "▶ Run Live Visibility Scan",
    type="primary",
    use_container_width=False,
):
    progress = scan_area.progress(0)
    status = st.empty()
    current_prompt_box = st.empty()
    scan_started = time.perf_counter()

    def update_scan_progress(
        completed: int,
        total: int,
        prompt_id: str,
        category: str,
        prompt_text: str,
    ) -> None:
        percent = int((completed / total) * 100) if total else 0
        display_number = min(completed + 1, total)
        elapsed = time.perf_counter() - scan_started

        progress.progress(
            percent,
            text=f"Scanning prompt {display_number} of {total}",
        )

        status.markdown(
            f"**OpenAI · GPT-5**  \n"
            f"Category: **{category}**  \n"
            f"Elapsed time: **{elapsed:.1f} seconds**"
        )

        current_prompt_box.info(
            f"**Current question**\n\n{prompt_text}"
        )

    try:
        with st.spinner("Running live AI visibility scan..."):
            scan = run_live_scan(
                progress_callback=update_scan_progress
            )

        elapsed = time.perf_counter() - scan_started

        progress.progress(
            100,
            text="Visibility scan complete",
        )

        current_prompt_box.empty()

        status.success(
            f"Completed {scan['responses']} live AI responses "
            f"in {elapsed:.1f} seconds."
        )

        st.session_state["scan_message"] = (
            f"Live scan complete. Added {scan['responses']} responses with "
            f"an average visibility score of {scan['avg_score']}. "
            f"OpenAI used {scan['total_tokens']:,} tokens."
        )

        st.rerun()

    except Exception as exc:
        progress.empty()
        status.empty()
        current_prompt_box.empty()

        st.error(
            "The live visibility scan could not be completed."
        )

        st.exception(exc)


with st.container(border=True):
    st.subheader("Latest Scan")

    col1, col2, col3, col4 = st.columns(4)

    if latest_scan.empty or pd.isna(latest_date):
        col1.metric("Latest Date", "N/A")
        col2.metric("Provider", "N/A")
        col3.metric("Responses", 0)
        col4.metric("Avg Score", 0)
    else:
        col1.metric(
            "Latest Date",
            latest_date.strftime("%b %d, %Y")
        )

        if "provider" in latest_scan.columns:
            providers = (
                latest_scan["provider"]
                .dropna()
                .astype(str)
                .str.title()
                .unique()
            )
            provider_display = ", ".join(providers) or "OpenAI"
        else:
            provider_display = ", ".join(
                latest_scan["platform"]
                .dropna()
                .astype(str)
                .unique()
            )

        col2.metric(
            "Provider",
            provider_display
        )

        col3.metric(
            "Responses",
            len(latest_scan)
        )

        col4.metric(
            "Avg Score",
            round(latest_scan["score"].mean(), 1)
        )

st.subheader("Latest AI Responses")

if latest_scan.empty:
    st.info("Run a live visibility scan to view AI responses.")
else:
    response_rows = latest_scan.sort_values(
        ["category", "prompt_id"]
    )

    for _, response_row in response_rows.iterrows():
        category = str(response_row.get("category", "Uncategorized"))
        prompt_id = str(response_row.get("prompt_id", ""))
        score = response_row.get("score", 0)
        prompt_text = str(response_row.get("prompt", ""))
        response_text = str(response_row.get("response", ""))

        latency = response_row.get("latency_seconds")
        total_tokens = response_row.get("total_tokens")
        model = str(response_row.get("model", "OpenAI"))

        expander_title = (
            f"{category} · Score {score}"
        )

        with st.expander(expander_title):
            st.markdown("#### Student question")
            st.write(prompt_text)

            st.markdown("#### AI response")
            st.write(response_text)

            metric1, metric2, metric3 = st.columns(3)

            metric1.metric(
                "Score",
                score
            )

            if pd.notna(latency):
                metric2.metric(
                    "Latency",
                    f"{float(latency):.1f} sec"
                )
            else:
                metric2.metric(
                    "Latency",
                    "N/A"
                )

            if pd.notna(total_tokens):
                metric3.metric(
                    "Tokens",
                    f"{int(total_tokens):,}"
                )
            else:
                metric3.metric(
                    "Tokens",
                    "N/A"
                )

            st.caption(
                f"Prompt ID: {prompt_id} · Model: {model}"
            )

show_executive_summary(filtered)

st.divider()
try:
    show_metrics(filtered, filtered_all)
except TypeError:
    show_metrics(filtered)

st.divider()
show_charts(filtered, filtered_all)

st.divider()
show_trends(filtered_all)

st.divider()
show_prompt_explorer(filtered)

st.divider()
show_competitors(filtered)

st.divider()
show_insights(filtered)

st.divider()

with st.expander("View Results Data"):
    st.dataframe(filtered, width="stretch")