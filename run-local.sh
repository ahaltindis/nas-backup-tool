#!/bin/bash
set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Setting up NAS Backup Tool...${NC}"

# Check Python version
REQUIRED_VERSION=$(grep "requires-python" pyproject.toml | sed -E 's/.*>=([0-9]+\.[0-9]+).*/\1/')
CURRENT_VERSION=$(python -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')

# Simple version comparison without external dependencies
if ! python -c "import sys; cv=tuple(map(int,'${CURRENT_VERSION}'.split('.'))); rv=tuple(map(int,'${REQUIRED_VERSION}'.split('.'))); exit(0 if cv >= rv else 1)"; then
    echo -e "${YELLOW}Python >= $REQUIRED_VERSION is required but found $CURRENT_VERSION${NC}"
    exit 1
fi

# Install uv if not installed
if ! command -v uv &> /dev/null; then
    echo -e "${GREEN}Installing uv...${NC}"
    pip install uv
fi

# Install dependencies using uv
echo -e "${GREEN}Installing dependencies...${NC}"
uv venv
uv pip install -e .

# Run the application
echo -e "${GREEN}Starting NAS Backup Tool...${NC}"
uv run python -m src.main --dry-run 