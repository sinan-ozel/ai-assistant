"""Evaluation runner for executing test cases.

Runs evaluation cases against LLM providers and validates expectations.
"""

import asyncio
import json
import logging
import re
import time
from typing import Any, Dict, List, Optional, Union

from common.llm import call_llm_by_model
from synced_memory import Memory

logger = logging.getLogger(__name__)


class EvaluationCancelledError(Exception):
    """Raised when the user cancels a running evaluation."""


def expect_equality(
    actual: Union[str, dict, int, float, None], spec: Dict[str, Any]
) -> None:
    """Check if output equals expected value.

    Supports dict, str, int, float, and None types. For dict comparison, compares only non-None values in
    expected dict, but actual must not have extra keys beyond what's in
    expected.

    Special handling for LLM responses:
    - If expected is dict and actual is string containing JSON in markdown code blocks,
      extracts and parses the JSON for comparison.
    - For string comparisons, strips trailing whitespace and newlines from actual.

    Raises AssertionError if not equal.
    """
    expected = spec["value"]

    # If expected is dict but actual is string, try to extract JSON from markdown
    if isinstance(expected, dict) and isinstance(actual, str):
        # Try to extract JSON from markdown code block
        json_match = re.search(
            r"```(?:json)?\s*\n(.*?)\n```", actual, re.DOTALL
        )
        if json_match:
            try:
                actual = json.loads(json_match.group(1))
            except json.JSONDecodeError:
                # If parsing fails, keep as string and let comparison fail below
                pass

    # Strip trailing whitespace from strings
    if isinstance(actual, str) and isinstance(expected, str):
        actual = actual.rstrip()

    # Handle dict comparison - only check non-None values in expected
    if isinstance(expected, dict) and isinstance(actual, dict):
        # Check for extra keys in actual
        expected_keys = set(expected.keys())
        actual_keys = set(actual.keys())
        extra_keys = actual_keys - expected_keys
        if extra_keys:
            raise AssertionError(
                f"equality failed: actual has extra keys {extra_keys}"
            )

        # Check each expected key
        for key, expected_value in expected.items():
            if expected_value is not None:
                if key not in actual:
                    raise AssertionError(
                        f"equality failed for key '{key}': key missing in actual"
                    )
                actual_value = actual[key]
                if actual_value != expected_value:
                    raise AssertionError(
                        f"equality failed for key '{key}': "
                        f"output='{actual_value}', expected='{expected_value}'"
                    )
    elif actual != expected:
        raise AssertionError(
            f"equality failed: output='{actual}', expected='{expected}'"
        )


def expect_in_range(
    actual: Union[str, int, float], spec: Dict[str, Any]
) -> None:
    """Check if output is within the range specified by spec['min'] and
    spec['max'].

    Note that output, spec['min'], and spec['max'] can be strings, but are
    converted to float for comparison. Raises AssertionError if not within
    range.
    """
    v = float(actual)
    lo = float(spec["min"])
    hi = float(spec["max"])

    if not (lo <= v <= hi):
        raise AssertionError(
            f"in_range failed: output={v}, expected between {lo} and {hi}"
        )


def expect_approx_pct(
    output: Union[str, int, float], spec: Dict[str, Any]
) -> None:
    """Check if output is approximately equal to spec['value'] within
    spec['tolerance_pct'] percent.

    Note that output, spec['value'], and spec['tolerance_pct'] can be strings,
    but are converted to float for comparison. Raises AssertionError if not
    within range.
    """
    value = float(spec["value"])
    tol_pct = float(spec["tolerance_pct"])

    v = float(output)
    lower = value * (1 - tol_pct / 100.0)
    upper = value * (1 + tol_pct / 100.0)

    if not (lower <= v <= upper):
        raise AssertionError(
            f"approx_pct failed: output={v}, expected≈{value} "
            f"±{tol_pct}%, range=({lower}, {upper})"
        )


