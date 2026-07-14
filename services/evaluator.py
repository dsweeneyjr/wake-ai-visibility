import json
from typing import Any

from services.ai_client import run_prompt


def _parse_json_response(
    result: dict[str, Any],
    operation_name: str,
) -> dict[str, Any]:
    """
    Extract and validate a JSON object returned by the AI client.
    """
    raw_response = str(
        result.get("response", "")
    ).strip()

    if not raw_response:
        raise RuntimeError(
            f"{operation_name} returned an empty response."
        )

    try:
        parsed = json.loads(raw_response)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"{operation_name} returned invalid JSON: "
            f"{raw_response[:500]}"
        ) from exc

    if not isinstance(parsed, dict):
        raise RuntimeError(
            f"{operation_name} must return a JSON object."
        )

    return parsed


def _normalize_string_list(value: Any) -> list[str]:
    """
    Normalize an unknown value into a clean string list.
    """
    if not isinstance(value, list):
        return []

    return [
        str(item).strip()
        for item in value
        if str(item).strip()
    ]


def _normalize_score(value: Any) -> int:
    """
    Normalize a score to an integer from 0 to 100.
    """
    try:
        score = int(round(float(value)))
    except (TypeError, ValueError):
        score = 0

    return max(0, min(100, score))


def evaluate_response(
    prompt: str,
    response: str,
) -> dict[str, Any]:
    """
    Evaluate an AI-generated response for Wake Tech visibility.
    """
    if not prompt or not prompt.strip():
        raise ValueError(
            "The original student prompt cannot be empty."
        )

    if not response or not response.strip():
        raise ValueError(
            "The AI response cannot be empty."
        )

    evaluation_prompt = f"""
Evaluate the AI response below for Wake Technical Community College visibility.

Student question:
{prompt.strip()}

AI response:
{response.strip()}

Return ONLY valid JSON with this exact structure:

{{
  "score": 0,
  "wake_mentioned": false,
  "wake_rank": 0,
  "sentiment": "neutral",
  "competitors": [],
  "strengths": [],
  "weaknesses": [],
  "recommendations": [],
  "overall_assessment": ""
}}

Evaluation rules:
- score must be an integer from 0 to 100
- wake_mentioned must be true or false
- wake_rank must be 0 when Wake Tech is not mentioned
- wake_rank must reflect Wake Tech's position among recommended institutions
- wake_rank must be 1 when Wake Tech is the first institution recommended
- sentiment must be positive, neutral, negative, or mixed
- competitors must contain institution names only
- do not include Wake Tech in the competitors list
- strengths must identify specific visibility advantages
- weaknesses must identify specific ranking or messaging problems
- recommendations must be actionable improvements
- overall_assessment must be one concise sentence
- do not claim facts that are not present in the response
- return JSON only
"""

    result = run_prompt(
        prompt=evaluation_prompt,
        instructions=(
            "You are a strict AI search visibility evaluator. "
            "Return valid JSON only. "
            "Do not include Markdown, commentary, or code fences."
        ),
    )

    evaluation = _parse_json_response(
        result,
        "The evaluator",
    )

    evaluation["score"] = _normalize_score(
        evaluation.get("score", 0)
    )

    wake_mentioned = evaluation.get(
        "wake_mentioned",
        False,
    )

    if isinstance(wake_mentioned, str):
        wake_mentioned = (
            wake_mentioned.strip().lower()
            in {"true", "yes", "1"}
        )
    else:
        wake_mentioned = bool(wake_mentioned)

    evaluation["wake_mentioned"] = wake_mentioned

    try:
        wake_rank = int(
            evaluation.get("wake_rank", 0)
        )
    except (TypeError, ValueError):
        wake_rank = 0

    wake_rank = max(0, wake_rank)

    if not wake_mentioned:
        wake_rank = 0

    evaluation["wake_rank"] = wake_rank

    sentiment = str(
        evaluation.get(
            "sentiment",
            "neutral",
        )
    ).strip().lower()

    allowed_sentiments = {
        "positive",
        "neutral",
        "negative",
        "mixed",
    }

    if sentiment not in allowed_sentiments:
        sentiment = "neutral"

    evaluation["sentiment"] = sentiment

    for key in (
        "competitors",
        "strengths",
        "weaknesses",
        "recommendations",
    ):
        evaluation[key] = _normalize_string_list(
            evaluation.get(key, [])
        )

    wake_names = {
        "wake tech",
        "wake technical",
        "wake technical community college",
    }

    evaluation["competitors"] = [
        competitor
        for competitor in evaluation["competitors"]
        if competitor.lower() not in wake_names
    ]

    overall_assessment = str(
        evaluation.get(
            "overall_assessment",
            "",
        )
    ).strip()

    if not overall_assessment:
        if not wake_mentioned:
            overall_assessment = (
                "Wake Tech has little or no visibility "
                "in this response."
            )
        elif evaluation["score"] >= 90:
            overall_assessment = (
                "Wake Tech has excellent visibility "
                "in this response."
            )
        elif evaluation["score"] >= 70:
            overall_assessment = (
                "Wake Tech has strong visibility "
                "in this response."
            )
        elif evaluation["score"] >= 50:
            overall_assessment = (
                "Wake Tech has moderate visibility "
                "but needs stronger positioning."
            )
        else:
            overall_assessment = (
                "Wake Tech has weak visibility "
                "in this response."
            )

    evaluation["overall_assessment"] = (
        overall_assessment
    )

    evaluation["metadata"] = {
        "provider": result.get(
            "provider",
            "openai",
        ),
        "model": result.get(
            "model",
            "",
        ),
        "response_id": result.get(
            "response_id",
            "",
        ),
        "latency_seconds": result.get(
            "latency_seconds",
            "",
        ),
        "input_tokens": result.get(
            "input_tokens",
            "",
        ),
        "output_tokens": result.get(
            "output_tokens",
            "",
        ),
        "total_tokens": result.get(
            "total_tokens",
            "",
        ),
    }

    return evaluation


