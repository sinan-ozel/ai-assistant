# Providers

A provider YAML file configures an LLM backend. Each file in `cortex/providers/` is discovered at startup, validated with a test call, and made available to endpoints and workflows.

## How it works

**Every top-level key in a provider YAML is passed directly as a keyword argument to LiteLLM's `acompletion()`.** The YAML is a thin config layer on top of LiteLLM — if LiteLLM accepts a parameter, you can put it in the YAML.

```python
# providers.py loads the YAML and passes it straight through:
response = await acompletion(
    model=config["model"],
    api_base=config.get("api_base"),
    api_key=config.get("api_key"),
    timeout=config.get("timeout"),
    # ... any other keys in the file
    messages=messages,
)
```

This means the full [LiteLLM parameter list](https://docs.litellm.ai/docs/completion/input) is available — `temperature`, `max_tokens`, `top_p`, `stop`, `response_format`, etc. — simply by adding them to the YAML.

## File location

```
cortex/
  providers/
    default.yaml       ← used unless overridden
    vision.yaml        ← named provider, referenced by workflows
    coding.yaml        ← another named provider
```

The filename (without `.yaml`) is the provider's name. `default.yaml` is special — it is the provider used by all endpoints unless a workflow specifies `provider:` or `DEFAULT_PROVIDER` points elsewhere.

Files starting with `_` are ignored. All other `.yaml` files in the directory are loaded.

## Canonical provider names

While any filename is valid, these names have standardised meaning across workflows, documentation, and built-in tooling. Using them makes your configuration portable and readable to anyone familiar with the framework.

| Name | Purpose |
|---|---|
| `default` | General-purpose fallback — used when no provider is specified |
| `large` | High-capability model for complex or long-context tasks |
| `small` | Fast, low-cost model for simple or high-volume tasks |
| `vision` | Multimodal model that accepts image inputs |
| `reasoning` | Model optimised for step-by-step reasoning (chain-of-thought, o-series, etc.) |
| `evaluation` | Model used by the self-evaluation / scoring pipeline |
| `coding` | Model optimised for code generation and analysis |
| `embedding` | Embedding model — returns vectors, not text completions |

Any name is accepted; these are conventions, not constraints. Workflows reference providers by name, so consistency matters across your `cortex/providers/` directory.

## Provider selection rules

At startup, the system picks a default provider following this priority:

1. `cortex/providers/default.yaml` — if it exists, this wins. The app crashes if it fails validation.
2. `DEFAULT_PROVIDER` env var matching a file in `cortex/providers/` — crashes on failure.
3. The only file in `cortex/providers/` if exactly one exists — used as default if it validates.
4. `DEFAULT_PROVIDER` env var matching a built-in provider — logs an error but continues.
5. Built-in `default.yaml` (Mistral large) — requires `MISTRAL_API_KEY`. On failure, runs in no-LLM mode.

Named providers (non-default) are loaded but not validated at startup. They are only used when a workflow explicitly declares `provider: <name>`.

## Environment variable substitution

Values matching `${VAR_NAME}` are substituted from environment variables at load time. This is the standard way to inject secrets and environment-specific values without hardcoding them.

```yaml
api_key: ${MISTRAL_API_KEY}
api_base: http://${OLLAMA_HOST}/v1
```

If a variable is not set, the raw `${VAR_NAME}` string is kept, and the provider is marked unavailable due to a missing API key check.

## Examples

### Mistral API (cloud)

```yaml
api_base: https://api.mistral.ai
model: mistral/mistral-large-2512
api_key: ${MISTRAL_API_KEY}
```

### Ollama (local or self-hosted)

```yaml
api_base: http://ollama-test:11434
model: ollama/gemma3:270m
```

No `api_key` needed. The `ollama/` prefix tells LiteLLM to use Ollama's API format. The model name after the slash must match the model tag loaded in Ollama (`ollama pull gemma3:270m`).

### Ollama over a VPN / remote host

```yaml
api_base: http://localhost:11434
model: ollama/gemma3:1b
timeout: 150
```

### llama.cpp (OpenAI-compatible server)

llama.cpp exposes an OpenAI-compatible API. Use the `openai/` prefix and provide a dummy key (llama.cpp ignores it):

```yaml
api_base: http://localhost:8080/v1
model: openai/gemma4:e2b
api_key: dummy
timeout: 150
```

Note: llama.cpp ignores the model name and serves whatever model is currently loaded. The name in the YAML is for documentation only.

### OpenAI

```yaml
model: gpt-4o
api_key: ${OPENAI_API_KEY}
```

No `api_base` needed — LiteLLM defaults to OpenAI's endpoint when the model name is an OpenAI model.

### Anthropic

```yaml
model: anthropic/claude-sonnet-4-5
api_key: ${ANTHROPIC_API_KEY}
```

### Adding LiteLLM parameters

Since all keys pass through to `acompletion()`, any LiteLLM parameter can be set at the provider level:

```yaml
api_base: https://api.mistral.ai
model: mistral/mistral-small-2501
api_key: ${MISTRAL_API_KEY}
timeout: 30
temperature: 0.2
max_tokens: 1024
```

These become the defaults for every request routed through this provider. Request-level parameters (from the request body) do NOT override provider-level parameters — the YAML takes precedence.

### Disabled provider

```yaml
_enabled: false
model: ollama/some-model
api_base: http://localhost:11434
```

`_enabled: false` causes the file to be loaded but skipped — the provider is never validated or made available. Useful for temporarily disabling a provider without deleting the file. (`_enabled` is a framework field, not passed to LiteLLM.)

### Commented-out provider (work in progress)

```yaml
# api_base: http://llamacpp-test:8080/v1
# model: openai/qwen3:0.6b
```

A fully-commented file loads as `None` from YAML and is treated as an error (missing `model` field). Use `_enabled: false` instead for a cleaner disabled state.

---

## Validation at startup

When a provider is selected as the default, the system makes a real LLM call (`messages: [{role: user, content: Hi}]`, `max_tokens: 10`, `timeout: 60`) to verify it is reachable and responding. If this fails, the system either crashes (for custom providers and `DEFAULT_PROVIDER`) or logs a warning and continues in no-LLM mode (for the built-in fallback).

Named (non-default) providers are not validated at startup — they are marked available based on API key presence only. Errors for named providers surface at request time.
