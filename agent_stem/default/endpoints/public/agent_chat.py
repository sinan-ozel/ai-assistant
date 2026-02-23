"""Agent chat endpoint with stateful conversation memory."""

import json
import logging
import os
import time
import uuid

import litellm
import tiktoken
from common.llm import call_llm_by_model, call_llm_by_model_streaming
from common.prompt_dsl import load_prompt_dsl
from fastapi import HTTPException
from fastapi.responses import StreamingResponse
from jsonschema import ValidationError, validate
from redis_memory import ConversationMemory
from situational.awareness import get_provider_context_window

# Default system message (can be overridden by env or DSL)
DEFAULT_SYSTEM_MESSAGE = os.environ.get(
    "DEFAULT_SYSTEM_MESSAGE",
    "You are a helpful assistant. "
    "You have access to conversation history and can maintain context across messages."
)

logger = logging.getLogger(__name__)


_encoding = tiktoken.get_encoding("cl100k_base")


def get_conversation_key(user_id: str, conversation_id: str) -> str:
    """Generate a unique key for a conversation."""
    return f"{user_id}:{conversation_id}"


def estimate_token_count(text: str) -> int:
    """Estimate token count using tiktoken, with fallback to character-
    based estimation."""
    if _encoding is not None:
        try:
            return len(_encoding.encode(text))
        except Exception:
            pass
    # Fallback to rough character-based estimation
    return len(text) // 4


