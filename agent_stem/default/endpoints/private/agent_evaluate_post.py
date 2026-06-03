"""POST /private/v1/agent/evaluate — start an evaluation run."""

import asyncio
import logging
from datetime import datetime, timezone
from pathlib import Path

from common.eval_dsl import (
    EvalCancelledError,
    find_eval_script,
    run_eval_suite,
)
from common.state import providers_state
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from synced_memory import Memory

logger = logging.getLogger(__name__)

_EVAL_STATE_KEY = "agent_evaluation_state"
_EVAL_LAST_KEY = "agent_evaluation_last_completed"


async def handler(request: dict):
    """Start an evaluation run from ``cortex/chat/eval.py``.

    Returns 202 Accepted when the run starts, or 409 Conflict if a run is
    already in progress.  An optional ``case`` field restricts the run to a
    single named case.
    """
    script_path = find_eval_script("/app/cortex")
    if script_path is None:
        raise HTTPException(
            status_code=404,
            detail=(
                "No evaluation script found. "
                "Create cortex/chat/eval.py to enable evaluation."
            ),
        )

    with Memory() as memory:
        state = getattr(memory, _EVAL_STATE_KEY, None)
        if state and state.get("status") == "running":
            return JSONResponse(
                status_code=409,
                content={"detail": "An evaluation run is already in progress."},
                headers={"Retry-After": "3"},
            )

    case_filter: str | None = request.get("case") if request else None

    started_at = datetime.now(timezone.utc).isoformat()

    with Memory() as memory:
        setattr(
            memory,
            _EVAL_STATE_KEY,
            {
                "status": "running",
                "started_at": started_at,
                "current_case": None,
                "completed_cases": 0,
                "total_cases": 0,
                "cancelled": False,
            },
        )

    async def _run_background():
        def _cancelled() -> bool:
            with Memory() as m:
                s = getattr(m, _EVAL_STATE_KEY, None) or {}
                return bool(s.get("cancelled"))

        def _on_case_start(case_name: str, idx: int, total: int):
            with Memory() as m:
                s = getattr(m, _EVAL_STATE_KEY, {}) or {}
                setattr(
                    m,
                    _EVAL_STATE_KEY,
                    {
                        **s,
                        "current_case": case_name,
                        "completed_cases": idx,
                        "total_cases": total,
                    },
                )

        def _on_case_done(case_name: str, case_result: dict):
            with Memory() as m:
                s = getattr(m, _EVAL_STATE_KEY, {}) or {}
                completed = s.get("completed_cases", 0) + 1
                setattr(
                    m,
                    _EVAL_STATE_KEY,
                    {
                        **s,
                        "current_case": case_name,
                        "completed_cases": completed,
                    },
                )

        loop = asyncio.get_event_loop()
        try:
            results = await loop.run_in_executor(
                None,
                lambda: run_eval_suite(
                    Path(script_path),
                    providers_state,
                    case_filter,
                    _cancelled,
                    _on_case_start,
                    _on_case_done,
                ),
            )
        except EvalCancelledError:
            logger.info("Evaluation run cancelled.")
            with Memory() as m:
                s = getattr(m, _EVAL_STATE_KEY, {}) or {}
                setattr(
                    m,
                    _EVAL_STATE_KEY,
                    {
                        **s,
                        "status": "cancelled",
                        "current_case": None,
                    },
                )
            return
        except Exception as e:
            logger.error("Evaluation run failed: %s", e, exc_info=True)
            with Memory() as m:
                s = getattr(m, _EVAL_STATE_KEY, {}) or {}
                setattr(
                    m,
                    _EVAL_STATE_KEY,
                    {
                        **s,
                        "status": "error",
                        "current_case": None,
                        "error": str(e),
                    },
                )
            return

        logger.info(
            "Evaluation run completed: passed=%d failed=%d total=%d",
            results.get("passed", 0),
            results.get("failed", 0),
            results.get("total", 0),
        )
        with Memory() as m:
            setattr(m, _EVAL_LAST_KEY, results)
            setattr(
                m,
                _EVAL_STATE_KEY,
                {
                    "status": "completed",
                    "started_at": started_at,
                    "current_case": None,
                    "completed_cases": results.get("total", 0),
                    "total_cases": results.get("total", 0),
                    "cancelled": False,
                },
            )

    asyncio.create_task(_run_background())

    return JSONResponse(
        status_code=202,
        content={"started_at": started_at},
    )


spec = {
    "path": "/private/v1/agent/evaluate",
    "methods": ["POST"],
    "summary": "Start an agent evaluation run",
    "description": (
        "Starts an asynchronous evaluation run from ``cortex/chat/eval.py``. "
        "Returns 202 Accepted when the run starts. "
        "Returns 409 Conflict if a run is already in progress. "
        "Pass an optional ``case`` field to run only that named case."
    ),
    "requestBody": {
        "required": False,
        "content": {
            "application/json": {
                "schema": {
                    "type": "object",
                    "properties": {
                        "case": {
                            "type": "string",
                            "description": (
                                "Optional: name of a single case to run. "
                                "If omitted, all cases run."
                            ),
                        }
                    },
                },
                "example": {"case": "greets_user"},
            }
        },
    },
    "responses": {
        202: {
            "description": "Evaluation run started",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "started_at": {
                                "type": "string",
                                "description": "ISO 8601 start timestamp",
                            }
                        },
                        "required": ["started_at"],
                    },
                    "example": {"started_at": "2025-04-01T14:00:00Z"},
                }
            },
        },
        404: {
            "description": "No eval.py found in cortex/chat/",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "detail": {
                                "type": "string",
                                "description": "Error message",
                            }
                        },
                    }
                }
            },
        },
        409: {
            "description": "A run is already in progress",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "detail": {
                                "type": "string",
                                "description": "Error message",
                            }
                        },
                    }
                }
            },
        },
    },
}
