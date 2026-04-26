"""Agent chat endpoint with stateful conversation memory."""

import asyncio
import json
import logging
import os
import time
import uuid

import litellm
import tiktoken
from common.llm import (
    call_llm_by_model,
    connect_llm_streaming,
    iterate_llm_stream,
)
from common.prompt_dsl import load_prompt_dsl
from common.search import EmbeddingUnavailableError
from common.state import providers_state
from fastapi import HTTPException
from fastapi.responses import StreamingResponse
from jsonschema import ValidationError, validate
from redis_memory import ConversationMemory
from situational.awareness import get_provider_context_window

# Override context window (tokens) regardless of what the model reports.
# Useful when VRAM is the real constraint, not the model's theoretical max.
_conversation_window_limit_raw = os.environ.get("CONVERSATION_WINDOW_LIMIT")
CONVERSATION_WINDOW_LIMIT: int | None = (
    int(_conversation_window_limit_raw)
    if _conversation_window_limit_raw is not None
    else None
)

# Default system message (can be overridden by env or DSL)
DEFAULT_SYSTEM_MESSAGE = os.environ.get(
    "DEFAULT_SYSTEM_MESSAGE",
    "You are a helpful assistant. "
    "You have access to conversation history and can maintain "
    "context across messages.",
)

EMBEDDING_TIMEOUT = float(os.environ.get("EMBEDDING_TIMEOUT", "0.5"))

logger = logging.getLogger(__name__)


_encoding = tiktoken.get_encoding("cl100k_base")


def get_conversation_key(user_id: str, conversation_id: str) -> str:
    """Generate a unique key for a conversation."""
    return f"{user_id}:{conversation_id}"


_TOKENS_PER_IMAGE = 384  # Based on llama.cpp KV cache usage per image


def estimate_token_count(text: str) -> int:
    """Estimate token count using tiktoken."""
    return len(_encoding.encode(text))


def count_images(content) -> int:
    """Count the number of images in message content."""
    if isinstance(content, list):
        return sum(
            1
            for part in content
            if isinstance(part, dict) and part.get("type") == "image_url"
        )
    return 0


def strip_base64_content(content) -> str:
    """Strip base64-encoded images from message content.

    Handles both string content and multi-part content with image_url. Returns
    plain text content only.
    """
    # If content is a string, return as-is
    if isinstance(content, str):
        return content

    # If content is a list (multi-part message), extract text only
    if isinstance(content, list):
        text_parts = []
        for part in content:
            if isinstance(part, dict):
                # Include text parts only
                if part.get("type") == "text":
                    text_parts.append(part.get("text", ""))
                # Skip image_url parts (especially base64)
        return " ".join(text_parts)

    # Unknown format, convert to string
    return str(content)


def fit_messages_to_context(
    messages: list[dict],
    max_context_token_count: int,
    system_message: str,
) -> list[dict]:
    """Fit messages into context window, keeping most recent messages.

    Base64-encoded images are stripped from content to avoid
    overwhelming the context window.

    Args:
        messages: List of conversation messages
        max_context_tokens: Maximum tokens allowed
        system_message: System message to include

    Returns:
        List of plain dict messages that fit in context window
    """
    # Reserve tokens for system message and response
    system_token_count = estimate_token_count(system_message)
    response_buffer = 1000  # Reserve tokens for response
    available_token_count = (
        max_context_token_count - system_token_count - response_buffer
    )

    if available_token_count < 100:
        # If context is too small, just return empty
        return []

    # Start from most recent and work backwards
    fitted_messages = []
    current_tokens = 0

    for message in reversed(messages):
        content = message.get("content", "")

        # Strip base64 images from content
        text_content = strip_base64_content(content)
        msg_tokens = (
            estimate_token_count(text_content)
            + count_images(content) * _TOKENS_PER_IMAGE
        )

        if current_tokens + msg_tokens <= available_token_count:
            # Create a fresh plain dict to avoid thread lock issues
            # with redis-memory. Use text-only content without base64
            # images
            plain_msg = {"role": message.get("role"), "content": text_content}
            fitted_messages.insert(0, plain_msg)
            current_tokens += msg_tokens
        else:
            # Can't fit more messages
            break

    return fitted_messages


