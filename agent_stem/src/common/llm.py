"""Common LLM completion interface using LiteLLM.

This module provides an abstraction layer over LiteLLM that can be used by all
endpoints (chat completions, generate, agent chat, etc.).
"""

import asyncio
import logging
import time
from typing import Any, AsyncGenerator, Dict, List, Optional

import litellm
from litellm import acompletion

logger = logging.getLogger(__name__)

# Fallback used when neither the provider YAML nor the caller specifies a
# timeout. Without this, asyncio.wait(timeout=None) blocks indefinitely when
# an LLM backend (e.g. Ollama) accepts the connection but never sends a reply.
_DEFAULT_TIMEOUT = 30.0

# A provider crossing both of these counts as a sustained outage rather than
# a transient blip, changing how failures get logged/reported. Chosen so a
# single prompt()'s own in-turn retry loop (2-3 attempts, ~15s of backoff)
# never triggers this on its own — it only fires once a provider has kept
# failing across multiple separate calls over more than a minute.
_SUSTAINED_OUTAGE_FAILURE_COUNT = 5
_SUSTAINED_OUTAGE_SECONDS = 60.0


def root_cause_message(exc: BaseException) -> str:
    """Return *exc*'s message plus its deepest chained cause's message.

    The ``openai`` SDK hardcodes ``APIConnectionError``'s message to the
    literal string "Connection error." regardless of what actually failed
    (DNS lookup, connection refused, timeout, ...), and litellm re-wraps
    that same generic string. The real reason survives only in Python's
    exception chain (``__cause__``), which ``str(exc)`` never includes —
    walk it so logs show what actually happened instead of a placeholder.
    """
    root = exc
    seen = {id(exc)}
    while root.__cause__ is not None and id(root.__cause__) not in seen:
        root = root.__cause__
        seen.add(id(root))
    if root is exc:
        return str(exc)
    return f"{exc} — caused by: {root}"


class _ProviderHealth:
    """Tracks consecutive completion failures per model, across calls.

    A single call's own retry loop only sees a couple of attempts a few
    seconds apart — not enough to tell a one-off blip from a provider that
    has been down across many turns and users. This keeps a small
    in-process streak per model so failure logging can tell the difference.
    """

    def __init__(self) -> None:
        self._consecutive_failures: Dict[str, int] = {}
        self._failing_since: Dict[str, float] = {}

    def note_success(self, model: str) -> None:
        self._consecutive_failures.pop(model, None)
        self._failing_since.pop(model, None)

    def note_failure(self, model: str) -> tuple[int, float]:
        now = time.monotonic()
        count = self._consecutive_failures.get(model, 0) + 1
        self._consecutive_failures[model] = count
        since = self._failing_since.setdefault(model, now)
        return count, now - since


_provider_health = _ProviderHealth()


def _annotate_failure(exc: BaseException, model: str) -> None:
    """Record *model*'s failure and stamp streak info onto *exc*.

    Callers up the stack catch this same exception object, so they can read
    ``exc.sustained_outage`` etc. directly instead of keeping their own
    tracker or re-deriving the provider key.
    """
    count, since = _provider_health.note_failure(model)
    exc.consecutive_failures = count
    exc.failing_since_seconds = since
    exc.sustained_outage = (
        count >= _SUSTAINED_OUTAGE_FAILURE_COUNT
        and since >= _SUSTAINED_OUTAGE_SECONDS
    )


def _truncate_value(value: Any, max_length: int = 100) -> Any:
    """Truncate long string values for logging."""
    if isinstance(value, str) and len(value) > max_length:
        return (
            value[:max_length] + f"... (truncated, total length: {len(value)})"
        )
    elif isinstance(value, dict):
        return {k: _truncate_value(v, max_length) for k, v in value.items()}
    elif isinstance(value, list):
        return [_truncate_value(item, max_length) for item in value]
    return value


def _truncate_messages(
    messages: List[Dict[str, Any]], max_length: int = 100
) -> List[Dict[str, Any]]:
    """Truncate long content in messages (e.g., base64 images)."""
    return [_truncate_value(msg, max_length) for msg in messages]


