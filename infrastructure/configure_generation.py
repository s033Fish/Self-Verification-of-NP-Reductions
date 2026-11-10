"""Store generation endpoint settings in the Modal gateway secret."""

from __future__ import annotations

import argparse
import json

import modal

from workflow.agents import AGENTS

SECRET_NAME = "reductions-endpoints"


def endpoint_registry() -> dict[str, dict[str, str]]:
    registry: dict[str, dict[str, str]] = {}
    missing: list[str] = []
    for agent in AGENTS:
        missing.extend(agent.missing_settings())
        if not agent.missing_settings():
            registry[agent.model] = {
                "api_base": agent.base_url.rstrip("/"),
                "api_key": agent.api_key,
            }
    if missing:
        raise ValueError(f"missing {', '.join(sorted(set(missing)))} in .env")
    return registry


def configure() -> None:
    values = {"ENDPOINTS_JSON": json.dumps(endpoint_registry(), sort_keys=True)}
    existing = {secret.name for secret in modal.Secret.objects.list()}
    if SECRET_NAME in existing:
        modal.Secret.from_name(SECRET_NAME).update(values)
    else:
        modal.Secret.objects.create(SECRET_NAME, values)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    try:
        configure()
    except (OSError, ValueError) as error:
        parser.error(str(error))
    print(f"configured Modal secret {SECRET_NAME!r} for:")
    for agent in AGENTS:
        print(f"  {agent.key:9} {agent.model}  ->  {agent.base_url}")


if __name__ == "__main__":
    main()