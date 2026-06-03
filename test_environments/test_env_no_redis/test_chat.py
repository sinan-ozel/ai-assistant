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


@pytest.mark.depends(name='test_chat_completions_basic',
                     on=['test_provider_context_window',
                         'providers_loaded'])
def test_chat_completions_basic():
    """Test basic chat completion with a trivial question."""
    url = f"{BASE_URL}/v1/chat/completions"

    # Ask a trivial question
    payload = {
        "model": "ollama/gemma3:4b",
        "messages": [
            {"role": "user", "content": "What is 2+2? Answer with only the number."}
        ],
        "temperature": 0.1,
        "max_tokens": 10
    }

    response = requests.post(url, json=payload)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

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


@pytest.mark.depends(on=['test_chat_completions_basic'])
def test_chat_completions_litellm():
    """Test chat completion using LiteLLM client interface."""
    # Configure LiteLLM to use our custom OpenAI-compatible endpoint
    api_base = f"{BASE_URL}/v1"

    # Use litellm to make a completion request
    # Prefix with "openai/" to tell LiteLLM to use OpenAI-compatible format
    response = litellm.completion(
        model="ollama/gemma3:4b",
        messages=[
            {"role": "user", "content": "What is the capital of France? Answer with only the city name."}
        ],
        api_base=api_base,
        temperature=0.1,
        max_tokens=10
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


@pytest.mark.depends(on=['test_chat_completions_basic'])
def test_chat_completions_timeout_validation():
    """Test that timeout values outside [15, 300] are rejected with 422."""
    url = f"{BASE_URL}/v1/chat/completions"

    payload = {
        "model": "ollama/gemma3:4b",
        "messages": [{"role": "user", "content": "Hello"}],
        "timeout": 0,
    }

    response = requests.post(url, json=payload)
    assert response.status_code == 422, f"Expected 422, got {response.status_code}: {response.text}"

    detail = response.json()["detail"]
    assert "15" in detail, f"Expected minimum (15) in error message, got: {detail}"
    assert "240" in detail, f"Expected maximum (240) in error message, got: {detail}"


@pytest.mark.depends(on=['test_chat_completions_timeout_validation'])
def test_chat_completions_timeout():
    """Test that a request with the minimum allowed timeout triggers 408."""
    url = f"{BASE_URL}/v1/chat/completions"

    payload = {
        "model": "ollama/gemma3:4b",
        "messages": [
            {"role": "user", "content": "Write a very long story about the history of the universe from the big bang to today."}
        ],
        "timeout": 15,
        "max_tokens": 1000
    }

    response = requests.post(url, json=payload)
    assert response.status_code == 408, f"Expected 408 (timeout), got {response.status_code}: {response.text}"

    data = response.json()
    assert "detail" in data
    assert "timeout" in data["detail"].lower(), f"Expected timeout message, got: {data['detail']}"


@pytest.mark.depends(on=['test_chat_completions_basic'])
def test_chat_completions_invalid_parameters():
    """Test that invalid parameters are handled with appropriate error."""
    url = f"{BASE_URL}/v1/chat/completions"

    # Test with invalid temperature (out of range)
    payload = {
        "model": "ollama/gemma3:4b",
        "messages": [
            {"role": "user", "content": "Hello"}
        ],
        "temperature": 10.0  # Way out of valid range
    }

    response = requests.post(url, json=payload)
    # Should either accept it (LiteLLM handles) or return error
    # Accept 400 (bad request), or 422 (validation error)
    if response.status_code >= 400:
        assert response.status_code in [400, 422], f"Expected 400 or 422, got {response.status_code}"


@pytest.mark.depends(on=['test_chat_completions_basic'])
def test_chat_completions_missing_required_fields():
    """Test that missing required fields returns 422 Unprocessable Entity."""
    url = f"{BASE_URL}/v1/chat/completions"

    # Test with missing messages
    payload = {
        "model": "ollama/gemma3:4b",
        # Missing required "messages" field
    }

    response = requests.post(url, json=payload)
    assert response.status_code == 422, f"Expected 422, got {response.status_code}: {response.text}"

    data = response.json()
    assert "detail" in data
