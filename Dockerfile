# Use a more specific and lighter base image
FROM python:3.12-slim

# Install uv.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# Create a non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

COPY . /app

# Set the working directory
WORKDIR /app

# Copy only requirements first to leverage Docker cache
RUN uv sync --frozen --no-cache && chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Set the entrypoint
ENTRYPOINT ["sh", "./boot.sh"]