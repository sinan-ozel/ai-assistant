"""Evaluation endpoint for running workflow evaluations."""

import asyncio
import logging

from common.state import providers_state, workflows_state

logger = logging.getLogger(__name__)


async def handler(path: str):
    """Trigger evaluation for a workflow.

    Args:
        path: Workflow path (e.g., /v1/extract-nutrition-information)

    Returns:
        Dict with status message

    Raises:
        HTTPException: If workflow not found or evaluation already in progress
    """
    from pathlib import Path

    import yaml
    from fastapi import HTTPException
    from synced_memory import Memory
    from self.evaluation.parser import parse_evaluation_yaml
    from self.evaluation.runner import run_all_evaluations

    # Check if workflow exists
    workflow = workflows_state.get("workflows", {}).get(path)
    if not workflow:
        raise HTTPException(
            status_code=404, detail=f"Workflow not found for path: {path}"
        )

    # Check if evaluation is already running for this workflow
    with Memory() as memory:
        try:
            existing_state = memory.workflow_evaluation_state.get(path)
        except AttributeError:
            existing_state = None
        if existing_state and existing_state.get("status") == "running":
            raise HTTPException(
                status_code=409,
                detail=f"Evaluation already in progress for: {path}",
            )

    # Check if workflow has evaluation section
    workflow_data = workflow.get("data")
    if not workflow_data or "evaluation" not in workflow_data:
        raise HTTPException(
            status_code=422,
            detail=f"Workflow does not have an evaluation section: {path}",
        )

    # Get the base directory for the workflow (to resolve relative paths)
    workflow_file = workflow.get("file")
    if workflow_file:
        base_dir = Path(workflow_file).parent
    else:
        base_dir = Path("/app/cortex/workflows")

    # Mark evaluation as in progress
    from datetime import datetime

    started_at_iso = datetime.now().isoformat()
    logger.info(
        f"Marking evaluation as running with started_at: {started_at_iso}"
    )

    with Memory() as memory:
        memory.workflow_evaluation_state = {
            path: {
                "status": "running",
                "current_evaluation": path,
                "results": None,
                "error": None,
                "started_at": started_at_iso,
                "cancelled": False,
            }
        }

    # Start evaluation in background
    async def run_evaluation_async():
        logger.info(f"Starting evaluation for workflow: {path}")

        # Check for cancellation before starting
        with Memory() as memory:
            try:
                state = memory.workflow_evaluation_state.get(path, {})
            except AttributeError:
                state = {}
            if state.get("cancelled"):
                logger.info(f"Evaluation was cancelled before starting: {path}")
                memory.workflow_evaluation_state = {
                    path: {
                        "status": "cancelled",
                        "current_evaluation": None,
                        "results": None,
                        "error": "Evaluation was cancelled",
                        "started_at": state.get("started_at"),
                        "cancelled": True,
                    }
                }
                return

        # Parse evaluation YAML
        eval_yaml_str = yaml.dump(workflow_data["evaluation"])
        test_cases = parse_evaluation_yaml(eval_yaml_str, base_dir)

        # Get provider configuration
        provider = {}
        provider_name = workflow_data.get("provider")
        if provider_name:
            # Find provider in providers_state
            for p in providers_state.get("providers", []):
                if p.get("name") == provider_name:
                    provider = p.copy()
                    break

        if not provider:
            # Use default provider
            default_provider_name = providers_state.get("default_provider")
            if default_provider_name:
                for p in providers_state.get("providers", []):
                    if p.get("name") == default_provider_name:
                        provider = p.copy()
                        break

        if not provider:
            if providers_state.get("loading", False):
                raise ValueError(
                    "Provider discovery is still in progress. "
                    "Check GET /private/v1/providers for status "
                    "and retry once status is no longer 'initializing'."
                )
            raise ValueError("No provider available for evaluation")

        # Log which provider is being used
        provider_name_used = (
            workflow_data.get("provider")
            or providers_state.get("default_provider")
            or "unknown"
        )
        logger.info(
            f"Using provider '{provider_name_used}' for evaluation "
            f"of workflow: {path}"
        )

        # Ensure provider has a model key
        if "model" not in provider:
            provider["model"] = provider.get("name")

        # Build system message from workflow (same logic as workflow handler)
        # This includes the prompt template + output schema instructions
        from self.evaluation.runner import EvaluationCancelledError
        from startup.workflows import json_schema_to_prompt_format

        # Get prompt from execution section or legacy root-level field
        if "execution" in workflow_data:
            exec_section = workflow_data["execution"]
            exec_type = exec_section["type"]

            if exec_type == "prompt":
                base_prompt = exec_section["prompt"]
            elif exec_type == "python":
                raise ValueError(
                    "Python execution not yet supported for evaluations"
                )
            else:
                raise ValueError(f"Unknown execution type: {exec_type}")
        else:
            # Legacy format - prompt at root level
            base_prompt = workflow_data.get("prompt", "")

        # Build system message with prompt + output schema instructions
        output_schema = workflow_data.get("output_schema", {})
        schema_instructions = json_schema_to_prompt_format(output_schema)
        system_message = f"{base_prompt.strip()}\n\n{schema_instructions}"

        # Run evaluations in executor to avoid blocking
        loop = asyncio.get_event_loop()
        try:
            results = await loop.run_in_executor(
                None,
                run_all_evaluations,
                test_cases,
                provider,
                providers_state,
                path,
                system_message,
            )
        except EvaluationCancelledError:
            logger.info(f"Evaluation was cancelled for workflow: {path}")
            with Memory() as memory:
                try:
                    state = memory.workflow_evaluation_state.get(path, {})
                except AttributeError:
                    state = {}
                memory.workflow_evaluation_state = {
                    path: {
                        "status": "cancelled",
                        "current_evaluation": None,
                        "results": None,
                        "error": "Evaluation was cancelled",
                        "started_at": state.get("started_at"),
                        "cancelled": True,
                    }
                }
            return
        except Exception as e:
            logger.error(
                f"Evaluation failed for workflow {path}: {e}", exc_info=True
            )
            with Memory() as memory:
                try:
                    state = memory.workflow_evaluation_state.get(path, {})
                except AttributeError:
                    state = {}
                memory.workflow_evaluation_state = {
                    path: {
                        "status": "error",
                        "current_evaluation": None,
                        "results": None,
                        "error": str(e),
                        "started_at": state.get("started_at"),
                        "cancelled": state.get("cancelled", False),
                    }
                }
            return

        # Store results
        with Memory() as memory:
            try:
                state = memory.workflow_evaluation_state.get(path, {})
            except AttributeError:
                state = {}
            memory.workflow_evaluation_state = {
                path: {
                    "status": "completed",
                    "current_evaluation": None,
                    "results": results,
                    "error": None,
                    "started_at": state.get("started_at"),
                    "cancelled": False,
                }
            }
        logger.info(f"Evaluation completed for workflow: {path}")

    # Start background task
    def _on_done(task):
        exc = task.exception() if not task.cancelled() else None
        if exc:
            logger.error(
                "Unhandled exception in evaluation background task", exc_info=exc
            )

    task = asyncio.create_task(run_evaluation_async())
    task.add_done_callback(_on_done)

    return {
        "message": f"Evaluation started for workflow: {path}",
        "workflow_path": path,
    }


spec = {
    "path": "/private/evaluate{path:path}",
    "methods": ["POST"],
    "summary": "Trigger workflow evaluation",
    "description": (
        "Starts an asynchronous evaluation of a workflow. "
        "The workflow path should match a registered workflow endpoint path. "
        "Returns 201 when evaluation is started successfully, or 409 if "
        "an evaluation is already in progress."
    ),
    "responses": {
        201: {
            "description": "Evaluation started successfully",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "message": {
                                "type": "string",
                                "description": "Status message",
                            },
                            "workflow_path": {
                                "type": "string",
                                "description": "Path of the workflow being evaluated",
                            },
                        },
                        "required": ["message", "workflow_path"],
                    },
                    "example": {
                        "message": (
                            "Evaluation started for workflow: "
                            "/v1/extract-nutrition-information"
                        ),
                        "workflow_path": "/v1/extract-nutrition-information",
                    },
                }
            },
        },
        404: {
            "description": "Workflow not found",
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
            "description": "Evaluation already in progress",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "detail": {
                                "type": "string",
                                "description": (
                                    "Error message indicating evaluation"
                                    " in progress"
                                ),
                            }
                        },
                    }
                }
            },
        },
        422: {
            "description": "Workflow does not have evaluation section",
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
