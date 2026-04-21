#!/bin/bash

# Script to run all linting and reformatting steps from GitHub Actions locally
# This script mirrors the reformat and lint jobs from .github/workflows/ci.yaml

set -e  # Exit on error

echo "=========================================="
echo "Installing dependencies..."
echo "=========================================="
echo "Skipping project install; using lint tools preinstalled in the image."

echo ""
echo "=========================================="
echo "Running Ruff (linter)..."
echo "=========================================="
ruff check ./agent_stem

echo ""
echo "=========================================="
echo "Checking for print() calls..."
echo "=========================================="
python3 ./lint/check_no_print.py

echo ""
echo "=========================================="
echo "All linting and formatting steps completed!"
echo "=========================================="
