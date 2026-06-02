"""GET /private/v1/agent/evaluate — poll evaluation status or fetch results."""

_EVAL_STATE_KEY = "agent_evaluation_state"
_EVAL_LAST_KEY = "agent_evaluation_last_completed"


async def handler():
    """Return the status of the current evaluation run, or the last result.

    - 200 OK: last completed run results.
    - 202 Accepted: a run is in progress — check back later.
    - 404 Not Found: no completed run exists yet.
    """
    from fastapi.responses import JSONResponse
    from synced_memory import Memory

    with Memory() as memory:
        state = getattr(memory, _EVAL_STATE_KEY, None)
        last_result = getattr(memory, _EVAL_LAST_KEY, None)

    if state is None:
        raise _not_found()

    status = state.get("status")

    if status == "running":
        return JSONResponse(
            status_code=202,
            content={
                "status": "running",
                "cancelled": state.get("cancelled", False),
                "provider": None,
                "started_at": state.get("started_at"),
                "current_case": state.get("current_case"),
                "completed_cases": state.get("completed_cases", 0),
                "total_cases": state.get("total_cases", 0),
            },
            headers={"Retry-After": "3"},
        )

    if status == "completed":
        if last_result is None:
            raise _not_found()
        return last_result

    if status == "cancelled":
        if last_result is None:
            raise _not_found()
        return last_result

    if status == "error":
        return JSONResponse(
            status_code=200,
            content={
                "status": "error",
                "error": state.get("error"),
                "started_at": state.get("started_at"),
            },
        )

    raise _not_found()


def _not_found():
    from fastapi import HTTPException

    return HTTPException(
        status_code=404,
        detail="No completed evaluation run found.",
    )


spec = {
    "path": "/private/v1/agent/evaluate",
    "methods": ["GET"],
    "summary": "Get evaluation status or results",
    "description": (
        "Returns results from the last completed run (200), "
        "a progress snapshot if a run is ongoing (202), "
        "or 404 when no completed run exists."
    ),
    "responses": {
        200: {
            "description": "Last completed evaluation run results",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "suite": {
                                "type": "string",
                                "nullable": True,
                                "description": "Suite name from module docstring",
                            },
                            "provider": {
                                "type": "string",
                                "description": "Provider used for the run",
                            },
                            "started_at": {
                                "type": "string",
                                "description": "ISO 8601 timestamp when the run started",
                            },
                            "completed_at": {
                                "type": "string",
                                "description": "ISO 8601 timestamp when the run completed",
                            },
                            "passed": {
                                "type": "integer",
                                "description": "Number of cases that passed",
                            },
                            "failed": {
                                "type": "integer",
                                "description": "Number of cases that failed",
                            },
                            "total": {
                                "type": "integer",
                                "description": "Total number of cases evaluated",
                            },
                            "cases": {
                                "type": "array",
                                "description": "Per-case evaluation results",
                                "items": {"type": "object"},
                            },
                        },
                        "required": [
                            "passed",
                            "failed",
                            "total",
                            "cases",
                        ],
                    },
                    "example": {
                        "suite": "Basic greeting suite",
                        "provider": "default",
                        "started_at": "2025-04-01T14:00:00Z",
                        "completed_at": "2025-04-01T14:01:00Z",
                        "passed": 1,
                        "failed": 0,
                        "total": 1,
                        "cases": [
                            {
                                "id": "greets_user",
                                "status": "pass",
                                "runs": [
                                    {
                                        "run": 1,
                                        "checks": [
                                            {
                                                "type": "regexp",
                                                "pattern": "(?i)hello",
                                                "passed": True,
                                            }
                                        ],
                                    }
                                ],
                                "passing_runs": 1,
                                "threshold": 1,
                            }
                        ],
                    },
                }
            },
        },
        202: {
            "description": "Run in progress — retry after a few seconds",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "status": {
                                "type": "string",
                                "description": "Current status of the evaluation run",
                            },
                            "started_at": {
                                "type": "string",
                                "description": "ISO 8601 timestamp when the run started",
                            },
                            "current_case": {
                                "type": "string",
                                "nullable": True,
                                "description": "Name of the case currently being evaluated",
                            },
                            "completed_cases": {
                                "type": "integer",
                                "description": "Number of cases completed so far",
                            },
                            "total_cases": {
                                "type": "integer",
                                "description": "Total number of cases in this run",
                            },
                        },
                        "required": ["status"],
                    },
                    "example": {
                        "status": "running",
                        "started_at": "2025-04-01T14:00:00Z",
                        "current_case": "greets_user",
                        "completed_cases": 0,
                        "total_cases": 2,
                    },
                }
            },
        },
        404: {
            "description": "No completed evaluation run exists yet",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "detail": {
                                "type": "string",
                                "description": "Error message explaining why the resource was not found",
                            }
                        },
                    },
                    "example": {"detail": "No completed evaluation run found."},
                }
            },
        },
    },
}
