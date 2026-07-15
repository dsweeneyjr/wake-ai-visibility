import os
import time
from typing import Any

import streamlit as st
from dotenv import load_dotenv
from openai import (
    APIConnectionError,
    APIStatusError,
    AuthenticationError,
    OpenAI,
    RateLimitError,
)


load_dotenv()

DEFAULT_MODEL = "gpt-5.5"


def get_secret(name: str) -> str:
    """
    Read a secret from local environment variables first,
    then from Streamlit Community Cloud secrets.
    """
    environment_value = os.getenv(name)

    if environment_value:
        return environment_value

    try:
        streamlit_value = st.secrets.get(name)

        if streamlit_value:
            return str(streamlit_value)
    except Exception:
        pass

    return ""


def get_openai_client() -> OpenAI:
    """
    Create an OpenAI client using the configured API key.
    """
    api_key = get_secret("OPENAI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is missing. Add it to the local .env file "
            "or the Streamlit Community Cloud Secrets settings."
        )

    return OpenAI(
        api_key=api_key
    )


def run_prompt(
    prompt: str,
    model: str = DEFAULT_MODEL,
    instructions: str | None = None,
) -> dict[str, Any]:
    """
    Send one prompt to OpenAI and return the response
    plus performance and usage metadata.
    """
    if not prompt or not prompt.strip():
        raise ValueError(
            "Prompt cannot be empty."
        )

    client = get_openai_client()
    started_at = time.perf_counter()

    try:
        request: dict[str, Any] = {
            "model": model,
            "input": prompt.strip(),
        }

        if instructions:
            request["instructions"] = (
                instructions.strip()
            )

        response = client.responses.create(
            **request
        )

        latency_seconds = round(
            time.perf_counter() - started_at,
            3,
        )

        usage = response.usage

        input_tokens = (
            usage.input_tokens
            if usage
            else 0
        )

        output_tokens = (
            usage.output_tokens
            if usage
            else 0
        )

        total_tokens = (
            usage.total_tokens
            if usage
            else 0
        )

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
            "OpenAI authentication failed. "
            "Check the configured OPENAI_API_KEY."
        ) from exc

    except RateLimitError as exc:
        raise RuntimeError(
            "OpenAI rejected the request because "
            "of a rate or usage limit."
        ) from exc

    except APIConnectionError as exc:
        raise RuntimeError(
            "Could not connect to OpenAI. "
            "Check the internet connection."
        ) from exc

    except APIStatusError as exc:
        raise RuntimeError(
            f"OpenAI returned API error "
            f"{exc.status_code}: {exc.message}"
        ) from exc