def strip_base64_content(content) -> str:
    """Strip base64-encoded images from message content.

    Handles both string content and multi-part content with image_url.
    Returns plain text content only.
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
        msg_tokens = estimate_token_count(text_content)

        if current_tokens + msg_tokens <= available_token_count:
            # Create a fresh plain dict to avoid thread lock issues with redis-memory
            # Use text-only content without base64 images
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


def handle_streaming(
    prompt_messages: list,
    providers_state: dict,
    timeout: float,
    max_tokens: int,
    conversation_id: str,
    user_id: str,
    message: str,
    conv_key: str,
    stream_format: str = STREAM_FORMAT_SSE,
):
    """Handle streaming agent chat requests.

    Args:
        stream_format: "sse" for Server-Sent Events (OpenAI-compatible),
                      "ndjson" for newline-delimited JSON (Ollama-style)

    Returns a StreamingResponse. After streaming completes,
    stores the full response in conversation memory.
    """
    created = int(time.time())

    async def generate_chunks():
        """Generate streaming chunks in the requested format."""
        full_content = []

        try:
            async for chunk in call_llm_by_model_streaming(
                messages=prompt_messages,
                providers_state=providers_state,
                model=None,  # Use default provider
                timeout=timeout,
                max_tokens=max_tokens,
            ):
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
            logger.error(f"Streaming error in agent chat: {e}")
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


# TODO: Completely get rid of this and stop support for non-streaming.
async def handler(request: dict, providers_state: dict):
    """Agent chat endpoint with stateful conversation memory.

    Features:
    - User and conversation ID based isolation
    - Redis-backed conversation memory
    - Automatic context window management
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
    message = request.get("message")
    conversation_id = request.get("conversation_id")
    user_id = request.get("user_id", "default-user")
    stream = request.get("stream", False)
    stream_format = request.get("stream_format", STREAM_FORMAT_SSE)
    timeout = request.get("timeout")
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
        raise HTTPException(
            status_code=503, detail="No default provider available"
        )

    max_context_window = get_provider_context_window(
        providers_state, default_provider
    )

    # Use default if context window not available
    if max_context_window is None:
        max_context_window = 4096

    # TODO: Refactor this to add user, make sure that there are some reserved usernames, __admin and __default
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
        dsl_result = load_prompt_dsl(
            input_text=message,
            message_history=messages,
            default_system_message=DEFAULT_SYSTEM_MESSAGE,
        )

        logger.info(f"Agent chat: DSL result present: {dsl_result is not None}")

        # Apply DSL customizations if available
        if dsl_result:
            # Override system message from docstring
            system_message = dsl_result.system_message or DEFAULT_SYSTEM_MESSAGE
            logger.info(f"Agent chat: Using DSL system message: {system_message[:100]}...")

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
            logger.info(f"Agent chat: Using default system message: {system_message[:100]}...")

        # Fit messages to context window
        fitted_history = fit_messages_to_context(
            messages, max_context_window, system_message
        )

        # Build prompt with system message
        prompt_messages = [{"role": "system", "content": system_message}]
        prompt_messages.extend(fitted_history)

        # Add current user message(s) to prompt
        user_msg = {"role": "user", "content": user_message_content}
        prompt_messages.append(user_msg)

        # Add any extra user messages from DSL (multiple prints)
        for extra_msg in extra_user_messages:
            prompt_messages.append({"role": "user", "content": extra_msg})

        logger.info(f"Agent chat: Prompt messages count: {len(prompt_messages)}")
        logger.info(f"Agent chat: System message in prompt: {prompt_messages[0]['content'][:100] if prompt_messages else 'N/A'}...")

        # Handle streaming if requested
        if stream:
            return handle_streaming(
                prompt_messages=prompt_messages,
                providers_state=providers_state,
                timeout=timeout,
                max_tokens=max_tokens,
                conversation_id=conversation_id,
                user_id=user_id,
                message=message,
                conv_key=conv_key,
                stream_format=stream_format,
            )

        # Call LLM with default provider
        logger.info(f"Agent chat: Calling LLM with {len(prompt_messages)} messages")
        logger.info(f"Agent chat: First message (system): {prompt_messages[0] if prompt_messages else 'N/A'}")
        try:
            response = call_llm_by_model(
                messages=prompt_messages,
                providers_state=providers_state,
                model=None,  # Use default provider
                timeout=timeout,
                max_tokens=max_tokens,
            )
        except litellm.Timeout as e:
            raise HTTPException(
                status_code=408,
                detail=f"Request timeout: The LLM provider did not respond within the specified timeout period. {str(e)}",
            )
        except litellm.APIConnectionError as e:
            # Check if this is a timeout error wrapped in APIConnectionError
            error_msg = str(e).lower()
            if "timeout" in error_msg or "timed out" in error_msg:
                raise HTTPException(
                    status_code=408,
                    detail=f"Request timeout: The LLM provider did not respond within the specified timeout period. {str(e)}",
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
    "description": "Send a message to an agent with stateful conversation memory. The server manages conversation history and context automatically.",
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
                            "description": "Conversation identifier (optional, will be generated if not provided)",
                        },
                        "user_id": {
                            "type": "string",
                            "description": "User identifier for isolation (optional, defaults to 'default-user')",
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
                            "description": "Streaming format: 'sse' for Server-Sent Events (OpenAI-compatible), 'ndjson' for newline-delimited JSON (Ollama-style)",
                        },
                        "timeout": {
                            "type": "number",
                            "minimum": 0,
                            "description": "Request timeout in seconds. Overrides the provider's default timeout if specified.",
                        },
                        "max_tokens": {
                            "type": "integer",
                            "minimum": 1,
                            "description": "Maximum number of tokens to generate in the response.",
                        },
                    },
                    "required": ["message"],
                },
                "example": {
                    "message": "What's the weather?",
                    "conversation_id": "conv-123",
                    "user_id": "user-456",
                    "stream": False,
                    "stream_format": "sse",
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
                                "description": "Unique identifier for the conversation",
                            },
                            "user_id": {
                                "type": "string",
                                "description": "User identifier for conversation isolation",
                            },
                            "message": {
                                "type": "string",
                                "description": "The assistant's response message",
                            },
                            "role": {
                                "type": "string",
                                "description": "Message role (always 'assistant' for responses)",
                            },
                            "created": {
                                "type": "integer",
                                "description": "Unix timestamp when the response was created",
                            },
                            "usage": {
                                "type": "object",
                                "description": "Token usage statistics for the request",
                                "properties": {
                                    "prompt_tokens": {
                                        "type": "integer",
                                        "description": "Number of tokens in the prompt",
                                    },
                                    "completion_tokens": {
                                        "type": "integer",
                                        "description": "Number of tokens in the completion",
                                    },
                                    "total_tokens": {
                                        "type": "integer",
                                        "description": "Total number of tokens used",
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
                        "conversation_id": "conv-123",
                        "user_id": "user-456",
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
            "description": "Request timeout - the LLM provider did not respond within the specified timeout period"
        },
        422: {"description": "Validation error"},
        503: {"description": "Service unavailable - no provider available"},
    },
}
