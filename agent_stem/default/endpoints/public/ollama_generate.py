"""Ollama generate endpoint - Ollama-native API."""

from typing import Optional, List
from pydantic import BaseModel, Field



class OllamaGenerateRequest(BaseModel):
    """Request body for Ollama generate."""
    model: str = Field(..., description="Model name to use")
    prompt: str = Field(..., description="The prompt to generate completion for")
    stream: Optional[bool] = Field(False, description="Whether to stream the response")
    temperature: Optional[float] = Field(0.8, description="Temperature for sampling")
    top_p: Optional[float] = Field(0.9, description="Top-p sampling parameter")
    top_k: Optional[int] = Field(40, description="Top-k sampling parameter")


async def handler(request: OllamaGenerateRequest, providers_state: dict):
    """
    Generate completion using Ollama format.

    This endpoint follows the Ollama Generate API format,
    making it compatible with Ollama clients and LiteLLM when using ollama/ prefix.
    """
    # Dummy response for now - implementation coming later
    return {
        "model": request.model,
        "created_at": "2024-12-20T00:00:00.000000Z",
        "response": "This is a dummy response. Implementation coming soon.",
        "done": True,
        "context": [1, 2, 3],
        "total_duration": 1000000000,
        "load_duration": 500000000,
        "prompt_eval_count": 10,
        "prompt_eval_duration": 200000000,
        "eval_count": 10,
        "eval_duration": 300000000
    }


spec = {
    "path": "/v1/api/generate",
    "methods": ["POST"],
    "summary": "Generate completion (Ollama format)",
    "description": "Generates a completion for a prompt using Ollama's native API format. Compatible with Ollama clients.",
    "requestBody": {
        "required": True,
        "content": {
            "application/json": {
                "schema": {
                    "type": "object",
                    "properties": {
                        "model": {
                            "type": "string",
                            "description": "Name of the model to use for generation"
                        },
                        "prompt": {
                            "type": "string",
                            "description": "Human-readable text prompt to generate a completion for"
                        },
                        "stream": {
                            "type": "boolean",
                            "default": False,
                            "description": "Whether to stream the response incrementally"
                        },
                        "temperature": {
                            "type": "number",
                            "minimum": 0.0,
                            "maximum": 2.0,
                            "default": 0.8,
                            "description": "Temperature for sampling. Higher values increase randomness"
                        },
                        "top_p": {
                            "type": "number",
                            "minimum": 0.0,
                            "maximum": 1.0,
                            "default": 0.9,
                            "description": "Top-p (nucleus) sampling parameter"
                        },
                        "top_k": {
                            "type": "integer",
                            "minimum": 1,
                            "default": 40,
                            "description": "Top-k sampling parameter. Limits to top k tokens"
                        }
                    },
                    "required": ["model", "prompt"]
                },
                "example": {
                    "model": "gemma3:4b",
                    "prompt": "What is the capital of France?",
                    "stream": False,
                    "temperature": 0.7
                }
            }
        }
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
                                "description": "The model used"
                            },
                            "created_at": {
                                "type": "string",
                                "description": "Timestamp of creation"
                            },
                            "response": {
                                "type": "string",
                                "description": "The generated text"
                            },
                            "done": {
                                "type": "boolean",
                                "description": "Whether generation is complete"
                            },
                            "context": {
                                "type": "array",
                                "description": "Context tokens",
                                "items": {"type": "integer"}
                            },
                            "total_duration": {
                                "type": "integer",
                                "description": "Total duration in nanoseconds"
                            },
                            "load_duration": {
                                "type": "integer",
                                "description": "Model load duration in nanoseconds"
                            },
                            "prompt_eval_count": {
                                "type": "integer",
                                "description": "Number of tokens in the prompt"
                            },
                            "prompt_eval_duration": {
                                "type": "integer",
                                "description": "Prompt evaluation duration in nanoseconds"
                            },
                            "eval_count": {
                                "type": "integer",
                                "description": "Number of tokens generated"
                            },
                            "eval_duration": {
                                "type": "integer",
                                "description": "Generation duration in nanoseconds"
                            }
                        },
                        "required": ["model", "created_at", "response", "done"]
                    },
                    "example": {
                        "model": "gemma3:4b",
                        "created_at": "2024-12-20T00:00:00.000000Z",
                        "response": "The capital of France is Paris.",
                        "done": True,
                        "context": [1, 2, 3],
                        "total_duration": 1000000000,
                        "load_duration": 500000000,
                        "prompt_eval_count": 10,
                        "prompt_eval_duration": 200000000,
                        "eval_count": 10,
                        "eval_duration": 300000000
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
