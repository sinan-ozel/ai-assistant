#!/usr/bin/env bash
set -euo pipefail

WORKSPACE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$WORKSPACE_ROOT"

BASE=$(grep '^version = ' pyproject.toml | awk -F'"' '{print $2}')

if [ "$1" = "--dev" ]; then
    BUILD_NUMBER_FILE="$WORKSPACE_ROOT/build_number.txt"
    [[ -f "$BUILD_NUMBER_FILE" ]] || { echo "ERROR: build_number.txt not found" >&2; exit 1; }

    BUILD=$(tr -d '[:space:]' < "$BUILD_NUMBER_FILE")
    [[ "$BUILD" =~ ^[0-9]+$ ]] || { echo "ERROR: build_number.txt contains '$BUILD', expected integer" >&2; exit 1; }

    VERSION="${BASE}-dev.${BUILD}"
    helm package helm/ai-assistant --version "${VERSION}" --app-version "${VERSION}"
    helm push "ai-assistant-helm-${VERSION}.tgz" oci://registry-1.docker.io/sinanozel
    rm -f "ai-assistant-helm-${VERSION}.tgz"

    NEW_BUILD=$(( BUILD + 1 ))
    echo "$NEW_BUILD" > "$BUILD_NUMBER_FILE"
    git add "$BUILD_NUMBER_FILE"
    git commit -m "chore: bump build number to ${NEW_BUILD} after dev Helm release ${VERSION}"
    git push origin main

    echo ""
    echo "Published Helm chart ${VERSION} to Docker Hub OCI"
    echo "  Build number incremented to ${NEW_BUILD} and committed."
else
    VERSION="${BASE}"
    helm package helm/ai-assistant
    helm push "ai-assistant-helm-${VERSION}.tgz" oci://registry-1.docker.io/sinanozel
    rm -f "ai-assistant-helm-${VERSION}.tgz"
    echo "Published ai-assistant ${VERSION} to Docker Hub OCI"
fi
