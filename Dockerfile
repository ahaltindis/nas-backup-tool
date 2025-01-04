FROM python:3.12-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Install required system packages
RUN apt-get update && apt-get install -y \
    cifs-utils \
    rsync \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies following the recommendations
# https://github.com/astral-sh/uv-docker-example/blob/main/Dockerfile

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy from the cache instead of linking since it's a mounted volume
ENV UV_LINK_MODE=copy

# Install the project's dependencies using the lockfile and settings
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

# Copy project files
COPY src/ ./src/
COPY run-container.sh ./

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"

# Make the script executable
RUN chmod +x /app/run-container.sh

# Use environment variable for config file
CMD ["/app/run-container.sh"]

