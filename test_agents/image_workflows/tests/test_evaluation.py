"""Test evaluation endpoint for workflows."""

import os
import time

import pytest
import requests

BASE_URL = os.getenv("BASE_URL", "http://app:8000")


@pytest.mark.depends(on=["test_providers.py::test_providers"])
def test_nutrition_workflow_evaluation(clear_evaluation_state):
    """Test triggering and monitoring workflow evaluation.

    This test:
    1. Triggers evaluation for the nutrition information extraction workflow
    2. Polls for results, first asserting status is 'running'
    3. Waits for completion with timeout
    4. Validates the result schema
    """
    # Step 1: Trigger evaluation
    eval_url = f"{BASE_URL}/private/evaluate/v1/extract-nutrition-information"
    response = requests.post(eval_url, timeout=10)

    assert response.status_code == 201, (
        f"Expected 201 Created when starting evaluation, got {response.status_code}. "
        f"Response: {response.text}"
    )

    data = response.json()
    assert "message" in data
    assert "workflow_path" in data
    assert data["workflow_path"] == "/v1/extract-nutrition-information"

    # Step 2: Poll for results
    results_url = f"{BASE_URL}/private/evaluate/v1/extract-nutrition-information/results"

    # First, confirm evaluation is running
    time.sleep(0.5)  # Brief delay to ensure evaluation has started
    response = requests.get(results_url, timeout=10)
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "running", (
        f"Expected status to be 'running' shortly after triggering, got '{data['status']}'"
    )
    assert data["current_evaluation"] == "/v1/extract-nutrition-information"
    assert data["workflow_path"] == "/v1/extract-nutrition-information"

    # Validate that started_at is present
    assert "started_at" in data, "Expected 'started_at' timestamp in response"
    assert isinstance(data["started_at"], str), "Expected 'started_at' to be a string (ISO format)"
    # Try to parse it as ISO datetime
    from datetime import datetime
    try:
        datetime.fromisoformat(data["started_at"])
    except ValueError:
        pytest.fail(f"'started_at' is not a valid ISO datetime: {data['started_at']}")

    # Step 3: Wait for completion with timeout
    start = time.time()
    timeout = 300  # 5 minutes - evaluations can take a while with LLM calls
    final_data = None

    while True:
        response = requests.get(results_url, timeout=10)
        assert response.status_code == 200

        data = response.json()
        status = data.get("status")

        if status in ["completed", "failed", "error", "cancelled"]:
            final_data = data
            break

        if time.time() - start > timeout:
            pytest.fail(
                f"Evaluation did not complete within {timeout} seconds. "
                f"Last status: {status}"
            )

        time.sleep(2)  # Poll every 2 seconds

    # Step 4: Validate the result schema
    assert final_data is not None
    assert final_data["status"] == "completed", (
        f"Expected evaluation to complete successfully, got status '{final_data['status']}'. "
        f"Error: {final_data.get('error')}"
    )

    # Validate results structure
    assert "results" in final_data
    results = final_data["results"]

    # Check top-level results fields
    assert "total_cases" in results
    assert "passed_cases" in results
    assert "failed_cases" in results
    assert "duration" in results
    assert "cases" in results

    # Validate types
    assert isinstance(results["total_cases"], int)
    assert isinstance(results["passed_cases"], int)
    assert isinstance(results["failed_cases"], int)
    assert isinstance(results["duration"], (int, float))
    assert isinstance(results["cases"], list)

    # Check that we have at least one case
    assert results["total_cases"] > 0, "Expected at least one test case"
    assert len(results["cases"]) == results["total_cases"]

    # All cases must pass
    assert results["failed_cases"] == 0, (
        f"Expected all cases to pass, but {results['failed_cases']} failed. "
        f"Cases: {[{'id': c['id'], 'passed': c['passed'], 'pass_count': c['pass_count'], 'repeat': c['repeat']} for c in results['cases']]}"
    )
    assert results["passed_cases"] == results["total_cases"], (
        f"Expected {results['total_cases']} passed cases, got {results['passed_cases']}"
    )

    # Validate case structure
    for case in results["cases"]:
        assert "id" in case
        assert "passed" in case
        assert "runs" in case
        assert "pass_count" in case
        assert "fail_count" in case
        assert "threshold" in case
        assert "repeat" in case

        assert isinstance(case["id"], str)
        assert isinstance(case["passed"], bool)
        assert case["passed"] is True, (
            f"Case '{case['id']}' failed: passed {case['pass_count']}/{case['repeat']} "
            f"(threshold: {case['threshold']})"
        )
        assert isinstance(case["runs"], list)
        assert isinstance(case["pass_count"], int)
        assert isinstance(case["fail_count"], int)
        assert isinstance(case["threshold"], int)
        assert isinstance(case["repeat"], int)

        # Validate run structure
        for run in case["runs"]:
            assert "run" in run
            assert "passed" in run
            assert "steps" in run
            assert "duration" in run

            assert isinstance(run["run"], int)
            assert isinstance(run["passed"], bool)
            assert isinstance(run["steps"], list)
            assert isinstance(run["duration"], (int, float))

            # Validate step structure
            for step in run["steps"]:
                assert "step" in step
                assert "duration" in step
                assert "actual" in step
                assert "expectations" in step
                assert "passed" in step

                assert isinstance(step["step"], int)
                assert isinstance(step["duration"], (int, float))
                assert isinstance(step["actual"], str)
                assert isinstance(step["expectations"], list)
                assert isinstance(step["passed"], bool)

    # Check that current_evaluation is now null (evaluation finished)
    assert final_data["current_evaluation"] is None

    print(f"\nEvaluation completed successfully!")
    print(f"Total cases: {results['total_cases']}")
    print(f"Passed: {results['passed_cases']}, Failed: {results['failed_cases']}")
    print(f"Duration: {results['duration']:.2f}s")