def validate_expectation(
    actual: Union[str, dict, int, float, None], expectation: Dict[str, Any]
) -> Dict[str, Any]:
    """Validate a single expectation against actual output.

    Args:
        actual: The actual output from the LLM
        expectation: The expectation specification

    Returns:
        Dict with 'passed' (bool) and optional 'error' (str) keys
    """
    try:
        exp_type = expectation["type"]

        if exp_type == "contains":
            if expectation["value"] not in actual:
                return {
                    "passed": False,
                    "error": f"Response does not contain '{expectation['value']}'",
                }

        elif exp_type == "equals":
            expect_equality(actual, expectation)

        elif exp_type == "oneOf":
            expected_values = expectation["values"]
            if not isinstance(expected_values, list):
                return {
                    "passed": False,
                    "error": (
                        f"oneOf expectation requires a list of values,"
                        f" got {type(expected_values)}"
                    ),
                }
            matched = False
            errors = []
            for expected_value in expected_values:
                try:
                    expect_equality(actual, {"value": expected_value})
                    matched = True
                    break
                except (AssertionError, Exception) as e:
                    errors.append(str(e))
            if not matched:
                return {
                    "passed": False,
                    "error": (
                        f"Response '{actual}' does not match any of"
                        f" {expected_values}. Errors: {errors}"
                    ),
                }

        elif exp_type in {"regex", "regexp", "regular_expression", "match"}:
            if not re.search(expectation["value"], str(actual)):
                return {
                    "passed": False,
                    "error": (
                        f"Response '{actual}' does not match"
                        f" regex '{expectation['value']}'"
                    ),
                }

        elif exp_type in {"in_range", "range", "within_range"}:
            expect_in_range(actual, expectation)

        elif exp_type in {
            "approx_pct",
            "approximate_percentage",
            "percent_error",
            "within_percentage",
        }:
            expect_approx_pct(actual, expectation)

        else:
            return {
                "passed": False,
                "error": f"Unknown expectation type: {exp_type}",
            }

        return {"passed": True}

    except AssertionError as e:
        return {"passed": False, "error": str(e)}
    except Exception as e:
        return {"passed": False, "error": f"Unexpected error: {str(e)}"}


def run_evaluation_case(
    test_case: Dict[str, Any],
    provider: Dict[str, Any],
    providers_state: Dict[str, Any],
    workflow_path: Optional[str] = None,
    system_message: Optional[str] = None,
) -> Dict[str, Any]:
    """Run a single evaluation case.

    Args:
        test_case: Parsed test case with id, repeat, threshold, and steps
        provider: Provider configuration (contains model name)
        providers_state: Provider discovery state for call_llm_by_model
        workflow_path: Optional workflow path for cancellation checking
        system_message: Optional system message (workflow prompt + schema instructions)

    Returns:
        Dict with results including:
        - id: test case ID
        - passed: overall pass/fail
        - runs: list of individual run results
        - pass_count: number of passing runs
        - fail_count: number of failing runs
        - threshold: required pass threshold
        - repeat: number of repetitions
    """
    test_id = test_case["id"]
    repeat = test_case.get("repeat", 1)
    threshold = test_case.get("threshold", repeat)
    steps = test_case["steps"]

    logger.info(
        f"Running evaluation case: {test_id} (repeat={repeat}, threshold={threshold})"
    )

    runs = []
    pass_count = 0
    fail_count = 0

    for run_idx in range(repeat):
        # Check for cancellation
        if workflow_path:
            with Memory() as memory:
                if hasattr(memory, "workflow_evaluation_state"):
                    state = memory.workflow_evaluation_state.get(
                        workflow_path, {}
                    )
                    if state.get("cancelled"):
                        logger.info(
                            f"Evaluation cancelled for workflow: {workflow_path}"
                        )
                        raise EvaluationCancelledError(
                            "Evaluation was cancelled by user"
                        )

        run_result = {
            "run": run_idx + 1,
            "passed": True,
            "steps": [],
            "duration": 0.0,
        }

        run_start_time = time.time()

        try:
            for step_idx, step in enumerate(steps):
                # Check for cancellation before each step
                if workflow_path:
                    with Memory() as memory:
                        if hasattr(memory, "workflow_evaluation_state"):
                            state = memory.workflow_evaluation_state.get(
                                workflow_path, {}
                            )
                            if state.get("cancelled"):
                                logger.info(
                                    f"Evaluation cancelled for workflow: {workflow_path}"
                                )
                                raise Exception(
                                    "Evaluation was cancelled by user"
                                )

                message_content = step["content"]
                max_tokens = step.get("max_tokens")
                expectations = step.get("expectations", [])

                # Build messages with system message (if provided) and user message
                messages = []
                if system_message:
                    messages.append(
                        {"role": "system", "content": system_message}
                    )

                messages.append({"role": "user", "content": message_content})

                # Get model from provider config
                model = provider.get("model") or provider.get("name")

                # Call LLM using common interface with timeout
                # Use 120 seconds (2 minutes) timeout for evaluation calls
                step_start_time = time.time()
                response = asyncio.run(
                    call_llm_by_model(
                        messages=messages,
                        providers_state=providers_state,
                        model=model,
                        max_tokens=max_tokens,
                        timeout=120.0,
                    )
                )
                step_duration = time.time() - step_start_time

                raw_choice = response.get("choices")[0].to_dict()
                raw_message = raw_choice.get("message", {})

                finish_reason = raw_choice.get("finish_reason")
                if finish_reason == "length":
                    logger.warning(
                        f"LLM hit max_tokens limit (finish_reason='length') for "
                        f"case={test_id}, run={run_idx + 1}, step={step_idx + 1}. "
                        f"Response content may be incomplete or empty."
                    )

                content = raw_message.get("content") or ""

                # Some models (e.g. Hermes 2 Pro) may route structured output
                # into tool_calls instead of content when the prompt resembles
                # a function-call schema.
                if not content.strip() and raw_message.get("tool_calls"):
                    try:
                        content = raw_message["tool_calls"][0]["function"][
                            "arguments"
                        ]
                        logger.info(
                            f"Extracted content from tool_calls for case={test_id}"
                        )
                    except (KeyError, IndexError, TypeError):
                        pass

                actual = content.strip()

                # Try to parse as JSON if any expectation value is a dict
                actual_parsed = actual
                for expectation in expectations:
                    if (
                        isinstance(expectation.get("value"), dict)
                        or expectation.get("type") == "oneOf"
                    ):
                        try:
                            actual_parsed = json.loads(actual)
                        except (json.JSONDecodeError, ValueError):
                            json_match = re.search(
                                r"```(?:json)?\s*\n(.*?)\n```",
                                actual,
                                re.DOTALL,
                            )
                            if json_match:
                                try:
                                    actual_parsed = json.loads(
                                        json_match.group(1)
                                    )
                                except (json.JSONDecodeError, ValueError):
                                    pass
                        break

                # Validate expectations
                step_result = {
                    "step": step_idx + 1,
                    "duration": step_duration,
                    "actual": actual,
                    "expectations": [],
                }

                step_passed = True
                for expectation in expectations:
                    exp_result = validate_expectation(
                        actual_parsed, expectation
                    )
                    step_result["expectations"].append(
                        {
                            "type": expectation["type"],
                            "passed": exp_result["passed"],
                            "error": exp_result.get("error"),
                        }
                    )
                    if not exp_result["passed"]:
                        step_passed = False
                        logger.warning(
                            f"Expectation failed: case={test_id}, run={run_idx + 1}, "
                            f"step={step_idx + 1}, type={expectation['type']}: "
                            f"{exp_result.get('error')}"
                        )

                step_result["passed"] = step_passed
                run_result["steps"].append(step_result)

                if not step_passed:
                    run_result["passed"] = False

        except Exception as e:
            logger.error(
                f"Error running test case {test_id}, run {run_idx + 1}: {e}"
            )
            logger.error("Stopping evaluation due to error")
            # Re-raise to stop evaluation flow immediately
            raise

        run_result["duration"] = time.time() - run_start_time
        runs.append(run_result)

        if run_result["passed"]:
            pass_count += 1
        else:
            fail_count += 1

        # Small delay between runs
        if run_idx < repeat - 1:
            time.sleep(1)

    overall_passed = pass_count >= threshold

    return {
        "id": test_id,
        "passed": overall_passed,
        "runs": runs,
        "pass_count": pass_count,
        "fail_count": fail_count,
        "threshold": threshold,
        "repeat": repeat,
    }


