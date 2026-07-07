#!/usr/bin/env bash
# scripts/publish-helm-chart.sh — Package and push the Helm chart.
#
# One artifact pair per release: the chart always carries the same version as
# the Docker image released moments earlier by release.sh, so image and chart
# ship together.
#
#   --dev   Chart version = the v<BASE>-dev.<build> tag release.sh --dev just
#           created (from pyproject.toml + build_number.txt, the two sources
#           of truth). release.sh owns the single build-number increment.
#   (none)  Chart version = <BASE> from pyproject.toml (stable release).

set -euo pipefail

WORKSPACE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$WORKSPACE_ROOT"

DOCKER_IMAGE="sinanozel/ai-assistant"
BASE=$(grep '^version = ' pyproject.toml | awk -F'"' '{print $2}')

if [ "${1:-}" = "--dev" ]; then
    LAST_TAG=$(git tag --list "v${BASE}-dev.*" --sort=-creatordate | head -1)
    if [[ -z "$LAST_TAG" ]]; then
        echo "ERROR: no v${BASE}-dev.* tag found — run the dev Docker" \
             "release first (release.sh --dev, via the Release (Dev) task)." >&2
        exit 1
    fi
    CHART_VERSION="${LAST_TAG#v}"
else
    CHART_VERSION="${BASE}"
fi
APP_VERSION="${CHART_VERSION}"

echo ">>> Chart version : ${CHART_VERSION}"
echo ">>> App version   : ${APP_VERSION} (Docker image)"

helm package helm/ai-assistant \
    --version "${CHART_VERSION}" \
    --app-version "${APP_VERSION}"
helm push "ai-assistant-helm-${CHART_VERSION}.tgz" oci://registry-1.docker.io/sinanozel
rm -f "ai-assistant-helm-${CHART_VERSION}.tgz"

echo "Published Helm chart ${CHART_VERSION} (deploys ${DOCKER_IMAGE}:${APP_VERSION})"
