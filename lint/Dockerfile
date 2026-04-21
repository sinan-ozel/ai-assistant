FROM python:3.11-slim

WORKDIR /workspace

# Copy pyproject.toml for dependency installation.
# Install only the declared dev dependencies (not the package itself) so that
# this layer is invalidated only when pyproject.toml changes, not on every
# source file edit.
COPY pyproject.toml /workspace/pyproject.toml
RUN pip install --no-cache-dir $(python3 -c \
    "import tomllib; d=tomllib.load(open('pyproject.toml','rb')); \
     print(' '.join(d['project']['optional-dependencies']['dev']))")

# Files will be mounted at /workspace at runtime
CMD ["./lint/lint.sh"]
