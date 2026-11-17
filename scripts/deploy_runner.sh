#!/usr/bin/env bash
# Store endpoint keys in a Modal secret, then deploy the gateway and the runner.
# Rerun after changing anything in .env or infrastructure/.
set -euo pipefail
cd "$(dirname -- "${BASH_SOURCE[0]}")/.."
uv run python -m infrastructure.configure_gateway
uv run modal deploy infrastructure/gateway.py
uv run modal deploy infrastructure/agent_runner.py