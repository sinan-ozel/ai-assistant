"""Common LLM completion interface using LiteLLM.

This module provides an abstraction layer over LiteLLM that can be used
by all endpoints (chat completions, generate, agent chat, etc.).
"""

import logging
from typing import Any, Dict, Optional

from litellm import completion

logger = logging.getLogger(__name__)


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
        # Strip provider prefix if present (e.g., "ollama/gemma3:4b" -> "gemma3:4b")
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


def call_llm_by_model(
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

    # Add provider-specific config
    if provider_config.get("api_base"):
        litellm_kwargs["api_base"] = provider_config["api_base"]
    if provider_config.get("api_key"):
        litellm_kwargs["api_key"] = provider_config["api_key"]

    # Add timeout - prioritize request parameter, then provider config, then no timeout
    if timeout is not None:
        litellm_kwargs["timeout"] = timeout
    elif provider_config.get("timeout"):
        litellm_kwargs["timeout"] = provider_config["timeout"]

    # Add optional parameters if provided
    if temperature is not None:
        litellm_kwargs["temperature"] = temperature
    if max_tokens is not None:
        litellm_kwargs["max_tokens"] = max_tokens
    if top_p is not None:
        litellm_kwargs["top_p"] = top_p
    if stop is not None:
        litellm_kwargs["stop"] = stop

    # Add any extra kwargs
    litellm_kwargs.update(kwargs)

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

    # Call LiteLLM
    response = completion(**litellm_kwargs)

    return response
