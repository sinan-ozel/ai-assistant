"""Health check endpoint."""


async def handler():
    """Health check endpoint."""
    return {"status": "ok"}


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
                        "properties": {"status": {"type": "string"}},
                        "required": ["status"],
                    },
                    "example": {"status": "ok"},
                }
            },
        }
    },
}
