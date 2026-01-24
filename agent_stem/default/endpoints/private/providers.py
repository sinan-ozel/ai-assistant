"""Providers information endpoint."""


async def handler(providers_state: dict):
    """Get information about available providers."""
    return {
        "available": providers_state.get("available_providers", []),
        "default": providers_state.get("default_provider"),
        "total": len(providers_state.get("providers", [])),
        "status": providers_state.get("status", "unknown"),
    }


spec = {
    "path": "/private/v1/providers",
    "methods": ["GET"],
    "summary": "Get providers information",
    "description": "Retrieve information about available LLM providers, including which are available and the default provider",
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
                                "description": "List of available provider names"
                            },
                            "default": {
                                "type": "string",
                                "nullable": True,
                                "description": "Default provider name, or null if none set"
                            },
                            "total": {
                                "type": "integer",
                                "description": "Total number of configured providers"
                            },
                            "status": {
                                "type": "string",
                                "description": "Provider discovery status"
                            },
                        },
                        "required": ["available", "default", "total", "status"],
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
