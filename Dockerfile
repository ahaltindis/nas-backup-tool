FROM python:3.12-slim

WORKDIR /app

# Install uv
RUN pip install uv

# Copy project files
COPY pyproject.toml .
COPY src/ ./src/
COPY config/ ./config/

# Install dependencies using uv
RUN uv pip install .

CMD ["python", "-m", "src.main"] 