FROM python:3.12-slim

WORKDIR /workspace

# Copy pyproject.toml for dependency installation.
# Install only the declared dev dependencies (not the package itself) so that
# this layer is invalidated only when pyproject.toml changes, not on every
# source file edit.
COPY pyproject.toml /workspace/pyproject.toml
RUN pip install --no-cache-dir $(python3 -c \
    "import tomllib; d=tomllib.load(open('pyproject.toml','rb')); \
     print(' '.join(d['project']['optional-dependencies']['dev']))")

# Run the reformat script (available via volume mount at runtime)
CMD ["/workspace/reformat/reformat.sh"]
