"""Health check endpoint."""

from common.state import providers_state
from fastapi import HTTPException


async def handler():
    """Health check endpoint.

    Returns 503 while providers are loading.
    """
    if providers_state.get("loading", True):
        raise HTTPException(
            status_code=503,
            detail="Providers are still loading",
        )
    return {"status": "ok"}


spec = {
    "path": "/health",
    "methods": ["GET"],
    "summary": "Health check",
    "description": "Check if the API is running and ready. Returns 503 while providers are still loading.",
    "responses": {
        200: {
            "description": "API is healthy and providers are ready",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "status": {
                                "type": "string",
                                "description": "Health status of the API",
                            },
                            # "providers_loading": {
                            #     "type": "boolean",
                            #     "description": (
                            #         "Whether providers are still "
                            #         "loading in the background"
                            #     ),
                            # },
                            # "available_providers": {
                            #     "type": "integer",
                            #     "description": (
                            #         "Number of available LLM providers"
                            #     ),
                            # },
                        },
                        "required": ["status"],
                    },
                    "example": {
                        "status": "ok",
                        # "providers_loading": False,
                        # "available_providers": 1,
                    },
                }
            },
        }
    },
}
