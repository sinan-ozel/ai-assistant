FROM python:3.12-slim

WORKDIR /docs

# Copy pyproject.toml so dependency versions are sourced from it.
# This layer is invalidated only when pyproject.toml changes.
COPY pyproject.toml /docs/pyproject.toml
RUN pip install --no-cache-dir $(python3 -c \
    "import tomllib; d=tomllib.load(open('pyproject.toml','rb')); \
     print(' '.join(d['project']['optional-dependencies']['docs']))")

# Copy docs source — baked into the image at build time.
# No mounts needed: success = exit 0, failure = non-zero exit.
COPY mkdocs.yml /docs/mkdocs.yml
COPY docs/ /docs/docs/

# Build the site; --strict turns warnings into errors.
RUN mkdocs build --strict
