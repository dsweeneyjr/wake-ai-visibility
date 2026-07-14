from datetime import datetime
from html import escape
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd
import streamlit as st

from components.styles import apply_wake_tech_style
from services.evaluator import evaluate_response
from services.optimizer import optimize_and_score


RESULTS_FILE = Path("data/results.csv")
PROMPTS_FILE = Path("prompts/prompts.csv")


st.set_page_config(
    page_title="AI Search Visibility Analyzer",
    layout="wide",
)

apply_wake_tech_style()


st.markdown(
    """
    <style>
        .visibility-score-card {
            border-radius: 14px;
            padding: 28px 30px;
            margin: 12px 0 20px 0;
            border: 1px solid rgba(0, 0, 0, 0.08);
        }

        .visibility-score-label {
            font-size: 0.95rem;
            font-weight: 700;
            letter-spacing: 0.04em;
            text-transform: uppercase;
            opacity: 0.75;
            margin-bottom: 4px;
        }

        .visibility-score-value {
            font-size: 4.5rem;
            line-height: 1;
            font-weight: 800;
            margin: 0;
        }

        .visibility-score-max {
            font-size: 1.35rem;
            font-weight: 600;
            opacity: 0.65;
        }

        .score-excellent {
            background: #e8f5ec;
            border-left: 8px solid #218739;
        }

        .score-strong {
            background: #e8f2fb;
            border-left: 8px solid #2167a6;
        }

        .score-moderate {
            background: #fff6dc;
            border-left: 8px solid #d99a00;
        }

        .score-weak {
            background: #fdeaea;
            border-left: 8px solid #c83f49;
        }

        .school-pill{
            display:inline-block;
            padding:7px 14px;
            margin:4px 6px 4px 0;
            border-radius:999px;
            font-size:.88rem;
            font-weight:700;
            border:1px solid rgba(0,0,0,.08);
            box-shadow:0 1px 2px rgba(0,0,0,.08);
        }

        .school-pill.wake-tech{
            background:#FFC72C;
            color:#111;
        }

        .school-pill.nc-state{
            background:#CC0000;
            color:#fff;
        }

        .school-pill.duke{
            background:#012169;
            color:#fff;
        }

        .school-pill.unc{
            background:#7BAFD4;
            color:#000;
        }

        .school-pill.durham-tech{
            background:#007A53;
            color:#fff;
        }

        .school-pill.central-piedmont{
            background:#005596;
            color:#fff;
        }

        .school-pill.default{
            background:#dfe6ec;
            color:#17324d;
        }

        .overall-assessment {
            border-radius: 12px;
            padding: 22px 24px;
            margin: 20px 0;
            border-left: 7px solid #0a5f88;
            background: #edf7fb;
        }

        .overall-assessment-label {
            font-size: 0.85rem;
            font-weight: 800;
            letter-spacing: 0.05em;
            text-transform: uppercase;
            color: #0a5f88;
            margin-bottom: 7px;
        }

        .overall-assessment-text {
            font-size: 1.35rem;
            line-height: 1.4;
            font-weight: 700;
            color: #12334e;
        }

        .recommendation-item {
            display: flex;
            gap: 14px;
            align-items: flex-start;
            background: #eaf3fb;
            border-radius: 9px;
            padding: 14px 16px;
            margin-bottom: 10px;
        }

        .recommendation-number {
            display: flex;
            align-items: center;
            justify-content: center;
            min-width: 30px;
            height: 30px;
            border-radius: 50%;
            background: #0b466f;
            color: white;
            font-weight: 800;
            font-size: 0.85rem;
        }

        .recommendation-text {
            padding-top: 4px;
            line-height: 1.45;
        }

        .optimized-score {
            font-size: 2.8rem;
            font-weight: 800;
            line-height: 1;
            color: #0b466f;
        }

        .optimized-score-label {
            font-size: 0.85rem;
            font-weight: 700;
            opacity: 0.7;
            text-transform: uppercase;
            margin-bottom: 6px;
        }

        .rewritten-response {
            background: #f7f9fb;
            border: 1px solid #dce3ea;
            border-radius: 10px;
            padding: 22px;
            line-height: 1.65;
            white-space: pre-wrap;
        }
        .workflow-card {
            display: flex;
            align-items: stretch;
            justify-content: space-between;
            gap: 12px;
            padding: 20px;
            margin: 18px 0;
            border-radius: 12px;
            background: #f4f7fa;
            border: 1px solid #dce3ea;
        }

        .workflow-step {
            flex: 1;
            min-width: 0;
            padding: 14px 10px;
            text-align: center;
            border-radius: 10px;
            background: #ffffff;
            border: 1px solid #dce3ea;
        }

        .workflow-number {
           display: flex;
            align-items: center;
            justify-content: center;
            width: 32px;
            height: 32px;
            margin: 0 auto 8px auto;
            border-radius: 50%;
            background: #0b466f;
            color: #ffffff;
            font-weight: 800;
        }

        .workflow-label {
            color: #12334e;
            font-size: 0.9rem;
            font-weight: 700;
            line-height: 1.3;
        }

        .workflow-arrow {
            display: flex;
            align-items: center;
            justify-content: center;
            color: #0b466f;
            font-size: 1.6rem;
            font-weight: 800;
        }

        @media (max-width: 900px) {
            .workflow-card {
                flex-direction: column;
            }

            .workflow-arrow {
               transform: rotate(90deg);
            }
        }
    </style>
    """,
    unsafe_allow_html=True,
)


