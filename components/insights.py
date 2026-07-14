import pandas as pd
import plotly.graph_objects as go
import streamlit as st


INSTITUTION_COLORS = {
    "Wake Tech": "#FDB927",
    "Durham Tech": "#007A53",
    "Central Piedmont": "#005596",
    "NC State": "#CC0000",
    "UNC": "#7BAFD4",
    "Duke": "#012169",
    "Cape Fear": "#009639",
    "Pitt CC": "#005A9C",
    "GTCC": "#006747",
    "Forsyth Tech": "#00703C",
    "Fayetteville Tech": "#8C1D40",
    "Johnston Community College": "#5B2C6F",
}

DEFAULT_INSTITUTION_COLOR = "#5F6B7A"


def normalize_institution_name(
    institution: str,
) -> str:
    """
    Normalize institution names so charts use consistent labels
    and school colors.
    """
    name = str(institution).strip()

    replacements = {
        "Wake Technical Community College": "Wake Tech",
        "Wake Technical": "Wake Tech",
        "Durham Technical Community College": "Durham Tech",
        "Central Piedmont Community College": "Central Piedmont",
        "Central Piedmont Community College (CPCC)": (
            "Central Piedmont"
        ),
        "CPCC": "Central Piedmont",
        "North Carolina State University": "NC State",
        "NC State University": "NC State",
        "University of North Carolina at Chapel Hill": "UNC",
        "UNC-Chapel Hill": "UNC",
        "UNC Chapel Hill": "UNC",
        "Duke University School of Nursing": "Duke",
        "Duke University": "Duke",
        "Forsyth Technical Community College": "Forsyth Tech",
        "Guilford Technical Community College": "GTCC",
        "Cape Fear Community College": "Cape Fear",
        "Pitt Community College": "Pitt CC",
        "Fayetteville Technical Community College": (
            "Fayetteville Tech"
        ),
    }

    return replacements.get(name, name)


def institution_color(
    institution: str,
) -> str:
    """
    Return the configured color for an institution.
    """
    return INSTITUTION_COLORS.get(
        institution,
        DEFAULT_INSTITUTION_COLOR,
    )


def build_institution_counts(
    institution_rows: list[str],
    limit: int = 10,
) -> pd.DataFrame:
    """
    Convert institution mentions into a sorted count table.
    """
    institution_df = (
        pd.Series(institution_rows)
        .value_counts()
        .reset_index()
    )

    institution_df.columns = [
        "Institution",
        "Mentions",
    ]

    institution_df = institution_df.head(limit).copy()

    institution_df["Color"] = institution_df[
        "Institution"
    ].apply(institution_color)

    return institution_df


def build_horizontal_bar_chart(
    institution_df: pd.DataFrame,
    x_axis_title: str,
    height: int,
) -> go.Figure:
    """
    Build a horizontal Plotly bar chart with one color per school.
    """
    chart_df = institution_df.sort_values(
        "Mentions",
        ascending=True,
    )

    fig = go.Figure(
        go.Bar(
            x=chart_df["Mentions"],
            y=chart_df["Institution"],
            orientation="h",
            text=chart_df["Mentions"],
            textposition="outside",
            marker={
                "color": chart_df["Color"],
                "line": {
                    "color": "rgba(0, 0, 0, 0.12)",
                    "width": 1,
                },
            },
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Mentions: %{x}<extra></extra>"
            ),
        )
    )

    max_mentions = int(
        chart_df["Mentions"].max()
    )

    fig.update_layout(
        height=height,
        showlegend=False,
        margin={
            "l": 10,
            "r": 70,
            "t": 10,
            "b": 10,
        },
        plot_bgcolor="rgba(0, 0, 0, 0)",
        paper_bgcolor="rgba(0, 0, 0, 0)",
        xaxis={
            "title": x_axis_title,
            "showgrid": True,
            "gridcolor": "rgba(0, 0, 0, 0.08)",
            "zeroline": False,
            "range": [
                0,
                max_mentions * 1.12,
            ],
        },
        yaxis={
            "title": "",
            "showgrid": False,
        },
        font={
            "color": "#5D6B78",
        },
    )

    return fig


