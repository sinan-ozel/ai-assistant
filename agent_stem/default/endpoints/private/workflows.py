"""Workflows listing endpoint."""


async def handler(workflows_state: dict):
    """Get list of all available workflows.

    Args:
        workflows_state: Global workflows state

    Returns:
        Dict with list of workflows
    """
    workflows = workflows_state.get("workflows", {})

    workflow_list = []
    for path, workflow_info in workflows.items():
        workflow_data = workflow_info.get("data", {})
        workflow_list.append(
            {
                "name": workflow_info.get("name"),
                "path": path,
                "description": workflow_data.get("description"),
                "provider": workflow_data.get("provider"),
                "has_evaluation": "evaluation" in workflow_data,
            }
        )

    return {"total": len(workflow_list), "workflows": workflow_list}


spec = {
    "path": "/private/v1/workflows",
    "methods": ["GET"],
    "summary": "List all workflows",
    "description": (
        "Retrieve a list of all available workflows with their metadata."
    ),
    "responses": {
        200: {
            "description": "Workflows retrieved successfully",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "total": {
                                "type": "integer",
                                "description": "Total number of workflows",
                            },
                            "workflows": {
                                "type": "array",
                                "description": "List of workflows",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "name": {
                                            "type": "string",
                                            "description": "Workflow name",
                                        },
                                        "path": {
                                            "type": "string",
                                            "description": "Workflow endpoint path",
                                        },
                                        "description": {
                                            "type": "string",
                                            "description": "Workflow description",
                                        },
                                        "provider": {
                                            "type": "string",
                                            "nullable": True,
                                            "description": "Provider name if specified",
                                        },
                                        "has_evaluation": {
                                            "type": "boolean",
                                            "description": (
                                                "Whether workflow has"
                                                " evaluation section"
                                            ),
                                        },
                                    },
                                    "required": [
                                        "name",
                                        "path",
                                        "has_evaluation",
                                    ],
                                },
                            },
                        },
                        "required": ["total", "workflows"],
                    },
                    "example": {
                        "total": 1,
                        "workflows": [
                            {
                                "name": "nutrition_information_extraction",
                                "path": "/v1/extract-nutrition-information",
                                "description": (
                                    "Takes an image of a packaged food"
                                    " product label and extracts the"
                                    " nutrition information as JSON."
                                ),
                                "provider": "vision",
                                "has_evaluation": True,
                            }
                        ],
                    },
                }
            },
        }
    },
}
