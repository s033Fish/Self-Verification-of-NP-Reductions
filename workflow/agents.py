"""The two models under test and where each one is served.

Settings come from .env (see .env.example). The gateway secret, the run
generator and the scorer all read this one list.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Agent:
    key: str                     # short name used in run IDs
    default_model: str           # model ID sent to the endpoint
    model_variable: str | None   # .env variable that overrides the model ID
    base_url_variable: str
    api_key_variable: str
    default_base_url: str | None = None
    temperature: float = 0.7     # > 0 so repeated seeds differ

    @property
    def model(self) -> str:
        if self.model_variable:
            return os.getenv(self.model_variable) or self.default_model
        return self.default_model

    @property
    def base_url(self) -> str:
        return os.getenv(self.base_url_variable) or self.default_base_url or ""

    @property
    def api_key(self) -> str:
        return os.getenv(self.api_key_variable, "")

    def missing_settings(self) -> list[str]:
        missing = []
        if not self.model:
            missing.append(self.model_variable or f"{self.key} model")
        if not self.base_url:
            missing.append(self.base_url_variable)
        if not self.api_key:
            missing.append(self.api_key_variable)
        return missing


AGENTS: tuple[Agent, ...] = (
    # Self-hosted on Modal (infrastructure/models.py).
    Agent(
        key="glm",
        default_model="zai-org/GLM-4.7-Flash",
        model_variable=None,
        base_url_variable="GLM_BASE_URL",
        api_key_variable="MODAL_PROXY_TOKEN",
    ),
    # Fireworks serverless. Set FIREWORKS_MODEL to the exact ID from the
    # model's Fireworks page, e.g. accounts/fireworks/models/<name>.
    Agent(
        key="deepseek",
        default_model="",
        model_variable="FIREWORKS_MODEL",
        base_url_variable="FIREWORKS_BASE_URL",
        api_key_variable="FIREWORKS_API_KEY",
        default_base_url="https://api.fireworks.ai/inference/v1",
    ),
)
AGENT_BY_KEY = {agent.key: agent for agent in AGENTS}
