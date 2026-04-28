#!/usr/bin/env bash
# scripts/post-release-test.sh
#
# Post-release Kubernetes integration test pipeline:
#   1. Start minikube (if needed)
#   2. For each example in EXAMPLES:
#      a. Create a Kubernetes Secret from examples/<example>/.env (if present)
#      b. Copy its cortex/ directory into the minikube node via SSH+tar
#      c. Helm install the ai-assistant chart with cortex.hostPath + helm/values.yaml
#      d. Port-forward :8000 and :8501 to the host
#      e. Run the containerised pytest suite (test_environments/helm_test/)
#      f. Tear down port-forward and Helm release
#   3. Report any failures
#
# minikube mount is not used — it is unreliable with the Docker driver on Mac.
# Minikube itself is left running so subsequent runs start faster.
# Use `minikube stop` to shut it down completely.
#
# Usage:
#   bash scripts/post-release-test.sh
#
# Environment:
#   IMAGE_TAG     Docker image tag to deploy (resolved from pyproject.toml + DockerHub if unset)
#   KEEP_RELEASE  Set to "1" to keep the last Helm release after a successful test run

set -euo pipefail

KEEP_RELEASE="${KEEP_RELEASE:-0}"
NODE_CORTEX_PATH="/mnt/ai-assistant-cortex"
SECRET_NAME="ai-assistant-api-keys"

WORKSPACE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CHART_DIR="$WORKSPACE/helm/ai-assistant"
TEST_DIR="$WORKSPACE/test_environments/helm_test"
RELEASE="ai-assistant"
TEST_IMAGE="ai-assistant-helm-test"

PF_PID=""

# ---------------------------------------------------------------------------
# Resolve IMAGE_TAG from the latest git tag
# ---------------------------------------------------------------------------

resolve_image_tag() {
    local latest_tag
    latest_tag="$(git -C "$WORKSPACE" tag --sort=-version:refname \
        | grep -E '^v[0-9]+\.[0-9]+\.[0-9]+' \
        | head -1)"
    if [[ -n "$latest_tag" ]]; then
        echo "${latest_tag#v}"
        return
    fi
    # Fallback: bare version from pyproject.toml
    grep -m1 '^version' "$WORKSPACE/pyproject.toml" | sed 's/.*= *"\(.*\)"/\1/'
}

IMAGE_TAG="${IMAGE_TAG:-$(resolve_image_tag)}"
echo ">>> Using image tag: $IMAGE_TAG"

# ---------------------------------------------------------------------------
# Examples to test (cloud-provider examples only — no self-hosted LLM servers)
# ---------------------------------------------------------------------------

EXAMPLES=(
    mistral_example
)

echo ">>> Testing examples: ${EXAMPLES[*]}"

# ---------------------------------------------------------------------------
# Cleanup helpers
# ---------------------------------------------------------------------------

stop_port_forward() {
    if [[ -n "$PF_PID" ]] && kill -0 "$PF_PID" 2>/dev/null; then
        kill "$PF_PID" 2>/dev/null || true
        wait "$PF_PID" 2>/dev/null || true
        echo "    Port-forward stopped."
        PF_PID=""
    fi
}

# ---------------------------------------------------------------------------
# API keys secret from .env
# ---------------------------------------------------------------------------

