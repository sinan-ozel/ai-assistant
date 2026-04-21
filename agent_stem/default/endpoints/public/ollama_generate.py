"""Ollama generate endpoint - Ollama-native API."""

import logging
from datetime import datetime, timezone

import litellm
from common.llm import call_llm_by_model
from common.state import providers_state
from fastapi import HTTPException
from jsonschema import ValidationError, validate

logger = logging.getLogger(__name__)


async def handler(request: dict):
    """Generate completion using Ollama format.

    This endpoint follows the Ollama Generate API format, making it compatible
    with Ollama clients and LiteLLM when using ollama/ prefix.
    """
    # Validate request against schema
    try:
        validate(
            instance=request,
            schema=spec["requestBody"]["content"]["application/json"]["schema"],
        )
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))

    # Extract request parameters
    model = request.get("model")
    prompt = request.get("prompt")
    temperature = request.get("temperature")
    top_p = request.get("top_p")
    top_k = request.get("top_k")
    stream = request.get("stream", False)
    timeout = request.get("timeout", 180)
    timeout_display = (
        f"{timeout}s" if timeout is not None else "the configured timeout"
    )

    if stream:
        raise HTTPException(
            status_code=501, detail="Streaming not yet implemented"
        )

    # Convert prompt to messages format for LiteLLM
    messages = [{"role": "user", "content": prompt}]

    # Build kwargs for LiteLLM
    kwargs = {}
    if top_k is not None:
        kwargs["top_k"] = top_k
    if timeout is not None:
        kwargs["timeout"] = timeout

    # Call LLM
    try:
        response = await call_llm_by_model(
            messages=messages,
            providers_state=providers_state,
            model=model,
            temperature=temperature,
            top_p=top_p,
            **kwargs,
        )
    except litellm.Timeout:
        raise HTTPException(
            status_code=408,
            detail=(
                f"Request timeout: the LLM did not respond within {timeout_display}. "
                f"To fix this: reduce max_tokens or switch to a faster model."
            ),
        )
    except litellm.APIConnectionError as e:
        error_msg = str(e).lower()
        if "timeout" in error_msg or "timed out" in error_msg:
            raise HTTPException(
                status_code=408,
                detail=(
                    f"Request timeout: the LLM did not respond within {timeout_display}. "
                    f"To fix this: reduce max_tokens or switch to a faster model."
                ),
            )
        raise HTTPException(
            status_code=500, detail=f"LLM call failed: {str(e)}"
        )
    except NotImplementedError as e:
        raise HTTPException(status_code=501, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"LLM call failed: {str(e)}"
        )

    # Extract response content
    choice = response.choices[0]
    response_text = choice.message.content

    # Build Ollama-format response
    # Note: Some fields are approximated since LiteLLM doesn't
    # provide all Ollama metrics
    return {
        "model": response.model,
        "created_at": datetime.now(timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%S.%fZ"
        ),
        "response": response_text,
        "done": True,
        "context": [],  # LiteLLM doesn't provide this
        "total_duration": 0,  # Would need timing instrumentation
        "load_duration": 0,
        "prompt_eval_count": (
            response.usage.prompt_tokens if response.usage else 0
        ),
        "prompt_eval_duration": 0,
        "eval_count": (
            response.usage.completion_tokens if response.usage else 0
        ),
        "eval_duration": 0,
    }


spec = {
    "path": "/v1/api/generate",
    "methods": ["POST"],
    "summary": "Generate completion (Ollama format)",
    "description": (
        "Generates a completion for a prompt using Ollama's native API "
        "format. Compatible with Ollama clients."
    ),
    "requestBody": {
        "required": True,
        "content": {
            "application/json": {
                "schema": {
                    "type": "object",
                    "properties": {
                        "model": {
                            "type": "string",
                            "description": (
                                "Name of the model to use for generation"
                            ),
                        },
                        "prompt": {
                            "type": "string",
                            "description": (
                                "Human-readable text prompt to generate a "
                                "completion for"
                            ),
                        },
                        "stream": {
                            "type": "boolean",
                            "default": False,
                            "description": (
                                "Whether to stream the response incrementally"
                            ),
                        },
                        "temperature": {
                            "type": "number",
                            "minimum": 0.0,
                            "maximum": 2.0,
                            "default": 0.8,
                            "description": (
                                "Temperature for sampling. Higher values "
                                "increase randomness"
                            ),
                        },
                        "top_p": {
                            "type": "number",
                            "minimum": 0.0,
                            "maximum": 1.0,
                            "default": 0.9,
                            "description": "Top-p (nucleus) sampling parameter",
                        },
                        "top_k": {
                            "type": "integer",
                            "minimum": 1,
                            "default": 40,
                            "description": (
                                "Top-k sampling parameter. Limits to top k "
                                "tokens"
                            ),
                        },
                        "timeout": {
                            "type": "number",
                            "minimum": 0,
                            "description": (
                                "Request timeout in seconds. Overrides the "
                                "provider's default timeout if specified."
                            ),
                        },
                    },
                    "required": ["model", "prompt"],
                },
                "example": {
                    "model": "gemma3:4b",
                    "prompt": "What is the capital of France?",
                    "stream": False,
                    "temperature": 0.7,
                },
            }
        },
    },
    "responses": {
        200: {
            "description": "Completion generated successfully",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "model": {
                                "type": "string",
                                "description": "The model used",
                            },
                            "created_at": {
                                "type": "string",
                                "description": "Timestamp of creation",
                            },
                            "response": {
                                "type": "string",
                                "description": "The generated text",
                            },
                            "done": {
                                "type": "boolean",
                                "description": "Whether generation is complete",
                            },
                            "context": {
                                "type": "array",
                                "description": "Context tokens",
                                "items": {"type": "integer"},
                            },
                            "total_duration": {
                                "type": "integer",
                                "description": "Total duration in nanoseconds",
                            },
                            "load_duration": {
                                "type": "integer",
                                "description": (
                                    "Model load duration in nanoseconds"
                                ),
                            },
                            "prompt_eval_count": {
                                "type": "integer",
                                "description": "Number of tokens in the prompt",
                            },
                            "prompt_eval_duration": {
                                "type": "integer",
                                "description": (
                                    "Prompt evaluation duration in "
                                    "nanoseconds"
                                ),
                            },
                            "eval_count": {
                                "type": "integer",
                                "description": "Number of tokens generated",
                            },
                            "eval_duration": {
                                "type": "integer",
                                "description": (
                                    "Generation duration in nanoseconds"
                                ),
                            },
                        },
                        "required": ["model", "created_at", "response", "done"],
                    },
                    "example": {
                        "model": "gemma3:4b",
                        "created_at": "2024-12-20T00:00:00.000000Z",
                        "response": "The capital of France is Paris.",
                        "done": True,
                        "context": [],
                        "total_duration": 0,
                        "load_duration": 0,
                        "prompt_eval_count": 10,
                        "prompt_eval_duration": 0,
                        "eval_count": 10,
                        "eval_duration": 0,
                    },
                }
            },
        },
        400: {"description": "Bad request - invalid parameters"},
        404: {"description": "Model not found or not available"},
        408: {
            "description": (
                "Request timeout - the LLM provider did not respond "
                "within the specified timeout period"
            )
        },
        422: {
            "description": "Validation error - request does not match schema"
        },
        501: {
            "description": "Not implemented - streaming is not yet supported"
        },
    },
}
