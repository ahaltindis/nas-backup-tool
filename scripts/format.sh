#!/bin/bash
set -e

# Format all Python files using ruff
uv run ruff format .

# Fix import sorting and other auto-fixable issues
uv run ruff check --fix .
