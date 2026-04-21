FROM python:3.12-slim

WORKDIR /tests

# Install curl for healthchecks and testing
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

# Copy pyproject.toml from the workspace root
COPY pyproject.toml .

RUN pip install --upgrade pip
RUN pip install --no-cache-dir .[test]  # Install test dependencies

# Create directory for test results
RUN mkdir -p /tests/test-results

# Set default command to run pytest with verbose output and JUnit XML
# CMD ["pytest", "-v", "--junitxml=/tests/test-results/junit.xml"]
CMD ["pytest", "-v"]