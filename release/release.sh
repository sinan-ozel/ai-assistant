#!/usr/bin/env bash
# release/release.sh — Build, tag, and push agent-stem to Docker Hub.
#
# Usage:
#   bash release/release.sh           # Production release
#   bash release/release.sh --dev     # Dev release (appends build number to version)
#
# Version is read from [project].version in pyproject.toml — that is the
# single source of truth. Bump it there before running a production release.
# For dev releases the build number is read from build_number.txt at the
# workspace root and auto-incremented after each successful dev release.
#
# Pre-conditions (both modes):
#   - Must be on branch 'main'
#   - git pull must succeed
#
# Additional pre-conditions for production release:
#   - Working tree must be clean (no uncommitted changes)
#   - pyproject.toml version must be valid semver (MAJOR.MINOR.PATCH)
#   - git tag v<version> must not already exist
#   - <version> must be strictly greater than the latest existing semver tag
#   - Docker daemon must be running; prompts for login if not already authenticated
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
    local ver="$1"
    local major minor patch
    IFS='.' read -r major minor patch <<< "$ver"
    echo $(( major * 1000000 + minor * 1000 + patch ))
}

# ---------------------------------------------------------------------------
# Parse arguments
# ---------------------------------------------------------------------------

DEV_RELEASE=false
for arg in "$@"; do
    case "$arg" in
        --dev) DEV_RELEASE=true ;;
        *) die "Unknown argument: '$arg'. Usage: release.sh [--dev]" ;;
    esac
done

# ---------------------------------------------------------------------------
# Git pre-flight: branch and pull (applies to both dev and prod)
# ---------------------------------------------------------------------------

cd "$WORKSPACE_ROOT"

CURRENT_BRANCH="$(git rev-parse --abbrev-ref HEAD)"
if [[ "$CURRENT_BRANCH" != "main" ]]; then
    die "Must be on branch 'main' to release (currently on '$CURRENT_BRANCH'). Switch to main first."
fi

echo ">>> Pulling latest changes from origin/main ..."
git pull origin main || die "git pull failed — resolve any conflicts or network issues before releasing."

# ---------------------------------------------------------------------------
# Read version from pyproject.toml
# ---------------------------------------------------------------------------

PYPROJECT="$WORKSPACE_ROOT/pyproject.toml"

VERSION=$(grep '^version = ' "$PYPROJECT" | sed 's/version = "\(.*\)"/\1/')

if [[ -z "$VERSION" ]]; then
    die "Could not read version from $PYPROJECT"
fi

if ! [[ "$VERSION" =~ ^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$ ]]; then
    die "Version '$VERSION' in pyproject.toml is not valid semver. Expected MAJOR.MINOR.PATCH (e.g. 1.2.3)"
fi

# ---------------------------------------------------------------------------
# Docker pre-flight (both modes)
# ---------------------------------------------------------------------------

if ! docker info > /dev/null 2>&1; then
    die "Docker daemon is not running or not reachable."
fi

if ! docker system info 2>/dev/null | grep -q 'Username:'; then
    echo ">>> Not logged in to Docker Hub. Running docker login ..."
    docker login || die "Docker login failed."
fi

# ---------------------------------------------------------------------------
# Dev release
# ---------------------------------------------------------------------------

if [[ "$DEV_RELEASE" == "true" ]]; then
    BUILD_NUMBER_FILE="$WORKSPACE_ROOT/build_number.txt"
    [[ -f "$BUILD_NUMBER_FILE" ]] || die "build_number.txt not found at $BUILD_NUMBER_FILE"

    BUILD_NUMBER=$(tr -d '[:space:]' < "$BUILD_NUMBER_FILE")
    [[ "$BUILD_NUMBER" =~ ^[0-9]+$ ]] || die "build_number.txt contains '$BUILD_NUMBER', expected a plain integer."

    DEV_VERSION="${VERSION}-dev.${BUILD_NUMBER}"
    echo ">>> Dev release: ${DEV_VERSION} (pyproject version ${VERSION}, build ${BUILD_NUMBER})"

    echo ">>> Building image ${DOCKER_IMAGE}:${DEV_VERSION} ..."
    docker build \
        --build-arg BUILD_DATE="$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
        --build-arg VERSION="$DEV_VERSION" \
        --label "org.opencontainers.image.version=${DEV_VERSION}" \
        --label "org.opencontainers.image.revision=$(git rev-parse HEAD)" \
        --label "org.opencontainers.image.created=$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
        -f "${WORKSPACE_ROOT}/agent_stem/Dockerfile" \
        -t "${DOCKER_IMAGE}:${DEV_VERSION}" \
        "${WORKSPACE_ROOT}"

    echo ">>> Pushing Docker image ${DOCKER_IMAGE}:${DEV_VERSION} ..."
    docker push "${DOCKER_IMAGE}:${DEV_VERSION}"

    NEW_BUILD_NUMBER=$(( BUILD_NUMBER + 1 ))
    echo "$NEW_BUILD_NUMBER" > "$BUILD_NUMBER_FILE"
    git add "$BUILD_NUMBER_FILE"
    git commit -m "chore: bump build number to ${NEW_BUILD_NUMBER} after dev release ${DEV_VERSION}"

    echo ""
    echo "Dev release ${DEV_VERSION} complete."
    echo "  Docker: ${DOCKER_IMAGE}:${DEV_VERSION}"
    echo "  Build number incremented to ${NEW_BUILD_NUMBER} and committed."
    echo ""
    exit 0
fi

# ---------------------------------------------------------------------------
# Production release
# ---------------------------------------------------------------------------

echo ">>> Releasing version $VERSION (from pyproject.toml)"

GIT_TAG="v${VERSION}"

if ! git diff --quiet || ! git diff --cached --quiet; then
    die "Working tree is not clean. Commit or stash all changes before releasing."
fi

if git tag | grep -qxF "$GIT_TAG"; then
    die "Git tag '$GIT_TAG' already exists. Bump the version in pyproject.toml before releasing."
fi

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
