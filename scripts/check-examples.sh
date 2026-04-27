#!/usr/bin/env bash
# Check that every example directory contains helm/values.yaml.
# Exit 1 if any are missing.

set -euo pipefail

EXAMPLES_DIR="$(cd "$(dirname "$0")/../examples" && pwd)"
MISSING=()

for example in "$EXAMPLES_DIR"/*/; do
    name="$(basename "$example")"
    if [ ! -f "$example/helm/values.yaml" ]; then
        MISSING+=("$name")
    fi
done

if [ ${#MISSING[@]} -eq 0 ]; then
    echo "OK: all examples have helm/values.yaml"
    exit 0
else
    echo "ERROR: the following examples are missing helm/values.yaml:"
    for name in "${MISSING[@]}"; do
        echo "  - $name"
    done
    exit 1
fi