@pytest.mark.depends(on=["test_nutrition_workflow_evaluation"])
def test_evaluation_already_in_progress(clear_evaluation_state):
    """Test that starting a second evaluation while one is running returns 409."""
    # This test assumes the previous test completed, so no evaluation should be running
    # We'll trigger one and immediately try to trigger another

    eval_url = f"{BASE_URL}/private/evaluate/v1/extract-nutrition-information"

    # Start first evaluation
    response1 = requests.post(eval_url, timeout=10)
    assert response1.status_code == 201

    # Immediately try to start another
    response2 = requests.post(eval_url, timeout=10)

    # Should get 409 Conflict
    assert response2.status_code == 409, (
        f"Expected 409 Conflict when evaluation already in progress, got {response2.status_code}"
    )

    data = response2.json()
    assert "detail" in data
    assert "already in progress" in data["detail"].lower()

    # Wait for the evaluation to complete before moving on
    results_url = f"{BASE_URL}/private/evaluate/v1/extract-nutrition-information/results"
    start = time.time()
    timeout = 300

    while True:
        response = requests.get(results_url, timeout=10)
        data = response.json()

        if data.get("status") in ["completed", "failed", "error", "cancelled", "idle"]:
            break

        if time.time() - start > timeout:
            break

        time.sleep(2)


def test_evaluation_workflow_not_found():
    """Test that evaluating a non-existent workflow returns 404."""
    eval_url = f"{BASE_URL}/private/evaluate/v1/non-existent-workflow"

    response = requests.post(eval_url, timeout=10)

    assert response.status_code == 404, (
        f"Expected 404 Not Found for non-existent workflow, got {response.status_code}"
    )

    data = response.json()
    assert "detail" in data
    assert "not found" in data["detail"].lower()


