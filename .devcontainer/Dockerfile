FROM python:3.12-bookworm

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        git \
        curl \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install kubectl
RUN curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl" \
    && chmod +x kubectl \
    && mv kubectl /usr/local/bin/

# Install helm
RUN curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Set working directory
WORKDIR /workspace

# Copy pyproject.toml for dependency installation
COPY ../pyproject.toml /workspace/pyproject.toml

# Install Python dependencies including dev dependencies
RUN pip install --no-cache-dir -e ".[dev]"

# Create non-root user and add to docker group
# Use ARG to allow passing host UID/GID
ARG USER_UID=1000
ARG USER_GID=1000

RUN groupadd -g 999 docker || true && \
    groupadd -g ${USER_GID} devuser || true && \
    useradd -m -s /bin/bash -u ${USER_UID} -g ${USER_GID} devuser && \
    usermod -aG docker devuser && \
    chown -R devuser:devuser /workspace

USER devuser

CMD ["/bin/bash"]
