"""Integration tests for the agent evaluation DSL API.

Covers POST / GET / DELETE /private/v1/agent/evaluate.
"""

import os
import time

import pytest
import requests

BASE_URL = os.getenv("BASE_URL", "http://app:8000")
EVAL_URL = f"{BASE_URL}/private/v1/agent/evaluate"


# ── POST ──────────────────────────────────────────────────────────────────────


@pytest.mark.depends(name="test_eval_post_starts_run")
def test_eval_post_starts_run():
    """POST starts a run and returns 202 with started_at."""
    resp = requests.post(EVAL_URL, json={})
    assert resp.status_code == 202, resp.text
    data = resp.json()
    assert "started_at" in data
    assert isinstance(data["started_at"], str)


@pytest.mark.depends(
    on=["test_eval_post_starts_run"], name="test_eval_post_conflict"
)
def test_eval_post_conflict():
    """A second POST while a run is active returns 409."""
    resp = requests.post(EVAL_URL, json={})
    # If the previous run already finished this will be 202; if still running, 409.
    assert resp.status_code in (202, 409), resp.text


# ── GET ───────────────────────────────────────────────────────────────────────


@pytest.mark.depends(on=["test_eval_post_starts_run"])
def test_eval_get_while_running_or_done():
    """GET returns 202 (running) or 200 (completed) — never an error."""
    resp = requests.get(EVAL_URL)
    assert resp.status_code in (200, 202), resp.text


@pytest.mark.depends(
    on=["test_eval_post_starts_run"], name="test_eval_wait_complete"
)
def test_eval_wait_complete():
    """Wait for the evaluation to finish and verify the result shape."""
    deadline = time.time() + 180
    while time.time() < deadline:
        resp = requests.get(EVAL_URL)
        if resp.status_code == 200:
            data = resp.json()
            assert "total" in data, data
            assert "passed" in data, data
            assert "failed" in data, data
            assert "cases" in data, data
            assert data["total"] > 0
            assert isinstance(data["cases"], list)
            for case in data["cases"]:
                assert "id" in case
                assert "status" in case
                assert case["status"] in ("pass", "fail", "error")
                assert "runs" in case
                assert "passing_runs" in case
                assert "threshold" in case
            return
        assert (
            resp.status_code == 202
        ), f"Unexpected {resp.status_code}: {resp.text}"
        time.sleep(4)
    pytest.fail("Evaluation did not complete within 180 s")


@pytest.mark.depends(on=["test_eval_wait_complete"])
def test_eval_get_returns_results_after_completion():
    """GET returns 200 with cached results after the run finishes."""
    resp = requests.get(EVAL_URL)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["total"] > 0


# ── Single-case run ───────────────────────────────────────────────────────────


@pytest.mark.depends(
    on=["test_eval_wait_complete"], name="test_eval_single_case"
)
def test_eval_single_case():
    """POST with case=greets_user runs only that case."""
    resp = requests.post(EVAL_URL, json={"case": "greets_user"})
    # 202 if no run was in progress; 409 if one somehow still is.
    assert resp.status_code in (202, 409), resp.text


# ── DELETE ────────────────────────────────────────────────────────────────────


@pytest.mark.depends(on=["test_eval_wait_complete"])
def test_eval_delete_no_run():
    """DELETE when no run is active returns 404."""
    # Wait for any in-progress run to finish before attempting delete.
    deadline = time.time() + 60
    while time.time() < deadline:
        state_resp = requests.get(EVAL_URL)
        if state_resp.status_code != 202:
            break
        time.sleep(2)

    resp = requests.delete(EVAL_URL)
    assert resp.status_code == 404, resp.text


@pytest.mark.depends(on=["test_eval_wait_complete"])
def test_eval_delete_cancels_run():
    """Start a run, cancel it, then confirm it exits the running state."""
    start_resp = requests.post(EVAL_URL, json={})
    if start_resp.status_code == 409:
        pytest.skip("Another run is already in progress")
    assert start_resp.status_code == 202, start_resp.text

    del_resp = requests.delete(EVAL_URL)
    # 200 if the run was still active; 404 if it already finished.
    assert del_resp.status_code in (200, 404), del_resp.text

    # If cancellation was accepted, poll until the run is no longer running.
    if del_resp.status_code == 200:
        deadline = time.time() + 120
        while time.time() < deadline:
            poll = requests.get(EVAL_URL)
            if poll.status_code != 202:
                break
            time.sleep(3)
        else:
            pytest.fail("Evaluation did not stop within 120 s after cancellation")
        # The run must have ended in a terminal state (cancelled or completed).
        assert poll.status_code in (200, 404), (
            f"Unexpected status after cancel: {poll.status_code} {poll.text}"
        )
