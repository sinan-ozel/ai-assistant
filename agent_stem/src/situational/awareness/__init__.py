"""Situational awareness utilities for the agent system.

This module provides functions to access cached information about the system state,
providers, and their capabilities.
"""

from typing import Optional


def get_provider_context_window(
    providers_state: dict,
    provider: str
) -> Optional[int]:
    """
    Get the cached context window size for a provider.

    This retrieves the context window that was queried during startup
    and cached in the providers_state global.

    Args:
        providers_state: Global providers state dict
        provider: Provider name

    Returns:
        Context window size in tokens, or None if not available
    """
    providers = providers_state.get("providers", [])

    for p in providers:
        if p["name"] == provider:
            # Check if provider is available
            if not p.get("available", False):
                return None

            # Get cached context window from llm_responses
            context_window = p.get("llm_responses", {}).get("context_window")
            return context_window

    return None
