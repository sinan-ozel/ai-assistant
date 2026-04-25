"""Provider discovery and validation module."""

import asyncio
import logging
import os
import re
import warnings
from pathlib import Path
from typing import Any, Dict, List

import yaml
from common import CUSTOMIZATION_FOLDER, DEFAULTS_FOLDER
from litellm import completion, get_model_info

logger = logging.getLogger(__name__)

# Allowed configuration keys for provider validation
ALLOWED_KEYS = ["model", "api_base", "api_key", "max_tokens", "timeout"]

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
        if isinstance(value, str):
            result[key] = re.sub(
                r"\$\{([^}]+)\}",
                lambda m: os.getenv(m.group(1), m.group(0)),
                value,
            )
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

    # Add timeout to prevent hanging indefinitely on slow providers
    # Allow up to 60 seconds for model loading and response
    # (larger models can be slow)
    kwargs["timeout"] = 60

    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            _ = completion(**kwargs)
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
    """Discover and validate default provider following priority rules.

    Priority:
    1. Custom providers/default.yaml if exists (crash if fails)
    2. DEFAULT_PROVIDER env var matching a custom provider (crash if fails)
    3. Single custom provider (if only one exists, use it as default)
    4. DEFAULT_PROVIDER env var pointing to built-in provider (warn if fails)
    5. Default providers/default.yaml (warn if API key missing, crash for other errors)

    If no providers are available and the built-in default can't be used
    (API key/rate limit), the system will run without a language model
    (tools-only mode).

    Returns:
        Dictionary containing:
        - providers: List of all provider data
        - available_providers: List of available provider names
        - default_provider: Name of default provider (or None if running without models)
    """
    # Check for custom providers
    custom_default_path = CUSTOM_PROVIDERS_DIR / "default.yaml"
    default_provider_data = None
    default_provider_name = None

    # Rule 1: Check for custom providers/default.yaml
    if custom_default_path.exists():
        logger.info(
            "Found custom providers/default.yaml - using as default provider"
        )
        provider_data = _load_and_validate_provider(
            custom_default_path, "default", is_custom=True
        )
        if not provider_data["available"]:
            config = provider_data.get("config", {})
            error_msg = (
                f"Custom default provider failed validation: "
                f"{provider_data['error']} "
                f"(model={config.get('model')}, api_base={config.get('api_base')})"
            )
            logger.error(error_msg)
            raise RuntimeError(error_msg)

        default_provider_data = provider_data
        default_provider_name = "default"

    # Rule 2: Check if DEFAULT_PROVIDER env var matches a custom provider
    if default_provider_data is None:
        env_default_provider = os.getenv("DEFAULT_PROVIDER")
        if env_default_provider and env_default_provider != "default":
            # Check if this matches a custom provider first
            if CUSTOM_PROVIDERS_DIR.exists():
                custom_provider_file = (
                    CUSTOM_PROVIDERS_DIR / f"{env_default_provider}.yaml"
                )
                if custom_provider_file.exists():
                    logger.info(
                        f"Using DEFAULT_PROVIDER env matching custom provider: "
                        f"{env_default_provider}"
                    )
                    provider_data = _load_and_validate_provider(
                        custom_provider_file,
                        env_default_provider,
                        is_custom=True,
                    )
                    if not provider_data["available"]:
                        error_msg = (
                            f"Custom provider '{env_default_provider}' "
                            f"(from DEFAULT_PROVIDER) failed validation: "
                            f"{provider_data['error']}"
                        )
                        logger.error(error_msg)
                        raise RuntimeError(error_msg)

                    default_provider_data = provider_data
                    default_provider_name = env_default_provider

    # Rule 2.5: If there's exactly one custom provider, use it as default
    if default_provider_data is None:
        if CUSTOM_PROVIDERS_DIR.exists():
            custom_provider_files = list(CUSTOM_PROVIDERS_DIR.glob("*.yaml"))
            if len(custom_provider_files) == 1:
                single_provider_file = custom_provider_files[0]
                single_provider_name = single_provider_file.stem
                logger.info(
                    f"Found single custom provider '{single_provider_name}' - "
                    f"using as default provider"
                )
                provider_data = _load_and_validate_provider(
                    single_provider_file,
                    single_provider_name,
                    is_custom=True,
                )
                if provider_data["available"]:
                    default_provider_data = provider_data
                    default_provider_name = single_provider_name
                else:
                    logger.warning(
                        f"Single custom provider '{single_provider_name}' "
                        f"failed validation: {provider_data['error']}. "
                        f"Continuing to check other options."
                    )

    # Rule 3: Check DEFAULT_PROVIDER env var for built-in provider
    if default_provider_data is None:
        env_default_provider = os.getenv("DEFAULT_PROVIDER")
        if env_default_provider and env_default_provider != "default":
            provider_file = (
                DEFAULT_PROVIDERS_DIR / f"{env_default_provider}.yaml"
            )
            if provider_file.exists():
                logger.info(
                    f"Using DEFAULT_PROVIDER env: {env_default_provider}"
                )
                provider_data = _load_and_validate_provider(
                    provider_file, env_default_provider, is_custom=False
                )
                if provider_data["available"]:
                    default_provider_data = provider_data
                    default_provider_name = env_default_provider
                else:
                    # Log error but don't crash - continue to next rule
                    available_defaults = [
                        f.stem for f in DEFAULT_PROVIDERS_DIR.glob("*.yaml")
                    ]
                    logger.error(
                        f"DEFAULT_PROVIDER '{env_default_provider}' failed validation: "
                        f"{provider_data['error']}. "
                        f"You can write your own provider by adding a "
                        f"providers/default.yaml file to your cortex mount. "
                        f"The properties in the file are keyword arguments to a "
                        f"LiteLLM call."
                    )
            else:
                # File doesn't exist - log error with available files
                available_defaults = [
                    f.stem for f in DEFAULT_PROVIDERS_DIR.glob("*.yaml")
                ]
                # Check if there are custom providers to list
                custom_providers = []
                if CUSTOM_PROVIDERS_DIR.exists():
                    custom_providers = [
                        f.stem for f in CUSTOM_PROVIDERS_DIR.glob("*.yaml")
                    ]

                error_msg = (
                    f"DEFAULT_PROVIDER '{env_default_provider}' not found. "
                )
                if custom_providers:
                    error_msg += (
                        f"Available custom providers: "
                        f"{', '.join(custom_providers)}. "
                    )
                error_msg += (
                    f"Available built-in providers: {', '.join(available_defaults)}. "
                    f"You can write your own provider by adding a "
                    f"providers/default.yaml file to your cortex mount. "
                    f"The properties in the file are keyword arguments to a "
                    f"LiteLLM call."
                )
                logger.error(error_msg)
                raise RuntimeError(error_msg)

    # Rule 4: Fall back to default providers/default.yaml
    if default_provider_data is None:
        default_file = DEFAULT_PROVIDERS_DIR / "default.yaml"
        logger.info("Using fallback default provider from default.yaml")
        provider_data = _load_and_validate_provider(
            default_file, "default", is_custom=False
        )
        if not provider_data["available"]:
            # Check if this is an API key or rate limit issue (treatable as non-fatal)
            error = provider_data.get("error", "")
            is_api_key_issue = (
                "API key" in error
                or "api_key" in error
                or "RateLimitError" in error
                or "rate limit" in error.lower()
                or "capacity exceeded" in error.lower()
            )

            if is_api_key_issue:
                # Check if there are custom providers that could be used
                custom_providers = []
                if CUSTOM_PROVIDERS_DIR.exists():
                    custom_providers = [
                        f.stem for f in CUSTOM_PROVIDERS_DIR.glob("*.yaml")
                    ]

                warning_msg = (
                    f"Built-in default provider unavailable: {error}. "
                    "Running without a language model. "
                    "Abilities will be restricted to tools only. "
                )

                if custom_providers:
                    warning_msg += (
                        f"Found custom provider(s): {', '.join(custom_providers)}. "
                        f"To use one as default, set "
                        f"DEFAULT_PROVIDER={custom_providers[0]} "
                        f"environment variable, or rename one to 'default.yaml'. "
                    )
                else:
                    warning_msg += (
                        "To enable LLM capabilities, either set MISTRAL_API_KEY "
                        "or create a providers/default.yaml file in your cortex mount."
                    )

                logger.warning(warning_msg)
                # Don't set default_provider_data - will run without model
            else:
                # Other error - this is a real problem, crash
                available_defaults = [
                    f.stem for f in DEFAULT_PROVIDERS_DIR.glob("*.yaml")
                ]
                error_msg = (
                    f"Default provider failed validation: {provider_data['error']}. "
                    "You need to create your own default.yaml in the providers "
                    f"folder of your cortex mount."
                )
                logger.error(error_msg)
                raise RuntimeError(error_msg)
        else:
            default_provider_data = provider_data
            default_provider_name = "default"

    # Now load all other providers for availability info
    all_providers = []

    # Load from default directory
    if DEFAULT_PROVIDERS_DIR.exists():
        for provider_file in sorted(DEFAULT_PROVIDERS_DIR.glob("*.yaml")):
            provider_name = provider_file.stem
            # Skip if this is already our default provider
            if (
                default_provider_data
                and not default_provider_data["is_default"]
                and provider_name == default_provider_name
            ):
                continue
            provider_data = _load_and_validate_provider(
                provider_file,
                provider_name,
                is_custom=False,
                validate_on_startup=False,
            )
            logger.debug(
                "discover_providers found new provider: %s", provider_data
            )
            all_providers.append(provider_data)

    # Load from custom directory
    if CUSTOM_PROVIDERS_DIR.exists():
        for provider_file in sorted(CUSTOM_PROVIDERS_DIR.glob("*.yaml")):
            provider_name = provider_file.stem
            # Skip if this is already our default provider
            if (
                default_provider_data
                and not default_provider_data["is_default"]
                and provider_name == default_provider_name
            ):
                continue
            provider_data = _load_and_validate_provider(
                provider_file,
                provider_name,
                is_custom=True,
                validate_on_startup=False,
            )
            all_providers.append(provider_data)

    # Add default provider to the list if one was found
    if default_provider_data is not None:
        all_providers.insert(0, default_provider_data)

    # Get available providers
    available_names = [p["name"] for p in all_providers if p["available"]]

    logger.debug(
        "discover_providers complete. "
        "providers: %s "
        "available_providers: %s "
        "default_provider: %s",
        all_providers,
        available_names,
        default_provider_name,
    )

    return {
        "providers": all_providers,
        "available_providers": available_names,
        "default_provider": default_provider_name,
        "status": "ready",
    }


