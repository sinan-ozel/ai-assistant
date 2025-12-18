"""Health check endpoint."""


async def handler(providers_state: dict):
    """Health check endpoint with provider loading status."""
    response = {"status": "ok"}

    if providers_state.get("loading", True):
        response["providers_loading"] = True

    return response


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
                            "status": {"type": "string"},
                            "providers_loading": {"type": "boolean"}
                        },
                        "required": ["status"],
                    },
                    "example": {"status": "ok", "providers_loading": False},
                }
            },
        }
    },
}
