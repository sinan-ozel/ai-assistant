"""Agent chat endpoint with stateful conversation memory."""

import time
import uuid
from jsonschema import validate, ValidationError
from fastapi import HTTPException
from redis_memory import ConversationMemory
import litellm

from common.llm import call_llm_by_model
from situational.awareness import get_provider_context_window


# Default system message
DEFAULT_SYSTEM_MESSAGE = (
    "You are a helpful assistant. "
    "You have access to conversation history and can maintain context across messages."
)

# Initialize tiktoken encoding
try:
    import tiktoken
    _encoding = tiktoken.get_encoding("cl100k_base")
except Exception:
    _encoding = None


def get_conversation_key(user_id: str, conversation_id: str) -> str:
    """Generate a unique key for a conversation."""
    return f"{user_id}:{conversation_id}"


def estimate_token_count(text: str) -> int:
    """Estimate token count using tiktoken, with fallback to character-based estimation."""
    if _encoding is not None:
        try:
            return len(_encoding.encode(text))
        except Exception:
            pass
    # Fallback to rough character-based estimation
    return len(text) // 4


def strip_base64_content(content) -> str:
    """
    Strip base64-encoded images from message content.

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
    """
    Fit messages into context window, keeping most recent messages.

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
    available_token_count = max_context_token_count - system_token_count - response_buffer

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
            plain_msg = {
                "role": message.get("role"),
                "content": text_content
            }
            fitted_messages.insert(0, plain_msg)
            current_tokens += msg_tokens
        else:
            # Can't fit more messages
            break

    return fitted_messages


async def handler(request: dict, providers_state: dict):
    """
    Agent chat endpoint with stateful conversation memory.

    Features:
    - User and conversation ID based isolation
    - Redis-backed conversation memory
    - Automatic context window management
    """
    # Validate request against schema
    try:
        validate(instance=request, schema=spec["requestBody"]["content"]["application/json"]["schema"])
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))

    # Extract request parameters
    message = request.get("message")
    conversation_id = request.get("conversation_id")
    user_id = request.get("user_id", "default-user")
    stream = request.get("stream", False)
    timeout = request.get("timeout")
    max_tokens = request.get("max_tokens")

    # Validate required fields
    if not message:
        raise HTTPException(status_code=400, detail="Message is required")

    if not isinstance(message, str):
        raise HTTPException(status_code=400, detail="Message must be a string")

    if len(message.strip()) == 0:
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    # System message is not customizable per request
    system_message = DEFAULT_SYSTEM_MESSAGE

    # Streaming not supported
    if stream:
        raise HTTPException(status_code=501, detail="Streaming not yet implemented")

    # Generate conversation_id if not provided
    if not conversation_id:
        conversation_id = str(uuid.uuid4())

    # Get default provider and its context window
    default_provider = providers_state.get("default_provider")
    if not default_provider:
        raise HTTPException(
            status_code=503,
            detail="No default provider available"
        )

    max_context_window = get_provider_context_window(
        providers_state,
        default_provider
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

        # Fit messages to context window
        fitted_history = fit_messages_to_context(
            messages,
            max_context_window,
            system_message
        )

        # Build prompt with system message
        prompt_messages = [{"role": "system", "content": system_message}]
        prompt_messages.extend(fitted_history)

        # Add current user message to prompt
        user_msg = {"role": "user", "content": message}
        prompt_messages.append(user_msg)

        # Call LLM with default provider
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
                detail=f"Request timeout: The LLM provider did not respond within the specified timeout period. {str(e)}"
            )
        except litellm.APIConnectionError as e:
            # Check if this is a timeout error wrapped in APIConnectionError
            error_msg = str(e).lower()
            if "timeout" in error_msg or "timed out" in error_msg:
                raise HTTPException(
                    status_code=408,
                    detail=f"Request timeout: The LLM provider did not respond within the specified timeout period. {str(e)}"
                )
            # Otherwise, re-raise to be handled by outer exception handler
            raise
        except litellm.InternalServerError as e:
            # Log the error and crash to expose the issue
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"InternalServerError from LLM provider in agent chat: {e}")
            raise

        # Extract response
        choice = response.choices[0]
        assistant_message = choice.message.content

        # Store user message and assistant response in memory
        # Use redis-memory's append() which handles persistence
        memory.messages.append({"role": "user", "content": message})
        memory.messages.append({"role": "assistant", "content": assistant_message})

        # Build response
        return {
            "conversation_id": conversation_id,
            "user_id": user_id,
            "message": assistant_message,
            "role": "assistant",
            "created": int(time.time()),
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                "total_tokens": response.usage.total_tokens if response.usage else 0,
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
                            "description": "The message to send to the agent"
                        },
                        "conversation_id": {
                            "type": "string",
                            "description": "Conversation identifier (optional, will be generated if not provided)"
                        },
                        "user_id": {
                            "type": "string",
                            "description": "User identifier for isolation (optional, defaults to 'default-user')"
                        },
                        "stream": {
                            "type": "boolean",
                            "description": "Whether to stream the response (not yet supported)",
                            "default": False
                        },
                        "timeout": {
                            "type": "number",
                            "minimum": 0,
                            "description": "Request timeout in seconds. Overrides the provider's default timeout if specified."
                        },
                        "max_tokens": {
                            "type": "integer",
                            "minimum": 1,
                            "description": "Maximum number of tokens to generate in the response."
                        }
                    },
                    "required": ["message"]
                },
                "example": {
                    "message": "What's the weather?",
                    "conversation_id": "conv-123",
                    "user_id": "user-456",
                    "stream": False
                }
            }
        }
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
                                "description": "Unique identifier for the conversation"
                            },
                            "user_id": {
                                "type": "string",
                                "description": "User identifier for conversation isolation"
                            },
                            "message": {
                                "type": "string",
                                "description": "The assistant's response message"
                            },
                            "role": {
                                "type": "string",
                                "description": "Message role (always 'assistant' for responses)"
                            },
                            "created": {
                                "type": "integer",
                                "description": "Unix timestamp when the response was created"
                            },
                            "usage": {
                                "type": "object",
                                "description": "Token usage statistics for the request",
                                "properties": {
                                    "prompt_tokens": {
                                        "type": "integer",
                                        "description": "Number of tokens in the prompt"
                                    },
                                    "completion_tokens": {
                                        "type": "integer",
                                        "description": "Number of tokens in the completion"
                                    },
                                    "total_tokens": {
                                        "type": "integer",
                                        "description": "Total number of tokens used"
                                    }
                                }
                            }
                        },
                        "required": ["conversation_id", "message", "role", "created"]
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
                            "total_tokens": 87
                        }
                    }
                }
            }
        },
        400: {
            "description": "Bad request - invalid input"
        },
        408: {
            "description": "Request timeout - the LLM provider did not respond within the specified timeout period"
        },
        422: {
            "description": "Validation error"
        },
        501: {
            "description": "Feature not implemented (e.g., streaming)"
        },
        503: {
            "description": "Service unavailable - no provider available"
        }
    }
}
