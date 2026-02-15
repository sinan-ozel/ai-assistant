#!/bin/bash
set -e

# repository subfolder to run formatting against
mfolder="agent_stem"

echo ""
echo "=========================================="
echo "Running formatters..."
echo "=========================================="

# directories to format under the repository subfolder
targets=("$mfolder/src" "$mfolder/default")

for d in "${targets[@]}"; do
  if [ -d "$d" ]; then
    echo ""
    echo "=========================================="
    echo "Running Black on $d..."
    echo "=========================================="
    black "$d"

    echo ""
    echo "=========================================="
    echo "Running docformatter on $d..."
    echo "=========================================="
    docformatter \
      --in-place \
      --recursive \
      --wrap-summaries 72 \
      --wrap-descriptions 72 \
      "$d"

    echo ""
    echo "=========================================="
    echo "Running isort on $d..."
    echo "=========================================="
    isort "$d"
  else
    echo "Skipping $d (directory not found)."
  fi
done

echo ""
echo "=========================================="
echo "Formatting complete!"
echo "=========================================="