def get_provider_config(
    providers_state: Dict[str, Any],
    requested_model: Optional[str] = None,
) -> tuple[str, Dict[str, Any]]:
    """Get provider configuration for the requested model.

    Args:
        providers_state: Provider discovery state
        requested_model: Requested model name (optional)

    Returns:
        Tuple of (model_to_use, provider_config)

    Raises:
        ValueError: If no providers available or requested model not found
    """
    if not providers_state.get("available_providers"):
        raise ValueError("No LLM providers available")

    # Find the provider to use
    provider_to_use = None

    if requested_model:
        # Strip provider prefix if present
        # (e.g., "ollama/gemma3:4b" -> "gemma3:4b")
        model_without_prefix = requested_model
        if "/" in requested_model:
            parts = requested_model.split("/", 1)
            if parts[0] in [
                "ollama",
                "openai",
                "anthropic",
                "google",
                "mistral",
                "cohere",
            ]:
                model_without_prefix = parts[1]

        # Try exact match with full requested model name
        for provider in providers_state["providers"]:
            if (
                provider["available"]
                and provider["config"].get("model") == requested_model
            ):
                provider_to_use = provider
                break

        # Try matching without prefix
        if not provider_to_use and model_without_prefix != requested_model:
            for provider in providers_state["providers"]:
                if (
                    provider["available"]
                    and provider["config"].get("model") == model_without_prefix
                ):
                    provider_to_use = provider
                    break

        # Try matching by provider name (with and without prefix)
        if not provider_to_use:
            for provider in providers_state["providers"]:
                if provider["available"] and (
                    provider["name"] == requested_model
                    or provider["name"] == model_without_prefix
                ):
                    provider_to_use = provider
                    break

    # Fall back to default provider
    if not provider_to_use:
        default_name = providers_state.get("default_provider")
        if default_name:
            for provider in providers_state["providers"]:
                if provider["available"] and provider["name"] == default_name:
                    provider_to_use = provider
                    break

    # Last resort: use first available
    if not provider_to_use:
        for provider in providers_state["providers"]:
            if provider["available"]:
                provider_to_use = provider
                break

    if not provider_to_use:
        raise ValueError("No available provider found")

    config = provider_to_use["config"]
    model = config.get("model")

    return model, config


