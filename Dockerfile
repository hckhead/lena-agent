# Use a lightweight Python base image
FROM python:3.11-slim-bookworm

# Install system dependencies (if any needed for extensions)
# curl is often useful for healthchecks
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Set working directory
WORKDIR /app

# Copy dependency files first to leverage cache
COPY pyproject.toml .
# COPY uv.lock . # Uncomment if you have a lock file

# Install dependencies
# --frozen: install from lockfile (if available), otherwise use pyproject.toml
# --no-cache: keep image small
RUN uv sync --no-cache

# Copy the rest of the application
COPY . .

# Set environment variables
# Ensure python output is sent directly to terminal (e.g. docker logs)
ENV PYTHONUNBUFFERED=1
# Add the virtual environment to PATH
ENV PATH="/app/.venv/bin:$PATH"
# Server mode: mcp or api
ENV SERVER_MODE=mcp

# Expose port for API mode
EXPOSE 8000

# Command to run the application
# Use SERVER_MODE to determine which server to run
CMD if [ "$SERVER_MODE" = "api" ]; then \
        python api_server.py; \
    else \
        python server.py; \
    fi
