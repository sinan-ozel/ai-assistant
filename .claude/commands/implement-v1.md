---
allowed-tools: Bash(docker compose *), Bash(git *), Edit(!tests/**), Write(!tests/**), Read
---

Implement the following feature: $ARGUMENTS

## Step 0:

Read agent_stem/default/endpoints/public/README.md
Read agent_stem/src/startup/WORKFLOWS.md

## Step 1:
Read the code in the following folders:
agent_stem/src
agent_stem/default

Understand the patterns for registering endpoints and their specification.

See the example implementations under
test_agents

Users are meant to customize the agent by mounting the `cortex` directory,
that's the point of this repo.

Understand terminology, especially `cortex`.

Familiarize yourself with the redis_memory library, see the examples in the code and the context management here:
https://pypi.org/project/redis-memory/
Do not use the library's private methods.

Familiarize yourself with the way logging is used, you will be using the same pattern.

Understand `.vscode/tasks.json`, this is where all of the development pipelines live.

Then look at all `**/Dockerfile` and `pyproject.toml` to understand the dependencies.

## Step 2:

Implement: $ARGUMENTS

Do not use try ... catch except (1) in small blocks around endpoints, where they are used for HTTP errors and (2) to log an informed error message before raising the original message and crashing. Only use a general Exception to catch if you intended to add something to the log message before crashing.

Add a new test server and tests if needed. If you do that, add it to tasks.json

Do NOT install anything, and do not run python directly. Always run and test through `docker compose`, based on `tasks.json`.

## Step 3: Reformat Code

Run the task "Reformat Code".
Run the task "Lint". Fix any errors.
Run the tasks "Reformat Code" and "Lint" and fix any remaining errors.

## Step 4: Run the tests

Run the tests in "(!) Run All Tests" exactly as in tasks.json.

## Step 5: Repeat until all tests pass.

Fix any errors from the previous step.
Run the tests in "(!) Run All Tests" exactly as in tasks.json.

## Step 6: Reformat Code

Run the task "Reformat Code".
Run the task "Lint". Fix any errors.
Run the tasks "Reformat Code" and "Lint" and fix any remaining errors.

