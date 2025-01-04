#!/bin/bash
set -e

# Default values
CONFIG_FILE=${CONFIG_FILE:-/app/config.yaml}

exec uv run python -m src.main --config "$CONFIG_FILE"