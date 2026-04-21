# Contributing

Contributions are welcome. You need: Git, Docker, and an LLM (Mistral, OpenAI, Anthropic, or local).

## Workflow

1. Fork the repository and clone locally.
2. Create a feature branch: `git checkout -b my-feature`
3. Under `test_agents/`, write a test agent that covers the behaviour you are adding.
4. Implement the feature.
5. Run **Reformat Code** then **Lint** from the VS Code task menu (or directly via `docker compose`).
6. Run the relevant integration tests. All existing tests must still pass.
7. Push and open a pull request.

## Bug reports

You do not need development experience to file a bug report.

Please include:
1. Your `cortex/` directory contents (or the relevant part).
2. What you expected to happen.
3. What happened instead.

Open an issue on GitHub.

## Code style

- Python 3.12
- Formatting: `black` (line length 80)
- Import sorting: `isort` (black profile)
- Linting: `ruff` (`I`, `F`, `E`, `W`, E501 ignored)
- Docstring formatting: `docformatter`

All of these run via the **Reformat Code** and **Lint** VS Code tasks (Docker-based — no local
Python install required).

## Adding an endpoint

1. Create a file under `agent_stem/default/endpoints/public/` or `private/`.
2. If the endpoint shares business logic with another endpoint or MCP tool, put the async
   logic in `agent_stem/src/common/`.
3. All LLM calls must go through `call_llm_by_model_streaming` in `agent_stem/src/common/llm.py`.
4. Write a test agent and add it to the integration test matrix in `tasks.json`.

## Docker-only development

The project is designed to run entirely inside Docker. Do not install packages locally
or run Python directly. All development commands go through `docker compose`:

- **Reformat**: `docker compose -f reformat/docker-compose.yaml up --build`
- **Lint**: `docker compose -f lint/docker-compose.yaml up --build --abort-on-container-exit --exit-code-from linter`
- **Test**: see [Testing](testing.md)