st.title("AI Search Visibility Analyzer")

st.markdown(
    """
    Measure how AI platforms recommend Wake Tech, compare our visibility against competing colleges, and identify the website improvements most likely to increase AI visibility.
    """
)

with st.container(border=True):
    st.markdown("### How to Use This Page")

    step1, step2, step3, step4 = st.columns(4)

    with step1:
        st.markdown("#### 1. Select")
        st.write(
            "Choose one of the monitored student questions."
        )

    with step2:
        st.markdown("#### 2. Paste")
        st.write(
            "Paste the complete response from an AI platform."
        )

    with step3:
        st.markdown("#### 3. Evaluate")
        st.write(
            "Measure Wake Tech's current visibility, rank, "
            "sentiment, and competitor mentions."
        )

    with step4:
        st.markdown("#### 4. Improve")
        st.write(
            "Generate an AI benchmark and specific website "
            "content recommendations."
        )

st.info(
    "The Original Response is not intended to be copied "
    "directly onto the website. It demonstrates the type of "
    "answer we want AI platforms to generate after Wake Tech's "
    "website content has been strengthened."
)


def load_csv(file_path: Path) -> pd.DataFrame:
    """
    Safely load a CSV file.
    """
    try:
        return pd.read_csv(file_path)
    except pd.errors.EmptyDataError:
        return pd.DataFrame()
    except FileNotFoundError:
        st.error(
            f"Required file was not found: {file_path}"
        )
        st.stop()


def normalize_string_list(value) -> list[str]:
    """
    Ensure evaluator values are returned as a clean list.
    """
    if value is None:
        return []

    if isinstance(value, list):
        return [
            str(item).strip()
            for item in value
            if str(item).strip()
        ]

    if isinstance(value, str):
        value = value.strip()

        if not value:
            return []

        if "|" in value:
            return [
                item.strip()
                for item in value.split("|")
                if item.strip()
            ]

        return [value]

    return [str(value).strip()]


def normalize_analysis(raw_analysis) -> dict:
    """
    Normalize the evaluator response for display and saving.
    """
    if not isinstance(raw_analysis, dict):
        raise ValueError(
            "The evaluator did not return a valid result."
        )

    wake_mentioned = raw_analysis.get(
        "wake_mentioned",
        False,
    )

    if isinstance(wake_mentioned, str):
        wake_mentioned = (
            wake_mentioned.strip().lower()
            in {"yes", "true", "1"}
        )
    else:
        wake_mentioned = bool(wake_mentioned)

    try:
        wake_rank = int(
            raw_analysis.get(
                "wake_rank",
                0,
            )
        )
    except (TypeError, ValueError):
        wake_rank = 0

    try:
        score = int(
            round(
                float(
                    raw_analysis.get(
                        "score",
                        0,
                    )
                )
            )
        )
    except (TypeError, ValueError):
        score = 0

    score = max(0, min(score, 100))

    sentiment = str(
        raw_analysis.get(
            "sentiment",
            "neutral",
        )
    ).strip().lower()

    if sentiment not in {
        "positive",
        "neutral",
        "negative",
        "mixed",
    }:
        sentiment = "neutral"

    return {
        "wake_mentioned": wake_mentioned,
        "wake_rank": max(0, wake_rank),
        "competitors": normalize_string_list(
            raw_analysis.get(
                "competitors",
                [],
            )
        ),
        "wake_tech_urls": normalize_string_list(
            raw_analysis.get(
                "wake_tech_urls",
                [],
            )
        ),
        "competitor_urls": normalize_string_list(
            raw_analysis.get(
                "competitor_urls",
                [],
            )
        ),
        "score": score,
        "sentiment": sentiment,
        "strengths": normalize_string_list(
            raw_analysis.get(
                "strengths",
                [],
            )
        ),
        "weaknesses": normalize_string_list(
            raw_analysis.get(
                "weaknesses",
                [],
            )
        ),
        "recommendations": normalize_string_list(
            raw_analysis.get(
                "recommendations",
                [],
            )
        ),
        "overall_assessment": str(
            raw_analysis.get(
                "overall_assessment",
                "",
            )
        ).strip(),
        "metadata": raw_analysis.get(
            "metadata",
            {},
        ),
    }


