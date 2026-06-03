"""Test that evaluation returns error status for incorrectly configured provider."""

import os
import time

import pytest
import requests

BASE_URL = os.getenv("BASE_URL", "http://app:8000")


@pytest.mark.depends(on=["test_providers.py::test_providers"])
def test_evaluation_returns_error():
    """Test that evaluation with bad provider configuration returns error status.

    This test:
    1. Triggers evaluation for the workflow with bad provider
    2. Waits for evaluation to complete
    3. Asserts that status is 'error' (not 'completed' or 'failed')
    4. Validates that error message mentions LiteLLM provider issue
    """
    # Step 1: Trigger evaluation
    eval_url = f"{BASE_URL}/private/evaluate/v1/test-bad-provider"
    response = requests.post(eval_url, timeout=10)

    assert response.status_code == 201, (
        f"Expected 201 Created when starting evaluation, got {response.status_code}. "
        f"Response: {response.text}"
    )

    data = response.json()
    assert "message" in data
    assert "workflow_path" in data
    assert data["workflow_path"] == "/v1/test-bad-provider"

    # Step 2: Poll for results
    results_url = f"{BASE_URL}/private/evaluate/v1/test-bad-provider/results"

    # Wait for completion with timeout
    start = time.time()
    timeout = 60  # 1 minute should be enough to fail
    final_data = None

    while True:
        response = requests.get(results_url, timeout=10)
        assert response.status_code == 200

        data = response.json()
        status = data.get("status")

        if status in ["completed", "failed", "error"]:
            final_data = data
            break

        if time.time() - start > timeout:
            pytest.fail(
                f"Evaluation did not complete within {timeout} seconds. "
                f"Last status: {status}"
            )

        time.sleep(2)  # Poll every 2 seconds

    # Step 3: Assert status is 'error'
    assert final_data is not None
    assert final_data["status"] == "error", (
        f"Expected status to be 'error' for bad provider config, got '{final_data['status']}'. "
        f"Results: {final_data}"
    )

    # Step 4: Validate error message
    assert "error" in final_data, "Expected 'error' field in response"
    error_msg = final_data["error"]

    # Check that error message mentions the LiteLLM provider issue
    assert "LLM Provider NOT provided" in error_msg or "BadRequestError" in error_msg, (
        f"Expected error message to mention LiteLLM provider issue, got: {error_msg}"
    )

    # Verify that model=vision was in the error
    assert "model=vision" in error_msg, (
        f"Expected error message to mention 'model=vision', got: {error_msg}"
    )

    print("\n✅ Evaluation correctly returned 'error' status")
    print(f"Error message: {error_msg}")