create_api_secret() {
    local example="$1"
    local env_file="$WORKSPACE/examples/${example}/.env"
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
# Build test image once
# ---------------------------------------------------------------------------

echo ">>> Building test image..."
docker build -t "$TEST_IMAGE" "$TEST_DIR"

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

# ---------------------------------------------------------------------------
# Run tests for each example
# ---------------------------------------------------------------------------

FAILED_EXAMPLES=()

for EXAMPLE in "${EXAMPLES[@]}"; do
    EXAMPLE_DIR="$WORKSPACE/examples/$EXAMPLE"
    CORTEX_DIR="$EXAMPLE_DIR/cortex"
    HELM_VALUES="$EXAMPLE_DIR/helm/values.yaml"

    echo ""
    echo "=========================================="
    echo ">>> Testing example: $EXAMPLE"
    echo "=========================================="

    prepull_images "$HELM_VALUES"
    create_api_secret "$EXAMPLE"

    echo ">>> Copying cortex into minikube node at $NODE_CORTEX_PATH..."
    _tmptar=$(mktemp /tmp/cortex-XXXXXX.tar)
    COPYFILE_DISABLE=1 tar -C "$CORTEX_DIR" --exclude='._*' --exclude='.DS_Store' -cf "$_tmptar" .
    minikube cp "$_tmptar" /tmp/cortex.tar
    rm "$_tmptar"
    minikube ssh -- "sudo mkdir -p $NODE_CORTEX_PATH && sudo tar --warning=no-unknown-keyword -xf /tmp/cortex.tar -C $NODE_CORTEX_PATH && sudo rm /tmp/cortex.tar"
    echo "    Cortex copied."

    echo ">>> Installing chart (image tag: $IMAGE_TAG)..."
    if ! helm upgrade --install "$RELEASE" "$CHART_DIR" \
        --set "image.tag=${IMAGE_TAG}" \
        --set "cortex.hostPath=${NODE_CORTEX_PATH}" \
        -f "$HELM_VALUES" \
        --wait --timeout 600s; then
        echo "ERROR: helm install failed for $EXAMPLE." >&2
        FAILED_EXAMPLES+=("$EXAMPLE")
        continue
    fi

    if lsof -ti tcp:8000 >/dev/null 2>&1; then
        echo "ERROR: Port 8000 is already in use on the host. Free it before running post-release tests." >&2
        echo "    Run: lsof -ti tcp:8000 | xargs kill" >&2
        helm uninstall "$RELEASE" 2>/dev/null || true
        FAILED_EXAMPLES+=("$EXAMPLE")
        continue
    fi

    echo ">>> Starting port-forward on :8000 and :8501..."
    kubectl port-forward \
        --address 0.0.0.0 \
        "svc/${RELEASE}" \
        8000:8000 8501:8501 &
    PF_PID=$!
    sleep 3

    if ! kill -0 "$PF_PID" 2>/dev/null; then
        echo "ERROR: port-forward failed — ports 8000/8501 may already be in use." >&2
        helm uninstall "$RELEASE" 2>/dev/null || true
        FAILED_EXAMPLES+=("$EXAMPLE")
        continue
    fi

    echo "    Port-forward running (PID $PF_PID)."

    if docker run --rm \
        -e BASE_URL="http://host.docker.internal:8000" \
        -e STREAMLIT_URL="http://host.docker.internal:8501" \
        -v "${TEST_DIR}:/tests" \
        "$TEST_IMAGE" \
        pytest -v; then
        echo ">>> Tests PASSED for $EXAMPLE."
    else
        echo ">>> Tests FAILED for $EXAMPLE — leaving release installed for inspection."
        echo "    kubectl logs deploy/${RELEASE}-ai-assistant"
        echo "    Run 'helm uninstall $RELEASE' to clean up manually."
        FAILED_EXAMPLES+=("$EXAMPLE")
        stop_port_forward
        continue
    fi

    stop_port_forward

    if [[ "$KEEP_RELEASE" != "1" ]]; then
        echo ">>> Uninstalling Helm release '$RELEASE'..."
        helm uninstall "$RELEASE" 2>/dev/null || true
    fi
done

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

echo ""
echo "=========================================="
if [[ ${#FAILED_EXAMPLES[@]} -eq 0 ]]; then
    echo ">>> All post-release Kubernetes tests passed."
    echo "    Tested: ${EXAMPLES[*]}"
else
    echo ">>> FAILED examples: ${FAILED_EXAMPLES[*]}"
    exit 1
fi
