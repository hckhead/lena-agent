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

# Expose any ports if necessary (MCP usually runs over stdio, but if using SSE/WebSockets, expose port)
# For stdio usage, we don't strictly need EXPOSE, but good practice if we add HTTP later.

# Command to run the application
CMD ["python", "server.py"]
