"""Provider context window endpoint."""

from common.state import providers_state
from fastapi import HTTPException
from situational.awareness import get_provider_context_window


async def handler(provider: str):
    """Get the maximum context window for a specific provider."""
    # Get cached context window
    context_window = get_provider_context_window(providers_state, provider)

    if context_window is None:
        # Check if provider exists
        providers = providers_state.get("providers", [])
        provider_exists = any(p["name"] == provider for p in providers)

        if not provider_exists:
            raise HTTPException(
                status_code=404, detail=f"Provider '{provider}' not found"
            )

        # Provider exists but context window not available
        raise HTTPException(
            status_code=404,
            detail=(
                f"Context window information not available "
                f"for provider '{provider}'"
            ),
        )

    return {"provider": provider, "max_context_window": context_window}


spec = {
    "path": "/private/v1/providers/{provider}/max-context-window",
    "methods": ["GET"],
    "summary": "Get provider's maximum context window",
    "description": (
        "Retrieve the maximum context window size in tokens "
        "for a specific provider. "
        "Currently, this endpoint works only with Ollama servers. "
        "Initial plan was to make the agent aware its models' capabilities, "
        "but this looks infeasiable at the moment. "
        "The agent designer needs to be aware and set them up accordingly. "
    ),
    "parameters": [
        {
            "name": "provider",
            "in": "path",
            "required": True,
            "schema": {"type": "string", "example": "pixtral"},
        }
    ],
    "responses": {
        200: {
            "description": "Context window information retrieved successfully",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "provider": {
                                "type": "string",
                                "description": "Name of the provider",
                            },
                            "max_context_window": {
                                "type": "integer",
                                "description": (
                                    "Maximum context window size in tokens"
                                ),
                            },
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
            "description": (
                "Provider not found, not available, or context window "
                "information not available"
            ),
        },
    },
}
