"""Provider discovery and validation module."""

import os
import warnings
from pathlib import Path
from typing import Any, Dict, List

import yaml
from litellm import completion

from common import CUSTOMIZATION_FOLDER, DEFAULTS_FOLDER

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
        - default_provider: Name of default provider (if only one available)
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

    # Set default if only one available
    default_provider = None
    if len(available) == 1:
        default_provider = available[0]["name"]

    # Determine status
    if len(available) == 0:
        status = "no_providers_available"
    elif len(available) == 1:
        status = "one_provider_available"
    else:
        status = "multiple_providers_available"

    return {
        "providers": all_providers,
        "available_providers": available_names,
        "default_provider": default_provider,
        "status": status,
    }
