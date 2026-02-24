"""Chat completions endpoint - OpenAI-compatible API."""

import json
import logging
import time
import uuid

import litellm
from common.llm import call_llm_by_model, call_llm_by_model_streaming
from fastapi import HTTPException
from fastapi.responses import StreamingResponse
from jsonschema import ValidationError, validate

logger = logging.getLogger(__name__)

# Supported streaming formats
STREAM_FORMAT_SSE = "sse"
STREAM_FORMAT_NDJSON = "ndjson"


async def handle_streaming(
    messages: list,
    providers_state: dict,
    model: str,
    stream_format: str = STREAM_FORMAT_SSE,
    temperature: float = None,
    max_tokens: int = None,
    top_p: float = None,
    stop: list = None,
    timeout: float = None,
):
    """Handle streaming chat completion requests.

    Args:
        stream_format: "sse" for Server-Sent Events (OpenAI-compatible),
                      "ndjson" for newline-delimited JSON (Ollama-style)

    Returns a StreamingResponse with appropriate format.
    """
    completion_id = f"chatcmpl-{uuid.uuid4().hex[:24]}"
    created = int(time.time())

    async def generate_chunks():
        """Generate streaming chunks in the requested format."""
        try:
            async for chunk in call_llm_by_model_streaming(
                messages=messages,
                providers_state=providers_state,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
                stop=stop,
                timeout=timeout,
            ):
                # Extract delta content from chunk
                if chunk.choices and len(chunk.choices) > 0:
                    choice = chunk.choices[0]
                    delta = choice.delta

                    # Build OpenAI-compatible streaming chunk
                    chunk_data = {
                        "id": completion_id,
                        "object": "chat.completion.chunk",
                        "created": created,
                        "model": model or chunk.model,
                        "choices": [
                            {
                                "index": 0,
                                "delta": {},
                                "finish_reason": choice.finish_reason,
                            }
                        ],
                    }

                    # Add role if present (usually first chunk)
                    if hasattr(delta, "role") and delta.role:
                        chunk_data["choices"][0]["delta"]["role"] = delta.role

                    # Add content if present
                    if hasattr(delta, "content") and delta.content:
                        chunk_data["choices"][0]["delta"][
                            "content"
                        ] = delta.content

                    # Yield in appropriate format
                    if stream_format == STREAM_FORMAT_SSE:
                        yield f"data: {json.dumps(chunk_data)}\n\n"
                    else:  # NDJSON
                        yield json.dumps(chunk_data) + "\n"

            # Send final message
            if stream_format == STREAM_FORMAT_SSE:
                yield "data: [DONE]\n\n"
            else:  # NDJSON
                yield json.dumps({"done": True}) + "\n"

        except litellm.Timeout as e:
            error_data = {"error": {"message": str(e), "type": "timeout"}}
            if stream_format == STREAM_FORMAT_SSE:
                yield f"data: {json.dumps(error_data)}\n\n"
            else:
                yield json.dumps(error_data) + "\n"
        except litellm.APIConnectionError as e:
            error_msg = str(e).lower()
            if "timeout" in error_msg or "timed out" in error_msg:
                error_data = {"error": {"message": str(e), "type": "timeout"}}
            else:
                error_data = {
                    "error": {"message": str(e), "type": "connection_error"}
                }
            if stream_format == STREAM_FORMAT_SSE:
                yield f"data: {json.dumps(error_data)}\n\n"
            else:
                yield json.dumps(error_data) + "\n"
        except Exception as e:
            logger.error(f"Streaming error: {e}")
            error_data = {
                "error": {
                    "message": f"LLM call failed: {str(e)}",
                    "type": "server_error",
                }
            }
            if stream_format == STREAM_FORMAT_SSE:
                yield f"data: {json.dumps(error_data)}\n\n"
            else:
                yield json.dumps(error_data) + "\n"

    # Set media type based on format
    if stream_format == STREAM_FORMAT_SSE:
        media_type = "text/event-stream"
    else:
        media_type = "application/x-ndjson"

    return StreamingResponse(
        generate_chunks(),
        media_type=media_type,
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


async def handler(request: dict, providers_state: dict):
    """Create a chat completion (OpenAI-compatible API).

    This endpoint follows the OpenAI Chat Completion API format, making
    it compatible with most LLM clients and tools.
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
    messages = request.get("messages", [])
    temperature = request.get("temperature")
    max_tokens = request.get("max_tokens")
    top_p = request.get("top_p")
    stop = request.get("stop")
    stream = request.get("stream", False)
    stream_format = request.get("stream_format", STREAM_FORMAT_SSE)
    timeout = request.get("timeout")

    if stream:
        return await handle_streaming(
            messages=messages,
            providers_state=providers_state,
            model=model,
            stream_format=stream_format,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            stop=stop,
            timeout=timeout,
        )

    try:
        # Call LLM
        response = call_llm_by_model(
            messages=messages,
            providers_state=providers_state,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            stop=stop,
            timeout=timeout,
        )

        # Extract response data
        choice = response.choices[0]

        # Build OpenAI-format response
        return {
            "id": f"chatcmpl-{uuid.uuid4().hex[:24]}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": (
                model or response.model
            ),  # TODO: Consider model usage - if the model does not exist,
            # are we using the default? Return the model that's actually
            # used.
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": choice.message.role,
                        "content": choice.message.content,
                    },
                    "finish_reason": choice.finish_reason,
                }
            ],
            "usage": {
                "prompt_tokens": (
                    response.usage.prompt_tokens if response.usage else 0
                ),
                "completion_tokens": (
                    response.usage.completion_tokens if response.usage else 0
                ),
                "total_tokens": (
                    response.usage.total_tokens if response.usage else 0
                ),
            },
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except NotImplementedError as e:
        raise HTTPException(status_code=501, detail=str(e))
    except litellm.Timeout as e:
        raise HTTPException(
            status_code=408,
            detail=(
                f"Request timeout: The LLM provider did not respond "
                f"within the specified timeout period. {str(e)}"
            ),
        )
    except litellm.APIConnectionError as e:
        # Check if this is a timeout error wrapped in APIConnectionError
        error_msg = str(e).lower()
        if "timeout" in error_msg or "timed out" in error_msg:
            raise HTTPException(
                status_code=408,
                detail=(
                    f"Request timeout: The LLM provider did not respond "
                    f"within the specified timeout period. {str(e)}"
                ),
            )
        # Otherwise, it's a different connection error
        raise HTTPException(
            status_code=500, detail=f"LLM call failed: {str(e)}"
        )
    except litellm.InternalServerError as e:
        # If a specific model was requested, inform user that model
        # doesn't support this
        if model:
            raise HTTPException(
                status_code=501,
                detail=(
                    f"The requested model '{model}' does not support this "
                    f"operation. {str(e)}"
                ),
            )
        # Otherwise, log and crash to expose the issue
        logger.error(f"InternalServerError from LLM provider: {e}")
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"LLM call failed: {str(e)}"
        )


spec = {
    "path": "/v1/chat/completions",
    "methods": ["POST"],
    "summary": "Create chat completion",
    "description": (
        "Creates a model response for the given chat conversation. "
        "Compatible with OpenAI's Chat Completion API format."
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
                                "ID of the model to use for completion"
                            ),
                        },
                        "messages": {
                            "type": "array",
                            "description": (
                                "List of messages in the conversation"
                            ),
                            "items": {
                                "type": "object",
                                "properties": {
                                    "role": {
                                        "type": "string",
                                        "enum": ["system", "user", "assistant"],
                                        "description": (
                                            "Role of the message author"
                                        ),
                                    },
                                    "content": {
                                        "type": "string",
                                        "description": (
                                            "Human-readable text content of "
                                            "the message"
                                        ),
                                    },
                                },
                                "required": ["role", "content"],
                            },
                            "minItems": 1,
                        },
                        "timeout": {
                            "type": "number",
                            "minimum": 0,
                            "description": (
                                "Request timeout in seconds. Overrides the "
                                "provider's default timeout if specified."
                            ),
                        },
                        "stream": {
                            "type": "boolean",
                            "default": False,
                            "description": (
                                "Whether to stream the response incrementally"
                            ),
                        },
                        "stream_format": {
                            "type": "string",
                            "enum": ["sse", "ndjson"],
                            "default": "sse",
                            "description": (
                                "Streaming format: 'sse' for Server-Sent "
                                "Events (OpenAI-compatible), 'ndjson' for "
                                "newline-delimited JSON (Ollama-style)"
                            ),
                        },
                        # "temperature": {
                        #     "type": "number",
                        #     "minimum": 0.0,
                        #     "maximum": 2.0,
                        #     "default": 1.0,
                        #     "description": (
                        #         "Sampling temperature. Higher values make "
                        #         "output more random, lower values more "
                        #         "deterministic"
                        #     )
                        # },
                        # "max_tokens": {
                        #     "type": "integer",
                        #     "minimum": 1,
                        #     "description": (
                        #         "Maximum number of tokens to generate in "
                        #         "the completion"
                        #     )
                        # },
                        # "stream": {
                        #     "type": "boolean",
                        #     "default": False,
                        #     "description": (
                        #         "Whether to stream the response "
                        #         "incrementally"
                        #     )
                        # },
                        # "top_p": {
                        #     "type": "number",
                        #     "exclusiveMinimum": 0.0,
                        #     "maximum": 1.0,
                        #     "default": 1.0,
                        #     "description": (
                        #         "Nucleus sampling parameter. Alternative to "
                        #         "temperature. Must be in (0, 1]."
                        #     )
                        # },
                        # "stop": {
                        #     "type": "array",
                        #     "items": {"type": "string"},
                        #     "maxItems": 4,
                        #     "description": (
                        #         "Up to 4 sequences where the API will "
                        #         "stop generating tokens"
                        #     )
                        # }
                    },
                    "required": ["messages"],
                },
                "example": {
                    # "model": "pixtral",
                    "messages": [
                        {
                            "role": "user",
                            "content": "What is the capital of France?",
                        }
                    ],
                    "stream": False,
                    # "temperature": 0.7,
                    # "max_tokens": 100
                },
            }
        },
    },
    "responses": {
        200: {
            "description": "Chat completion response",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "id": {
                                "type": "string",
                                "description": (
                                    "Unique identifier for the completion"
                                ),
                            },
                            "object": {
                                "type": "string",
                                "description": (
                                    "Object type, always 'chat.completion'"
                                ),
                            },
                            "created": {
                                "type": "integer",
                                "description": (
                                    "Unix timestamp of when the completion "
                                    "was created"
                                ),
                            },
                            "model": {
                                "type": "string",
                                "description": "The model used for completion",
                            },
                            "choices": {
                                "type": "array",
                                "description": "List of completion choices",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "index": {
                                            "type": "integer",
                                            "description": "Choice index",
                                        },
                                        "message": {
                                            "type": "object",
                                            "description": (
                                                "The generated message"
                                            ),
                                            "properties": {
                                                "role": {
                                                    "type": "string",
                                                    "description": (
                                                        "Role of the message "
                                                        "author"
                                                    ),
                                                },
                                                "content": {
                                                    "type": "string",
                                                    "description": (
                                                        "Content of the message"
                                                    ),
                                                },
                                            },
                                        },
                                        "finish_reason": {
                                            "type": "string",
                                            "description": (
                                                "Reason for completion finish "
                                                "(stop, length, etc.)"
                                            ),
                                        },
                                    },
                                },
                            },
                            "usage": {
                                "type": "object",
                                "description": "Token usage statistics",
                                "properties": {
                                    "prompt_tokens": {
                                        "type": "integer",
                                        "description": (
                                            "Number of tokens in the prompt"
                                        ),
                                    },
                                    "completion_tokens": {
                                        "type": "integer",
                                        "description": (
                                            "Number of tokens in the completion"
                                        ),
                                    },
                                    "total_tokens": {
                                        "type": "integer",
                                        "description": "Total tokens used",
                                    },
                                },
                            },
                        },
                        "required": [
                            "id",
                            "object",
                            "created",
                            "model",
                            "choices",
                        ],
                    },
                    "example": {
                        "id": "chatcmpl-abc123",
                        "object": "chat.completion",
                        "created": 1734700000,
                        "model": "pixtral",
                        "choices": [
                            {
                                "index": 0,
                                "message": {
                                    "role": "assistant",
                                    "content": (
                                        "Hello! How can I help you today?"
                                    ),
                                },
                                "finish_reason": "stop",
                            }
                        ],
                        "usage": {
                            "prompt_tokens": 20,
                            "completion_tokens": 10,
                            "total_tokens": 30,
                        },
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
            "description": (
                "Not implemented - the requested model does not support "
                "this operation"
            )
        },
    },
}
