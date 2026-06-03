"""Evaluation results endpoint."""

from synced_memory import Memory


async def handler(path: str):
    """Get evaluation results for a specific workflow.

    Args:
        path: Workflow path (e.g., /v1/extract-nutrition-information)

    Returns:
        Dict with evaluation results or status
    """
    # Get evaluation state for this workflow
    with Memory() as memory:
        try:
            state = memory.workflow_evaluation_state.get(path)
        except AttributeError:
            state = None

    if not state:
        return {
            "status": "idle",
            "workflow_path": path,
            "current_evaluation": None,
            "results": None,
        }

    response = {
        "status": state.get("status", "idle"),
        "workflow_path": path,
        "current_evaluation": state.get("current_evaluation"),
    }

    if state.get("started_at"):
        response["started_at"] = state["started_at"]

    if state.get("cancelled") is not None:
        response["cancelled"] = state["cancelled"]

    if state.get("results"):
        response["results"] = state["results"]

    if state.get("error"):
        response["error"] = state["error"]

    return response


spec = {
    "path": "/private/evaluate{path:path}/results",
    "methods": ["GET"],
    "summary": "Get evaluation results for workflow",
    "description": (
        "Retrieve the results of the most recent evaluation run for a "
        "specific workflow, or the status of a currently running evaluation."
    ),
    "responses": {
        200: {
            "description": "Evaluation results retrieved successfully",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "status": {
                                "type": "string",
                                "enum": [
                                    "idle",
                                    "running",
                                    "completed",
                                    "failed",
                                    "error",
                                    "cancelled",
                                ],
                                "description": "Current evaluation status",
                            },
                            "workflow_path": {
                                "type": "string",
                                "description": "Path of the workflow",
                            },
                            "current_evaluation": {
                                "type": "string",
                                "nullable": True,
                                "description": (
                                    "Path of currently running evaluation"
                                    " (null if none)"
                                ),
                            },
                            "results": {
                                "type": "object",
                                "nullable": True,
                                "description": (
                                    "Evaluation results (null if no"
                                    " evaluation completed)"
                                ),
                                "properties": {
                                    "total_cases": {
                                        "type": "integer",
                                        "description": "Total number of test cases",
                                    },
                                    "passed_cases": {
                                        "type": "integer",
                                        "description": "Number of passed test cases",
                                    },
                                    "failed_cases": {
                                        "type": "integer",
                                        "description": "Number of failed test cases",
                                    },
                                    "duration": {
                                        "type": "number",
                                        "description": "Total duration in seconds",
                                    },
                                    "cases": {
                                        "type": "array",
                                        "description": (
                                            "Detailed results for each"
                                            " test case"
                                        ),
                                    },
                                },
                            },
                            "error": {
                                "type": "string",
                                "nullable": True,
                                "description": "Error message if evaluation failed",
                            },
                        },
                        "required": [
                            "status",
                            "workflow_path",
                            "current_evaluation",
                        ],
                    },
                    "example": {
                        "status": "idle",
                        "workflow_path": "/v1/extract-nutrition-information",
                        "current_evaluation": None,
                        "results": None,
                    },
                }
            },
        }
    },
}