def run_all_evaluations(
    test_cases: List[Dict[str, Any]],
    provider: Dict[str, Any],
    providers_state: Dict[str, Any],
    workflow_path: Optional[str] = None,
    system_message: Optional[str] = None,
) -> Dict[str, Any]:
    """Run all evaluation cases.

    Args:
        test_cases: List of parsed test cases
        provider: Provider configuration (contains model name)
        providers_state: Provider discovery state for call_llm_by_model
        workflow_path: Optional workflow path for cancellation checking
        system_message: Optional system message (workflow prompt + schema instructions)

    Returns:
        Dict with overall results including:
        - total_cases: total number of test cases
        - passed_cases: number of passed cases
        - failed_cases: number of failed cases
        - cases: detailed results for each case
        - errors: list of error messages from failed runs (if any)
    """
    start_time = time.time()

    results = []
    passed_cases = 0
    failed_cases = 0
    errors = []

    for test_case in test_cases:
        case_result = run_evaluation_case(
            test_case, provider, providers_state, workflow_path, system_message
        )
        results.append(case_result)

        if case_result["passed"]:
            passed_cases += 1
        else:
            failed_cases += 1

            # Collect errors from failed step expectations
            for run in case_result.get("runs", []):
                for step in run.get("steps", []):
                    for exp in step.get("expectations", []):
                        if not exp.get("passed") and exp.get("error"):
                            error_msg = (
                                f"Case '{case_result['id']}', run {run['run']}, "
                                f"step {step['step']} ({exp['type']}): {exp['error']}"
                            )
                            errors.append(error_msg)
                            logger.error(error_msg)

    total_duration = time.time() - start_time

    result = {
        "total_cases": len(test_cases),
        "passed_cases": passed_cases,
        "failed_cases": failed_cases,
        "duration": total_duration,
        "cases": results,
    }

    # Include errors if any were found
    if errors:
        result["errors"] = errors

    return result
