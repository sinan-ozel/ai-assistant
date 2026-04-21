#!/bin/bash
set -e

# repository subfolder to run formatting against
mfolder="agent_stem"

echo ""
echo "=========================================="
echo "Running formatters..."
echo "=========================================="

# directories to format under the repository subfolder
targets=("$mfolder/src" "$mfolder/default" "test_agents/text_workflows/tests" "test_agents/image_workflows/tests" "test_agents/agent_with_eval/tests" "test_agents/agent_with_incorrect_eval/tests" "test_environments/test_env_everything" "test_environments/test_env_local_llm" "test_environments/test_self_hosted_llm" "test_environments/test_env_mistral" "test_environments/test_env_no_llm" "test_environments/test_env_nothing")

for d in "${targets[@]}"; do
  if [ -d "$d" ]; then
    echo ""
    echo "=========================================="
    echo "Running isort on $d..."
    echo "=========================================="
    isort "$d"

    echo ""
    echo "=========================================="
    echo "Running Black on $d..."
    echo "=========================================="
    black "$d"

    echo ""
    echo "=========================================="
    echo "Running docformatter on $d..."
    echo "=========================================="
    docformatter "$d"

    echo ""
    echo "=========================================="
    echo "Running ruff --fix on $d..."
    echo "=========================================="
    ruff check "$d" --fix
  else
    echo "Skipping $d (directory not found)."
  fi
done

echo ""
echo "=========================================="
echo "Formatting complete!"
echo "=========================================="
