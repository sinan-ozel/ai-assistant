"""Integration tests for agent_with_incorrect_eval.

Verifies that a NameError in eval.py is caught per-case, recorded in the
results with status "error", and does not prevent other cases from running.
"""

import os
import time

import pytest
import requests

BASE_URL = os.getenv("BASE_URL", "http://app:8000")
EVAL_URL = f"{BASE_URL}/private/v1/agent/evaluate"


@pytest.mark.depends(name="test_incorrect_eval_starts")
def test_incorrect_eval_starts():
    """POST returns 202 — eval.py is present even though it has a bug."""
    resp = requests.post(EVAL_URL, json={})
    assert resp.status_code == 202, resp.text
    data = resp.json()
    assert "started_at" in data


@pytest.mark.depends(
    on=["test_incorrect_eval_starts"], name="test_incorrect_eval_results"
)
def test_incorrect_eval_results():
    """Wait for completion; the error case must appear with status='error'."""
    deadline = time.time() + 180
    while time.time() < deadline:
        resp = requests.get(EVAL_URL)
        if resp.status_code == 200:
            data = resp.json()
            assert "cases" in data, data
            cases = {c["id"]: c for c in data["cases"]}

            # greets_user uses expekt() — should be recorded as error
            assert (
                "greets_user" in cases
            ), f"greets_user missing from {list(cases)}"
            assert cases["greets_user"]["status"] == "error", cases[
                "greets_user"
            ]
            assert "error" in cases["greets_user"], cases["greets_user"]
            assert (
                "expekt" in cases["greets_user"]["error"]
                or "NameError" in cases["greets_user"]["error"]
            ), f"Expected NameError mentioning 'expekt', got: {cases['greets_user']['error']}"

            # answers_simple_math uses expect() correctly — should pass or fail but not error
            assert (
                "answers_simple_math" in cases
            ), f"answers_simple_math missing from {list(cases)}"
            assert cases["answers_simple_math"]["status"] in (
                "pass",
                "fail",
            ), cases["answers_simple_math"]

            return
        assert (
            resp.status_code == 202
        ), f"Unexpected {resp.status_code}: {resp.text}"
        time.sleep(4)
    pytest.fail("Evaluation did not complete within 180 s")
