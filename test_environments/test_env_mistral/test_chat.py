import pytest
import requests
import litellm
import os


litellm.set_verbose = False
litellm.verbose = False
litellm.suppress_debug_info = True
litellm.log_raw_llm_output = False
litellm.drop_params = True


BASE_URL = os.getenv("BASE_URL", "http://app:8000")


@pytest.mark.depends(name='test_chat_completions_basic', on=['test_provider_context_window'])
def test_chat_completions_basic(mistral_api_key_available):
    """Test basic chat completion with a trivial question."""
    url = f"{BASE_URL}/v1/chat/completions"

    # Ask a trivial question
    payload = {
        "model": "ministral-3b",
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
def test_chat_completions_litellm(mistral_api_key_available):
    """Test chat completion using LiteLLM client interface."""
    # Configure LiteLLM to use our custom OpenAI-compatible endpoint
    api_base = f"{BASE_URL}/v1"

    # Use litellm to make a completion request
    # Prefix with "openai/" to tell LiteLLM to use OpenAI-compatible format
    response = litellm.completion(
        model="openai/ministral-3b",
        messages=[
            {"role": "user", "content": "What is the capital of France? Answer with only the city name."}
        ],
        api_base=api_base,
        api_key="dummy",  # Dummy key since authentication is handled by our server
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
def test_chat_completions_timeout(mistral_api_key_available):
    """Test that timeout parameter triggers 408 when request times out."""
    url = f"{BASE_URL}/v1/chat/completions"

    # Request with very short timeout (1 second) that should timeout
    payload = {
        "model": "ministral-3b",
        "messages": [
            {"role": "user", "content": "Write a very long story about the history of the universe from the big bang to today."}
        ],
        "timeout": 1,  # 1 second timeout - should timeout for this prompt
        "max_tokens": 1000
    }

    response = requests.post(url, json=payload)
    assert response.status_code == 408, f"Expected 408 (timeout), got {response.status_code}: {response.text}"

    data = response.json()
    assert "detail" in data
    assert "timeout" in data["detail"].lower(), f"Expected timeout message, got: {data['detail']}"
