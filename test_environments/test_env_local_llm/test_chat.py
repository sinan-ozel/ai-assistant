import json
import os

import litellm
import pytest
import requests

litellm.set_verbose = False
litellm.verbose = False
litellm.suppress_debug_info = True
litellm.log_raw_llm_output = False
litellm.drop_params = True


BASE_URL = os.getenv("BASE_URL", "http://app:8000")


@pytest.mark.depends(
    name="test_chat_completions_basic", on=["test_provider_context_window"]
)
def test_chat_completions_basic():
    """Test basic chat completion with a trivial question."""
    url = f"{BASE_URL}/v1/chat/completions"

    # Ask a trivial question
    payload = {
        "model": "ollama/gemma3:4b",
        "messages": [
            {
                "role": "user",
                "content": "What is 2+2? Answer with only the number.",
            }
        ],
        "temperature": 0.1,
        "max_tokens": 10,
    }

    response = requests.post(url, json=payload)
    assert (
        response.status_code == 200
    ), f"Expected 200, got {response.status_code}: {response.text}"

    data = response.json()

    # Verify response structure
    assert "id" in data
    assert "object" in data
    assert data["object"] == "chat.completion"
    assert "created" in data
    assert "model" in data
    assert "choices" in data
    assert len(data["choices"]) > 0

    # Verify choice structure
    choice = data["choices"][0]
    assert "index" in choice
    assert "message" in choice
    assert "role" in choice["message"]
    assert "content" in choice["message"]
    assert choice["message"]["role"] == "assistant"
    assert "finish_reason" in choice

    # Verify usage information
    assert "usage" in data
    assert "prompt_tokens" in data["usage"]
    assert "completion_tokens" in data["usage"]
    assert "total_tokens" in data["usage"]

    # Check that we got a response (even if dummy)
    content = choice["message"]["content"]
    assert content is not None
    assert len(content) > 0

    print(f"Response content: {content}")


@pytest.mark.depends(on=["test_chat_completions_basic"])
def test_chat_completions_litellm():
    """Test chat completion using LiteLLM client interface."""
    # Configure LiteLLM to use our custom OpenAI-compatible endpoint
    api_base = f"{BASE_URL}/v1"

    # Use litellm to make a completion request
    # Prefix with "openai/" to tell LiteLLM to use OpenAI-compatible format
    response = litellm.completion(
        model="ollama/gemma3:4b",
        messages=[
            {
                "role": "user",
                "content": "What is the capital of France? Answer with only the city name.",
            }
        ],
        api_base=api_base,
        temperature=0.1,
        max_tokens=10,
    )

    # Verify response structure (litellm returns a ModelResponse object)
    assert response is not None
    assert hasattr(response, "choices")
    assert len(response.choices) > 0

    choice = response.choices[0]
    assert hasattr(choice, "message")
    assert hasattr(choice.message, "content")
    assert hasattr(choice.message, "role")
    assert choice.message.role == "assistant"

    # Check that we got a response
    content = choice.message.content
    assert content is not None
    assert len(content) > 0

    print(f"LiteLLM response content: {content}")

    # Verify usage information
    assert hasattr(response, "usage")
    assert hasattr(response.usage, "prompt_tokens")
    assert hasattr(response.usage, "completion_tokens")
    assert hasattr(response.usage, "total_tokens")


@pytest.mark.depends(on=["test_chat_completions_basic"])
def test_chat_completions_streaming_sse():
    """Test streaming with SSE format (default)."""
    url = f"{BASE_URL}/v1/chat/completions"

    payload = {
        "model": "ollama/gemma3:4b",
        "messages": [
            {"role": "user", "content": "Say hello in exactly 3 words."}
        ],
        "stream": True,
        "stream_format": "sse",
        "max_tokens": 20,
    }

    response = requests.post(url, json=payload, stream=True)
    assert (
        response.status_code == 200
    ), f"Expected 200, got {response.status_code}: {response.text}"
    assert (
        response.headers.get("content-type")
        == "text/event-stream; charset=utf-8"
    )

    chunks = []
    content_parts = []
    done_received = False

    for line in response.iter_lines(decode_unicode=True):
        if line:
            if line.startswith("data: "):
                data = line[6:]  # Remove "data: " prefix
                if data == "[DONE]":
                    done_received = True
                else:
                    chunk = json.loads(data)
                    chunks.append(chunk)
                    # Extract content from delta
                    if "choices" in chunk and chunk["choices"]:
                        delta = chunk["choices"][0].get("delta", {})
                        if "content" in delta:
                            content_parts.append(delta["content"])

    assert len(chunks) > 0, "Expected at least one chunk"
    assert done_received, "Expected [DONE] message"

    # Verify chunk structure
    first_chunk = chunks[0]
    assert "id" in first_chunk
    assert "object" in first_chunk
    assert first_chunk["object"] == "chat.completion.chunk"
    assert "created" in first_chunk
    assert "choices" in first_chunk

    # Verify we got content
    full_content = "".join(content_parts)
    assert len(full_content) > 0, "Expected content in streaming response"
    print(f"SSE streaming content: {full_content}")


