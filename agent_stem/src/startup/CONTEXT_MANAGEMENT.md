# Context Management

Context management is a two-stage problem: determining the model's context window size, and fitting the conversation history within it.

---

## Stage 1: Determining the Context Window

On startup, `providers.py` queries all available providers concurrently via `discover_context_windows()`. Each query calls `query_context_window()`, which uses LiteLLM's `get_model_info()` to retrieve the model's `max_tokens` or `max_input_tokens` field. Results are cached in the provider state at `provider["llm_responses"]["context_window"]` and retrieved at runtime via `get_provider_context_window()` in `src/situational/awareness/__init__.py`.

At request time, the effective context window is resolved in this order:

1. `CONVERSATION_WINDOW_LIMIT` environment variable — manual override
2. LiteLLM's queried model info — authoritative model capability
3. **Hard fallback: 4096 tokens**

### VRAM / Hardware Constraints

`CONVERSATION_WINDOW_LIMIT` is the bridge between model capability and deployment reality. A model may support 32k tokens theoretically, but if the inference server is memory-constrained, setting `CONVERSATION_WINDOW_LIMIT=4096` keeps sequence lengths within hardware limits without modifying the model.

The local LLM test environments (`test_environments/test_env_local_llm/`) illustrate this: Docker containers reserve 1 GB per model, `CONVERSATION_WINDOW_LIMIT=4096` is set in docker-compose, and the commented-out llama.cpp flag `-c 4096` applies the same limit at the inference server level.

Known context window values from test environments:
- `gemma3:270m` (Ollama local): 32,768 tokens
- `mistral-7b` (Mistral API): 8,191 tokens

---

## Stage 2: Fitting Conversation History

On every request, `fit_messages_to_context()` in `agent_chat.py` trims the message history to fit within the resolved context window:

1. Counts system prompt tokens using `tiktoken` (`cl100k_base` encoding)
2. Reserves 1,000 tokens for the LLM response buffer
3. Available budget: `context_window - system_tokens - 1000`
4. If fewer than 100 tokens remain, returns empty history
5. Works **backwards** from the most recent messages, keeping as many as fit
6. Strips base64-encoded image content to prevent overflow

The **full conversation history is always retained in Redis**. Only the subset of messages sent to the LLM on a given request is trimmed. Long-term memory survives even when old turns exceed the context window.

---

## Configuration Hierarchy

From highest to lowest precedence:

| Level | Mechanism |
|---|---|
| Request | `max_tokens` in the API request body |
| DSL | `agent.max_tokens` in `cortex/chat/prompt.py` |
| Provider | `max_tokens` in the provider YAML file |
| System | `CONVERSATION_WINDOW_LIMIT` environment variable |
| Model | LiteLLM `get_model_info()` at startup |
| Fallback | Hard-coded 4096 tokens |

Note: request-level parameters do not override provider-level settings (see `PROVIDERS.md`).
