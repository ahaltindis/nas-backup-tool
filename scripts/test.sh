#!/bin/bash
set -e

uv pip install -e ".[test]"

uv run pytest

