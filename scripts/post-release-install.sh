#!/usr/bin/env bash
# scripts/post-release-install.sh
#
# Starts minikube (if not already running), copies the cortex directory into the
# minikube node via SSH+tar, installs the ai-assistant Helm chart, and
# port-forwards :8000 (API) and :8501 (Streamlit).
#
# minikube mount is not used — it is unreliable with the Docker driver on Mac
# (the 9p share is empty inside the node). Files are copied directly instead.
#
# API keys are read from examples/<example>/.env and created as a Kubernetes
# Secret (ai-assistant-api-keys) before the chart is installed.
#
# Press Ctrl+C to stop. The release stays installed; use helm uninstall +
# minikube stop to tear down.
#
# Usage:
#   bash scripts/post-release-install.sh [example_name]
#
# Arguments:
#   example_name  Subdirectory under examples/ to use (default: basic_example)
#
# Environment:
#   IMAGE_TAG     Docker image tag to deploy (resolved from pyproject.toml + DockerHub if unset)

set -euo pipefail

EXAMPLE="${1:-basic_example}"
NODE_CORTEX_PATH="/mnt/ai-assistant-cortex"
SECRET_NAME="ai-assistant-api-keys"

WORKSPACE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
EXAMPLE_DIR="$WORKSPACE/examples/$EXAMPLE"
CORTEX_DIR="$EXAMPLE_DIR/cortex"
HELM_VALUES="$EXAMPLE_DIR/helm/values.yaml"
CHART_DIR="$WORKSPACE/helm/ai-assistant"
RELEASE="ai-assistant"
REPO="sinanozel/ai-assistant"
HELM_INSTALLED=false

cleanup() {
    local exit_code=$?
    if [[ $exit_code -ne 0 ]] && [[ "$HELM_INSTALLED" == "false" ]]; then
        echo ">>> Install failed — uninstalling release '$RELEASE'..."
        helm uninstall "$RELEASE" 2>/dev/null || true
    fi
}

trap cleanup EXIT

# ---------------------------------------------------------------------------
# Resolve IMAGE_TAG from pyproject.toml + DockerHub
# ---------------------------------------------------------------------------

resolve_image_tag() {
    local version
    version="$(grep -m1 '^version' "$WORKSPACE/pyproject.toml" | sed 's/.*= *"\(.*\)"/\1/')"

    local tags_json
    tags_json="$(curl -fsSL "https://hub.docker.com/v2/repositories/${REPO}/tags/?page_size=100" 2>/dev/null || echo '{}')"

    local latest_build
    latest_build="$(echo "$tags_json" \
        | grep -o "\"name\":\"${version}-dev\.[0-9]*\"" \
        | grep -o '[0-9]*"$' \
        | tr -d '"' \
        | sort -n \
        | tail -1)"

    if [[ -n "$latest_build" ]]; then
        echo "${version}-dev.${latest_build}"
    else
        echo "${version}"
    fi
}

IMAGE_TAG="${IMAGE_TAG:-$(resolve_image_tag)}"
echo ">>> Using image tag: $IMAGE_TAG"

# ---------------------------------------------------------------------------
# Validate
# ---------------------------------------------------------------------------

[[ -d "$CORTEX_DIR" ]] || {
    echo "ERROR: cortex not found at $CORTEX_DIR" >&2
    echo "       Available examples: $(ls "$WORKSPACE/examples")" >&2
    exit 1
}

[[ -f "$HELM_VALUES" ]] || {
    echo "ERROR: $HELM_VALUES not found" >&2
    exit 1
}

# ---------------------------------------------------------------------------
# minikube
# ---------------------------------------------------------------------------

if ! minikube status --profile minikube 2>/dev/null | grep -q "Running"; then
    echo ">>> Starting minikube (Docker driver)..."
    minikube start --driver=docker
else
    echo ">>> minikube already running."
fi

# ---------------------------------------------------------------------------
# Copy cortex into minikube node
# ---------------------------------------------------------------------------

echo ">>> Copying cortex into minikube node at $NODE_CORTEX_PATH..."
echo "    (Full directory tree — chat/, providers/, workflows/, etc.)"

_tmptar=$(mktemp /tmp/cortex-XXXXXX.tar)
COPYFILE_DISABLE=1 tar -C "$CORTEX_DIR" --exclude='._*' --exclude='.DS_Store' -cf "$_tmptar" .
minikube cp "$_tmptar" /tmp/cortex.tar
rm "$_tmptar"
minikube ssh -- "sudo mkdir -p $NODE_CORTEX_PATH && sudo tar --warning=no-unknown-keyword -xf /tmp/cortex.tar -C $NODE_CORTEX_PATH && sudo rm /tmp/cortex.tar"

