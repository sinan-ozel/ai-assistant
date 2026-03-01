"""Cancel endpoint for stopping running evaluations."""

import logging

logger = logging.getLogger(__name__)


async def handler(path: str):
    """
    Cancel a running evaluation for a workflow.

    Args:
        path: Workflow path (e.g., /v1/extract-nutrition-information)

    Returns:
        Dict with status message

    Raises:
        HTTPException: If no evaluation is running
    """
    from fastapi import HTTPException
    from redis_memory import Memory

    # Mark evaluation as cancelled
    with Memory() as memory:
        if not hasattr(memory, 'workflow_evaluation_state'):
            memory.workflow_evaluation_state = {}

        state = memory.workflow_evaluation_state.get(path, {})
        if not state or state.get("status") != "running":
            raise HTTPException(
                status_code=404,
                detail=f"No running evaluation found for: {path}"
            )

        # Immediately update status to cancelled
        memory.workflow_evaluation_state[path] = {
            **state,
            "status": "cancelled",
            "cancelled": True,
            "current_evaluation": None,
            "error": "Evaluation was cancelled by user"
        }

    logger.info(f"Evaluation cancelled for workflow: {path}")

    return {
        "message": f"Evaluation cancelled for workflow: {path}",
        "workflow_path": path
    }


spec = {
    "path": "/private/cancel-evaluation{path:path}",
    "methods": ["POST"],
    "summary": "Cancel workflow evaluation",
    "description": (
        "Cancels a currently running evaluation. "
        "The evaluation status is immediately set to cancelled."
    ),
    "responses": {
        200: {
            "description": "Evaluation cancelled successfully",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "message": {
                                "type": "string",
                                "description": "Status message"
                            },
                            "workflow_path": {
                                "type": "string",
                                "description": "Path of the workflow"
                            }
                        },
                        "required": ["message", "workflow_path"]
                    },
                    "example": {
                        "message": "Evaluation cancelled for workflow: /v1/extract-nutrition-information",
                        "workflow_path": "/v1/extract-nutrition-information"
                    }
                }
            }
        },
        404: {
            "description": "No running evaluation found",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "detail": {
                                "type": "string",
                                "description": "Error message"
                            }
                        }
                    }
                }
            }
        }
    }
}
