# Base stage
FROM python:3.14.3-slim-bookworm AS base

# Build stage
FROM base AS build

# - Enable bytecode compilation
# - Copy from the cache instead of linking since it's a mounted volume
# - Disable Python downloads, because we want to use the system interpreter
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV UV_PYTHON_DOWNLOADS=0

# Install uv
COPY --from=ghcr.io/astral-sh/uv:0.11.4 /uv /uvx /bin/

# Use `/app` as the working directory
WORKDIR /app

# Install project dependencies
ARG UV_SYNC_OPTIONS="--locked --no-dev"
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync $UV_SYNC_OPTIONS

# Set up directories
COPY src/ /app/src
COPY bin/ /app/bin

# Runtime stage
FROM base AS runtime

# Setup a non-root user
RUN useradd --uid 1000 --shell /bin/bash --create-home appuser

# Copy the application from the builder
COPY --from=build --chown=appuser:appuser /app /app

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"

# Use the non-root user
USER appuser

# Use `/app` as the working directory
WORKDIR /app

# Expose the port
EXPOSE 9696

# Run the app
ENTRYPOINT [ "gunicorn", "--bind", "0.0.0.0:9696", "src.app:app" ]
