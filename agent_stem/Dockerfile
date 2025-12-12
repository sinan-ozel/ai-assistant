FROM python:3.12-slim

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy pyproject.toml for dependency installation
COPY pyproject.toml /app/pyproject.toml

# Install Python dependencies from pyproject.toml
RUN pip install --no-cache-dir .

# Copy all agent_stem contents
COPY agent_stem/src/ /app/src/
COPY agent_stem/default/ /app/default/
COPY agent_stem/tests/ /app/tests/

# Set PYTHONPATH to include src directory
ENV PYTHONPATH=/app/src:$PYTHONPATH

# Copy supervisor configuration
COPY agent_stem/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Expose ports
# Streamlit
EXPOSE 8501
# FastAPI
EXPOSE 8000

# Run supervisor to manage all services
CMD ["supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]