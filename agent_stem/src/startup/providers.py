"""Provider discovery and validation module."""

import asyncio
import logging
import os
import re
import warnings
from pathlib import Path
from typing import Any, Dict, List

import yaml
from litellm import acompletion, completion

from common import CUSTOMIZATION_FOLDER, DEFAULTS_FOLDER

logger = logging.getLogger(__name__)

# Allowed configuration keys for provider validation
ALLOWED_KEYS = ["model", "api_base", "api_key", "max_tokens"]

# Base directories for providers
DEFAULT_PROVIDERS_DIR = DEFAULTS_FOLDER / "providers"
CUSTOM_PROVIDERS_DIR = CUSTOMIZATION_FOLDER / "providers"


def substitute_env_vars(config: Dict[str, Any]) -> Dict[str, Any]:
    """Substitute environment variables in configuration values.

    Args:
        config: Configuration dictionary with potential ${VAR} references

    Returns:
        Configuration with environment variables substituted
    """
    result = {}
    for key, value in config.items():
        if (
            isinstance(value, str)
            and value.startswith("${")
            and value.endswith("}")
        ):
            env_var = value[2:-1]
            result[key] = os.getenv(env_var, value)
        elif isinstance(value, dict):
            result[key] = substitute_env_vars(value)
        else:
            result[key] = value
    return result


def check_api_key_available(config: Dict[str, Any]) -> bool:
    """Check if required API key is available in environment.

    Args:
        config: Provider configuration

    Returns:
        True if no API key required or if API key is set
    """
    api_key = config.get("api_key", "")

    # If api_key is not set or is empty, no key required
    if not api_key:
        return True

    # If it's still a template variable, the key wasn't found
    if api_key.startswith("${") and api_key.endswith("}"):
        return False

    return True


def validate_provider(config: Dict[str, Any]) -> tuple[bool, str]:
    """Validate a provider by making a test call.

    Args:
        config: Provider configuration

    Returns:
        Tuple of (success, error_message)
    """
    # Build kwargs for litellm
    kwargs = {}
    for key in ALLOWED_KEYS:
        if config.get(key):
            kwargs[key] = config[key]

    # Simple test message
    kwargs["messages"] = [{"role": "user", "content": "Hi"}]
    kwargs["max_tokens"] = kwargs.get("max_tokens", 10)

    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            response = completion(**kwargs)
        return True, ""
    except Exception as e:
        return False, str(e)


def load_providers_from_directory(
    directory: Path, is_default: bool = True
) -> List[Dict[str, Any]]:
    """Load and validate providers from a directory.

    Args:
        directory: Path to provider directory
        is_default: True if loading from default, False if custom

    Returns:
        List of provider dictionaries with metadata
    """
    providers = []

    if not directory.exists():
        if is_default:
            raise RuntimeError(
                f"Default providers directory not found: {directory}"
            )
        return providers

    for provider_file in sorted(directory.glob("*.yaml")):
        provider_data = {
            "name": provider_file.stem,
            "file": str(provider_file),
            "is_default": is_default,
            "available": False,
            "is_enabled": True,
            "error": None,
            "config": {},
        }

        try:
            # Load YAML
            with open(provider_file, "r") as f:
                config = yaml.safe_load(f)

            # Substitute environment variables
            config = substitute_env_vars(config)

            # Check if disabled
            if not config.get("_enabled", True):
                provider_data["is_enabled"] = False
                providers.append(provider_data)
                continue

            # Validate required fields
            if "model" not in config:
                error_msg = (
                    f"Provider {provider_file.name} missing 'model' field"
                )
                if is_default:
                    raise RuntimeError(error_msg)
                else:
                    provider_data["error"] = error_msg
                    providers.append(provider_data)
                    continue

            # Initialize extra dict if not present
            if "extra" not in config:
                config["extra"] = {}

            provider_data["config"] = config

            # Check API key availability
            if not check_api_key_available(config):
                provider_data["error"] = (
                    "Required API key not found in environment"
                )
                providers.append(provider_data)
                continue

            # Validate provider with test call
            success, error = validate_provider(config)
            if success:
                provider_data["available"] = True
            else:
                provider_data["error"] = error
                logger.warning(
                    f"Provider {provider_file.stem} validation failed: {error}"
                )

            providers.append(provider_data)

        except Exception as e:
            if is_default:
                raise RuntimeError(
                    f"Error loading default provider {provider_file.name}: {e}"
                )
            else:
                provider_data["error"] = str(e)
                providers.append(provider_data)

    return providers


