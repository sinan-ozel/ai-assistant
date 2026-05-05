#!/usr/bin/env bash
set -e

BASE=$(grep '^version = ' pyproject.toml | awk -F'"' '{print $2}')

if [ "$1" = "--dev" ]; then
    BUILD=$(cat build_number.txt)
    VERSION="${BASE}-dev.$((BUILD - 1))"
    helm package helm/ai-assistant --version "${VERSION}" --app-version "${VERSION}"
else
    VERSION="${BASE}"
    helm package helm/ai-assistant
fi

helm push "ai-assistant-${VERSION}.tgz" oci://registry-1.docker.io/sinanozel
rm -f "ai-assistant-${VERSION}.tgz"
echo "Published ai-assistant ${VERSION} to Docker Hub OCI"