def show_competitors(
    df: pd.DataFrame,
) -> None:
    st.subheader("AI Competitive Share of Voice")

    st.caption(
        "Based on the currently selected AI responses. "
        "Multiple institutions may be mentioned within a "
        "single response."
    )

    institution_rows = []

    for _, row in df.iterrows():
        wake_mentioned = str(
            row.get(
                "wake_tech_mentioned",
                "",
            )
        ).strip().lower()

        if wake_mentioned == "yes":
            institution_rows.append(
                "Wake Tech"
            )

        competitors = row.get(
            "competitors"
        )

        if pd.isna(competitors):
            continue

        for competitor in str(
            competitors
        ).split("|"):
            competitor = normalize_institution_name(
                competitor
            )

            if competitor:
                institution_rows.append(
                    competitor
                )

    if not institution_rows:
        st.info(
            "No institution mentions were found "
            "for the current filters."
        )
        return

    institution_df = build_institution_counts(
        institution_rows
    )

    fig = build_horizontal_bar_chart(
        institution_df=institution_df,
        x_axis_title="Mentions",
        height=500,
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )

    wake_mentions = institution_df.loc[
        institution_df["Institution"]
        == "Wake Tech",
        "Mentions",
    ]

    top_competitor = (
        institution_df[
            institution_df["Institution"]
            != "Wake Tech"
        ]
        .sort_values(
            "Mentions",
            ascending=False,
        )
        .head(1)
    )

    if (
        not wake_mentions.empty
        and not top_competitor.empty
    ):
        wake_count = int(
            wake_mentions.iloc[0]
        )

        competitor_name = (
            top_competitor.iloc[0][
                "Institution"
            ]
        )

        competitor_count = int(
            top_competitor.iloc[0][
                "Mentions"
            ]
        )

        margin = wake_count - competitor_count

        if wake_count > competitor_count:
            st.success(
                f"Wake Tech currently owns the largest "
                f"AI share of voice with "
                f"**{wake_count} mentions**, leading "
                f"**{competitor_name}** by "
                f"**{margin} mention"
                f"{'s' if margin != 1 else ''}**."
            )

        elif wake_count == competitor_count:
            st.warning(
                f"Wake Tech is tied with "
                f"**{competitor_name}** at "
                f"**{wake_count} mentions**."
            )

        else:
            gap = competitor_count - wake_count

            st.warning(
                f"**{competitor_name}** currently leads "
                f"Wake Tech by **{gap} mention"
                f"{'s' if gap != 1 else ''}** "
                f"(**{competitor_count} vs. "
                f"{wake_count}**)."
            )

    elif not wake_mentions.empty:
        wake_count = int(
            wake_mentions.iloc[0]
        )

        st.success(
            f"Wake Tech was mentioned "
            f"**{wake_count} times**, and no competing "
            f"institutions were detected."
        )

    else:
        st.warning(
            "Wake Tech was not detected in the currently "
            "selected responses."
        )


