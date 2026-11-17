"""Credentialed gateway from the agent sandbox to the model endpoints.

Agent-written code never sees API keys: the runner calls this Modal function,
which holds the keys in a Modal secret and forwards one OpenAI-compatible
chat completion. Each model has its own base URL and key, so the self-hosted
GLM endpoint (Modal proxy token) and Fireworks (Fireworks API key) both work.

Adapted from the Assignment 2 `generation_gateway.py`.
"""

from __future__ import annotations

import json
import os
import time
from typing import Any

import modal

APP_NAME = "reductions-gateway"
FUNCTION_NAME = "complete"
SECRET_NAME = "reductions-endpoints"
RETRY_STATUS = {429, 500, 502, 503, 504}
MIN_OUTPUT_TOKENS = 512
CONTEXT_ERROR_MARKERS = (
    "maximum context length", "context length", "context window",
    "max_model_len", "too long", "too many tokens",
)

app = modal.App(APP_NAME)
image = modal.Image.debian_slim(python_version="3.12").uv_pip_install(
    "requests==2.32.4"
)
endpoint_secret = modal.Secret.from_name(SECRET_NAME)


def _endpoint(model: str) -> dict[str, str]:
    registry = json.loads(os.getenv("ENDPOINTS_JSON", "{}"))
    try:
        configured = registry[model]
    except KeyError as error:
        raise ValueError(f"no endpoint configured for {model!r}") from error
    return {"api_base": configured["api_base"], "api_key": configured["api_key"]}


MESSAGE_FIELDS = ("role", "content", "name", "tool_calls", "tool_call_id")


def clean_messages(messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Keep only standard chat-completion fields. The agent framework adds
    provider-specific keys (function_call, provider_specific_fields,
    reasoning_content, ...) to messages it replays; some endpoints reject any
    unknown field with a 400, so strip them for every provider."""
    cleaned = []
    for message in messages:
        kept = {k: message[k] for k in MESSAGE_FIELDS if message.get(k) is not None}
        if "tool_calls" in kept:
            kept["tool_calls"] = [
                {
                    "id": call.get("id"),
                    "type": call.get("type") or "function",
                    "function": {
                        "name": (call.get("function") or {}).get("name"),
                        "arguments": (call.get("function") or {}).get("arguments") or "",
                    },
                }
                for call in kept["tool_calls"]
            ]
        if kept.get("role") == "assistant" and "content" not in kept:
            kept["content"] = ""  # some endpoints require the key
        cleaned.append(kept)
    return cleaned


def _is_context_error(response) -> bool:
    return response.status_code == 400 and any(
        marker in response.text.lower() for marker in CONTEXT_ERROR_MARKERS
    )


@app.function(image=image, secrets=[endpoint_secret], timeout=10 * 60)
def complete(request: dict[str, Any]) -> dict[str, Any]:
    """Forward one chat completion; the response keeps its `usage` block.

    If the conversation no longer fits the model's context window, retry with
    smaller output limits (halving down to MIN_OUTPUT_TOKENS). If even that
    does not fit, return {"gateway_error": {"kind": "context_exceeded", ...}}
    instead of raising, so the runner can end the run cleanly.
    """
    import requests

    endpoint = _endpoint(request["model"])
    base = endpoint["api_base"].rstrip("/")
    url = base if base.endswith("/chat/completions") else base + "/chat/completions"
    headers = {"Authorization": f"Bearer {endpoint['api_key']}"}
    generation = dict(request.get("generation", {}))

    while True:
        payload = {
            "model": request["model"],
            "messages": clean_messages(request["messages"]),
            "tools": request.get("tools", []),
            **generation,
        }
        response = None
        for attempt in range(6):
            response = requests.post(url, json=payload, headers=headers, timeout=300)
            if response.status_code not in RETRY_STATUS:
                break
            time.sleep(min(30, 2**attempt))
        assert response is not None
        if _is_context_error(response):
            max_tokens = generation.get("max_tokens", 4096)
            if max_tokens > MIN_OUTPUT_TOKENS:
                generation["max_tokens"] = max(MIN_OUTPUT_TOKENS, max_tokens // 2)
                continue
            return {"gateway_error": {
                "kind": "context_exceeded",
                "status": response.status_code,
                "detail": response.text[:1000],
            }}
        if not response.ok:
            # Include the provider's message: a bare "400 Bad Request" does not
            # say which parameter was rejected.
            raise RuntimeError(
                f"{response.status_code} from {request['model']}: {response.text[:1500]}"
            )
        return response.json()