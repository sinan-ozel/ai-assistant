#!/bin/bash
set -e

# repository subfolder to run formatting against
mfolder="agent_stem"

echo ""
echo "=========================================="
echo "Running formatters..."
echo "=========================================="

# directories to format under the repository subfolder
targets=(
    "$mfolder/src"
    "$mfolder/default"
    "test_agents/agent_with_collection_search/tests"
    "test_agents/agent_with_cortex_tools/tests"
    "test_agents/agent_with_default_tools/tests"
    "test_agents/agent_with_eval/tests"
    "test_agents/agent_with_incorrect_eval/tests"
    "test_agents/agent_with_memory/tests"
    "test_agents/agent_with_only_a_system_message/tests"
    "test_agents/agent_with_search/tests"
    "test_agents/agent_with_search_2/tests"
    "test_agents/agent_with_search_3/tests"
    "test_agents/agent_with_temperature/tests"
    "test_agents/agent_with_tool_and_delay/tests"
    "test_agents/agent_with_tool_and_delay_on_mistral/tests"
    "test_agents/agent_with_tools/tests"
    "test_agents/agent_with_tools_advanced/tests"
    "test_agents/agent_with_two_mcp_servers/tests"
    "test_agents/agent_without_tool_title/tests"
    "test_agents/anthropic_agent/tests"
    "test_agents/bad_agent/tests"
    "test_agents/coding_agent/tests"
    "test_agents/complex_agent_1/tests"
    "test_agents/image_workflows/tests"
    "test_agents/incorrect_agent/tests"
    "test_agents/mistral_agent/tests"
    "test_agents/no_agent/tests"
    "test_agents/son_of_anton/tests"
    "test_agents/talk_to_your_documents/tests"
    "test_agents/text_workflows/tests"
    "test_environments/helm_test"
    "test_environments/test_env_anthropic"
    "test_environments/test_env_bad_agent"
    "test_environments/test_env_default"
    "test_environments/test_env_local_llm"
    "test_environments/test_env_mcp"
    "test_environments/test_env_mistral"
    "test_environments/test_env_no_llm"
    "test_environments/test_env_no_qdrant"
    "test_environments/test_env_no_redis"
    "test_environments/test_env_nothing"
    "test_environments/test_env_openapi"
    "test_environments/test_env_self_hosted_llm"
)

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
