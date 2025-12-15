FROM python:3.12-slim

WORKDIR /tests

# Install curl for healthchecks and testing
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

# Install pytest and dependencies
RUN pip install --no-cache-dir \
    pytest==9.0.1 \
    pytest-depends==1.0.1 \
    requests

# Copy test files
COPY test_*.py .

# Create directory for test results
RUN mkdir -p /tests/test-results

# Set default command to run pytest with verbose output and JUnit XML
CMD ["pytest", "-v", "--junitxml=/tests/test-results/junit.xml"]