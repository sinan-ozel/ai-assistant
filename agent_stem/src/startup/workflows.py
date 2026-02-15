"""Workflow discovery and dynamic endpoint registration module.

Discovers YAML workflow definitions and creates dynamic endpoints based
on them. Workflows are LLM-focused tools with standardized input
(messages) and typed outputs.
"""

import base64
import json
import logging
from io import BytesIO
from pathlib import Path
from typing import Any, Dict

import litellm
import yaml
from common.llm import call_llm_by_model
from fastapi import HTTPException
from jsonschema import ValidationError, validate
from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger(__name__)

# Default workflows directory (can be overridden)
DEFAULT_WORKFLOWS_DIR = Path("/app/cortex/workflows")


def generate_example_image() -> str:
    """Generate a base64-encoded example image for API documentation.

    Creates a 256x32 white box with "this is an image" text.

    Returns:
        Base64-encoded JPEG image string
    """
    # Create a white 256x32 image
    img = Image.new("RGB", (256, 32), color="white")
    draw = ImageDraw.Draw(img)

    # Use a font with 24px height
    font = ImageFont.truetype(
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24
    )

    text = "this is an image"
    # Get text bounding box for centering
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    position = ((256 - text_width) // 2, (32 - text_height) // 2)
    draw.text(position, text, fill="black", font=font)

    # Convert to base64
    buffer = BytesIO()
    img.save(buffer, format="JPEG")
    buffer.seek(0)
    return base64.b64encode(buffer.read()).decode("utf-8")


def example_from_schema(schema: Dict[str, Any]) -> Any:
    """Generate a concrete example value from a JSON schema.

    Args:
        schema: JSON schema dictionary

    Returns:
        An example value matching the schema or a reasonable fallback.
    """
    if schema is None:
        return None
    if "example" in schema:
        return schema["example"]
    t = schema.get("type")
    if t == "string":
        return "example"
    if t == "integer":
        return 0
    if t == "number":
        return 0.0
    if t == "boolean":
        return False
    if t == "array":
        items = schema.get("items") or {}
        return [example_from_schema(items)]
    if t == "object":
        props = schema.get("properties") or {}
        example_obj: Dict[str, Any] = {}
        for k, v in props.items():
            example_obj[k] = example_from_schema(v)
        return example_obj
    # Fallback
    return None


def json_schema_to_prompt_format(schema: Dict[str, Any]) -> str:
    """Convert JSON schema to a formatted prompt instruction.

    Args:
        schema: JSON schema dictionary

    Returns:
        Formatted string for inclusion in system prompt
    """
    if schema.get("type") == "string":
        return "Return your response as a plain string with no additional formatting."

    # For object schemas, provide a concrete example JSON matching the schema
    example = example_from_schema(schema)
    try:
        example_json = json.dumps(example, indent=2)
    except Exception:
        example_json = json.dumps({}, indent=2)

    return f"""Use this exact format for your response:

```json
{example_json}
```

Return ONLY valid JSON matching this schema, with no additional text or markdown formatting."""


def load_workflow_yaml(workflow_file: Path) -> Dict[str, Any]:
    """Load and validate a workflow YAML file.

    Args:
        workflow_file: Path to workflow YAML file

    Returns:
        Parsed workflow configuration dictionary

    Raises:
        ValueError: If workflow file is invalid
    """
    try:
        with open(workflow_file, "r") as f:
            workflow = yaml.safe_load(f)

        # Validate required fields
        required_fields = ["name", "path", "description", "output_schema"]
        for field in required_fields:
            if field not in workflow:
                raise ValueError(f"Missing required field: {field}")

        # Validate execution section or legacy prompt field
        if "execution" in workflow:
            exec_section = workflow["execution"]
            if "type" not in exec_section:
                raise ValueError("execution section must have 'type' field")

            exec_type = exec_section["type"]
            if exec_type == "prompt" and "prompt" not in exec_section:
                raise ValueError(
                    "prompt execution type requires 'prompt' field"
                )
            elif exec_type == "python" and "python" not in exec_section:
                raise ValueError(
                    "python execution type requires 'python' field"
                )
        elif "prompt" not in workflow:
            # Legacy format check - allow root-level prompt for backwards compatibility
            raise ValueError(
                "Workflow must have 'execution' section or legacy 'prompt' field"
            )

        return workflow

    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML: {e}")
    except Exception as e:
        raise ValueError(f"Failed to load workflow: {e}")


async def create_workflow_handler(workflow: Dict[str, Any]):
    """Create a dynamic handler function for a workflow.

    Args:
        workflow: Workflow configuration dictionary

    Returns:
        Async handler function
    """
    workflow_name = workflow["name"]
    output_schema = workflow["output_schema"]
    provider_name = workflow.get("provider")

    # Get prompt from execution section or legacy root-level field
    if "execution" in workflow:
        exec_section = workflow["execution"]
        exec_type = exec_section["type"]

        if exec_type == "prompt":
            base_prompt = exec_section["prompt"]
        elif exec_type == "python":
            # Python execution not yet implemented
            raise NotImplementedError(
                f"Python execution not yet supported for workflow: {workflow_name}"
            )
        else:
            raise ValueError(f"Unknown execution type: {exec_type}")
    else:
        # Legacy format - prompt at root level
        base_prompt = workflow["prompt"]

    # Build system message with prompt + output schema instructions
    schema_instructions = json_schema_to_prompt_format(output_schema)
    system_message = f"{base_prompt.strip()}\n\n{schema_instructions}"

    async def handler(request: dict, providers_state: dict):
        """Dynamic workflow handler.

        Accepts standardized input (messages, model, etc.) and returns
        typed output.
        """
        # Extract request parameters (same as /v1/agent/chat input)
        messages = request.get("messages", [])
        model = request.get("model")  # Accepted but may be ignored
        temperature = request.get("temperature", 0.7)
        max_tokens = request.get("max_tokens", 4096)
        stream = request.get("stream", False)

        # Validate input
        if not messages or len(messages) == 0:
            raise HTTPException(
                status_code=422, detail="messages array cannot be empty"
            )

        # Streaming not supported
        if stream:
            raise HTTPException(
                status_code=501, detail="Streaming not supported for workflows"
            )

        # Build messages for LLM
        prompt_messages = [{"role": "system", "content": system_message}]

        # Add user messages from request
        prompt_messages.extend(messages)

        # Determine which provider to use
        # Priority: workflow-specified provider > request model > default provider
        provider_to_use = None

        if provider_name:
            # Use provider specified in workflow YAML
            provider_to_use = provider_name
        elif model:
            # Use model from request (though we accept it, we may override)
            provider_to_use = model

        # Call LLM
        try:
            # For object schemas, force JSON mode to suppress reasoning content
            llm_kwargs = {
                "messages": prompt_messages,
                "providers_state": providers_state,
                "model": provider_to_use,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }

            if output_schema.get("type") == "object":
                llm_kwargs["response_format"] = {"type": "json_object"}

            response = call_llm_by_model(**llm_kwargs)
        except litellm.RateLimitError as e:
            logger.warning(
                f"Rate limit exceeded for workflow {workflow_name}: {e}"
            )
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded. Please try again later.",
            )
        except litellm.Timeout as e:
            logger.warning(f"Timeout for workflow {workflow_name}: {e}")
            raise HTTPException(
                status_code=408,
                detail=f"Request timeout: The LLM provider did not respond within the specified timeout period. {str(e)}",
            )
        except litellm.APIConnectionError as e:
            # Check if this is a timeout error wrapped in APIConnectionError
            error_msg = str(e).lower()
            if "timeout" in error_msg or "timed out" in error_msg:
                logger.warning(f"Timeout for workflow {workflow_name}: {e}")
                raise HTTPException(
                    status_code=408,
                    detail=f"Request timeout: The LLM provider did not respond within the specified timeout period. {str(e)}",
                )
            # Otherwise, it's a different error
            logger.error(f"LLM call failed for workflow {workflow_name}: {e}")
            raise HTTPException(
                status_code=500, detail=f"LLM call failed: {str(e)}"
            )
        except litellm.InternalServerError as e:
            # Log the error and crash to expose the issue
            logger.error(
                f"InternalServerError from LLM provider in workflow {workflow_name}: {e}"
            )
            raise
        except Exception as e:
            logger.error(f"LLM call failed for workflow {workflow_name}: {e}")
            raise HTTPException(
                status_code=500, detail=f"LLM call failed: {str(e)}"
            )

        # Extract response content
        choice = response.choices[0]
        content = choice.message.content
        # Check for empty content
        # if not content or content.strip() == "":
        #     logger.error(f"LLM returned empty content for workflow {workflow_name}")
        #     logger.error(f"Response choice: {choice}")
        #     raise HTTPException(
        #         status_code=500,
        #         detail="LLM returned empty response. This may indicate the model does not support the requested operation (e.g., image processing without vision capabilities)."
        #     )
        # For string schemas, return as-is
        if output_schema.get("type") == "string":
            return {
                "result": content,
                "usage": {
                    "prompt_tokens": (
                        response.usage.prompt_tokens if response.usage else 0
                    ),
                    "completion_tokens": (
                        response.usage.completion_tokens
                        if response.usage
                        else 0
                    ),
                    "total_tokens": (
                        response.usage.total_tokens if response.usage else 0
                    ),
                },
            }

        # For object schemas, parse JSON and validate
        try:
            # Try to extract JSON from markdown code blocks if present
            if "```json" in content:
                json_start = content.find("```json") + 7
                json_end = content.find("```", json_start)
                if json_end > json_start:
                    content = content[json_start:json_end].strip()
            elif "```" in content:
                # Handle plain code blocks
                json_start = content.find("```") + 3
                json_end = content.find("```", json_start)
                if json_end > json_start:
                    content = content[json_start:json_end].strip()

            result = json.loads(content)

            # Validate against schema
            validate(instance=result, schema=output_schema)

            return {
                "result": result,
                "usage": {
                    "prompt_tokens": (
                        response.usage.prompt_tokens if response.usage else 0
                    ),
                    "completion_tokens": (
                        response.usage.completion_tokens
                        if response.usage
                        else 0
                    ),
                    "total_tokens": (
                        response.usage.total_tokens if response.usage else 0
                    ),
                },
            }

        except json.JSONDecodeError as e:
            logger.error(
                f"Failed to parse JSON response for workflow {workflow_name}: {e}"
            )
            logger.error(f"Raw content: {content}")
            raise HTTPException(
                status_code=500, detail=f"LLM returned invalid JSON: {str(e)}"
            )
        except ValidationError as e:
            logger.error(
                f"Response validation failed for workflow {workflow_name}: {e}"
            )
            raise HTTPException(
                status_code=500,
                detail=f"LLM response does not match schema: {str(e)}",
            )

    return handler


