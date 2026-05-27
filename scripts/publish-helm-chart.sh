#!/usr/bin/env bash
set -euo pipefail

WORKSPACE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$WORKSPACE_ROOT"

DOCKER_IMAGE="sinanozel/ai-assistant"
BASE=$(grep '^version = ' pyproject.toml | awk -F'"' '{print $2}')

if [ "$1" = "--dev" ]; then
    BUILD_NUMBER_FILE="$WORKSPACE_ROOT/build_number.txt"
    [[ -f "$BUILD_NUMBER_FILE" ]] || { echo "ERROR: build_number.txt not found" >&2; exit 1; }

    # Skip publish if helm/ai-assistant/ has not changed since the last dev tag
    LAST_TAG=$(git tag --sort=-version:refname | grep "^v${BASE}-dev\." | head -1)
    if [[ -n "$LAST_TAG" ]]; then
        if git diff --quiet "${LAST_TAG}" HEAD -- helm/ai-assistant/; then
            echo ">>> No changes to helm/ai-assistant/ since ${LAST_TAG} — skipping Helm chart publish."
            exit 0
        fi
        echo ">>> Changes detected in helm/ai-assistant/ since ${LAST_TAG} — publishing."
    fi

    # Helm chart version: current build_number (source of truth: build_number - 1 after publish)
    BUILD_NUMBER=$(tr -d '[:space:]' < "$BUILD_NUMBER_FILE")
    [[ "$BUILD_NUMBER" =~ ^[0-9]+$ ]] || { echo "ERROR: build_number.txt contains '$BUILD_NUMBER'" >&2; exit 1; }
    CHART_VERSION="${BASE}-dev.${BUILD_NUMBER}"

    # appVersion: latest git tag = the Docker image that actually exists
    APP_VERSION=$(git tag --sort=-version:refname | grep "^v${BASE}-dev\." | head -1 | sed 's/^v//')
    if [[ -z "$APP_VERSION" ]]; then
        APP_VERSION="${BASE}"
    fi

    echo ">>> Chart version : ${CHART_VERSION}"
    echo ">>> App version   : ${APP_VERSION} (Docker image)"

    helm package helm/ai-assistant \
        --version "${CHART_VERSION}" \
        --app-version "${APP_VERSION}"
    helm push "ai-assistant-helm-${CHART_VERSION}.tgz" oci://registry-1.docker.io/sinanozel
    rm -f "ai-assistant-helm-${CHART_VERSION}.tgz"

    NEXT_BUILD=$(( BUILD_NUMBER + 1 ))
    echo "$NEXT_BUILD" > "$BUILD_NUMBER_FILE"
    git add "$BUILD_NUMBER_FILE"
    git commit -m "chore: bump build number to ${NEXT_BUILD} after dev Helm release ${CHART_VERSION}"
    git push origin main

    echo ""
    echo "Published Helm chart ${CHART_VERSION} (deploys ${DOCKER_IMAGE}:${APP_VERSION})"
    echo "  Build number incremented to ${NEXT_BUILD}."
else
    VERSION="${BASE}"
    APP_VERSION=$(git tag --sort=-version:refname | grep "^v${BASE}$" | head -1 | sed 's/^v//')
    [[ -z "$APP_VERSION" ]] && APP_VERSION="${BASE}"
    helm package helm/ai-assistant \
        --version "${VERSION}" \
        --app-version "${APP_VERSION}"
    helm push "ai-assistant-helm-${VERSION}.tgz" oci://registry-1.docker.io/sinanozel
    rm -f "ai-assistant-helm-${VERSION}.tgz"
    echo "Published ai-assistant ${VERSION} (deploys ${DOCKER_IMAGE}:${APP_VERSION})"
fi