echo "    Cortex copied."

# ---------------------------------------------------------------------------
# API keys secret from .env
# ---------------------------------------------------------------------------

create_api_secret() {
    local env_file="$EXAMPLE_DIR/.env"
    [[ -f "$env_file" ]] || return 0

    local args=()
    while IFS='=' read -r key value; do
        [[ "$key" =~ ^(MISTRAL_API_KEY|ANTHROPIC_API_KEY)$ ]] || continue
        [[ -n "$value" ]] || continue
        args+=("--from-literal=${key}=${value}")
    done < <(grep -v '^[[:space:]]*#' "$env_file" | grep -v '^[[:space:]]*$')

    [[ ${#args[@]} -eq 0 ]] && return 0

    echo ">>> Creating secret '$SECRET_NAME' from .env..."
    kubectl create secret generic "$SECRET_NAME" \
        "${args[@]}" \
        --dry-run=client -o yaml | kubectl apply -f -
}

create_api_secret

# ---------------------------------------------------------------------------
# Pre-pull images into minikube to avoid helm --wait timeout on cold clusters
# ---------------------------------------------------------------------------

prepull_images() {
    local values_file="$1"

    local images=()
    images+=("sinanozel/ai-assistant:${IMAGE_TAG}")

    local emb_repo emb_tag
    emb_repo="$(grep -A3 'repository: sinanozel/ollama' "$CHART_DIR/values.yaml" | head -1 | awk '{print $2}')"
    emb_tag="$(grep -A4 'repository: sinanozel/ollama' "$CHART_DIR/values.yaml" | grep 'tag:' | head -1 | awk '{print $2}')"
    images+=("${emb_repo}:${emb_tag}")

    if grep -q 'ollama:' "$values_file" 2>/dev/null; then
        local ol_enabled
        ol_enabled="$(awk '/^ollama:/{f=1} f && /enabled:/{print $2; exit}' "$values_file")"
        if [[ "$ol_enabled" == "true" ]]; then
            local ol_repo ol_tag
            ol_repo="$(awk '/^ollama:/{f=1} f && /repository:/{print $2; exit}' "$values_file")"
            ol_tag="$(awk '/^ollama:/{f=1} f && /tag:/{print $2; exit}' "$values_file")"
            [[ -n "$ol_repo" && -n "$ol_tag" ]] && images+=("${ol_repo}:${ol_tag}")
        fi
    fi

    if grep -q 'llamacpp:' "$values_file" 2>/dev/null; then
        local lc_enabled
        lc_enabled="$(awk '/^llamacpp:/{f=1} f && /enabled:/{print $2; exit}' "$values_file")"
        if [[ "$lc_enabled" == "true" ]]; then
            local lc_repo lc_tag
            lc_repo="$(awk '/^llamacpp:/{f=1} f && /repository:/{print $2; exit}' "$values_file")"
            lc_tag="$(awk '/^llamacpp:/{f=1} f && /tag:/{print $2; exit}' "$values_file")"
            [[ -n "$lc_repo" && -n "$lc_tag" ]] && images+=("${lc_repo}:${lc_tag}")
        fi
    fi

    echo ">>> Pre-pulling images into minikube (this may take a while on a cold cluster)..."
    for img in "${images[@]}"; do
        echo "    Pulling: $img"
        docker pull "$img" 2>/dev/null || true
        minikube image load "$img"
        echo "    Loaded:  $img"
    done
}

prepull_images "$HELM_VALUES"

# ---------------------------------------------------------------------------
# Helm install / upgrade
# ---------------------------------------------------------------------------

echo ">>> Installing chart for example: $EXAMPLE (image tag: $IMAGE_TAG)..."

helm upgrade --install "$RELEASE" "$CHART_DIR" \
    --set "image.tag=${IMAGE_TAG}" \
    --set "cortex.hostPath=${NODE_CORTEX_PATH}" \
    -f "$HELM_VALUES" \
    --wait --timeout 600s

HELM_INSTALLED=true
echo ">>> Release '$RELEASE' is up."

# ---------------------------------------------------------------------------
# Port-forward (blocking — Ctrl+C to stop)
# ---------------------------------------------------------------------------

echo ""
echo ">>> Port-forwarding:"
echo "     API       →  http://localhost:8000"
echo "     Streamlit →  http://localhost:8501"
echo ">>> Press Ctrl+C to stop."
echo ""

kubectl port-forward \
    --address 0.0.0.0 \
    "svc/${RELEASE}" \
    8000:8000 8501:8501
