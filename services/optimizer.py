from typing import Any

from services.evaluator import (
    evaluate_response,
    optimize_response,
)


def optimize_and_score(
    prompt: str,
    original_response: str,
    original_analysis: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Rewrite an AI response and verify the improvement by
    evaluating the rewritten response with the same evaluator
    used for the original response.

    When original_analysis is supplied, the original response
    is not evaluated again. This avoids an unnecessary API call.
    """

    if not prompt or not prompt.strip():
        raise ValueError(
            "The original student prompt cannot be empty."
        )

    if not original_response or not original_response.strip():
        raise ValueError(
            "The original AI response cannot be empty."
        )

    clean_prompt = prompt.strip()
    clean_response = original_response.strip()

    if original_analysis is None:
        original_analysis = evaluate_response(
            clean_prompt,
            clean_response,
        )

    if not isinstance(original_analysis, dict):
        raise ValueError(
            "The original analysis must be a dictionary."
        )

    optimization = optimize_response(
        prompt=clean_prompt,
        original_response=clean_response,
        analysis=original_analysis,
    )

    rewritten_response = str(
        optimization.get(
            "rewritten_response",
            "",
        )
    ).strip()

    if not rewritten_response:
        raise RuntimeError(
            "The optimizer did not return a rewritten response."
        )

    optimized_analysis = evaluate_response(
        clean_prompt,
        rewritten_response,
    )

    original_score = _normalize_score(
        original_analysis.get("score", 0)
    )

    optimized_score = _normalize_score(
        optimized_analysis.get("score", 0)
    )

    score_change = optimized_score - original_score

    original_rank = _normalize_rank(
        original_analysis.get("wake_rank", 0)
    )

    optimized_rank = _normalize_rank(
        optimized_analysis.get("wake_rank", 0)
    )

    return {
        "original_response": clean_response,
        "optimized_response": rewritten_response,
        "original_analysis": original_analysis,
        "optimized_analysis": optimized_analysis,
        "original_score": original_score,
        "optimized_score": optimized_score,
        "score_change": score_change,
        "original_rank": original_rank,
        "optimized_rank": optimized_rank,
        "improvement_summary": _normalize_string_list(
            optimization.get(
                "improvement_summary",
                [],
            )
        ),
        "optimization_rationale": str(
            optimization.get(
                "optimization_rationale",
                "",
            )
        ).strip(),
        "website_recommendations": optimization.get(
            "website_recommendations",
            [],
        ),
        "optimization_metadata": optimization.get(
            "metadata",
            {},
        ),
    }


def _normalize_score(value: Any) -> int:
    """
    Normalize a visibility score to an integer from 0 to 100.
    """
    try:
        score = int(round(float(value)))
    except (TypeError, ValueError):
        score = 0

    return max(0, min(100, score))


def _normalize_rank(value: Any) -> int:
    """
    Normalize a recommendation rank to a non-negative integer.
    """
    try:
        rank = int(value)
    except (TypeError, ValueError):
        rank = 0

    return max(0, rank)


def _normalize_string_list(value: Any) -> list[str]:
    """
    Normalize an unknown value into a clean list of strings.
    """
    if not isinstance(value, list):
        return []

    return [
        str(item).strip()
        for item in value
        if str(item).strip()
    ]