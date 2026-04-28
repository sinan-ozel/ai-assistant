Do NOT install anything, and do not run python directly. Always run and test
through `docker compose`, based on `tasks.json`.

# Coding Practices

Do not use try ... catch except (1) in small blocks around endpoints, where
they are used for HTTP errors and (2) to log an informed error message before
raising the original message and crashing. Only use a general Exception to
catch if you intended to add something to the log message before crashing.

Do not use print, use existing patterns in the code to log.

For all async processes running in the executor, make sure that there is a
callback to print the errors.

For all classes and objects with inheritance, do not go any levels
deeper than one parent, one child

# Testing

Tests should use endpoints from agent_stem, and should not connect to Redis or
Qdrant or any other service directly. The system needs to be able to operate
without any services, and in fact, new services could be added underneath
without changing the tests. pytext fixtures can connect directly, but these
need to be graceful if these services do not exist. This is black-box testing,
everything is being test through request bodies and the responses.


# redis-memory examples:

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
https://github.com/sinan-ozel/redis-memory

Here is the code base: https://github.com/sinan-ozel/redis-memory/blob/main/src/redis_memory/__init__.py

