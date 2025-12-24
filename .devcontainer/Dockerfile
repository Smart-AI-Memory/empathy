# Empathy Framework Development Container
# Python 3.11 with dev tools pre-installed

FROM mcr.microsoft.com/devcontainers/python:1-3.11-bullseye

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    redis-tools \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python tools
RUN pip install --no-cache-dir \
    pip --upgrade \
    wheel \
    setuptools

# Set working directory
WORKDIR /workspace

# Create non-root user (already exists in base image as 'vscode')
USER vscode

# Install pre-commit globally for the user
RUN pip install --user pre-commit

# Add local bin to PATH
ENV PATH="/home/vscode/.local/bin:${PATH}"

# Default command
CMD ["sleep", "infinity"]
