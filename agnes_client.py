"""Optional Agnes AI client for the Quant Research Lab.

The key is intentionally read only from AGNES_API_KEY at runtime.
"""
from __future__ import annotations

import os
from typing import Any


def configured() -> bool:
    return bool(os.getenv("AGNES_API_KEY"))


def ask(prompt: str, *, model: str | None = None, tools: list[dict[str, Any]] | None = None) -> str:
    """Call Agnes through its OpenAI-compatible endpoint."""
    if not configured():
        raise RuntimeError("AGNES_API_KEY is not configured")
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise RuntimeError("Install the optional client with: pip install openai") from exc
    client = OpenAI(
        api_key=os.environ["AGNES_API_KEY"],
        base_url=os.getenv("AGNES_BASE_URL", "https://apihub.agnes-ai.com/v1"),
    )
    response = client.chat.completions.create(
        model=model or os.getenv("AGNES_MODEL", "agnes-2.5-flash"),
        messages=[{"role": "user", "content": prompt}],
        tools=tools or [],
    )
    return response.choices[0].message.content or ""


if __name__ == "__main__":
    print("configured=" + str(configured()))
