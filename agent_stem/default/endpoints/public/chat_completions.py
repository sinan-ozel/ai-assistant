"""Chat completions endpoint - OpenAI-compatible API."""

import time
import uuid
from jsonschema import validate, ValidationError
from fastapi import HTTPException

from common.llm import call_llm_by_model


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

    # Extract request parameters
    model = request.get("model")
    messages = request.get("messages", [])
    temperature = request.get("temperature")
    max_tokens = request.get("max_tokens")
    top_p = request.get("top_p")
    stop = request.get("stop")
    stream = request.get("stream", False)

    if stream:
        raise HTTPException(status_code=501, detail="Streaming not yet implemented")

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
        )

        # Extract response data
        choice = response.choices[0]

        # Build OpenAI-format response
        return {
            "id": f"chatcmpl-{uuid.uuid4().hex[:24]}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": model or response.model,  # TODO: Consider model usage - if the model does not exist, are we using the default? Return the model that's actually used.
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
                "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                "total_tokens": response.usage.total_tokens if response.usage else 0,
            },
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except NotImplementedError as e:
        raise HTTPException(status_code=501, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM call failed: {str(e)}")


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
                        # "temperature": {
                        #     "type": "number",
                        #     "minimum": 0.0,
                        #     "maximum": 2.0,
                        #     "default": 1.0,
                        #     "description": "Sampling temperature. Higher values make output more random, lower values more deterministic"
                        # },
                        # "max_tokens": {
                        #     "type": "integer",
                        #     "minimum": 1,
                        #     "description": "Maximum number of tokens to generate in the completion"
                        # },
                        # "stream": {
                        #     "type": "boolean",
                        #     "default": False,
                        #     "description": "Whether to stream the response incrementally"
                        # },
                        # "top_p": {
                        #     "type": "number",
                        #     "exclusiveMinimum": 0.0,
                        #     "maximum": 1.0,
                        #     "default": 1.0,
                        #     "description": "Nucleus sampling parameter. Alternative to temperature. Must be in (0, 1]."
                        # },
                        # "stop": {
                        #     "type": "array",
                        #     "items": {"type": "string"},
                        #     "maxItems": 4,
                        #     "description": "Up to 4 sequences where the API will stop generating tokens"
                        # }
                    },
                    "required": ["messages"]
                },
                "example": {
                    # "model": "pixtral",
                    "messages": [
                        {"role": "user", "content": "What is the capital of France?"}
                    ],
                    # "temperature": 0.7,
                    # "max_tokens": 100
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
        },
        422: {
            "description": "Validation error - request does not match schema"
        },
        501: {
            "description": "Not implemented - streaming is not yet supported"
        }
    }
}
