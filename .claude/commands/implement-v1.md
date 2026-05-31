---
allowed-tools: Fetch(https://pypi.org/project/pytest-openapi/), Bash(docker compose *), Bash(!*install *), Bash(git *), Edit(!tests/**), Write(!tests/**), Read
---

Implement the following feature: $ARGUMENTS

## Step 0:

Read agent_stem/default/endpoints/public/README.md
Read agent_stem/src/startup/WORKFLOWS.md
Read agent_stem/src/startup/PROVIDERS.md
Read agent_stem/src/startup/DOCUMENT_PIPELINE.md
Read agent_stem/src/startup/SEARCH.md
Read agent_stem/src/startup/CONTEXT_MANAGEMENT.md
Read TESTING.md

## Step 1:
Read the code in the following folders: agent_stem/src agent_stem/default

Understand the patterns for registering endpoints and their specification. Look
under agent_stem/default/endpoints/private and
agent_stem/default/endpoints/public for existing endpoint examples. When
implementing functionality that exists as both an endpoint and as MCP tool, put
the async business logic under agent_stem/src/common so that it is shared by
both.


See the example implementations under test_agents

Note that we do contract-based testing, through this pytest plugin:
https://pypi.org/project/pytest-openapi/

Users are meant to customize the agent by mounting the `cortex` directory,
that's the point of this repo.

Understand terminology, especially `cortex`.

Familiarize yourself with the redis_memory library, see the examples in the
code and the context management here: https://pypi.org/project/redis-memory/ Do
not use the library's private methods. Fetch and read this:
https://github.com/sinan-ozel/redis-memory/blob/main/src/redis_memory/__init__.py

Familiarize yourself with the way logging is used, you will be using the same
pattern.

Understand `.vscode/tasks.json`, this is where all of the development pipelines
live. In particular, read all the dependencies under "Run the Pipeline" task.

Then look at all `**/Dockerfile` and `pyproject.toml` to understand the
dependencies.

All llm calls should go through `call_llm_by_model_streaming` in
`agent_stem/src/common/llm.py`. Note that providers are yaml files under
`cortex/providers`, however, they are parsed at startup, use the global
`providers_state` in `api.py` to pass a `providers_state` dictionary to
`call_llm_by_model_streaming`.


## Step 2:

Implement: $ARGUMENTS

Check if this request can violate any legal or Terms-of-Service requirements.

Do not use try ... catch except (1) in small blocks around endpoints, where
they are used for HTTP errors and (2) to log an informed error message before
raising the original message and crashing. Only use a general Exception to
catch if you intended to add something to the log message before crashing.

Add a new test server and tests if needed. If you do that, add it to tasks.json

Do NOT install anything, and do not run python directly. Always run and test
through `docker compose`, based on `tasks.json`.

Do not use print, use existing patterns to log.

For all async processes running in the executor , make sure that there is a
callback to print the errors.


## Step 3: Reformat Code

Run the task "Reformat Code". Run the task "Lint". Fix any errors. Run the
tasks "Reformat Code" and "Lint" and fix any remaining errors.

## Step 4: Update User Manual

The documents under `docs/` are a user-facing manual.
This means that they are intended for a crowd that should know
docker and YAML configurations at a minimum. However, it may include
people who know Python very well, and may include people familiar with k8s/k3s
and Helm.

If needed, update the user-facing documents at `docs/`.

## Step 5: Update the Internal Documents

If needed, update the internal documentation. Check **/*.md