async def call_llm_by_model(
    messages: list[Dict[str, str]],
    providers_state: Dict[str, Any],
    model: Optional[str] = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
    top_p: Optional[float] = None,
    stop: Optional[list[str]] = None,
    timeout: Optional[float] = None,
    **kwargs,
) -> Dict[str, Any]:
    """Call LLM via LiteLLM with provider configuration.

    Args:
        messages: List of message dicts with 'role' and 'content'
        providers_state: Provider discovery state
        model: Requested model name (optional, uses default if not specified)
        temperature: Sampling temperature
        max_tokens: Maximum tokens to generate
        top_p: Nucleus sampling parameter
        stop: Stop sequences
        timeout: Request timeout in seconds (overrides provider config)
        **kwargs: Additional parameters for litellm.completion

    Returns:
        LiteLLM completion response

    Raises:
        ValueError: If no providers available
        litellm.Timeout: If request times out
        Exception: If LLM call fails
    """
    # Get provider configuration
    model_to_use, provider_config = get_provider_config(providers_state, model)

    # Build kwargs for litellm
    litellm_kwargs = {
        "model": model_to_use,
        "messages": messages,
    }

    # Apply provider config defaults first
    if provider_config.get("api_base"):
        litellm_kwargs["api_base"] = provider_config["api_base"]
    if provider_config.get("api_key"):
        litellm_kwargs["api_key"] = provider_config["api_key"]
    for _key in ("temperature", "max_tokens", "top_p", "stop", "timeout"):
        if provider_config.get(_key) is not None:
            litellm_kwargs[_key] = provider_config[_key]

    # Explicit call parameters override provider config
    if timeout is not None:
        litellm_kwargs["timeout"] = timeout
    if temperature is not None:
        litellm_kwargs["temperature"] = temperature
    if max_tokens is not None:
        litellm_kwargs["max_tokens"] = max_tokens
    if top_p is not None:
        litellm_kwargs["top_p"] = top_p
    if stop is not None:
        litellm_kwargs["stop"] = stop

    # Disable SDK-level retries by default — the OpenAI SDK retries on 503
    # and similar errors transparently, which circumvents our timeout logic
    # and can block for many minutes.  Retry decisions belong to our framework.
    # Callers may pass max_retries=N explicitly to override.
    litellm_kwargs.setdefault("max_retries", 0)

    # Add any extra kwargs
    litellm_kwargs.update(kwargs)

    # Fall back to a default timeout so the call never waits indefinitely
    # when neither the provider YAML nor the caller specifies one.
    if litellm_kwargs.get("timeout") is None:
        litellm_kwargs["timeout"] = _DEFAULT_TIMEOUT

    # Debug: Log what we're sending to the LLM
    logger.debug("=" * 80)
    logger.debug("LLM Call Parameters")
    logger.debug("=" * 80)
    logger.debug(f"Model: {litellm_kwargs.get('model')}")
    logger.debug(f"API Base: {litellm_kwargs.get('api_base')}")
    logger.debug(f"Temperature: {litellm_kwargs.get('temperature')}")
    logger.debug(f"Max Tokens: {litellm_kwargs.get('max_tokens')}")
    logger.debug(f"Timeout: {litellm_kwargs.get('timeout')}")
    logger.debug(f"Response Format: {litellm_kwargs.get('response_format')}")
    logger.debug(f"Messages ({len(messages)} total):")
    for i, msg in enumerate(messages):
        role = msg.get("role", "unknown")
        content = msg.get("content", "")
        # Handle both string and structured content
        if isinstance(content, str):
            content_preview = (
                content[:100] + "..." if len(content) > 100 else content
            )
        else:
            # For structured content (like image URLs), just show the structure
            content_preview = f"<structured content: {type(content).__name__}>"
        logger.debug(f"  [{i}] role='{role}' content='{content_preview}'")
    logger.debug("=" * 80)

    # Call LiteLLM — enforce the timeout client-side since LiteLLM does not
    # reliably honour it for all providers (e.g. Ollama streaming).
    # Use asyncio.wait() instead of asyncio.wait_for() to avoid the Python 3.12
    # behaviour where wait_for blocks until the cancelled task fully finishes
    # before raising TimeoutError (which can be many minutes when httpx is stuck).
    enforced_timeout = litellm_kwargs.get("timeout")
    _t0 = time.monotonic()
    logger.debug(
        "[llm] call_llm_by_model: starting acompletion task "
        "(model=%s, timeout=%s, t=%.3f)",
        litellm_kwargs.get("model"),
        enforced_timeout,
        _t0,
    )
    _task = asyncio.ensure_future(acompletion(**litellm_kwargs))
    try:
        _, pending = await asyncio.wait({_task}, timeout=enforced_timeout)
        _elapsed = time.monotonic() - _t0
        if pending:
            _task.cancel()
            logger.warning(
                "[llm] call_llm_by_model: timed out after %.1fs "
                "(model=%s, enforced_timeout=%s)",
                _elapsed,
                litellm_kwargs.get("model"),
                enforced_timeout,
            )
            raise litellm.APIConnectionError(
                message=f"Timed out after {enforced_timeout}s (enforced client-side)",
                llm_provider=litellm_kwargs.get("model", "").split("/")[0],
                model=litellm_kwargs.get("model", ""),
            )
        logger.debug(
            "[llm] call_llm_by_model: acompletion finished in %.3fs",
            _elapsed,
        )
        response = _task.result()
    except (
        litellm.Timeout,
        litellm.APIConnectionError,
        litellm.InternalServerError,
    ) as e:
        _annotate_failure(e, model_to_use)
        if e.sustained_outage:
            logger.error(
                "[llm] call_llm_by_model: provider '%s' (api_base=%s) has "
                "been failing for %.0fs across %d consecutive calls — this "
                "looks like a sustained outage, not a transient blip: %s",
                model_to_use,
                litellm_kwargs.get("api_base"),
                e.failing_since_seconds,
                e.consecutive_failures,
                root_cause_message(e),
            )
        else:
            logger.warning(
                "[llm] call_llm_by_model: provider '%s' (api_base=%s) call "
                "failed (consecutive failures: %d): %s",
                model_to_use,
                litellm_kwargs.get("api_base"),
                e.consecutive_failures,
                root_cause_message(e),
            )
        raise
    except Exception as e:
        _annotate_failure(e, model_to_use)
        kwargs_for_log = litellm_kwargs.copy()
        if "api_key" in kwargs_for_log:
            kwargs_for_log["api_key"] = "***masked***"
        if "messages" in kwargs_for_log:
            kwargs_for_log["messages"] = _truncate_messages(
                kwargs_for_log["messages"]
            )
        logger.error(f"LiteLLM completion failed with kwargs: {kwargs_for_log}")
        logger.error(f"Error: {root_cause_message(e)}")
        raise
    else:
        _provider_health.note_success(model_to_use)

    return response


