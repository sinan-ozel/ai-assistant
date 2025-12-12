FROM python:3.12-slim

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        git \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /workspace

# Copy pyproject.toml for dependency installation
COPY ../pyproject.toml /workspace/pyproject.toml

# Install Python dependencies including dev dependencies
RUN pip install --no-cache-dir -e ".[dev]"

# Create non-root user and add to docker group
RUN groupadd -g 999 docker || true && \
    useradd -m -s /bin/bash devuser && \
    usermod -aG docker devuser && \
    chown -R devuser:devuser /workspace

USER devuser

CMD ["/bin/bash"]
