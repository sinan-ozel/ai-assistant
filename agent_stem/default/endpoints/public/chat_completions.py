"""Chat completions endpoint - OpenAI-compatible API."""

from jsonschema import validate, ValidationError
from fastapi import HTTPException


async def handler(request: dict, providers_state: dict):
    """
    Create a chat completion (OpenAI-compatible API).

    This endpoint follows the OpenAI Chat Completion API format,
    making it compatible with most LLM clients and tools.
    """
    # Validate request against schema
    try:
        validate(instance=request, schema=spec["requestBody"]["content"]["application/json"]["schema"])
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))

    # Access request fields as dict keys
    model = request.get("model")
    messages = request.get("messages", [])

    # Dummy response for now - implementation coming later
    return {
        "id": "chatcmpl-dummy123",
        "object": "chat.completion",
        "created": 1734700000,
        "model": model,
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "This is a dummy response. Implementation coming soon."
                },
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": 10,
            "completion_tokens": 10,
            "total_tokens": 20
        }
    }


spec = {
    "path": "/v1/chat/completions",
    "methods": ["POST"],
    "summary": "Create chat completion",
    "description": "Creates a model response for the given chat conversation. Compatible with OpenAI's Chat Completion API format.",
    "requestBody": {
        "required": True,
        "content": {
            "application/json": {
                "schema": {
                    "type": "object",
                    "properties": {
                        "model": {
                            "type": "string",
                            "description": "ID of the model to use for completion"
                        },
                        "messages": {
                            "type": "array",
                            "description": "List of messages in the conversation",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "role": {
                                        "type": "string",
                                        "enum": ["system", "user", "assistant"],
                                        "description": "Role of the message author"
                                    },
                                    "content": {
                                        "type": "string",
                                        "description": "Human-readable text content of the message"
                                    }
                                },
                                "required": ["role", "content"]
                            },
                            "minItems": 1
                        },
                        "temperature": {
                            "type": "number",
                            "minimum": 0.0,
                            "maximum": 2.0,
                            "default": 1.0,
                            "description": "Sampling temperature. Higher values make output more random, lower values more deterministic"
                        },
                        "max_tokens": {
                            "type": "integer",
                            "minimum": 1,
                            "description": "Maximum number of tokens to generate in the completion"
                        },
                        "stream": {
                            "type": "boolean",
                            "default": False,
                            "description": "Whether to stream the response incrementally"
                        },
                        "top_p": {
                            "type": "number",
                            "minimum": 0.0,
                            "maximum": 1.0,
                            "default": 1.0,
                            "description": "Nucleus sampling parameter. Alternative to temperature"
                        },
                        "stop": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Up to 4 sequences where the API will stop generating tokens"
                        }
                    },
                    "required": ["model", "messages"]
                },
                "example": {
                    "model": "pixtral",
                    "messages": [
                        {"role": "user", "content": "What is the capital of France?"}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 100
                }
            }
        }
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
                                "description": "Unique identifier for the completion"
                            },
                            "object": {
                                "type": "string",
                                "description": "Object type, always 'chat.completion'"
                            },
                            "created": {
                                "type": "integer",
                                "description": "Unix timestamp of when the completion was created"
                            },
                            "model": {
                                "type": "string",
                                "description": "The model used for completion"
                            },
                            "choices": {
                                "type": "array",
                                "description": "List of completion choices",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "index": {
                                            "type": "integer",
                                            "description": "Choice index"
                                        },
                                        "message": {
                                            "type": "object",
                                            "description": "The generated message",
                                            "properties": {
                                                "role": {
                                                    "type": "string",
                                                    "description": "Role of the message author"
                                                },
                                                "content": {
                                                    "type": "string",
                                                    "description": "Content of the message"
                                                }
                                            }
                                        },
                                        "finish_reason": {
                                            "type": "string",
                                            "description": "Reason for completion finish (stop, length, etc.)"
                                        }
                                    }
                                }
                            },
                            "usage": {
                                "type": "object",
                                "description": "Token usage statistics",
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
                                        "description": "Total tokens used"
                                    }
                                }
                            }
                        },
                        "required": ["id", "object", "created", "model", "choices"]
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
                                    "content": "Hello! How can I help you today?"
                                },
                                "finish_reason": "stop"
                            }
                        ],
                        "usage": {
                            "prompt_tokens": 20,
                            "completion_tokens": 10,
                            "total_tokens": 30
                        }
                    }
                }
            }
        },
        400: {
            "description": "Bad request - invalid parameters"
        },
        404: {
            "description": "Model not found or not available"
        }
    }
}