def _load_and_validate_provider(
    provider_file: Path,
    provider_name: str,
    is_custom: bool,
    validate_on_startup: bool = True,
) -> Dict[str, Any]:
    """Load and optionally validate a single provider.

    Args:
        provider_file: Path to provider YAML file
        provider_name: Name of the provider
        is_custom: True if from custom/cortex directory
        validate_on_startup: Whether to validate with a test call

    Returns:
        Provider dictionary with metadata
    """
    provider_data = {
        "name": provider_name,
        "file": str(provider_file),
        "is_default": not is_custom,
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
            return provider_data

        # Validate required fields
        if "model" not in config:
            provider_data["error"] = "Provider missing 'model' field"
            return provider_data

        # Initialize extra dict if not present
        if "extra" not in config:
            config["extra"] = {}

        provider_data["config"] = config

        # Check API key availability
        if not check_api_key_available(config):
            provider_data["error"] = "Required API key not found in environment"
            return provider_data

        # Validate provider with test call if requested
        if validate_on_startup:
            success, error = validate_provider(config)
            if success:
                provider_data["available"] = True
            else:
                provider_data["error"] = error
                logger.warning(
                    f"Provider {provider_name} validation failed: {error}"
                )
        else:
            # For non-startup providers, just mark as available if API key is present
            provider_data["available"] = True

    except Exception as e:
        provider_data["error"] = str(e)

    return provider_data


async def query_context_window(provider_data: Dict[str, Any]) -> int | None:
    """Query a provider for their context window size using LiteLLM's
    get_model_info.

    Args:
        provider_data: Provider dictionary with config

    Returns:
        Context window size as integer, or None if query fails
    """
    config = provider_data.get("config", {})
    model = config.get("model")

    if not model:
        return None

    api_base = config.get("api_base")
    env_backup = None

    if api_base and "ollama" in model.lower():
        env_backup = os.environ.get("OLLAMA_API_BASE")
        os.environ["OLLAMA_API_BASE"] = api_base

    # Run get_model_info in a thread executor to avoid blocking the event loop
    # — for some providers (e.g. ollama) LiteLLM may make a synchronous
    # network call to fetch model metadata.
    loop = asyncio.get_event_loop()
    try:
        model_info = await loop.run_in_executor(None, get_model_info, model)
    except Exception as e:
        logger.debug(f"Failed to get context window via model info: {e}")
        return None
    finally:
        if env_backup is not None:
            os.environ["OLLAMA_API_BASE"] = env_backup
        elif api_base and "OLLAMA_API_BASE" in os.environ:
            del os.environ["OLLAMA_API_BASE"]

    context_window = model_info.get("max_tokens") or model_info.get(
        "max_input_tokens"
    )

    if context_window:
        logger.info(f"Context window from model info: {context_window}")

    return context_window or None


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
    tasks = [query_context_window(provider) for provider in available_providers]
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
