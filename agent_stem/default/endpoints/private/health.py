"""Health check endpoint."""


async def handler(providers_state: dict):
    """Health check endpoint with provider loading status."""
    return {
        "status": "ok",
        "providers_loading": providers_state.get("loading", True),
        "available_providers": len(
            providers_state.get("available_providers", [])
        ),
    }


spec = {
    "path": "/health",
    "methods": ["GET"],
    "summary": "Health check",
    "description": "Check if the API is running and healthy",
    "responses": {
        200: {
            "description": "API is healthy",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "status": {
                                "type": "string",
                                "description": "Health status of the API",
                            },
                            "providers_loading": {
                                "type": "boolean",
                                "description": "Whether providers are still loading in the background",
                            },
                            "available_providers": {
                                "type": "integer",
                                "description": "Number of available LLM providers",
                            },
                        },
                        "required": ["status"],
                    },
                    "example": {
                        "status": "ok",
                        "providers_loading": False,
                        "available_providers": 1,
                    },
                }
            },
        }
    },
}
