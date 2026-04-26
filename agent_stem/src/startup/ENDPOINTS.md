# Endpoint Discovery

`endpoints.py` scans a directory for Python files and registers each one as an
HTTP route on the FastAPI app at startup.

---

## Directory Layout

By default the scanner looks at `/app/default/endpoints/`, which maps to
`agent_stem/default/endpoints/` in the repository. Subdirectories are traversed
recursively; the subdirectory name is purely organisational and has no effect on
the registered path.

```
default/endpoints/
  public/
    agent_chat.py          →  POST /v1/agent/chat
    chat_completions.py    →  POST /v1/chat/completions
    ollama_generate.py     →  POST /v1/api/generate
  private/
    health.py              →  GET  /health
    books.py               →  GET  /private/v1/books
    providers.py           →  GET  /private/v1/providers
    workflows.py           →  GET  /private/v1/workflows
    ...
```

Files whose names start with `_` are skipped.

---

## What Each File Must Export

Every endpoint file must define exactly two module-level names:

### `handler`

An `async def handler(...)` function. Its signature determines whether the
route receives a request body:

- If the function has a `request` parameter **and** `spec["requestBody"]` is
  non-empty, `api.py` wraps it in a FastAPI `Body(...)` parameter so the
  request body is parsed and validated automatically.
- If neither condition is met, the handler is registered as-is (e.g. a GET
  endpoint with no body).

Path parameters (e.g. `path: str` for a `{path:path}` route) are passed as
keyword arguments.

### `spec`

A plain `dict` that describes the route in OpenAPI terms:

```python
spec = {
    # Required
    "path":    "/private/v1/books",   # FastAPI path string
    "methods": ["GET"],               # list of HTTP verbs (uppercase)

    # Optional but recommended
    "summary":     "List indexed books",
    "description": "Long description shown in Swagger.",

    # At least one 2xx code is required — api.py enforces this at startup.
    "responses": {
        200: {
            "description": "Success",
            "content": {
                "application/json": {
                    "schema":  { ... },   # JSON Schema for the response body
                    "example": { ... },   # Concrete example shown in Swagger
                }
            },
        },
        503: { "description": "Vector store unreachable" },
    },

    # Only needed for POST/PUT/PATCH endpoints
    "requestBody": {
        "required": True,
        "content": {
            "application/json": {
                "schema":  { ... },
                "example": { ... },
            }
        },
    },
}
```

---

## How Routes Are Registered

`api.py` calls `discover_endpoints()` during the `startup` event, then for each
`(name, handler, spec)` tuple:

1. Determines the primary HTTP status code from `spec["responses"]` (defaults
   to 200; uses the lowest 2xx code if 200 is absent).
2. If `requestBody` is present and the handler accepts `request`, wraps the
   handler so FastAPI injects the parsed body.
3. Calls `app.add_api_route(path, handler, methods=..., tags=[tag], ...)` where
   `tag` is `"private"` if the path starts with `/private`, otherwise `"public"`.

Workflow endpoints (from YAML files) follow the same shape but are always
tagged `"workflows"`.

---

## Adding a New Endpoint

1. Create a `.py` file anywhere under `default/endpoints/` (use `public/` or
   `private/` by convention).
2. Define `handler` and `spec` as described above.
3. Restart the container — discovery runs at startup, no code changes needed
   elsewhere.
