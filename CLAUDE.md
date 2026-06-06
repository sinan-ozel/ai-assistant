Do NOT install anything, and do not run python directly. Always run and test
through `docker compose`, based on `tasks.json`.

# Docker image conventions

**`agent_stem/` and `test_environments/`** use `build:` in docker-compose — no
`image:` field for the app container. Docker Compose builds the image locally
from `agent_stem/Dockerfile`. Never add `image: <local-name>` to these files;
it causes Docker to try to pull a non-existent registry image.

The "Run Agent" tasks in `tasks.json` pass `--build` to `docker compose up` so
the image is always rebuilt from the current source. The standalone "Build
Container" task tags the image as `ai-assistant-dev:latest` for inspection or
sharing; it is not a prerequisite for running the agent.

**`examples/`** always pull from Docker Hub:
`image: sinanozel/ai-assistant:<TAG>`. The Helm charts do the same. Tag
resolution for post-release tests is computed from `pyproject.toml` +
`build_number.txt`: `VERSION-dev.(BUILD_NUMBER-1)` for dev releases, bare
`VERSION` for production releases.

# Coding Practices

## Error handling

Use try...except only around very small blocks and with specific errors.

Make sure that errors related to configuration and devops concerns such as hostnames
fail at started with an exit 1, after logging the error.
If you rewrite the error, make sure that it is facing devops operations
and includes an actionable item.

Make sure that the errors during API calls that are originating from user behaviour are caught
and responded with a 400 message. The message should clarify what went wrong specifically,
and explain the responses expected from the user, including even an example
In general, errors that are created because of the user behaviour should respond
include an action suggestion, and an example if applicable.
Do not do a general catch-all here, we want to catch fails through the test harness.

If there is an async process within the server, catch the exceptions with the particular
error, log the error, and continue execution. General catches can be fine, but if
there is something important to add the to logging message, first catch the specific
error that the additonal info is related to.

## Logging

Do not use print, use existing patterns in the code to log.

## Async Processes

For all async processes running in the executor, make sure that there is a
callback to print the errors.

## Object Classes

For all classes and objects with inheritance, do not go any levels
deeper than one parent, one child.

LLM calls should all go through:
agent_stem/src/common/llm.py call_llm_by_model_streaming



# Testing

Tests should use endpoints from agent_stem, and should not connect to Redis or
Qdrant or any other service directly. The system needs to be able to operate
without any services, and in fact, new services could be added underneath
without changing the tests. pytext fixtures can connect directly, but these
need to be graceful if these services do not exist. This is black-box testing,
everything is being test through request bodies and the responses.


# synced-memory examples:

```
with Memory() as memory:
    memory.session = "active"
    print(memory.session)  # "active"

# Later, in a new context:
with Memory() as memory:
    print(memory.session)  # "active"
```

Always use this pattern. Correct if used otherwise.

Here is the github repo if you need to check the repo:
https://github.com/sinan-ozel/synced-memory

Here is the code base with the cor logic for synced-memory.
https://raw.githubusercontent.com/sinan-ozel/synced-memory/refs/heads/main/src/synced_memory/common/__init__.py

# Environment

There is no python in the development environment, it runs in containers only.
Do not install python or anything else.
Do not try to use pip or pip3.
Instead, look into pyproject.toml for the source of truth for libraries.

Use bash whenever possible, jq and yq are also there.
If something needs to be part of the CI/CD pipeline,
create containerized scripts.
