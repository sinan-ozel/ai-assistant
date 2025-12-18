"""Provider context window endpoint."""

from fastapi import HTTPException


async def handler(provider: str, providers_state: dict):
    """Get the maximum context window for a specific provider."""
    # Find the provider in the providers list
    providers = providers_state.get("providers", [])

    for p in providers:
        if p["name"] == provider:
            # Check if provider is available
            if not p.get("available", False):
                raise HTTPException(
                    status_code=404,
                    detail=f"Provider '{provider}' is not available"
                )

            # Get context window from llm_responses
            context_window = p.get("llm_responses", {}).get("context_window")

            if context_window is None:
                raise HTTPException(
                    status_code=404,
                    detail=f"Context window information not available for provider '{provider}'"
                )

            return {
                "provider": provider,
                "max_context_window": context_window
            }

    # Provider not found
    raise HTTPException(
        status_code=404,
        detail=f"Provider '{provider}' not found"
    )


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
