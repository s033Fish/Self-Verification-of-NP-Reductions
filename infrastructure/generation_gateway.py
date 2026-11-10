"""Credentialed gateway from the agent scaffold to fixed generation endpoints."""

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

app = modal.App(APP_NAME)
image = modal.Image.debian_slim(python_version="3.12").uv_pip_install(
    "requests==2.32.4"
)
endpoint_secret = modal.Secret.from_name(SECRET_NAME)


def _endpoint(model: str) -> dict[str, str]:
    registry = json.loads(os.getenv("GENERATION_ENDPOINTS_JSON", "{}"))
    try:
        configured = registry[model]
    except KeyError as error:
        raise ValueError(f"no generation endpoint configured for {model!r}") from error
    return {
        "api_base": configured["api_base"],
        "api_key": configured["api_key"],
    }

@app.function(image=image, secrets=[endpoint_secret], timeout=10 * 60)
def complete(request: dict[str, Any]) -> dict[str, Any]:
    """Forward one OpenAI-compatible completion without exposing credentials."""
    import requests

    endpoint = _endpoint(request["model"])
    base = endpoint["api_base"].rstrip("/")
    url = base if base.endswith("/chat/completions") else base + "/chat/completions"
    payload = {
        "model": request["model"],
        "messages": request["messages"],
        "tools": request.get("tools", []),
        **request.get("generation", {}),
    }
    headers = {"Authorization": f"Bearer {endpoint['api_key']}"}

    response = None
    for attempt in range(6):
        response = requests.post(url, json=payload, headers=headers, timeout=300)
        if response.status_code not in RETRY_STATUS:
            break
        time.sleep(min(30, 2**attempt))
    assert response is not None
    response.raise_for_status()
    return response.json()