def get_score_class(score: int) -> str:
    """
    Return the CSS class associated with a score band.
    """
    if score >= 90:
        return "score-excellent"

    if score >= 70:
        return "score-strong"

    if score >= 50:
        return "score-moderate"

    return "score-weak"


def display_score_card(score: int) -> None:
    """
    Display the primary visibility score.
    """
    score_class = get_score_class(score)

    st.markdown(
        f"""
        <div class="visibility-score-card {score_class}">
            <div class="visibility-score-label">
                AI Visibility Score
            </div>
            <div>
                <span class="visibility-score-value">
                    {score}
                </span>
                <span class="visibility-score-max">
                    / 100
                </span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def display_institution_pills(
    competitors: list[str],
    wake_mentioned: bool,
) -> None:
    """
    Display Wake Tech and competing institutions using
    recognizable school brand colors.
    """

    st.markdown("#### Institutions Mentioned")

    institutions = []

    if wake_mentioned:
        institutions.append(
            "Wake Technical Community College"
        )

    institutions.extend(competitors)

    if not institutions:
        st.caption(
            "No institutions were detected in the response."
        )
        return

    school_classes = {
        "wake technical community college": "wake-tech",
        "wake tech": "wake-tech",
        "nc state university": "nc-state",
        "nc state": "nc-state",
        "north carolina state university": "nc-state",
        "north carolina state": "nc-state",
        "duke university": "duke",
        "duke university school of nursing": "duke",
        "university of north carolina at chapel hill": "unc",
        "unc-chapel hill": "unc",
        "unc chapel hill": "unc",
        "unc": "unc",
        "durham technical community college": "durham-tech",
        "durham tech": "durham-tech",
        "central piedmont community college": "central-piedmont",
        "central piedmont": "central-piedmont",
        "cpcc": "central-piedmont",
    }

    pills = []

    for institution in institutions:
        normalized_name = institution.strip().lower()

        css_class = school_classes.get(
            normalized_name,
            "default",
        )

        pills.append(
            f'<span class="school-pill {css_class}">'
            f"{escape(institution)}"
            "</span>"
        )

    st.markdown(
        "".join(pills),
        unsafe_allow_html=True,
    )


def display_recommendations(
    recommendations: list[str],
) -> None:
    """
    Display recommendations as a numbered sequence.
    """
    st.markdown("### Recommended Improvements")

    if not recommendations:
        st.info(
            "No additional improvements were recommended."
        )
        return

    for index, recommendation in enumerate(
        recommendations,
        start=1,
    ):
        st.markdown(
            f"""
            <div class="recommendation-item">
                <div class="recommendation-number">
                    {index}
                </div>
                <div class="recommendation-text">
                    {escape(recommendation)}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def display_assessment(
    analysis: dict,
) -> None:
    """
    Display a prominent overall assessment.
    """
    assessment = analysis.get(
        "overall_assessment",
        "",
    )

    if not assessment:
        score = analysis["score"]

        if score >= 90:
            assessment = (
                "Wake Tech has excellent visibility "
                "in this response."
            )
        elif score >= 70:
            assessment = (
                "Wake Tech has strong visibility "
                "in this response."
            )
        elif score >= 50:
            assessment = (
                "Wake Tech has moderate visibility "
                "but needs stronger positioning."
            )
        else:
            assessment = (
                "Wake Tech has weak visibility "
                "in this response."
            )

    st.markdown(
        f"""
        <div class="overall-assessment">
            <div class="overall-assessment-label">
                Overall Assessment
            </div>
            <div class="overall-assessment-text">
                {escape(assessment)}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def display_analysis(
    analysis: dict,
) -> None:
    """
    Display the latest response analysis.
    """
    st.divider()
    st.subheader("Visibility Analysis")

    display_score_card(
        analysis["score"]
    )

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Wake Tech Mentioned",
        (
            "Yes"
            if analysis["wake_mentioned"]
            else "No"
        ),
    )

    col2.metric(
        "Detected Position",
        (
            f"#{analysis['wake_rank']}"
            if analysis["wake_rank"] > 0
            else "Not Recommended"
        ),
    )

    col3.metric(
        "Sentiment",
        analysis["sentiment"].title(),
    )

    display_institution_pills(
        competitors=analysis["competitors"],
        wake_mentioned=analysis["wake_mentioned"],
    )

    st.markdown("### Evaluation Details")

    strengths_col, weaknesses_col = st.columns(2)

    with strengths_col:
        st.markdown("#### Strengths")

        if analysis["strengths"]:
            for item in analysis["strengths"]:
                st.success(item)
        else:
            st.info(
                "No specific strengths identified."
            )

    with weaknesses_col:
        st.markdown("#### Weaknesses")

        if analysis["weaknesses"]:
            for item in analysis["weaknesses"]:
                st.warning(item)
        else:
            st.success(
                "No major visibility weaknesses identified."
            )

    display_recommendations(
        analysis["recommendations"]
    )

    display_assessment(analysis)

    with st.expander("View analyzed response"):
        st.write(
            st.session_state.get(
                "latest_response",
                "",
            )
        )

def display_website_recommendations(
    recommendations: list[dict],
) -> None:
    """
    Display specific actions for the Wake Tech web and
    content teams.
    """
    st.markdown("### Website Changes Needed")

    st.caption(
        "The Original Response is not intended to be "
        "copied onto the website. These recommendations "
        "translate the benchmark into specific content work."
    )

    if not recommendations:
        st.info(
            "No specific website changes were generated."
        )
        return

    priority_order = {
        "High": 0,
        "Medium": 1,
        "Low": 2,
    }

    sorted_recommendations = sorted(
        recommendations,
        key=lambda item: priority_order.get(
            str(item.get("priority", "Medium")),
            1,
        ),
    )

    for index, recommendation in enumerate(
        sorted_recommendations,
        start=1,
    ):
        priority = str(
            recommendation.get(
                "priority",
                "Medium",
            )
        ).strip()

        page_or_section = str(
            recommendation.get(
                "page_or_section",
                "",
            )
        ).strip()

        recommended_change = str(
            recommendation.get(
                "recommended_change",
                "",
            )
        ).strip()

        reason = str(
            recommendation.get(
                "reason",
                "",
            )
        ).strip()

        evidence_needed = str(
            recommendation.get(
                "evidence_needed",
                "",
            )
        ).strip()

        heading = (
            f"{index}. {page_or_section}"
            if page_or_section
            else f"{index}. Website Content Update"
        )

        with st.container(border=True):
            heading_col, priority_col = st.columns(
                [5, 1]
            )

            heading_col.markdown(
                f"#### {heading}"
            )

            if priority == "High":
                priority_col.error("HIGH")
            elif priority == "Low":
                priority_col.info("LOW")
            else:
                priority_col.warning("MEDIUM")

            st.markdown("**Recommended change**")
            st.write(recommended_change)

            if reason:
                st.markdown("**Why this matters**")
                st.write(reason)

            if evidence_needed:
                st.markdown(
                    "**Verify before publishing**"
                )
                st.warning(evidence_needed)

def display_optimized_response(
    optimization_result: dict,
) -> None:
    """
    Display the optimized response with verified before-and-after
    scores from the same evaluator.
    """
    st.divider()
    st.subheader("AI Benchmark and Verified Improvement")

    original_score = optimization_result[
        "original_score"
    ]

    optimized_score = optimization_result[
        "optimized_score"
    ]

    score_change = optimization_result[
        "score_change"
    ]

    original_rank = optimization_result[
        "original_rank"
    ]

    optimized_rank = optimization_result[
        "optimized_rank"
    ]

    score_col1, arrow_col, score_col2, change_col = (
        st.columns([2, 1, 2, 2])
    )

    with score_col1:
        st.markdown(
            """
            <div class="optimized-score-label">
                Original Score
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
            <div class="optimized-score">
                {original_score}/100
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.caption(
            (
                f"Original rank: #{original_rank}"
                if original_rank > 0
                else "Original rank: Not recommended"
            )
        )

    with arrow_col:
        st.markdown(
            """
            <div style="
                font-size: 3rem;
                text-align: center;
                padding-top: 20px;
            ">
                →
            </div>
            """,
            unsafe_allow_html=True,
        )

    with score_col2:
        st.markdown(
            """
            <div class="optimized-score-label">
                Verified Benchmark Response Score
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
            <div class="optimized-score">
                {optimized_score}/100
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.caption(
            (
                f"Optimized rank: #{optimized_rank}"
                if optimized_rank > 0
                else "Optimized rank: Not recommended"
            )
        )

    with change_col:
        st.metric(
            "Verified Improvement",
            f"{score_change:+d} points",
        )

        if (
            original_rank > 0
            and optimized_rank > 0
        ):
            rank_change = (
                original_rank - optimized_rank
            )

            if rank_change > 0:
                st.success(
                    f"Improved by {rank_change} "
                    f"ranking position"
                    f"{'s' if rank_change != 1 else ''}."
                )
            elif rank_change == 0:
                st.info(
                    "Recommendation rank stayed the same."
                )
            else:
                st.warning(
                    "Recommendation rank decreased."
                )

    if score_change > 0:
        st.success(
            "The rewritten response received a higher score "
            "when evaluated with the same scoring system."
        )
    elif score_change == 0:
        st.info(
            "The rewritten response received the same score "
            "as the original."
        )
    else:
        st.warning(
            "The rewritten response scored lower than the original."
        )

    improvement_summary = optimization_result.get(
        "improvement_summary",
        [],
    )

    if improvement_summary:
        st.markdown("#### What Changed")

        for item in improvement_summary:
            st.success(item)

    rationale = optimization_result.get(
        "optimization_rationale",
        "",
    )

    if rationale:
        st.markdown("#### Why the Benchmark Performs Better")
        st.info(rationale)

    website_recommendations = (
        optimization_result.get(
            "website_recommendations",
            [],
        )
    )

    display_website_recommendations(
        website_recommendations
    )

    original_tab, optimized_tab, evaluation_tab = st.tabs(
        [
            "Original Response",
            "Optimized Response",
            "Optimization Results",
        ]
    )

    with original_tab:
        st.text_area(
            "Original response",
            value=optimization_result[
                "original_response"
            ],
            height=420,
            disabled=True,
            label_visibility="collapsed",
        )

    with optimized_tab:
        st.text_area(
            "Original Response",
            value=optimization_result[
                "optimized_response"
            ],
            height=420,
            key="optimized_response_text",
            label_visibility="collapsed",
        )

    with evaluation_tab:
        optimized_analysis = optimization_result[
            "optimized_analysis"
        ]

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Wake Tech Mentioned",
            (
                "Yes"
                if optimized_analysis.get(
                    "wake_mentioned",
                    False,
                )
                else "No"
            ),
        )

        optimized_analysis_rank = optimized_analysis.get(
            "wake_rank",
            0,
        )

        col2.metric(
            "Recommendation Rank",
            (
                f"#{optimized_analysis_rank}"
                if optimized_analysis_rank > 0
                else "Not Recommended"
            ),
        )

        col3.metric(
            "Sentiment",
            str(
                optimized_analysis.get(
                    "sentiment",
                    "neutral",
                )
            ).title(),
        )

        optimized_assessment = optimized_analysis.get(
            "overall_assessment",
            "",
        )

        if optimized_assessment:
            st.info(optimized_assessment)

        optimized_strengths = optimized_analysis.get(
            "strengths",
            [],
        )

        optimized_weaknesses = optimized_analysis.get(
            "weaknesses",
            [],
        )

        strengths_col, weaknesses_col = st.columns(2)

        with strengths_col:
            st.markdown("#### Verified Strengths")

            if optimized_strengths:
                for item in optimized_strengths:
                    st.success(item)
            else:
                st.info(
                    "No specific strengths identified."
                )

        with weaknesses_col:
            st.markdown("#### Remaining Weaknesses")

            if optimized_weaknesses:
                for item in optimized_weaknesses:
                    st.warning(item)
            else:
                st.success(
                    "No major visibility weaknesses identified."
                )


prompts = load_csv(PROMPTS_FILE)
results = load_csv(RESULTS_FILE)


required_prompt_columns = {
    "prompt_id",
    "category",
    "prompt",
}

missing_prompt_columns = (
    required_prompt_columns
    - set(prompts.columns)
)

if missing_prompt_columns:
    st.error(
        "The prompts file is missing these columns: "
        + ", ".join(
            sorted(missing_prompt_columns)
        )
    )
    st.stop()


prompt_choices = {
    (
        f"{row['prompt_id']} — "
        f"{row['category']} — "
        f"{row['prompt']}"
    ): row.to_dict()
    for _, row in prompts.iterrows()
}

selected_prompt_label = st.selectbox(
    "Select Prompt",
    list(prompt_choices.keys()),
)

selected_prompt = prompt_choices[
    selected_prompt_label
]

platform = st.selectbox(
    "AI Platform",
    [
        "ChatGPT",
        "Gemini",
        "Perplexity",
        "Copilot",
        "Claude",
        "Other",
    ],
)

st.markdown("### Response to Evaluate")

st.caption(
    "Paste the complete AI response exactly as it was generated. "
    "Keep all competitor recommendations, rankings, links, and "
    "supporting details so the analysis reflects the full answer."
)

response = st.text_area(
    "Complete AI Platform Response",
    height=300,
    placeholder=(
        "Paste the complete response from the "
        "selected AI platform here..."
    ),
)

analyze_col, optimize_col = st.columns(2)

with analyze_col:
    analyze_clicked = st.button(
        "Evaluate Current Visibility",
        type="primary",
        use_container_width=True,
    )

with optimize_col:
    optimize_clicked = st.button(
        "Generate Optimized AI Response",
        use_container_width=True,
    )


if analyze_clicked:
    if not response.strip():
        st.error(
            "Paste an AI response first."
        )
    else:
        try:
            with st.spinner(
                "Evaluating AI visibility..."
            ):
                raw_analysis = evaluate_response(
                    str(
                        selected_prompt["prompt"]
                    ),
                    response.strip(),
                )

                analysis = normalize_analysis(
                    raw_analysis
                )

            st.session_state[
                "latest_analysis"
            ] = analysis

            st.session_state[
                "latest_response"
            ] = response.strip()

            st.session_state[
                "latest_platform"
            ] = platform

            st.session_state[
                "latest_prompt"
            ] = {
                "prompt_id": selected_prompt[
                    "prompt_id"
                ],
                "category": selected_prompt[
                    "category"
                ],
                "prompt": selected_prompt[
                    "prompt"
                ],
            }

            st.session_state[
                "result_saved"
            ] = False

            st.session_state.pop(
                "latest_optimized",
                None,
            )

        except Exception as error:
            st.error(
                "The response could not be analyzed."
            )
            st.exception(error)


if optimize_clicked:
    if not response.strip():
        st.error(
            "Paste an AI response first."
        )
    else:
        try:
            current_prompt = str(
                selected_prompt["prompt"]
            )

            current_response = response.strip()

            saved_prompt = st.session_state.get(
                "latest_prompt",
                {},
            )

            saved_response = st.session_state.get(
                "latest_response",
                "",
            )

            existing_analysis = st.session_state.get(
                "latest_analysis"
            )

            analysis_matches = (
                existing_analysis is not None
                and saved_response == current_response
                and saved_prompt.get("prompt")
                == current_prompt
            )

            if analysis_matches:
                original_analysis = existing_analysis
            else:
                with st.spinner(
                    "Evaluating the original response..."
                ):
                    raw_analysis = evaluate_response(
                        current_prompt,
                        current_response,
                    )

                    original_analysis = (
                        normalize_analysis(
                            raw_analysis
                        )
                    )

                st.session_state[
                    "latest_analysis"
                ] = original_analysis

                st.session_state[
                    "latest_response"
                ] = current_response

                st.session_state[
                    "latest_platform"
                ] = platform

                st.session_state[
                    "latest_prompt"
                ] = {
                    "prompt_id": selected_prompt[
                        "prompt_id"
                    ],
                    "category": selected_prompt[
                        "category"
                    ],
                    "prompt": current_prompt,
                }

                st.session_state[
                    "result_saved"
                ] = False

            with st.spinner(
                "Rewriting and verifying the optimized "
                "response..."
            ):
                optimization_result = (
                    optimize_and_score(
                        prompt=current_prompt,
                        original_response=(
                            current_response
                        ),
                        original_analysis=(
                            original_analysis
                        ),
                    )
                )

            st.session_state[
                "latest_optimized"
            ] = optimization_result

        except Exception as error:
            st.error(
                "The response could not be optimized."
            )
            st.exception(error)


if "latest_analysis" in st.session_state:
    display_analysis(
        st.session_state[
            "latest_analysis"
        ]
    )

    if "latest_optimized" in st.session_state:
        display_optimized_response(
            st.session_state[
            "latest_optimized"
            ]
        )

    st.divider()
    st.subheader("Save Analysis")

    analyzed_platform = st.session_state.get(
        "latest_platform",
        platform,
    )

    analyzed_prompt = st.session_state.get(
        "latest_prompt",
        selected_prompt,
    )

    st.caption(
        f"Platform: {analyzed_platform}  |  "
        f"Prompt ID: "
        f"{analyzed_prompt['prompt_id']}"
    )

    save_disabled = st.session_state.get(
        "result_saved",
        False,
    )

    if st.button(
        "Add to Dashboard",
        disabled=save_disabled,
        use_container_width=True,
    ):
        try:
            analysis = st.session_state[
                "latest_analysis"
            ]

            metadata = analysis.get(
                "metadata",
                {},
            )

            now = datetime.now(
                ZoneInfo(
                    "America/New_York"
                )
            )

            weaknesses = analysis[
                "weaknesses"
            ]

            new_row = {
                "run_date": now.strftime(
                    "%Y-%m-%d"
                ),
                "run_timestamp": (
                    now.isoformat(
                        timespec="seconds"
                    )
                ),
                "scan_id": (
                    "manual_"
                    + now.strftime(
                        "%Y%m%d_%H%M%S"
                    )
                ),
                "platform": analyzed_platform,
                "provider": metadata.get(
                    "provider",
                    analyzed_platform.lower()
                    .replace(" ", "_"),
                ),
                "model": metadata.get(
                    "model",
                    "Manual Response",
                ),
                "prompt_id": analyzed_prompt[
                    "prompt_id"
                ],
                "category": analyzed_prompt[
                    "category"
                ],
                "prompt": analyzed_prompt[
                    "prompt"
                ],
                "wake_tech_mentioned": (
                    "Yes"
                    if analysis[
                        "wake_mentioned"
                    ]
                    else "No"
                ),
                "position": analysis[
                    "wake_rank"
                ],
                "competitors": "|".join(
                    analysis["competitors"]
                ),
                "wake_tech_url": "|".join(
                    analysis[
                        "wake_tech_urls"
                    ]
                ),
                "competitor_urls": "|".join(
                    analysis[
                        "competitor_urls"
                    ]
                ),
                "score": analysis["score"],
                "sentiment": analysis[
                    "sentiment"
                ],
                "strengths": "|".join(
                    analysis["strengths"]
                ),
                "weaknesses": "|".join(
                    weaknesses
                ),
                "recommendations": "|".join(
                    analysis[
                        "recommendations"
                    ]
                ),
                "notes": (
                    " | ".join(weaknesses)
                    if weaknesses
                    else analysis.get(
                        "overall_assessment",
                        (
                            "No major visibility "
                            "weaknesses identified."
                        ),
                    )
                ),
                "response": st.session_state[
                    "latest_response"
                ],
                "latency_seconds": (
                    metadata.get(
                        "latency_seconds",
                        "",
                    )
                ),
                "input_tokens": (
                    metadata.get(
                        "input_tokens",
                        "",
                    )
                ),
                "output_tokens": (
                    metadata.get(
                        "output_tokens",
                        "",
                    )
                ),
                "total_tokens": (
                    metadata.get(
                        "total_tokens",
                        "",
                    )
                ),
                "response_id": (
                    metadata.get(
                        "response_id",
                        "",
                    )
                ),
            }

            updated_results = pd.concat(
                [
                    results,
                    pd.DataFrame(
                        [new_row]
                    ),
                ],
                ignore_index=True,
                sort=False,
            )

            RESULTS_FILE.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            updated_results.to_csv(
                RESULTS_FILE,
                index=False,
            )

            st.session_state[
                "result_saved"
            ] = True

            st.success(
                "Result saved. Return to the Dashboard "
                "to see it included."
            )

        except Exception as error:
            st.error(
                "The result could not be saved."
            )
            st.exception(error)

    if save_disabled:
        st.success(
            "This analysis has already been saved."
        )