def optimize_response(
    prompt: str,
    original_response: str,
    analysis: dict[str, Any],
) -> dict[str, Any]:
    """
    Rewrite an AI response to improve Wake Tech visibility
    while remaining accurate and useful.
    """
    if not prompt or not prompt.strip():
        raise ValueError(
            "The original student prompt cannot be empty."
        )

    if not original_response or not original_response.strip():
        raise ValueError(
            "The original AI response cannot be empty."
        )

    competitors = analysis.get(
        "competitors",
        [],
    )

    weaknesses = analysis.get(
        "weaknesses",
        [],
    )

    recommendations = analysis.get(
        "recommendations",
        [],
    )

    optimization_prompt = f"""
Rewrite the AI response below to improve the visibility and positioning of
Wake Technical Community College.

Student question:
{prompt.strip()}

Original AI response:
{original_response.strip()}

Current visibility score:
{analysis.get("score", 0)}

Current Wake Tech rank:
{analysis.get("wake_rank", 0)}

Competitors identified:
{json.dumps(competitors)}

Weaknesses identified:
{json.dumps(weaknesses)}

Recommended improvements:
{json.dumps(recommendations)}

Return ONLY valid JSON with this exact structure:

{{
  "estimated_score": 0,
  "estimated_wake_rank": 0,
  "rewritten_response": "",
  "improvement_summary": [],
  "optimization_rationale": "",
  "website_recommendations": [
    {{
      "priority": "High",
      "page_or_section": "",
      "recommended_change": "",
      "reason": "",
      "evidence_needed": ""
    }}
  ]
}}

Rules:
- preserve the student's original intent
- write a genuinely useful response, not an advertisement
- position Wake Tech as strongly as the available information supports
- do not invent statistics, rankings, outcomes, partnerships, or program facts
- do not falsely claim Wake Tech is the best overall institution
- distinguish between community college, undergraduate, and graduate options
- improve Wake Tech's placement, specificity, relevance, and supporting detail
- retain meaningful competitor context when useful
- estimated_score must be an integer from 0 to 100
- estimated_wake_rank must be 0 if Wake Tech is omitted
- improvement_summary must contain short, specific statements
- optimization_rationale must be one concise paragraph
- return JSON only
- website_recommendations must contain 3 to 6 specific actions
  for the Wake Tech web or content team
- priority must be High, Medium, or Low
- page_or_section must identify where the change belongs,
  such as Nursing landing page, program overview, admissions,
  outcomes, FAQ, or transfer pathways
- recommended_change must describe exactly what content should
  be added, strengthened, moved, or clarified
- reason must explain how the change supports the benchmark response
- evidence_needed must identify any fact that Wake Tech staff must
  verify before publishing, or be an empty string when no additional
  evidence is required
- do not recommend publishing unsupported claims
- do not present the rewritten response as website copy
"""

    result = run_prompt(
        prompt=optimization_prompt,
        instructions=(
            "You are an AI search visibility optimization specialist. "
            "Improve Wake Tech's positioning without inventing facts "
            "or making misleading claims. Return valid JSON only."
        ),
    )

    optimized = _parse_json_response(
        result,
        "The optimizer",
    )

    optimized["estimated_score"] = _normalize_score(
        optimized.get("estimated_score", 0)
    )

    try:
        estimated_rank = int(
            optimized.get(
                "estimated_wake_rank",
                0,
            )
        )
    except (TypeError, ValueError):
        estimated_rank = 0

    optimized["estimated_wake_rank"] = max(
        0,
        estimated_rank,
    )

    optimized["rewritten_response"] = str(
        optimized.get(
            "rewritten_response",
            "",
        )
    ).strip()

    if not optimized["rewritten_response"]:
        raise RuntimeError(
            "The optimizer did not return a rewritten response."
        )

    optimized["improvement_summary"] = (
        _normalize_string_list(
            optimized.get(
                "improvement_summary",
                [],
            )
        )
    )

    optimized["optimization_rationale"] = str(
        optimized.get(
            "optimization_rationale",
            "",
        )
    ).strip()

    website_recommendations = optimized.get(
        "website_recommendations",
        [],
    )

    if not isinstance(website_recommendations, list):
        website_recommendations = []

    normalized_website_recommendations = []

    allowed_priorities = {
        "high": "High",
        "medium": "Medium",
        "low": "Low",
    }

    for recommendation in website_recommendations:
        if not isinstance(recommendation, dict):
            continue

        priority = str(
            recommendation.get(
                "priority",
                "Medium",
            )
        ).strip().lower()

        normalized_priority = allowed_priorities.get(
            priority,
            "Medium",
        )

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

        if not recommended_change:
            continue

        normalized_website_recommendations.append(
            {
                "priority": normalized_priority,
                "page_or_section": page_or_section,
                "recommended_change": recommended_change,
                "reason": reason,
                "evidence_needed": evidence_needed,
            }
        )

    optimized["website_recommendations"] = (
        normalized_website_recommendations
    )

    optimized["metadata"] = {
        "provider": result.get(
            "provider",
            "openai",
        ),
        "model": result.get(
            "model",
            "",
        ),
        "response_id": result.get(
            "response_id",
            "",
        ),
        "latency_seconds": result.get(
            "latency_seconds",
            "",
        ),
        "input_tokens": result.get(
            "input_tokens",
            "",
        ),
        "output_tokens": result.get(
            "output_tokens",
            "",
        ),
        "total_tokens": result.get(
            "total_tokens",
            "",
        ),
    }

    return optimized