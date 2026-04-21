"""Chat completions endpoint - OpenAI-compatible API."""

import asyncio
import json
import logging
import time
import uuid

import litellm
from common.llm import (
    call_llm_by_model,
    connect_llm_streaming,
    iterate_llm_stream,
)
from common.state import providers_state
from fastapi import HTTPException
from fastapi.responses import StreamingResponse
from jsonschema import ValidationError, validate

logger = logging.getLogger(__name__)

# Supported streaming formats
STREAM_FORMAT_SSE = "sse"
STREAM_FORMAT_NDJSON = "ndjson"


async def handle_streaming(
    messages: list,
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
    timeout_display = (
        f"{timeout}s" if timeout is not None else "the configured timeout"
    )
    # Pre-connect before creating StreamingResponse so timeout raises 408
    try:
        llm_response, enforced_timeout, model_to_use = (
            await connect_llm_streaming(
                messages=messages,
                providers_state=providers_state,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
                stop=stop,
                timeout=timeout,
            )
        )
    except (litellm.Timeout, asyncio.TimeoutError):
        raise HTTPException(
            status_code=408,
            detail=(
                f"Request timeout: the LLM did not respond within {timeout_display}. "
                f"To fix this: (1) reduce max_tokens, "
                f"(2) if the problem persists, ask your admin to switch "
                f"to a faster model or provider."
            ),
        )
    except litellm.APIConnectionError as e:
        error_msg = str(e).lower()
        if "timeout" in error_msg or "timed out" in error_msg:
            raise HTTPException(
                status_code=408,
                detail=(
                    f"Request timeout: the LLM did not respond within {timeout_display}. "
                    f"To fix this: (1) reduce max_tokens, "
                    f"(2) if the problem persists, ask your admin to switch "
                    f"to a faster model or provider."
                ),
            )
        raise HTTPException(
            status_code=500, detail=f"LLM connection failed: {str(e)}"
        )

    # Prefetch first token before committing to 200 OK — same fix as agent_chat.
    # Use asyncio.wait() instead of asyncio.wait_for() to avoid the Python 3.12
    # behaviour where wait_for blocks until the cancelled task finishes.
    first_chunk = None
    _first_chunk_task = asyncio.ensure_future(llm_response.__anext__())
    _, pending = await asyncio.wait(
        {_first_chunk_task},
        timeout=enforced_timeout,
    )
    if pending:
        _first_chunk_task.cancel()
        raise HTTPException(
            status_code=408,
            detail=(
                f"Request timeout: the LLM did not produce a response within "
                f"{timeout_display}. "
                f"To fix this: (1) reduce max_tokens, "
                f"(2) if the problem persists, ask your admin to switch "
                f"to a faster model or provider."
            ),
        )
    try:
        first_chunk = _first_chunk_task.result()
    except StopAsyncIteration:
        pass
    except litellm.APIConnectionError as e:
        error_msg = str(e).lower()
        if "timeout" in error_msg or "timed out" in error_msg:
            raise HTTPException(
                status_code=408,
                detail=(
                    f"Request timeout: the LLM did not produce a response within "
                    f"{timeout_display}. "
                    f"To fix this: (1) reduce max_tokens, "
                    f"(2) if the problem persists, ask your admin to switch "
                    f"to a faster model or provider."
                ),
            )
        if "illegal base64" in error_msg or "base64 data" in error_msg:
            raise HTTPException(
                status_code=422,
                detail=f"Invalid image data: the image could not be decoded. {str(e)}",
            )
        if (
            "missing data required for image input" in error_msg
            or "does not support image" in error_msg
            or "vision" in error_msg
            and "not supported" in error_msg
        ):
            raise HTTPException(
                status_code=422,
                detail=(
                    "The configured model does not support image input. "
                    "Configure a vision-capable provider to use this feature."
                ),
            )
        raise HTTPException(
            status_code=500, detail=f"LLM connection failed: {str(e)}"
        )

    completion_id = f"chatcmpl-{uuid.uuid4().hex[:24]}"
    created = int(time.time())

    async def generate_chunks():
        """Generate streaming chunks in the requested format."""

        async def _chunks():
            if first_chunk is not None:
                yield first_chunk
            async for chunk in iterate_llm_stream(
                llm_response, enforced_timeout, model_to_use
            ):
                yield chunk

        try:
            async for chunk in _chunks():
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
        except litellm.APIConnectionError:
            return  # connection dropped mid-stream; headers already sent

        # Send final message
        if stream_format == STREAM_FORMAT_SSE:
            yield "data: [DONE]\n\n"
        else:  # NDJSON
            yield json.dumps({"done": True}) + "\n"

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


async def handler(request: dict):
    """Create a chat completion (OpenAI-compatible API).

    This endpoint follows the OpenAI Chat Completion API format, making it
    compatible with most LLM clients and tools.
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
    timeout = request.get("timeout", 180)
    timeout_display = f"{timeout}s"

    if stream:
        return await handle_streaming(
            messages=messages,
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
        response = await call_llm_by_model(
            messages=messages,
            providers_state=providers_state,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            stop=stop,
            timeout=timeout,
        )
    except litellm.Timeout:
        raise HTTPException(
            status_code=408,
            detail=(
                f"Request timeout: the LLM did not respond within {timeout_display}. "
                f"To fix this: (1) reduce max_tokens, "
                f"(2) enable streaming (stream=true) so responses "
                f"arrive token-by-token, or (3) if the problem "
                f"persists, ask your admin to switch to a faster "
                f"model or provider."
            ),
        )
    except litellm.APIConnectionError as e:
        error_msg = str(e).lower()
        if "timeout" in error_msg or "timed out" in error_msg:
            raise HTTPException(
                status_code=408,
                detail=(
                    f"Request timeout: the LLM did not respond within {timeout_display}. "
                    f"To fix this: (1) reduce max_tokens, "
                    f"(2) enable streaming (stream=true) so responses "
                    f"arrive token-by-token, or (3) if the problem "
                    f"persists, ask your admin to switch to a faster "
                    f"model or provider."
                ),
            )
        if "illegal base64" in error_msg or "base64 data" in error_msg:
            raise HTTPException(
                status_code=422,
                detail=f"Invalid image data: the image could not be decoded. {str(e)}",
            )
        if (
            "missing data required for image input" in error_msg
            or "does not support image" in error_msg
            or "vision" in error_msg
            and "not supported" in error_msg
        ):
            raise HTTPException(
                status_code=422,
                detail=(
                    "The configured model does not support image input. "
                    "Configure a vision-capable provider to use this feature."
                ),
            )
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
    except NotImplementedError as e:
        raise HTTPException(status_code=501, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"LLM call failed: {str(e)}"
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


spec = {
    "path": "/v1/chat/completions",
    "methods": ["POST"],
    "summary": "Create chat completion",
    "description": (
        "Creates a model response for the given chat conversation. "
        "Compatible with OpenAI's Chat Completion API format. "
        "Supports both plain-text and multimodal (image + text) messages. "
        "To send an image, set the message content to an array of parts "
        "containing an image_url part and a text part, and select a "
        "vision-capable provider via the model field (e.g. 'vision')."
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
                                "Named provider to use for this request "
                                "(e.g. 'vision' for the vision.yaml provider, "
                                "'coding' for the coding.yaml provider). "
                                "Defaults to the configured default provider."
                            ),
                        },
                        "messages": {
                            "type": "array",
                            "description": (
                                "List of messages in the conversation. "
                                "Each message content can be a plain string "
                                "or an array of content parts for multimodal "
                                "input (text + image_url)."
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
                                        "oneOf": [
                                            {
                                                "type": "string",
                                                "description": (
                                                    "Plain text content"
                                                ),
                                            },
                                            {
                                                "type": "array",
                                                "description": (
                                                    "Multimodal content parts "
                                                    "(text and/or images). "
                                                    "Use this format to send "
                                                    "images alongside text."
                                                ),
                                                "items": {
                                                    "type": "object",
                                                    "oneOf": [
                                                        {
                                                            "properties": {
                                                                "type": {
                                                                    "type": "string",
                                                                    "enum": [
                                                                        "text"
                                                                    ],
                                                                },
                                                                "text": {
                                                                    "type": "string",
                                                                    "description": "The text content",
                                                                },
                                                            },
                                                            "required": [
                                                                "type",
                                                                "text",
                                                            ],
                                                        },
                                                        {
                                                            "properties": {
                                                                "type": {
                                                                    "type": "string",
                                                                    "enum": [
                                                                        "image_url"
                                                                    ],
                                                                },
                                                                "image_url": {
                                                                    "type": "object",
                                                                    "description": (
                                                                        "Image to send to "
                                                                        "the model. The url "
                                                                        "field accepts either "
                                                                        "a public HTTPS URL or "
                                                                        "a base64 data URL "
                                                                        "(data:image/jpeg;base64,...). "
                                                                        "Requires a vision-capable "
                                                                        "provider."
                                                                    ),
                                                                    "properties": {
                                                                        "url": {
                                                                            "type": "string",
                                                                            "description": (
                                                                                "HTTPS URL or "
                                                                                "base64 data URL "
                                                                                "of the image"
                                                                            ),
                                                                        }
                                                                    },
                                                                    "required": [
                                                                        "url"
                                                                    ],
                                                                },
                                                            },
                                                            "required": [
                                                                "type",
                                                                "image_url",
                                                            ],
                                                        },
                                                    ],
                                                },
                                                "minItems": 1,
                                            },
                                        ],
                                        "description": (
                                            "Message content: either a plain "
                                            "string or an array of content "
                                            "parts (text and/or image_url)"
                                        ),
                                    },
                                },
                                "required": ["role", "content"],
                            },
                            "minItems": 1,
                        },
                        "timeout": {
                            "type": "number",
                            "minimum": 15,
                            "maximum": 240,
                            "description": (
                                "Request timeout in seconds (15–240). "
                                "Overrides the provider's default timeout if specified."
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
                "examples": {
                    "text": {
                        "summary": "Plain text request",
                        "value": {
                            "messages": [
                                {
                                    "role": "user",
                                    "content": "What is the capital of France?",
                                }
                            ],
                            "stream": False,
                        },
                    },
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