@pytest.mark.depends(on=["test_chat_completions_basic"])
def test_chat_completions_streaming_ndjson():
    """Test streaming with NDJSON format."""
    url = f"{BASE_URL}/v1/chat/completions"

    payload = {
        "model": "ollama/gemma3:4b",
        "messages": [
            {"role": "user", "content": "Say goodbye in exactly 3 words."}
        ],
        "stream": True,
        "stream_format": "ndjson",
        "max_tokens": 20,
    }

    response = requests.post(url, json=payload, stream=True)
    assert (
        response.status_code == 200
    ), f"Expected 200, got {response.status_code}: {response.text}"
    assert "application/x-ndjson" in response.headers.get("content-type", "")

    chunks = []
    content_parts = []
    done_received = False

    for line in response.iter_lines(decode_unicode=True):
        if line:
            chunk = json.loads(line)
            if chunk.get("done"):
                done_received = True
            else:
                chunks.append(chunk)
                # Extract content from delta
                if "choices" in chunk and chunk["choices"]:
                    delta = chunk["choices"][0].get("delta", {})
                    if "content" in delta:
                        content_parts.append(delta["content"])

    assert len(chunks) > 0, "Expected at least one chunk"
    assert done_received, "Expected done message"

    # Verify chunk structure
    first_chunk = chunks[0]
    assert "id" in first_chunk
    assert "object" in first_chunk
    assert first_chunk["object"] == "chat.completion.chunk"

    # Verify we got content
    full_content = "".join(content_parts)
    assert len(full_content) > 0, "Expected content in streaming response"
    print(f"NDJSON streaming content: {full_content}")


@pytest.mark.depends(on=["test_chat_completions_basic"])
def test_chat_completions_streaming_invalid_format():
    """Test that invalid stream_format returns 422 (schema validation
    error)."""
    url = f"{BASE_URL}/v1/chat/completions"

    payload = {
        "model": "ollama/gemma3:4b",
        "messages": [{"role": "user", "content": "Hello"}],
        "stream": True,
        "stream_format": "invalid_format",
    }

    response = requests.post(url, json=payload)
    assert (
        response.status_code == 422
    ), f"Expected 422, got {response.status_code}: {response.text}"

    data = response.json()
    assert "detail" in data
    # Schema validation error will mention the enum or validation failure
    assert (
        "stream_format" in data["detail"].lower()
        or "enum" in data["detail"].lower()
        or "invalid" in data["detail"].lower()
    )


@pytest.mark.depends(on=["test_chat_completions_basic"])
def test_chat_completions_invalid_parameters():
    """Test that invalid parameters are handled with appropriate error."""
    url = f"{BASE_URL}/v1/chat/completions"

    # Test with invalid temperature (out of range)
    payload = {
        "model": "ollama/gemma3:4b",
        "messages": [{"role": "user", "content": "Hello"}],
        "temperature": 10.0,  # Way out of valid range
    }

    response = requests.post(url, json=payload)
    # Should either accept it (LiteLLM handles) or return error
    # Accept 400 (bad request), or 422 (validation error)
    if response.status_code >= 400:
        assert response.status_code in [
            400,
            422,
        ], f"Expected 400 or 422, got {response.status_code}"


@pytest.mark.depends(on=["test_chat_completions_basic"])
def test_chat_completions_timeout():
    """Test that timeout parameter triggers 408 when request times out."""
    url = f"{BASE_URL}/v1/chat/completions"

    # Request with very short timeout (1 second) that should timeout
    payload = {
        "model": "ollama/gemma3:4b",
        "messages": [
            {
                "role": "user",
                "content": "Write a very long story about the history of the universe from the big bang to today.",
            }
        ],
        "timeout": 1,  # 1 second timeout - should timeout for this prompt
        "max_tokens": 1000,
    }

    response = requests.post(url, json=payload)
    assert (
        response.status_code == 408
    ), f"Expected 408 (timeout), got {response.status_code}: {response.text}"

    data = response.json()
    assert "detail" in data
    assert (
        "timeout" in data["detail"].lower()
    ), f"Expected timeout message, got: {data['detail']}"


@pytest.mark.depends(on=["test_chat_completions_basic"])
def test_chat_completions_missing_required_fields():
    """Test that missing required fields returns 422 Unprocessable Entity."""
    url = f"{BASE_URL}/v1/chat/completions"

    # Test with missing messages
    payload = {
        "model": "ollama/gemma3:4b",
        # Missing required "messages" field
    }

    response = requests.post(url, json=payload)
    assert (
        response.status_code == 422
    ), f"Expected 422, got {response.status_code}: {response.text}"

    data = response.json()
    assert "detail" in data