# Supported streaming formats
STREAM_FORMAT_SSE = "sse"
STREAM_FORMAT_NDJSON = "ndjson"


async def handle_streaming(
    prompt_messages: list,
    timeout: float,
    max_tokens: int,
    conversation_id: str,
    user_id: str,
    message: str,
    conv_key: str,
    stream_format: str = STREAM_FORMAT_SSE,
    model: str = None,
    temperature: float = None,
):
    """Handle streaming agent chat requests.

    Args:
        stream_format: "sse" for Server-Sent Events (OpenAI-compatible),
                      "ndjson" for newline-delimited JSON (Ollama-style)

    Returns a StreamingResponse. After streaming completes,
    stores the full response in conversation memory.
    """
    timeout_display = (
        f"{timeout}s" if timeout is not None else "the configured timeout"
    )
    # Phase 1: establish streaming connection (raises 408 if LLM unreachable)
    try:
        llm_response, enforced_timeout, model_to_use = (
            await connect_llm_streaming(
                messages=prompt_messages,
                providers_state=providers_state,
                model=model,
                timeout=timeout,
                max_tokens=max_tokens,
                temperature=temperature,
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
        if "image" in error_msg or "base64" in error_msg:
            raise HTTPException(
                status_code=422,
                detail=(
                    "The model could not process the image input. "
                    "Ensure media URLs are valid base64 data URLs and that "
                    "the model supports image input."
                ),
            )
        raise HTTPException(
            status_code=500, detail=f"LLM connection failed: {str(e)}"
        )

    # Phase 1.5: prefetch the first token before committing to a 200 response.
    # connect_llm_streaming only waits for the generator object to be created —
    # the actual LLM inference happens on the first __anext__() call.  By
    # awaiting that call here (with a timeout) we can still raise a 408 before
    # any HTTP headers are sent.
    #
    # NOTE: asyncio.wait_for in Python 3.12 waits for the cancelled task to
    # fully finish before raising TimeoutError.  If the underlying httpx/Ollama
    # thread is stuck (e.g. allocating context for a huge max_tokens value) this
    # blocks indefinitely.  asyncio.wait() returns immediately on timeout
    # without waiting for task cancellation, so we use that instead.
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
        pass  # Empty model response; stream will just send [DONE]
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
        raise HTTPException(
            status_code=500, detail=f"LLM connection failed: {str(e)}"
        )

    created = int(time.time())

    async def generate_chunks():
        """Generate streaming chunks in the requested format."""
        full_content = []

        # Chain pre-fetched first chunk with the remainder of the stream.
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

                    # Build agent chat streaming chunk
                    chunk_data = {
                        "conversation_id": conversation_id,
                        "user_id": user_id,
                        "role": "assistant",
                        "created": created,
                        "delta": {},
                        "finish_reason": choice.finish_reason,
                    }

                    # Add content if present
                    if hasattr(delta, "content") and delta.content:
                        chunk_data["delta"]["content"] = delta.content
                        full_content.append(delta.content)

                    # Yield in appropriate format
                    if stream_format == STREAM_FORMAT_SSE:
                        yield f"data: {json.dumps(chunk_data)}\n\n"
                    else:  # NDJSON
                        yield json.dumps(chunk_data) + "\n"

        except litellm.APIConnectionError as e:
            error_chunk = {
                "conversation_id": conversation_id,
                "user_id": user_id,
                "role": "assistant",
                "created": created,
                "delta": {},
                "finish_reason": "error",
                "error": str(e),
            }
            if stream_format == STREAM_FORMAT_SSE:
                yield f"data: {json.dumps(error_chunk)}\n\n"
                yield "data: [DONE]\n\n"
            else:  # NDJSON
                yield json.dumps({**error_chunk, "done": True}) + "\n"
            return

        # After streaming completes, store messages in memory
        assistant_message = "".join(full_content)
        with ConversationMemory(conversation_id=conv_key) as memory:
            if not hasattr(memory, "messages") or not isinstance(
                memory.messages, list
            ):
                memory.messages = []
            memory.messages.append({"role": "user", "content": message})
            memory.messages.append(
                {"role": "assistant", "content": assistant_message}
            )

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


# TODO: Completely get rid of this and stop support for non-streaming.
async def handler(request: dict):
    """Agent chat endpoint with stateful conversation memory.

    Features:
    - User and conversation ID based isolation
    - Redis-backed conversation memory
    - Automatic context window management
    """
    logger.debug(f"Agent chat request body: {json.dumps(request, default=str)}")

    # Validate request against schema
    try:
        validate(
            instance=request,
            schema=spec["requestBody"]["content"]["application/json"]["schema"],
        )
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))

    # Extract request parameters
    message = request.get("message")
    media = request.get("media", [])
    conversation_id = request.get("conversation_id")
    user_id = request.get("user_id", "default-user")
    stream = request.get("stream", False)
    stream_format = request.get("stream_format", STREAM_FORMAT_SSE)
    timeout = request.get("timeout", 180)
    timeout_display = (
        f"{timeout}s" if timeout is not None else "the configured timeout"
    )
    max_tokens = request.get("max_tokens")

    # Validate required fields
    if not message:
        raise HTTPException(status_code=400, detail="Message is required")

    if not isinstance(message, str):
        raise HTTPException(status_code=400, detail="Message must be a string")

    if len(message.strip()) == 0:
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    # Generate conversation_id if not provided
    if not conversation_id:
        conversation_id = str(uuid.uuid4())

    # Get default provider and its context window
    default_provider = providers_state.get("default_provider")
    if not default_provider:
        # Build detailed error message
        all_providers = providers_state.get("providers", [])
        custom_providers = [
            p["name"]
            for p in all_providers
            if not p.get("is_default", True) and p.get("is_enabled", True)
        ]

        error_detail = "No default provider available. "

        if custom_providers:
            # Custom providers exist but none is set as default
            error_detail += (
                f"Found custom provider(s): {', '.join(custom_providers)}. "
                f"To use one as default, either: "
                f"(1) Set DEFAULT_PROVIDER={custom_providers[0]} "
                f"environment variable, or "
                f"(2) Rename one to 'default.yaml' in cortex/providers/. "
            )
        else:
            error_detail += (
                "No custom providers found. "
                "To add one, create a YAML file in cortex/providers/. "
            )

        error_detail += (
            "The built-in fallback provider requires MISTRAL_API_KEY "
            "to be set."
        )

        logger.error(
            f"Agent chat request failed: {error_detail} "
            f"Available providers: {providers_state.get('available_providers', [])}"
        )

        raise HTTPException(status_code=503, detail=error_detail)

    if CONVERSATION_WINDOW_LIMIT is not None:
        max_context_window = CONVERSATION_WINDOW_LIMIT
    else:
        max_context_window = get_provider_context_window(
            providers_state, default_provider
        )
        if max_context_window is None:
            max_context_window = 4096

    # TODO: Refactor this to add user, make sure that there are some
    # reserved usernames, __admin and __default
    # Get or create conversation memory
    conv_key = get_conversation_key(user_id, conversation_id)

    # Use context manager to ensure Redis flush before returning
    with ConversationMemory(conversation_id=conv_key) as memory:
        # Get existing messages or initialize
        if not hasattr(memory, "messages"):
            memory.messages = []

        messages = memory.messages

        # TODO: Upgrade memory and re-implement
        if not isinstance(messages, list):
            messages = []
            memory.messages = messages

        # Try to load prompt DSL from cortex folder
        try:
            dsl_result = load_prompt_dsl(
                input_text=message,
                message_history=messages,
                default_system_message=DEFAULT_SYSTEM_MESSAGE,
            )
        except EmbeddingUnavailableError as e:
            logger.error(
                "Agent chat: embedding server did not respond within %s ms "
                "for user=%s conversation=%s — search unavailable. "
                "The embedding server may be busy processing documents. "
                "Error: %s",
                EMBEDDING_TIMEOUT * 1000,
                user_id,
                conversation_id,
                e,
            )
            raise HTTPException(
                status_code=503,
                detail=(
                    "The embedding server did not respond in time. "
                    "Search is temporarily unavailable — "
                    "the server may be busy processing documents. "
                    "Please try again in a moment."
                ),
            )

        logger.info(f"Agent chat: DSL result present: {dsl_result is not None}")

        # Apply DSL customizations if available
        if dsl_result:
            # Override system message from docstring
            system_message = dsl_result.system_message or DEFAULT_SYSTEM_MESSAGE
            logger.info(
                f"Agent chat: Using DSL system message: "
                f"{system_message[:100]}..."
            )

            # Override user message from stdout
            if dsl_result.user_messages:
                # If DSL printed output, use that instead of raw message
                user_message_content = dsl_result.user_messages[0]
                # Store additional messages if multiple prints
                extra_user_messages = dsl_result.user_messages[1:]
            else:
                # No stdout, use original message
                user_message_content = message
                extra_user_messages = []

            # Apply agent config overrides
            if dsl_result.agent_config.max_tokens is not None:
                max_tokens = dsl_result.agent_config.max_tokens
            if dsl_result.agent_config.stream is not None:
                stream = dsl_result.agent_config.stream
            if dsl_result.agent_config.stream_format is not None:
                stream_format = dsl_result.agent_config.stream_format

            # Use modified history if DSL changed it
            if dsl_result.message_history is not None:
                messages = dsl_result.message_history
                memory.messages = messages
        else:
            # No DSL, use defaults
            system_message = DEFAULT_SYSTEM_MESSAGE
            user_message_content = message
            extra_user_messages = []
            logger.info(
                f"Agent chat: Using default system message: "
                f"{system_message[:100]}..."
            )

        # Collect model and temperature overrides from DSL
        model_override = None
        temperature = None
        if dsl_result:
            if dsl_result.agent_config.model:
                model_override = dsl_result.agent_config.model
            if dsl_result.agent_config.temperature is not None:
                temperature = dsl_result.agent_config.temperature

        # Fit messages to context window
        fitted_history = fit_messages_to_context(
            messages, max_context_window, system_message
        )

        # Build prompt with system message
        prompt_messages = [{"role": "system", "content": system_message}]
        prompt_messages.extend(fitted_history)

        # Add current user message(s) to prompt.
        # If the caller attached images, build a multimodal content list:
        # [text part, ...media parts].  Images are NOT stored in Redis memory
        # (only the plain-text message is), so base64 blobs never accumulate
        # in the conversation history.
        if media:
            text = (
                user_message_content
                if isinstance(user_message_content, str)
                else str(user_message_content)
            )
            user_message_content = [{"type": "text", "text": text}] + media
        user_msg = {"role": "user", "content": user_message_content}
        prompt_messages.append(user_msg)

        # Add any extra user messages from DSL (multiple prints)
        for extra_msg in extra_user_messages:
            prompt_messages.append({"role": "user", "content": extra_msg})

        # Apply full _override from DSL: replace prompt_messages and/or model
        if dsl_result and dsl_result.full_override:
            override = dsl_result.full_override
            if "messages" in override and override["messages"]:
                prompt_messages = override["messages"]
                logger.info(
                    "Agent chat: Using _override messages " "(%d messages)",
                    len(prompt_messages),
                )
            if "model" in override and override["model"]:
                model_override = override["model"]
                logger.info(
                    "Agent chat: Using _override model: %s", model_override
                )

        logger.info(
            f"Agent chat: Prompt messages count: {len(prompt_messages)}"
        )
        logger.debug(
            prompt_messages[:3]
            + [{"role": "...", "content": "..."}]
            + prompt_messages[-3:]
            if len(prompt_messages) > 6
            else prompt_messages
        )
        content_preview = (
            prompt_messages[0]["content"][:100] if prompt_messages else "N/A"
        )
        logger.info(
            f"Agent chat: System message in prompt: {content_preview}..."
        )

        # Handle streaming if requested
        if stream:
            return await handle_streaming(
                prompt_messages=prompt_messages,
                timeout=timeout,
                max_tokens=max_tokens,
                conversation_id=conversation_id,
                user_id=user_id,
                message=message,
                conv_key=conv_key,
                stream_format=stream_format,
                model=model_override,
                temperature=temperature,
            )

        # Call LLM with default provider
        logger.info(
            f"Agent chat: Calling LLM with {len(prompt_messages)} messages"
        )
        logger.info(
            f"Agent chat: First message (system): "
            f"{prompt_messages[0] if prompt_messages else 'N/A'}"
        )
        try:
            response = await call_llm_by_model(
                messages=prompt_messages,
                providers_state=providers_state,
                model=model_override,
                timeout=timeout,
                max_tokens=max_tokens,
                temperature=temperature,
            )
        except litellm.Timeout as e:
            logger.error(
                f"Agent chat request timeout - LLM provider did not respond. "
                f"User: {user_id}, Conversation: {conversation_id}, "
                f"Message: {message[:100]}..., "
                f"Max tokens: {max_tokens}, Timeout: {timeout}s, "
                f"Error: {str(e)}"
            )
            raise HTTPException(
                status_code=408,
                detail=(
                    f"Request timeout: the LLM did not respond within {timeout_display}."
                    f"To fix this: (1) reduce max_tokens, "
                    f"(2) enable streaming (stream=true) so responses "
                    f"arrive token-by-token, or (3) if the problem "
                    f"persists, ask your admin to switch to a faster "
                    f"model or provider."
                ),
            )
        except litellm.APIConnectionError as e:
            # Check if this is a timeout error wrapped in APIConnectionError
            error_msg = str(e).lower()
            if "timeout" in error_msg or "timed out" in error_msg:
                logger.error(
                    f"Agent chat request timeout (APIConnectionError) - "
                    f"LLM provider did not respond. "
                    f"User: {user_id}, Conversation: {conversation_id}, "
                    f"Message: {message[:100]}..., "
                    f"Max tokens: {max_tokens}, Timeout: {timeout}s, "
                    f"Error: {str(e)}"
                )
                raise HTTPException(
                    status_code=408,
                    detail=(
                        f"Request timeout: the LLM did not respond within {timeout_display}."
                        f"To fix this: (1) reduce max_tokens, "
                        f"(2) enable streaming (stream=true) so responses "
                        f"arrive token-by-token, or (3) if the problem "
                        f"persists, ask your admin to switch to a faster "
                        f"model or provider."
                    ),
                )
            if "image" in error_msg or "base64" in error_msg:
                raise HTTPException(
                    status_code=422,
                    detail=(
                        "The model could not process the image input. "
                        "Ensure media URLs are valid base64 data URLs and that "
                        "the model supports image input."
                    ),
                )
            # Otherwise, re-raise to be handled by outer exception handler
            raise
        except litellm.InternalServerError as e:
            # Log the error and crash to expose the issue
            logger.error(
                f"InternalServerError from LLM provider in agent chat: {e}"
            )
            raise

        # Extract response
        choice = response.choices[0]
        assistant_message = choice.message.content

        # Store user message and assistant response in memory
        # Use redis-memory's append() which handles persistence
        memory.messages.append({"role": "user", "content": message})
        memory.messages.append(
            {"role": "assistant", "content": assistant_message}
        )

        # Build response
        return {
            "conversation_id": conversation_id,
            "user_id": user_id,
            "message": assistant_message,
            "role": "assistant",
            "created": int(time.time()),
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
    "path": "/v1/agent/chat",
    "methods": ["POST"],
    "summary": "Send message to agent",
    "description": (
        "Send a message to an agent with stateful conversation memory. "
        "The server manages conversation history and context "
        "automatically."
    ),
    "requestBody": {
        "required": True,
        "content": {
            "application/json": {
                "schema": {
                    "type": "object",
                    "properties": {
                        "message": {
                            "type": "string",
                            "description": "The message to send to the agent",
                        },
                        "conversation_id": {
                            "type": "string",
                            "description": (
                                "Conversation identifier (optional, will be "
                                "generated if not provided)"
                            ),
                        },
                        "user_id": {
                            "type": "string",
                            "description": (
                                "User identifier for isolation (optional, "
                                "defaults to 'default-user')"
                            ),
                        },
                        "stream": {
                            "type": "boolean",
                            "description": "Whether to stream the response",
                            "default": False,
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
                        "timeout": {
                            "type": "number",
                            "minimum": 15,
                            "maximum": 240,
                            "description": (
                                "Request timeout in seconds. Overrides the "
                                "provider's default timeout if specified."
                            ),
                        },
                        "max_tokens": {
                            "type": "integer",
                            "minimum": 1,
                            "description": (
                                "Maximum number of tokens to generate in the "
                                "response."
                            ),
                        },
                        "media": {
                            "type": "array",
                            "description": (
                                "Optional list of images to attach to the "
                                "message. Supported formats: JPEG "
                                "(image/jpeg), PNG (image/png), GIF "
                                "(image/gif), WebP (image/webp). Each item "
                                "must use type 'image_url' with a base64 "
                                "data URL: "
                                "data:<mime_type>;base64,<base64_data>."
                            ),
                            "items": {
                                "type": "object",
                                "properties": {
                                    "type": {
                                        "type": "string",
                                        "enum": ["image_url"],
                                        "description": (
                                            "Media type identifier; "
                                            "must be 'image_url'."
                                        ),
                                    },
                                    "image_url": {
                                        "type": "object",
                                        "description": (
                                            "Image reference containing "
                                            "the base64 data URL."
                                        ),
                                        "properties": {
                                            "url": {
                                                "type": "string",
                                                "description": (
                                                    "Base64 data URL, e.g. "
                                                    "data:image/jpeg;base64,..."
                                                ),
                                            }
                                        },
                                        "required": ["url"],
                                    },
                                },
                                "required": ["type", "image_url"],
                            },
                        },
                    },
                    "required": ["message"],
                },
                "example": {
                    "message": "What's the weather?",
                    "stream": False,
                },
            }
        },
    },
    "responses": {
        200: {
            "description": "Agent response generated successfully",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "conversation_id": {
                                "type": "string",
                                "description": (
                                    "Unique identifier for the conversation"
                                ),
                            },
                            "user_id": {
                                "type": "string",
                                "description": (
                                    "User identifier for conversation isolation"
                                ),
                            },
                            "message": {
                                "type": "string",
                                "description": (
                                    "The assistant's response message"
                                ),
                            },
                            "role": {
                                "type": "string",
                                "description": (
                                    "Message role (always 'assistant' for "
                                    "responses)"
                                ),
                            },
                            "created": {
                                "type": "integer",
                                "description": (
                                    "Unix timestamp when the response was "
                                    "created"
                                ),
                            },
                            "usage": {
                                "type": "object",
                                "description": (
                                    "Token usage statistics for the request"
                                ),
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
                                        "description": (
                                            "Total number of tokens used"
                                        ),
                                    },
                                },
                            },
                        },
                        "required": [
                            "conversation_id",
                            "message",
                            "role",
                            "created",
                        ],
                    },
                    "example": {
                        "message": "The weather is sunny today!",
                        "role": "assistant",
                        "created": 1703347200,
                        "usage": {
                            "prompt_tokens": 56,
                            "completion_tokens": 31,
                            "total_tokens": 87,
                        },
                    },
                }
            },
        },
        400: {"description": "Bad request - invalid input"},
        408: {
            "description": (
                "Request timeout - the LLM provider did not respond "
                "within the specified timeout period"
            )
        },
        422: {"description": "Validation error"},
        503: {
            "description": (
                "Service unavailable. Possible causes: "
                "(1) No default provider configured — set DEFAULT_PROVIDER "
                "environment variable or ensure MISTRAL_API_KEY is set. "
                "(2) Embedding server did not respond in time — the server "
                "may be busy processing documents; retry shortly."
            )
        },
    },
}
