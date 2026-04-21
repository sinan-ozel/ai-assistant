#!/usr/bin/env bash
# release/release.sh — Build, tag, and push agent-stem to Docker Hub.
#
# Usage: bash release/release.sh
#
# Version is read from [project].version in pyproject.toml — that is the
# single source of truth. Bump it there before running this script.
#
# Pre-conditions (script exits with error if any fail):
#   - Must be on branch 'main'
#   - Working tree must be clean (no uncommitted changes)
#   - pyproject.toml version must be valid semver (MAJOR.MINOR.PATCH)
#   - git tag v<version> must not already exist
#   - <version> must be strictly greater than the latest existing semver tag
#
# TODO: Release documentation (MkDocs site) at the same time as the image.
#       Consider: mkdocs gh-deploy or publishing to a hosting service in CI.

set -euo pipefail

DOCKER_IMAGE="sinanozel/agent-stem"
WORKSPACE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

die() {
    echo "ERROR: $*" >&2
    exit 1
}

semver_to_int() {
    # Convert MAJOR.MINOR.PATCH to a comparable integer: MAJOR*1000000 + MINOR*1000 + PATCH
    local ver="$1"
    local major minor patch
    IFS='.' read -r major minor patch <<< "$ver"
    echo $(( major * 1000000 + minor * 1000 + patch ))
}

# ---------------------------------------------------------------------------
# Read version from pyproject.toml
# ---------------------------------------------------------------------------

PYPROJECT="$WORKSPACE_ROOT/pyproject.toml"

VERSION=$(grep '^version = ' "$PYPROJECT" | sed 's/version = "\(.*\)"/\1/')

if [[ -z "$VERSION" ]]; then
    die "Could not read version from $PYPROJECT"
fi

# Validate semver: must be MAJOR.MINOR.PATCH with no leading zeros
if ! [[ "$VERSION" =~ ^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$ ]]; then
    die "Version '$VERSION' in pyproject.toml is not valid semver. Expected MAJOR.MINOR.PATCH (e.g. 1.2.3)"
fi

echo ">>> Releasing version $VERSION (from pyproject.toml)"

GIT_TAG="v${VERSION}"

# ---------------------------------------------------------------------------
# Git pre-flight checks
# ---------------------------------------------------------------------------

cd "$WORKSPACE_ROOT"

# Must be on main
CURRENT_BRANCH="$(git rev-parse --abbrev-ref HEAD)"
if [[ "$CURRENT_BRANCH" != "main" ]]; then
    die "Must be on branch 'main' to release (currently on '$CURRENT_BRANCH')"
fi

# Working tree must be clean
if ! git diff --quiet || ! git diff --cached --quiet; then
    die "Working tree is not clean. Commit or stash all changes before releasing."
fi

# Tag must not already exist
if git tag | grep -qxF "$GIT_TAG"; then
    die "Git tag '$GIT_TAG' already exists. Bump the version in pyproject.toml before releasing."
fi

# New version must be strictly greater than the latest existing semver tag
LATEST_TAG=""
LATEST_INT=0
while IFS= read -r tag; do
    ver="${tag#v}"
    if [[ "$ver" =~ ^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$ ]]; then
        tag_int="$(semver_to_int "$ver")"
        if (( tag_int > LATEST_INT )); then
            LATEST_INT=$tag_int
            LATEST_TAG="$tag"
        fi
    fi
done < <(git tag)

NEW_INT="$(semver_to_int "$VERSION")"

if (( NEW_INT <= LATEST_INT )) && [[ -n "$LATEST_TAG" ]]; then
    die "Version '$VERSION' is not greater than the current latest tag '$LATEST_TAG'. Bump the version in pyproject.toml."
fi

# ---------------------------------------------------------------------------
# Docker pre-flight check
# ---------------------------------------------------------------------------

if ! docker info > /dev/null 2>&1; then
    die "Docker daemon is not running or not reachable."
fi

if ! docker system info 2>/dev/null | grep -q 'Username:'; then
    echo ">>> Not logged in to Docker Hub. Running docker login ..."
    docker login || die "Docker login failed."
fi

# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------

echo ">>> Building image ${DOCKER_IMAGE}:${VERSION} ..."
docker build \
    --build-arg BUILD_DATE="$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
    --build-arg VERSION="$VERSION" \
    --label "org.opencontainers.image.version=${VERSION}" \
    --label "org.opencontainers.image.revision=$(git rev-parse HEAD)" \
    --label "org.opencontainers.image.created=$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
    -f "${WORKSPACE_ROOT}/agent_stem/Dockerfile" \
    -t "${DOCKER_IMAGE}:${VERSION}" \
    -t "${DOCKER_IMAGE}:latest" \
    "${WORKSPACE_ROOT}"

# ---------------------------------------------------------------------------
# Tag and push
# ---------------------------------------------------------------------------

echo ">>> Tagging git commit as $GIT_TAG ..."
git tag -a "$GIT_TAG" -m "Release $VERSION"

echo ">>> Pushing Docker image ${DOCKER_IMAGE}:${VERSION} ..."
docker push "${DOCKER_IMAGE}:${VERSION}"

echo ">>> Pushing Docker image ${DOCKER_IMAGE}:latest ..."
docker push "${DOCKER_IMAGE}:latest"

echo ">>> Pushing branch main ..."
git push origin main

echo ">>> Pushing git tag $GIT_TAG ..."
git push origin "$GIT_TAG"

echo ""
echo "Release $VERSION complete."
echo "  Docker: ${DOCKER_IMAGE}:${VERSION}"
echo "  Git tag: $GIT_TAG"
echo ""
echo "TODO: Release documentation at the same time as the image."
echo "      Consider: mkdocs gh-deploy or publishing the site in CI alongside this step."
