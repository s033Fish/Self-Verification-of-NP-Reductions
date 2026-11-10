#!/usr/bin/env bash
# Deploy the self-hosted GLM-4.7-Flash endpoint. Prints the URL for .env.
set -euo pipefail
cd "$(dirname -- "${BASH_SOURCE[0]}")/.."
exec uv run modal deploy infrastructure/generation_models.py
