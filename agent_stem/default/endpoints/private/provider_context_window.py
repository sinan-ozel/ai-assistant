"""Provider context window endpoint."""

from fastapi import HTTPException
from situational.awareness import get_provider_context_window


async def handler(provider: str, providers_state: dict):
    """Get the maximum context window for a specific provider."""
    # Get cached context window
    context_window = get_provider_context_window(providers_state, provider)

    if context_window is None:
        # Check if provider exists
        providers = providers_state.get("providers", [])
        provider_exists = any(p["name"] == provider for p in providers)

        if not provider_exists:
            raise HTTPException(
                status_code=404,
                detail=f"Provider '{provider}' not found"
            )

        # Provider exists but context window not available
        raise HTTPException(
            status_code=404,
            detail=f"Context window information not available for provider '{provider}'"
        )

    return {
        "provider": provider,
        "max_context_window": context_window
    }


spec = {
    "path": "/private/v1/providers/{provider}/max-context-window",
    "methods": ["GET"],
    "summary": "Get provider's maximum context window",
    "description": "Retrieve the maximum context window size in tokens for a specific provider",
    "responses": {
        200: {
            "description": "Context window information retrieved successfully",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "provider": {"type": "string"},
                            "max_context_window": {"type": "integer"},
                        },
                        "required": ["provider", "max_context_window"],
                    },
                    "example": {
                        "provider": "pixtral",
                        "max_context_window": 128000,
                    },
                }
            },
        },
        404: {
            "description": "Provider not found, not available, or context window information not available",
        },
    },
}
