# Base stage
FROM python:3.14.3-slim-bookworm AS base

# Set up common environment variables
ENV HF_HOME="/app/hf_home"
ENV SENTENCE_TRANSFORMERS_HOME="/app/st_home"

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