def show_competitor_wins(
    df: pd.DataFrame,
) -> None:
    st.subheader(
        "Who AI Recommends Instead of Wake Tech"
    )

    st.caption(
        "For selected student questions where AI did not "
        "recommend Wake Tech, this chart shows which "
        "institutions were mentioned instead."
    )

    losses = df[
        df["wake_tech_mentioned"]
        .astype(str)
        .str.strip()
        .str.lower()
        == "no"
    ]

    if losses.empty:
        st.success(
            "Wake Tech was recommended in every "
            "currently selected AI response."
        )
        return

    competitor_rows = []

    for competitors in losses[
        "competitors"
    ].dropna():
        for competitor in str(
            competitors
        ).split("|"):
            competitor = normalize_institution_name(
                competitor
            )

            if competitor:
                competitor_rows.append(
                    competitor
                )

    if not competitor_rows:
        st.info(
            "Wake Tech was not recommended in some "
            "responses, but no alternative institutions "
            "were identified."
        )
        return

    competitor_df = build_institution_counts(
        competitor_rows
    )

    fig = build_horizontal_bar_chart(
        institution_df=competitor_df,
        x_axis_title=(
            "Times Mentioned When Wake Tech Was Omitted"
        ),
        height=450,
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )

    winner = competitor_df.sort_values(
        "Mentions",
        ascending=False,
    ).iloc[0]

    total_responses = len(df)
    missed_responses = len(losses)

    missed_percentage = (
        missed_responses
        / total_responses
        * 100
        if total_responses
        else 0
    )

    st.warning(
        f"Wake Tech was omitted from "
        f"**{missed_responses} of "
        f"{total_responses} responses** "
        f"({missed_percentage:.0f}%). "
        f"In those responses, "
        f"**{winner['Institution']}** appeared most "
        f"frequently with "
        f"**{int(winner['Mentions'])} mentions**."
    )


def show_insights(
    df: pd.DataFrame,
) -> None:
    st.subheader("Insights")

    if df.empty:
        st.info(
            "No results are available for the "
            "current filters."
        )
        return

    low_categories = (
        df.groupby(
            "category"
        )["score"]
        .mean()
        .reset_index()
        .sort_values(
            "score"
        )
        .head(3)
    )

    st.markdown(
        "#### Priority Opportunities"
    )

    for _, row in low_categories.iterrows():
        st.warning(
            f"**{row['category']}** is averaging "
            f"**{round(row['score'], 1)}** visibility. "
            "Review related pages for clearer program "
            "descriptions, stronger FAQs, comparison-friendly "
            "content, outcomes, costs, and structured data."
        )

    st.markdown(
        "#### Prompt-Level Issues"
    )

    opportunities = df[
        (
            df["wake_tech_mentioned"]
            .astype(str)
            .str.strip()
            .str.lower()
            == "no"
        )
        | (
            pd.to_numeric(
                df["score"],
                errors="coerce",
            )
            < 70
        )
    ].sort_values(
        "score"
    )

    if opportunities.empty:
        st.success(
            "No major prompt-level opportunities were "
            "found in the selected dataset."
        )
        return

    for _, row in opportunities.iterrows():
        competitors = (
            row["competitors"]
            if pd.notna(
                row["competitors"]
            )
            else "no clear competitors"
        )

        normalized_competitors = " • ".join(
            normalize_institution_name(
                competitor
            )
            for competitor in str(
                competitors
            ).split("|")
            if competitor.strip()
        )

        if not normalized_competitors:
            normalized_competitors = (
                "no clear competitors"
            )

        wake_mentioned = str(
            row.get(
                "wake_tech_mentioned",
                "",
            )
        ).strip().lower()

        if wake_mentioned == "no":
            message = (
                f"🚨 **{row['platform']}** did not "
                "recommend Wake Tech for this prompt.\n\n"
                f"Instead it mentioned "
                f"**{normalized_competitors}**.\n\n"
                "Recommendation: Compare Wake Tech's "
                "related content against the institutions "
                "AI is already surfacing. Strengthen "
                "program-specific evidence, outcomes, "
                "cost information, geographic relevance, "
                "FAQs, and structured data."
            )
        else:
            message = (
                f"⚠️ Wake Tech appeared in "
                f"**{row['platform']}**, but visibility "
                f"is weak "
                f"(Score: **{row['score']}**).\n\n"
                "Recommendation: Expand the page with "
                "plain-language answers, program outcomes, "
                "cost details, admissions steps, FAQs, "
                "comparison-friendly content, and "
                "schema-friendly structure."
            )

        with st.expander(
            f"{row['platform']} • "
            f"{row['category']} • "
            f"Score {row['score']}"
        ):
            st.markdown(
                message
            )