def discover_providers() -> Dict[str, Any]:
    """Discover and validate all available providers.

    Returns:
        Dictionary containing:
        - providers: List of all provider data
        - available_providers: List of available provider names
        - default_provider: Name of default provider (determined by logic)
    """
    # Load from default directory
    default_providers = load_providers_from_directory(
        DEFAULT_PROVIDERS_DIR, is_default=True
    )

    # Load from custom directory
    custom_providers = load_providers_from_directory(
        CUSTOM_PROVIDERS_DIR, is_default=False
    )

    # Combine all providers
    all_providers = default_providers + custom_providers

    # Get available providers
    available = [p for p in all_providers if p["available"]]
    available_names = [p["name"] for p in available]

    # Get custom (mounted) providers
    custom_available = [p for p in custom_providers if p["available"]]
    custom_available_names = [p["name"] for p in custom_available]

    # Get DEFAULT_PROVIDER from environment
    env_default_provider = os.getenv("DEFAULT_PROVIDER")

    # Determine default provider with various logic
    default_provider = None

    if len(available) == 0:
        status = "no_providers_available"
    elif len(available) == 1:
        # One provider available
        default_provider = available[0]["name"]

        # If DEFAULT_PROVIDER is set but doesn't match, log warning
        if env_default_provider and env_default_provider != default_provider:
            logger.warning(
                f"DEFAULT_PROVIDER env '{env_default_provider}' does not match "
                f"the only available provider '{default_provider}'. "
                f"Using '{default_provider}'."
            )

        status = "one_provider_available"
    else:
        # Multiple providers available
        if env_default_provider:
            # DEFAULT_PROVIDER is set
            if env_default_provider in available_names:
                # Valid: DEFAULT_PROVIDER matches one of the providers
                default_provider = env_default_provider
                status = "multiple_providers_available"
            else:
                # Error: DEFAULT_PROVIDER doesn't match any available provider
                raise RuntimeError(
                    f"DEFAULT_PROVIDER env '{env_default_provider}' does not match "
                    f"any available provider. Available providers: {available_names}"
                )
        else:
            # DEFAULT_PROVIDER not set
            if len(custom_available) == 1:
                # Only one mounted provider - use it as default
                default_provider = custom_available[0]["name"]
                logger.info(
                    f"Multiple providers available but only one mounted provider "
                    f"'{default_provider}'. Using it as default."
                )
                status = "multiple_providers_available"
            else:
                # Multiple providers, no clear default
                logger.warning(
                    f"Multiple providers available ({available_names}) "
                    f"but no DEFAULT_PROVIDER env set. No default provider selected."
                )
                status = "multiple_providers_available"

    return {
        "providers": all_providers,
        "available_providers": available_names,
        "default_provider": default_provider,
        "status": status,
    }


def parse_context_window(response_text: str) -> int | None:
    """Parse context window from LLM response.

    Args:
        response_text: Raw response text from LLM

    Returns:
        Context window size as integer, or None if parsing fails
    """
    if not response_text:
        return None

    # Strip whitespace
    text = response_text.strip()

    # Try direct int conversion
    try:
        return int(text)
    except ValueError:
        pass

    # Look for a single number pattern in the text
    # Pattern matches numbers with optional whitespace around them
    numbers = re.findall(r'\b(\d+)\b', text)

    if len(numbers) == 1:
        try:
            return int(numbers[0])
        except ValueError:
            pass

    return None


async def query_context_window(provider_data: Dict[str, Any]) -> int | None:
    """Query a provider for their context window size.

    Args:
        provider_data: Provider dictionary with config

    Returns:
        Context window size as integer, or None if query fails
    """
    config = provider_data.get("config", {})

    # Build kwargs for litellm
    kwargs = {}
    for key in ALLOWED_KEYS:
        if config.get(key):
            kwargs[key] = config[key]

    # Prompt asking for context window
    kwargs["messages"] = [
        {
            "role": "user",
            "content": (
                "What is your maximum context window size in tokens? "
                "Please respond with only the number, nothing else."
            ),
        }
    ]
    kwargs["max_tokens"] = kwargs.get("max_tokens", 50)

    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            response = await acompletion(**kwargs)

        # Extract text from response
        response_text = response.choices[0].message.content
        logger.info(f"Context window query response: {response_text}")

        return parse_context_window(response_text)

    except Exception:
        return None


async def discover_context_windows(providers_state: Dict[str, Any]) -> None:
    """Query all available providers for their context windows.

    Updates the providers_state dictionary in-place, adding:
    provider_data -> llm_responses -> context_window

    Args:
        providers_state: Dictionary returned by discover_providers()
    """
    # Get all available providers
    available_providers = [
        p for p in providers_state["providers"] if p["available"]
    ]

    # Query all providers concurrently
    tasks = [
        query_context_window(provider) for provider in available_providers
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Update provider data with results
    for provider, result in zip(available_providers, results):
        # Initialize llm_responses if not present
        if "llm_responses" not in provider:
            provider["llm_responses"] = {}

        # Store context window (can be None if query failed)
        if isinstance(result, Exception):
            provider["llm_responses"]["context_window"] = None
        else:
            provider["llm_responses"]["context_window"] = result
