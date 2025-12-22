#!/bin/bash

# Run all test environments, filter output to show only test results, and exit with code 1 if any test fails

set -e

WORKSPACE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FAILED=0

echo "========================================"
echo "Running All Test Suites"
echo "========================================"

# Test environments to run
declare -a TEST_ENVS=(
    "test_env_no_llm"
    "test_env_nothing"
    # "test_env_mistral"
    "test_env_self_hosted_llm"
    # "test_env_local_llm"
)

for env in "${TEST_ENVS[@]}"; do
    echo ""
    echo "========================================"
    echo "Running: $env"
    echo "========================================"

    # Run docker compose and capture output
    output=$(docker compose \
        -f "$WORKSPACE_ROOT/test_environments/$env/docker-compose.yaml" \
        --project-directory "$WORKSPACE_ROOT/test_environments/$env" \
        up --build --abort-on-container-exit --exit-code-from tests 2>&1) || true

    # Filter and display test results
    filtered_output=$(echo "$output" | grep -E 'PASSED|FAILED|SKIPPED|passed|failed|skipped|ERROR' || true)
    echo "$filtered_output"

    # Check if any tests failed
    if echo "$filtered_output" | grep -qiE 'FAILED|ERROR'; then
        echo "❌ $env: FAILED"
        FAILED=1
    else
        echo "✅ $env: PASSED"
    fi
done

echo ""
echo "========================================"
echo "Test Suite Summary"
echo "========================================"

if [ $FAILED -eq 1 ]; then
    echo "❌ Some tests FAILED"
    exit 1
else
    echo "✅ All tests PASSED"
    exit 0
fi
