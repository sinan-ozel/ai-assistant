FROM python:3.11-slim

WORKDIR /workspace

# Install only the linting / formatting tools needed for this image.
# The project dev dependencies are declared in `pyproject.toml`'s `dev`
# extra, but for a lint-only container we install the tools directly
# to avoid building the package.
RUN pip install --upgrade pip && \
    pip install --no-cache-dir ruff black isort docformatter && \
    rm -rf /var/lib/apt/lists/* /root/.cache/pip

# Files will be mounted at /workspace at runtime
CMD ["./lint/lint.sh"]