"""DELETE /private/v1/agent/evaluate — cancel the in-progress evaluation
run."""

import logging

from fastapi import HTTPException
from synced_memory import Memory

logger = logging.getLogger(__name__)

_EVAL_STATE_KEY = "agent_evaluation_state"


async def handler():
    """Cancel the in-progress evaluation run.

    Gracefully signals the runner to stop after the current step completes.
    Returns 200 when cancellation is queued, or 404 if no run is active.
    """
    with Memory() as memory:
        state = getattr(memory, _EVAL_STATE_KEY, None)
        if not state or state.get("status") != "running":
            raise HTTPException(
                status_code=404,
                detail="No evaluation run is currently in progress.",
            )

        setattr(
            memory,
            _EVAL_STATE_KEY,
            {
                **state,
                "cancelled": True,
            },
        )

    logger.info("Evaluation run cancellation requested.")
    return {"message": "Evaluation run cancellation requested."}


spec = {
    "path": "/private/v1/agent/evaluate",
    "methods": ["DELETE"],
    "summary": "Cancel the in-progress evaluation run",
    "description": (
        "Signals the running evaluation to stop gracefully. "
        "The current step completes before the run is cancelled. "
        "Returns 404 if no run is active."
    ),
    "responses": {
        200: {
            "description": "Cancellation queued",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "message": {
                                "type": "string",
                                "description": "Confirmation that cancellation was queued",
                            }
                        },
                        "required": ["message"],
                    },
                    "example": {
                        "message": "Evaluation run cancellation requested."
                    },
                }
            },
        },
        404: {
            "description": "No run is currently active",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "detail": {
                                "type": "string",
                                "description": "Error message explaining why no active run was found",
                            }
                        },
                    }
                }
            },
        },
    },
}
