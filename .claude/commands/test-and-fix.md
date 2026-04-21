---
allowed-tools: Fetch(https://pypi.org/project/pytest-openapi/), Bash(*docker compose *), Bash(!*install *), Edit(!test_agents/**), Write(!test_agents/**), Edit(!tests/**), Write(!tests/**), Read, Edit, Write
---

## Step 0:

Read agent_stem/default/endpoints/public/README.md
Read agent_stem/src/startup/WORKFLOWS.md
Read agent_stem/src/startup/PROVIDERS.md
Read agent_stem/src/startup/DOCUMENT_PIPELINE.md
Read agent_stem/src/startup/SEARCH.md
Read TESTING.md

See the example implementations under test_agents

Note that we do contract-based testing, through this pytest plugin:
https://pypi.org/project/pytest-openapi/
Do not search this module locally, download the URL and read it.
You will not find it locally because it is containerized.

Understand `.vscode/tasks.json`, this is where all of the development pipelines
live. In particular, read all the dependencies under "Run the Pipeline" task.

Note that all tests run containerized. You are not allowed to install anything
on the environment.


## Step 1: Run the tests

Run the tests as in the task "Run Integration Tests: $ARGUMENTS"

Summarize the output. If all tests pass and no tests are skipped, report and finish.

## Step 2: Fix

If some tests are failing, fix.

Do not use try ... catch except (1) in small blocks around endpoints, where
they are used for HTTP errors and (2) to log an informed error message before
raising the original message and crashing. Only use a general Exception to
catch if you intended to add something to the log message before crashing.

Do not use print, use existing patterns to log.

DO NOT EDIT THE TESTS. DO NOT EDIT ENVIRONMENT.

Fix the code under `agent_stem` without asking for permission.

Do not edit anything under `tests`. Do not edit anything under `test_agents`.

If you hit the point where you have to fix something in the tests, stop and ask.

## Step 3: Reformat Code

Run the task "Reformat Code".
Run the task "Lint". Fix any errors.
Run the tasks "Reformat Code" and "Lint" and fix any remaining errors.
