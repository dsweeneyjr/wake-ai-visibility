import os
import time
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI
from openai import APIConnectionError, APIStatusError, AuthenticationError, RateLimitError

load_dotenv()

DEFAULT_MODEL = "gpt-5.5"

_api_key = os.getenv("OPENAI_API_KEY")

if not _api_key:
    raise RuntimeError(
        "OPENAI_API_KEY is missing. Add it to the project root .env file."
    )

client = OpenAI(api_key=_api_key)


def run_prompt(
    prompt: str,
    model: str = DEFAULT_MODEL,
    instructions: str | None = None,
) -> dict[str, Any]:
    """
    Send one prompt to OpenAI and return response text plus useful metadata.
    """

    if not prompt or not prompt.strip():
        raise ValueError("Prompt cannot be empty.")

    started_at = time.perf_counter()

    try:
        request: dict[str, Any] = {
            "model": model,
            "input": prompt.strip(),
        }

        if instructions:
            request["instructions"] = instructions.strip()

        response = client.responses.create(**request)

        latency_seconds = round(time.perf_counter() - started_at, 3)

        usage = response.usage

        input_tokens = usage.input_tokens if usage else 0
        output_tokens = usage.output_tokens if usage else 0
        total_tokens = usage.total_tokens if usage else 0

        return {
            "success": True,
            "provider": "openai",
            "model": response.model or model,
            "response_id": response.id,
            "response": response.output_text or "",
            "latency_seconds": latency_seconds,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens,
            "error": "",
        }

    except AuthenticationError as exc:
        raise RuntimeError(
            "OpenAI authentication failed. Check OPENAI_API_KEY in .env."
        ) from exc

    except RateLimitError as exc:
        raise RuntimeError(
            "OpenAI rejected the request because of a rate or usage limit."
        ) from exc

    except APIConnectionError as exc:
        raise RuntimeError(
            "Could not connect to OpenAI. Check the internet connection."
        ) from exc

    except APIStatusError as exc:
        raise RuntimeError(
            f"OpenAI returned API error {exc.status_code}: {exc.message}"
        ) from exc