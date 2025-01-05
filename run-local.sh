#!/bin/bash
set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default values
DRY_RUN=true
CONFIG_FILE=""
RUN_ONCE=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --prod)
            DRY_RUN=false
            shift
            ;;
        --config)
            CONFIG_FILE="$2"
            shift 2
            ;;
        --once)
            RUN_ONCE=true
            shift
            ;;
        --help)
            echo "Usage: $0 [--prod] [--config <path>]"
            echo
            echo "Options:"
            echo "  --prod          Run in production mode (actual changes)"
            echo "  --config <path> Use custom config file (default: config/backup_config.yaml)"
            echo "  --once          Run once without scheduling"
            echo "  --help          Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

echo -e "${GREEN}Setting up NAS Backup Tool...${NC}"

# Check if config file exists
if [ -n "$CONFIG_FILE" ] && [ ! -f "$CONFIG_FILE" ]; then
    echo -e "${YELLOW}Config file not found: $CONFIG_FILE${NC}"
    exit 1
fi

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
if [ "$DRY_RUN" = true ]; then
    echo -e "${YELLOW}Running in DRY RUN mode (no actual changes)${NC}"
    ARGS="--dry-run"
else
    echo -e "${YELLOW}Running in PRODUCTION mode (will make actual changes)${NC}"
    ARGS=""
fi

if [ "$RUN_ONCE" = true ]; then
    echo -e "${YELLOW}Running once without scheduling${NC}"
    ARGS="$ARGS --once"
fi

uv run python -m src.main $ARGS --config "$CONFIG_FILE"
exit_code=$?

# Pass through the exit code from the Python script
exit $exit_code