def create_workflow_spec(workflow: Dict[str, Any]) -> Dict[str, Any]:
    """Create OpenAPI spec for a workflow endpoint.

    Args:
        workflow: Workflow configuration dictionary

    Returns:
        OpenAPI specification dictionary
    """
    path = workflow["path"]
    description = workflow["description"]
    output_schema = workflow["output_schema"]
    input_requirements = workflow.get("input_requirements", {})
    content_types = input_requirements.get("content_types", ["text"])
    input_desc = input_requirements.get("description", "")

    # Enhance description with input requirements
    full_description = description
    if input_desc:
        full_description = (
            f"{description}\n\n**Input Requirements:** {input_desc}"
        )

    # Build response schema
    if output_schema.get("type") == "string":
        response_schema = {
            "type": "object",
            "properties": {
                "result": {
                    "type": "string",
                    "description": "The workflow result as a string",
                },
                "usage": {
                    "type": "object",
                    "description": "Token usage statistics",
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
        }
    else:
        # Add description to output_schema if it doesn't have one
        result_schema = output_schema.copy()
        if "description" not in result_schema:
            result_schema["description"] = "The workflow result"

        response_schema = {
            "type": "object",
            "properties": {
                "result": result_schema,
                "usage": {
                    "type": "object",
                    "description": "Token usage statistics",
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
        }

    # Standard input schema (based on /v1/agent/chat)
    request_schema = {
        "type": "object",
        "properties": {
            "messages": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "role": {
                            "type": "string",
                            "enum": ["user", "assistant", "system"],
                            "description": "Role of the message sender",
                        },
                        "content": {
                            "description": "Message content (text or multimodal)",
                            "oneOf": [
                                {
                                    "type": "string",
                                    "description": "Text content",
                                },
                                {
                                    "type": "array",
                                    "description": "Multimodal content with text and/or images",
                                    "items": {
                                        "type": "object",
                                        "description": "Content part (text or image)",
                                    },
                                },
                            ],
                        },
                    },
                    "required": ["role", "content"],
                },
                "description": "Array of message objects with role and content",
            },
            "model": {
                "type": "string",
                "description": "Model name (optional, may be overridden by workflow configuration)",
            },
            "temperature": {
                "type": "number",
                "minimum": 0,
                "maximum": 2,
                "default": 0.7,
                "description": "Sampling temperature",
            },
            "max_tokens": {
                "type": "integer",
                "minimum": 1,
                "default": 4096,
                "description": "Maximum tokens to generate",
            },
        },
        "required": ["messages"],
    }

    spec = {
        "path": path,
        "methods": ["POST"],
        "summary": workflow["name"],
        "description": full_description,
        "requestBody": {
            "required": True,
            "content": {
                "application/json": {
                    "schema": request_schema,
                    "example": None,  # Will be set below based on input requirements
                }
            },
        },
        "responses": {
            "200": {
                "description": "Successful response",
                "content": {"application/json": {"schema": response_schema}},
            },
            "422": {
                "description": "Validation error (e.g., empty messages array)",
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "properties": {
                                "detail": {
                                    "type": "string",
                                    "description": "Error message describing the validation failure",
                                }
                            },
                        }
                    }
                },
            },
            "429": {
                "description": "Rate limit exceeded",
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "properties": {
                                "detail": {
                                    "type": "string",
                                    "description": "Error message indicating rate limit was exceeded",
                                }
                            },
                        }
                    }
                },
            },
            "501": {
                "description": "Not implemented (e.g., streaming not supported)",
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "properties": {
                                "detail": {
                                    "type": "string",
                                    "description": "Error message indicating the feature is not implemented",
                                }
                            },
                        }
                    }
                },
            },
        },
    }

    # Add a generated example to the successful response so contract
    # validators have a concrete 200/201 example to check against.
    # Re-use the top-level example helper
    def _example_from_schema(schema: Dict[str, Any]) -> Any:
        return example_from_schema(schema)

    # Build response example
    usage_example = {
        "prompt_tokens": 0,
        "completion_tokens": 0,
        "total_tokens": 0,
    }

    if output_schema.get("type") == "string":
        response_example = {"result": "example", "usage": usage_example}
    else:
        response_example = {
            "result": _example_from_schema(output_schema),
            "usage": usage_example,
        }

    # Insert the example into the spec
    spec["responses"]["200"]["content"]["application/json"][
        "example"
    ] = response_example

    # Generate appropriate request example based on input requirements
    if "image" in content_types:
        # Image input example - generate actual example image
        example_image_base64 = generate_example_image()
        request_example = {
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{example_image_base64}"
                            },
                        }
                    ],
                }
            ],
            "temperature": 0.7,
            "max_tokens": 4096,
        }
    else:
        # Text input example
        request_example = {
            "messages": [{"role": "user", "content": "Your message here"}],
            "temperature": 0.7,
            "max_tokens": 4096,
        }

    spec["requestBody"]["content"]["application/json"][
        "example"
    ] = request_example

    return spec


async def discover_workflows(workflows_dir: Path = DEFAULT_WORKFLOWS_DIR):
    """Discover and load all workflow YAML files.

    Args:
        workflows_dir: Directory containing workflow YAML files

    Yields:
        Tuples of (workflow_name, handler, spec)
    """
    if not workflows_dir.exists():
        logger.warning(f"Workflows directory not found: {workflows_dir}")
        return

    for workflow_file in sorted(workflows_dir.rglob("*.yaml")):
        if workflow_file.name.startswith("_"):
            continue

        try:
            logger.info(
                f"Loading workflow: {workflow_file.relative_to(workflows_dir)}"
            )
            workflow = load_workflow_yaml(workflow_file)

            # Create handler and spec
            handler = await create_workflow_handler(workflow)
            spec = create_workflow_spec(workflow)

            yield workflow["name"], handler, spec

        except Exception as e:
            logger.error(f"Failed to load workflow {workflow_file.name}: {e}")
            # Don't raise - continue loading other workflows
            continue