async def connect_llm_streaming(
    messages: list[Dict[str, str]],
    providers_state: Dict[str, Any],
    model: Optional[str] = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
    top_p: Optional[float] = None,
    stop: Optional[list[str]] = None,
    timeout: Optional[float] = None,
    **kwargs,
) -> tuple:
    """Connect to LLM and return an open streaming response.

    This is the first phase of two-phase streaming. Call this before creating
    a StreamingResponse so that connection/timeout errors can be raised as
    proper HTTP exceptions before headers are committed.

    Returns:
        Tuple of (response, enforced_timeout, model_to_use)

    Raises:
        litellm.APIConnectionError: On timeout or connection failure
        ValueError: If no providers available
    """
    model_to_use, provider_config = get_provider_config(providers_state, model)

    litellm_kwargs = {
        "model": model_to_use,
        "messages": messages,
        "stream": True,
    }

    if provider_config.get("api_base"):
        litellm_kwargs["api_base"] = provider_config["api_base"]
    if provider_config.get("api_key"):
        litellm_kwargs["api_key"] = provider_config["api_key"]

    if timeout is not None:
        litellm_kwargs["timeout"] = timeout
    elif provider_config.get("timeout"):
        litellm_kwargs["timeout"] = provider_config["timeout"]

    if temperature is not None:
        litellm_kwargs["temperature"] = temperature
    if max_tokens is not None:
        litellm_kwargs["max_tokens"] = max_tokens
    if top_p is not None:
        litellm_kwargs["top_p"] = top_p
    if stop is not None:
        litellm_kwargs["stop"] = stop

    litellm_kwargs.setdefault("max_retries", 0)

    litellm_kwargs.update(kwargs)

    if litellm_kwargs.get("timeout") is None:
        litellm_kwargs["timeout"] = _DEFAULT_TIMEOUT

    logger.debug("=" * 80)
    logger.debug("LLM Streaming Call Parameters")
    logger.debug("=" * 80)
    logger.debug(f"Model: {litellm_kwargs.get('model')}")
    logger.debug(f"API Base: {litellm_kwargs.get('api_base')}")
    logger.debug(f"Temperature: {litellm_kwargs.get('temperature')}")
    logger.debug(f"Max Tokens: {litellm_kwargs.get('max_tokens')}")
    logger.debug(f"Timeout: {litellm_kwargs.get('timeout')}")
    logger.debug(f"Messages ({len(messages)} total)")
    logger.debug("=" * 80)

    enforced_timeout = litellm_kwargs.get("timeout")
    _t0 = time.monotonic()
    logger.debug(
        "[llm] connect_llm_streaming: starting acompletion task "
        "(model=%s, timeout=%s, t=%.3f)",
        litellm_kwargs.get("model"),
        enforced_timeout,
        _t0,
    )
    _task = asyncio.ensure_future(acompletion(**litellm_kwargs))
    try:
        _, pending = await asyncio.wait({_task}, timeout=enforced_timeout)
        _elapsed = time.monotonic() - _t0
        if pending:
            _task.cancel()
            logger.warning(
                "[llm] connect_llm_streaming: timed out after %.1fs "
                "(model=%s, enforced_timeout=%s)",
                _elapsed,
                litellm_kwargs.get("model"),
                enforced_timeout,
            )
            raise litellm.APIConnectionError(
                message=f"Streaming timed out after {enforced_timeout}s (enforced client-side)",
                llm_provider=model_to_use.split("/")[0],
                model=model_to_use,
            )
        logger.debug(
            "[llm] connect_llm_streaming: acompletion finished in %.3fs",
            _elapsed,
        )
        response = _task.result()
    except litellm.Timeout as e:
        _annotate_failure(e, model_to_use)
        if e.sustained_outage:
            logger.error(
                "[llm] connect_llm_streaming: provider '%s' (api_base=%s) "
                "has been timing out for %.0fs across %d consecutive calls "
                "— this looks like a sustained outage, not a transient "
                "blip: %s",
                model_to_use,
                litellm_kwargs.get("api_base"),
                e.failing_since_seconds,
                e.consecutive_failures,
                root_cause_message(e),
            )
        else:
            logger.warning(
                "LiteLLM streaming timed out for model '%s' (api_base=%s, "
                "consecutive failures: %d): %s.",
                litellm_kwargs.get("model"),
                litellm_kwargs.get("api_base"),
                e.consecutive_failures,
                root_cause_message(e),
            )
        raise
    except litellm.APIConnectionError as e:
        _annotate_failure(e, model_to_use)
        if e.sustained_outage:
            logger.error(
                "[llm] connect_llm_streaming: provider '%s' (api_base=%s) "
                "has been unreachable for %.0fs across %d consecutive "
                "calls — this looks like a sustained outage, not a "
                "transient blip: %s",
                model_to_use,
                litellm_kwargs.get("api_base"),
                e.failing_since_seconds,
                e.consecutive_failures,
                root_cause_message(e),
            )
        else:
            logger.warning(
                "LiteLLM streaming could not connect to model '%s' "
                "(api_base=%s, consecutive failures: %d): %s.",
                litellm_kwargs.get("model"),
                litellm_kwargs.get("api_base"),
                e.consecutive_failures,
                root_cause_message(e),
            )
        raise
    except Exception as e:
        _annotate_failure(e, model_to_use)
        kwargs_for_log = litellm_kwargs.copy()
        if "api_key" in kwargs_for_log:
            kwargs_for_log["api_key"] = "***masked***"
        if "messages" in kwargs_for_log:
            kwargs_for_log["messages"] = _truncate_messages(
                kwargs_for_log["messages"]
            )
        logger.error("LiteLLM streaming failed with kwargs: %s", kwargs_for_log)
        logger.error("Error: %s", root_cause_message(e))
        raise
    else:
        _provider_health.note_success(model_to_use)

    return response, enforced_timeout, model_to_use


