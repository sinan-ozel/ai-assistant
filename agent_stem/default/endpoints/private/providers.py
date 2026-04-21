"""Providers information endpoint."""

from common.state import providers_state


async def handler():
    """Get information about available providers."""
    # Check if discovery is still in progress
    if providers_state.get("loading", False):
        status = "initializing"
    else:
        status = providers_state.get("status", "unknown")

    return {
        "available": providers_state.get("available_providers", []),
        "default": providers_state.get("default_provider"),
        "total": len(providers_state.get("providers", [])),
        "status": status,
    }


spec = {
    "path": "/private/v1/providers",
    "methods": ["GET"],
    "summary": "Get providers information",
    "description": (
        "Retrieve information about available LLM providers, "
        "including which are available and the default provider"
    ),
    "responses": {
        200: {
            "description": "Provider information retrieved successfully",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "available": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": (
                                    "List of available provider names"
                                ),
                            },
                            "default": {
                                "type": "string",
                                "nullable": True,
                                "description": (
                                    "Default provider name, or null if none set"
                                ),
                            },
                            "total": {
                                "type": "integer",
                                "description": (
                                    "Total number of configured providers"
                                ),
                            },
                            "status": {
                                "type": "string",
                                "enum": [
                                    "initializing",
                                    "ready",
                                    "no_providers_available",
                                    "one_provider_available",
                                    "multiple_providers_available",
                                    "unknown",
                                ],
                                "description": (
                                    "Provider discovery status: "
                                    "'initializing' (discovery in progress), "
                                    "'ready' (discovery complete), "
                                    "'no_providers_available' "
                                    "(no working providers found), "
                                    "'one_provider_available' "
                                    "(exactly one provider available), "
                                    "'multiple_providers_available' "
                                    "(multiple providers available), "
                                    "'unknown' (unexpected state)"
                                ),
                            },
                        },
                        "required": ["available", "total", "status"],
                    },
                    "example": {
                        "available": ["pixtral", "gemma3_on_vpn"],
                        "default": "pixtral",
                        "total": 2,
                        "status": "ready",
                    },
                }
            },
        }
    },
}
