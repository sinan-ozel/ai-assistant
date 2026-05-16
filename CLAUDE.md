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

Do not use try ... catch except (1) in small blocks around endpoints, where
they are used for HTTP errors and (2) to log an informed error message before
raising the original message and crashing. Only use a general Exception to
catch if you intended to add something to the log message before crashing.

Do not use print, use existing patterns in the code to log.

For all async processes running in the executor, make sure that there is a
callback to print the errors.

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
Use bash whenever possible, jq and yq are also there.
If something needs to be part of the CI/CD pipeline,
create containerized scripts.