async def iterate_llm_stream(
    response: Any,
    enforced_timeout: Optional[float],
    model: str,
) -> AsyncGenerator[Any, None]:
    """Iterate over an open streaming LLM response with client-side timeout.

    This is the second phase of two-phase streaming. Call after connect_llm_streaming.

    Yields:
        LiteLLM streaming chunks

    Raises:
        litellm.APIConnectionError: On timeout or mid-stream connection failure
    """
    deadline = time.monotonic() + enforced_timeout if enforced_timeout else None

    while True:
        remaining = (deadline - time.monotonic()) if deadline else None
        if remaining is not None and remaining <= 0:
            raise litellm.APIConnectionError(
                message=f"Streaming timed out after {enforced_timeout}s (enforced client-side)",
                llm_provider=model.split("/")[0],
                model=model,
            )
        try:
            chunk = await asyncio.wait_for(
                response.__anext__(), timeout=remaining
            )
        except StopAsyncIteration:
            break
        except asyncio.TimeoutError:
            raise litellm.APIConnectionError(
                message=f"Streaming timed out after {enforced_timeout}s (enforced client-side)",
                llm_provider=model.split("/")[0],
                model=model,
            ) from None
        except (litellm.Timeout, litellm.APIConnectionError):
            raise
        except Exception as e:
            logger.warning(
                "LiteLLM streaming failed during chunk iteration for model '%s': %s",
                model,
                root_cause_message(e),
            )
            raise litellm.APIConnectionError(
                message=str(e),
                llm_provider=model.split("/")[0],
                model=model,
            ) from e
        yield chunk


async def call_llm_by_model_streaming(
    messages: list[Dict[str, str]],
    providers_state: Dict[str, Any],
    model: Optional[str] = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
    top_p: Optional[float] = None,
    stop: Optional[list[str]] = None,
    timeout: Optional[float] = None,
    **kwargs,
) -> AsyncGenerator[Any, None]:
    """Call LLM via LiteLLM with streaming enabled.

    Combines connect_llm_streaming and iterate_llm_stream. Use those directly
    when you need to raise HTTP errors before headers are committed.

    Yields:
        LiteLLM streaming chunks
    """
    response, enforced_timeout, model_to_use = await connect_llm_streaming(
        messages=messages,
        providers_state=providers_state,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        top_p=top_p,
        stop=stop,
        timeout=timeout,
        **kwargs,
    )
    async for chunk in iterate_llm_stream(
        response, enforced_timeout, model_to_use
    ):
        yield chunk
