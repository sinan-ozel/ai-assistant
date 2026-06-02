FROM python:3.12-slim

# OCI Image Spec annotations — https://specs.opencontainers.org/image-spec/annotations/
LABEL org.opencontainers.image.title="agent-stem" \
      org.opencontainers.image.description="Lightweight AI agent framework: run locally with Docker, deploy at scale on Kubernetes" \
      org.opencontainers.image.url="https://github.com/sinan-ozel/ai-assistant" \
      org.opencontainers.image.source="https://github.com/sinan-ozel/ai-assistant" \
      org.opencontainers.image.documentation="https://sinan-ozel.github.io/ai-assistant" \
      org.opencontainers.image.authors="Sinan Ozel <coding@sinan.slmail.me>" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.base.name="docker.io/library/python:3.12-slim"

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential ca-certificates fonts-dejavu \
        tesseract-ocr tesseract-ocr-eng \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy pyproject.toml for dependency installation
COPY pyproject.toml /app/pyproject.toml

# Install only the declared dependencies (not the package itself) so that
# this layer is invalidated only when pyproject.toml changes, not on every
# source file edit.
RUN pip install --no-cache-dir $(python -c \
    "import tomllib; d=tomllib.load(open('/app/pyproject.toml','rb')); print(' '.join(d['project']['dependencies']))")

# Pre-download tiktoken BPE data so containers without internet access can start.
RUN python -c "import tiktoken; tiktoken.get_encoding('cl100k_base')"

# Pre-download the fastembed embedding model so containers without internet access can start.
RUN python -c "from fastembed import TextEmbedding; TextEmbedding('nomic-ai/nomic-embed-text-v1.5')"

# Copy all agent_stem contents
COPY agent_stem/src/ /app/src/
COPY agent_stem/default/ /app/default/

# Set PYTHONPATH to include src directory
ENV PYTHONPATH=/app/src:$PYTHONPATH

# Copy supervisor configuration
COPY agent_stem/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Expose ports

# MCP server
EXPOSE 8001
# FastAPI
EXPOSE 8000
# Streamlit
EXPOSE 8501

# Entrypoint: run supervisord and propagate exit code 1 on fatal errors.
# supervisord exits 0 on SIGTERM; if a fatal-error sentinel was written first
# (by api.py before sending SIGTERM), exit 1 so Kubernetes shows "Error" not
# "Completed" in kubectl describe pod.
COPY agent_stem/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

CMD ["/entrypoint.sh"]