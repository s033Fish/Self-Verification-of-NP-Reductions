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
    max_tokens: int = 4096       # output tokens per model call

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


# The final pair, chosen on the dev set: DeepSeek V4.1 Flash (strong) and
# GPT-OSS 120B (mid-strength, largest gain from self-testing). GLM-4.7-Flash
# (self-hosted) solved 0% of single-shot dev tasks and never finished a
# self-testing run; GLM 5.3 Flash was at ceiling. Both served by Fireworks.
AGENTS: tuple[Agent, ...] = (
    Agent(
        key="deepseek",
        default_model="accounts/fireworks/models/deepseek-v4p1-flash",
        model_variable="FIREWORKS_MODEL",
        base_url_variable="FIREWORKS_BASE_URL",
        api_key_variable="FIREWORKS_API_KEY",
        default_base_url="https://api.fireworks.ai/inference/v1",
        # Reasons before answering: 4096, then 16384, cut off tool calls while
        # it designed gadgets for 3-SAT -> 3-Coloring.
        max_tokens=32768,
    ),
    Agent(
        key="gptoss",
        default_model="accounts/fireworks/models/gpt-oss-120b",
        model_variable="FIREWORKS_GPTOSS_MODEL",
        base_url_variable="FIREWORKS_BASE_URL",
        api_key_variable="FIREWORKS_API_KEY",
        default_base_url="https://api.fireworks.ai/inference/v1",
        max_tokens=16384,
    ),
)
AGENT_BY_KEY = {agent.key: agent for agent in AGENTS}