def test_workflows_list():
    """Test listing all workflows."""
    url = f"{BASE_URL}/private/v1/workflows"

    response = requests.get(url, timeout=10)

    assert response.status_code == 200, (
        f"Expected 200 OK for workflows list, got {response.status_code}"
    )

    data = response.json()
    assert "total" in data
    assert "workflows" in data
    assert isinstance(data["total"], int)
    assert isinstance(data["workflows"], list)

    # Should have at least the nutrition workflow
    assert data["total"] > 0

    # Validate workflow structure
    for workflow in data["workflows"]:
        assert "name" in workflow
        assert "path" in workflow
        assert "has_evaluation" in workflow
        assert isinstance(workflow["name"], str)
        assert isinstance(workflow["path"], str)
        assert isinstance(workflow["has_evaluation"], bool)

        # Optional fields
        if "description" in workflow:
            assert isinstance(workflow["description"], str)
        if "provider" in workflow:
            assert isinstance(workflow["provider"], (str, type(None)))

    # Find the nutrition workflow
    nutrition_workflow = next(
        (w for w in data["workflows"] if "nutrition" in w["name"].lower()),
        None
    )
    assert nutrition_workflow is not None, "Expected to find nutrition workflow"
    assert nutrition_workflow["has_evaluation"] is True


@pytest.mark.depends(on=["test_workflows_list"])
def test_evaluation_cancellation(clear_evaluation_state):
    """Test that evaluations can be cancelled.

    This test:
    1. Starts an evaluation
    2. Immediately cancels it
    3. Verifies the status becomes 'cancelled'
    """
    eval_url = f"{BASE_URL}/private/evaluate/v1/extract-nutrition-information"

    # Start evaluation
    response = requests.post(eval_url, timeout=10)
    assert response.status_code == 201, (
        f"Expected 201 when starting evaluation, got {response.status_code}"
    )

    # Brief delay to ensure evaluation has started
    time.sleep(0.5)

    # Cancel the evaluation
    cancel_url = f"{BASE_URL}/private/cancel-evaluation/v1/extract-nutrition-information"
    cancel_response = requests.post(cancel_url, timeout=10)

    assert cancel_response.status_code == 200, (
        f"Expected 200 when cancelling evaluation, got {cancel_response.status_code}. "
        f"Response: {cancel_response.text}"
    )

    cancel_data = cancel_response.json()
    assert "message" in cancel_data
    assert "workflow_path" in cancel_data

    # Wait for status to update to cancelled
    results_url = f"{BASE_URL}/private/evaluate/v1/extract-nutrition-information/results"
    start = time.time()
    timeout = 30  # Should be quick
    final_status = None

    while True:
        response = requests.get(results_url, timeout=10)
        assert response.status_code == 200

        data = response.json()
        status = data.get("status")

        if status in ["cancelled", "completed", "error"]:
            final_status = status
            break

        if time.time() - start > timeout:
            pytest.fail(
                f"Evaluation did not reach terminal state within {timeout} seconds. "
                f"Last status: {status}"
            )

        time.sleep(0.5)

    # Verify it was cancelled
    assert final_status == "cancelled", (
        f"Expected status to be 'cancelled' after cancellation, got '{final_status}'"
    )

    # Verify cancelled flag is set
    response = requests.get(results_url, timeout=10)
    data = response.json()
    assert data.get("cancelled") is True, "Expected 'cancelled' flag to be True"
    assert "error" in data
    assert "cancelled" in data["error"].lower()

    print("\n✅ Evaluation cancellation test passed")


@pytest.mark.depends(on=["test_evaluation_cancellation"])
def test_cancel_non_running_evaluation():
    """Test that cancelling a non-running evaluation returns 404."""
    # Make sure no evaluation is running (previous test should have finished)
    time.sleep(1)

    cancel_url = f"{BASE_URL}/private/cancel-evaluation/v1/extract-nutrition-information"
    response = requests.post(cancel_url, timeout=10)

    assert response.status_code == 404, (
        f"Expected 404 when cancelling non-running evaluation, got {response.status_code}"
    )

    data = response.json()
    assert "detail" in data
    assert "no running evaluation" in data["detail"].lower()
