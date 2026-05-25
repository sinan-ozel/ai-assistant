#!/usr/bin/env bash
set -euo pipefail

WORKSPACE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$WORKSPACE_ROOT"

DOCKER_IMAGE="sinanozel/ai-assistant"
BASE=$(grep '^version = ' pyproject.toml | awk -F'"' '{print $2}')

if [ "$1" = "--dev" ]; then
    BUILD_NUMBER_FILE="$WORKSPACE_ROOT/build_number.txt"
    [[ -f "$BUILD_NUMBER_FILE" ]] || { echo "ERROR: build_number.txt not found" >&2; exit 1; }

    # Highest build number across git tags: v{BASE}-dev.{N}
    GIT_BUILD=$(git tag --list "v${BASE}-dev.*" \
        | sed "s|^v${BASE}-dev\.||" \
        | grep -E '^[0-9]+$' \
        | sort -n | tail -1)
    GIT_BUILD=${GIT_BUILD:-0}

    # Highest build number from Docker Hub: {BASE}-dev.{N}
    DOCKER_BUILD=$(curl -sf \
        "https://hub.docker.com/v2/repositories/${DOCKER_IMAGE}/tags/?page_size=100" \
        2>/dev/null \
        | jq -r '.results[].name' \
        | grep "^${BASE}-dev\." \
        | sed "s|^${BASE}-dev\.||" \
        | grep -E '^[0-9]+$' \
        | sort -n | tail -1 \
        || true)
    DOCKER_BUILD=${DOCKER_BUILD:-0}

    echo ">>> Git max dev build   : ${GIT_BUILD}"
    echo ">>> Docker Hub max build: ${DOCKER_BUILD}"

    # Use max(git_build, docker_build + 1) so we never reuse an existing tag
    NEW_BUILD=$(( GIT_BUILD > DOCKER_BUILD + 1 ? GIT_BUILD : DOCKER_BUILD + 1 ))
    VERSION="${BASE}-dev.${NEW_BUILD}"
    echo ">>> Publishing Helm chart ${VERSION} ..."

    helm package helm/ai-assistant --version "${VERSION}" --app-version "${VERSION}"
    helm push "ai-assistant-helm-${VERSION}.tgz" oci://registry-1.docker.io/sinanozel
    rm -f "ai-assistant-helm-${VERSION}.tgz"

    NEXT_BUILD=$(( NEW_BUILD + 1 ))
    echo "$NEXT_BUILD" > "$BUILD_NUMBER_FILE"
    git add "$BUILD_NUMBER_FILE"
    git commit -m "chore: bump build number to ${NEXT_BUILD} after dev Helm release ${VERSION}"
    git push origin main

    echo ""
    echo "Published Helm chart ${VERSION} to Docker Hub OCI"
    echo "  Build number incremented to ${NEXT_BUILD} and committed."
else
    VERSION="${BASE}"
    helm package helm/ai-assistant
    helm push "ai-assistant-helm-${VERSION}.tgz" oci://registry-1.docker.io/sinanozel
    rm -f "ai-assistant-helm-${VERSION}.tgz"
    echo "Published ai-assistant ${VERSION} to Docker Hub OCI"
fi
