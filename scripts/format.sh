#!/bin/bash
set -e

uv pip install -e ".[dev]"

# Format all Python files using ruff
uv run ruff format .

# Fix import sorting and other auto-fixable issues
uv run ruff check --fix .
