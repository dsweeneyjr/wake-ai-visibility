import pandas as pd
import streamlit as st


def show_charts(df, historical_df=None):
    left, right = st.columns(2)

    with left:
        st.subheader("Average Visibility by Platform")

        platform_scores = (
            df.groupby("platform")["score"]
            .mean()
            .reset_index()
            .sort_values("score", ascending=False)
        )

        st.bar_chart(platform_scores, x="platform", y="score")

        if historical_df is not None and not historical_df.empty:
            history = historical_df.copy()
            history["run_date"] = pd.to_datetime(history["run_date"], errors="coerce")

            scan_ids = (
                history[["scan_id", "run_date"]]
                .drop_duplicates()
                .sort_values("run_date")["scan_id"]
                .tolist()
            )

            if len(scan_ids) >= 2:
                current_scan_id = scan_ids[-1]
                previous_scan_id = scan_ids[-2]

                current = (
                    history[history["scan_id"] == current_scan_id]
                    .groupby("platform")["score"]
                    .mean()
                )

                previous = (
                    history[history["scan_id"] == previous_scan_id]
                    .groupby("platform")["score"]
                    .mean()
                )

                comparison = pd.DataFrame({
                    "Current": current,
                    "Previous": previous
                }).dropna()

                comparison["Change"] = comparison["Current"] - comparison["Previous"]
                comparison = comparison.reset_index()
                comparison["Current"] = comparison["Current"].round(1)
                comparison["Previous"] = comparison["Previous"].round(1)
                comparison["Change"] = comparison["Change"].round(1)

                st.caption("Change vs previous scan")
                st.dataframe(comparison, use_container_width=True, hide_index=True)

    with right:
        st.subheader("Average Visibility by Category")

        category_scores = (
            df.groupby("category")["score"]
            .mean()
            .reset_index()
            .sort_values("score", ascending=False)
        )

        st.bar_chart(category_scores, x="category", y="score")
        if historical_df is not None and not historical_df.empty:
            history = historical_df.copy()
            history["run_date"] = pd.to_datetime(history["run_date"], errors="coerce")

            scan_ids = (
                history[["scan_id", "run_date"]]
                .drop_duplicates()
                .sort_values("run_date")["scan_id"]
                .tolist()
            )

            if len(scan_ids) >= 2:
                current_scan_id = scan_ids[-1]
                previous_scan_id = scan_ids[-2]

                current = (
                    history[history["scan_id"] == current_scan_id]
                    .groupby("category")["score"]
                    .mean()
                )

                previous = (
                    history[history["scan_id"] == previous_scan_id]
                    .groupby("category")["score"]
                    .mean()
                )

                comparison = pd.DataFrame({
                   "Current": current,
                    "Previous": previous
                }).dropna()

                comparison["Change"] = comparison["Current"] - comparison["Previous"]
                comparison = comparison.reset_index()
                comparison["Current"] = comparison["Current"].round(1)
                comparison["Previous"] = comparison["Previous"].round(1)
                comparison["Change"] = comparison["Change"].round(1)

                st.caption("Change vs previous scan")
                st.dataframe(comparison, use_container_width=True, hide_index=True)