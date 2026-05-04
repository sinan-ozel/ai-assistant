"""Python-based DSL runtime for agent evaluation.

This module provides a runtime for executing user-defined ``eval.py`` scripts
that test the agent across multiple cases and steps.

DSL Contract:

- Module docstring  → suite name
- ``eval(...)``     → suite-level configuration
- ``def case():``   → test case (any non-underscore function)
- ``def _helper():``→ not collected (underscore prefix)

Minimal example (``cortex/chat/eval.py``)::

    \"\"\"My eval suite.\"\"\"

    eval(repeat=2, threshold=1)

    def greets_user():
        with question("Hello!"):
            expect(r"(?i)hello|hi")

Injected globals (no imports needed in ``eval.py``):

==================  =====================================================
Name                Description
==================  =====================================================
``eval(...)``       Suite-level configuration
``step(...)``       Context manager: send a turn, collect expectations
``question(...)``   Alias for ``step``
``response_to(...)``Alias for ``step``
``expect(value)``   Attach a check to the enclosing step
``assume(text)``    Send a turn, discard the response
``similar_to(t, n)``Embedding cosine-similarity checker
``judge(prompt?)``  LLM-as-judge checker
==================  =====================================================
"""

import asyncio
import logging
import os
import re
import threading
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

_AGENT_CHAT_URL = "http://localhost:8000/v1/agent/chat"
_EVAL_USER_ID = "__eval__"
_LLM_TIMEOUT = 120.0

# Thread-local storage for DSL execution context
_tls = threading.local()


class EvalCancelledError(Exception):
    """Raised when the evaluation run is cancelled."""


class _EvalRateLimitError(Exception):
    """Raised when the agent or judge hits a rate limit during evaluation."""


# ── Data classes ──────────────────────────────────────────────────────────────


@dataclass
class SuiteConfig:
    """Configuration from the ``eval()`` call in the script."""

    repeat: int = 1
    threshold: int = 1
    model: Optional[str] = None
    judge_model: Optional[str] = None
    delay: float = 1.0


@dataclass
class ParsedSuite:
    """Result of parsing an ``eval.py`` script."""

    suite_name: Optional[str]
    config: SuiteConfig
    # (case_name, docstring) in definition order
    cases: List[Tuple[str, Optional[str]]]


# ── Thread-local execution context ───────────────────────────────────────────


@dataclass
class _CaseContext:
    providers_state: dict
    suite_config: SuiteConfig
    case_docstring: Optional[str]
    conversation_id: str
    cancellation_checker: Optional[Callable[[], bool]]
    # mutable state during execution
    step_index: int = 0
    step_results: List[Dict] = field(default_factory=list)
    current_response: Optional[str] = None
    current_step: Optional["StepContext"] = None


# ── StepContext (context manager) ─────────────────────────────────────────────


class StepContext:
    """Context manager for a single evaluation step.

    On ``__enter__``: sends the message to the agent and stores the response.
    On ``__exit__``:  records the step result (pass/fail) and its checks.
    """

    def __init__(self, text=None, image=None, audio=None, **kwargs):
        self._text = text
        self._image = image
        self._audio = audio
        self._max_tokens: Optional[int] = kwargs.get("max_tokens")
        self._checks: List[Dict] = []
        self._prev_response: Optional[str] = None
        self._prev_step: Optional["StepContext"] = None

    def __enter__(self):
        ctx = _tls.ctx

        if ctx.cancellation_checker and ctx.cancellation_checker():
            raise EvalCancelledError("Evaluation cancelled")

        response = _send_step(ctx, self)

        self._prev_response = ctx.current_response
        self._prev_step = ctx.current_step
        ctx.current_response = response
        ctx.current_step = self
        ctx.step_index += 1

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        ctx = _tls.ctx

        step_passed = all(c.get("passed", False) for c in self._checks)
        ctx.step_results.append(
            {
                "step": ctx.step_index,
                "passed": step_passed,
                "checks": self._checks,
            }
        )

        ctx.current_response = self._prev_response
        ctx.current_step = self._prev_step

        return False  # never suppress exceptions


# ── Agent communication ───────────────────────────────────────────────────────


def _send_step(ctx: _CaseContext, step: StepContext) -> str:
    """Send a step's message to the agent and return the text response."""
    import time

    import requests

    if ctx.suite_config.delay > 0:
        time.sleep(ctx.suite_config.delay)

    if step._image or step._audio:
        raise NotImplementedError(
            "Image and audio steps are not yet supported in the Python eval DSL. "
            "Use text steps for now."
        )

    if not step._text:
        raise ValueError(
            "step() requires at least a text argument. "
            "Image and audio are not yet supported."
        )

    body: Dict[str, Any] = {
        "message": step._text,
        "conversation_id": ctx.conversation_id,
        "user_id": _EVAL_USER_ID,
        "timeout": int(_LLM_TIMEOUT),
    }
    if step._max_tokens:
        body["max_tokens"] = step._max_tokens

    for attempt in range(1, _JUDGE_MAX_RETRIES + 1):
        resp = requests.post(_AGENT_CHAT_URL, json=body, timeout=_LLM_TIMEOUT + 10)
        if resp.status_code != 429:
            break
        if attempt == _JUDGE_MAX_RETRIES:
            raise _EvalRateLimitError("Rate limit exceeded — try again later.")
        wait = _JUDGE_RETRY_BASE_DELAY * (2 ** (attempt - 1))
        logger.warning(
            "Chat rate-limited (attempt %d/%d); retrying in %.0fs.",
            attempt,
            _JUDGE_MAX_RETRIES,
            wait,
        )
        time.sleep(wait)

    resp.raise_for_status()
    return resp.json()["message"]


def _send_assume(ctx: _CaseContext, text: str) -> None:
    """Send a turn to the agent and discard the response."""
    import time

    import requests

    if ctx.suite_config.delay > 0:
        time.sleep(ctx.suite_config.delay)

    body: Dict[str, Any] = {
        "message": text,
        "conversation_id": ctx.conversation_id,
        "user_id": _EVAL_USER_ID,
        "timeout": int(_LLM_TIMEOUT),
    }
    for attempt in range(1, _JUDGE_MAX_RETRIES + 1):
        resp = requests.post(_AGENT_CHAT_URL, json=body, timeout=_LLM_TIMEOUT + 10)
        if resp.status_code != 429:
            break
        if attempt == _JUDGE_MAX_RETRIES:
            raise _EvalRateLimitError("Rate limit exceeded — try again later.")
        wait = _JUDGE_RETRY_BASE_DELAY * (2 ** (attempt - 1))
        logger.warning(
            "Chat rate-limited (attempt %d/%d); retrying in %.0fs.",
            attempt,
            _JUDGE_MAX_RETRIES,
            wait,
        )
        time.sleep(wait)

    resp.raise_for_status()


# ── Judge and similarity helpers ──────────────────────────────────────────────


def _resolve_judge_model(providers_state: dict, override: Optional[str]) -> str:
    """Return the model name to use for judge LLM calls.

    Priority: suite's ``judge_model`` → ``evaluation`` provider → ``DEFAULT_PROVIDER``
    env var → ``default``.
    """
    if override:
        return override

    providers = providers_state.get("providers", [])

    for p in providers:
        if p.get("name") == "evaluation" and p.get("available"):
            return "evaluation"

    env_default = os.environ.get("DEFAULT_PROVIDER")
    if env_default:
        for p in providers:
            if p.get("name") == env_default and p.get("available"):
                return env_default

    return "default"


_JUDGE_MAX_RETRIES = 3
_JUDGE_RETRY_BASE_DELAY = 5.0


def _run_judge(
    ctx: _CaseContext, response: str, prompt: str
) -> Tuple[bool, Optional[str]]:
    """Call the judge LLM and return (passed, reason).

    Retries up to ``_JUDGE_MAX_RETRIES`` times with exponential backoff on
    rate-limit errors.
    """
    import time

    import litellm

    from common.llm import call_llm_by_model

    judge_model = _resolve_judge_model(
        ctx.providers_state, ctx.suite_config.judge_model
    )

    if ctx.suite_config.delay > 0:
        time.sleep(ctx.suite_config.delay)

    system = (
        "You are an evaluation judge. "
        "Given an AI assistant's response and evaluation criteria, "
        "decide whether the response passes. "
        "Reply with YES or NO on the first line, followed by a brief reason."
    )
    user = (
        f"Response to evaluate:\n{response}\n\n"
        f"Evaluation criteria:\n{prompt}"
    )

    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]

    for attempt in range(1, _JUDGE_MAX_RETRIES + 1):
        try:
            result = asyncio.run(
                call_llm_by_model(
                    messages=messages,
                    providers_state=ctx.providers_state,
                    model=judge_model,
                    timeout=60.0,
                )
            )
            break
        except litellm.RateLimitError:
            if attempt == _JUDGE_MAX_RETRIES:
                raise _EvalRateLimitError("Rate limit exceeded — try again later.")
            wait = _JUDGE_RETRY_BASE_DELAY * (2 ** (attempt - 1))
            logger.warning(
                "Judge rate-limited (attempt %d/%d); retrying in %.0fs.",
                attempt,
                _JUDGE_MAX_RETRIES,
                wait,
            )
            time.sleep(wait)

    content = result.choices[0].message.content.strip()
    first_line = content.split("\n")[0].strip().upper()
    passed = first_line.startswith("YES")
    reason = content if not passed else None
    return passed, reason


def _cosine_similarity(a: List[float], b: List[float]) -> float:
    """Compute cosine similarity between two vectors."""
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x * x for x in a) ** 0.5
    norm_b = sum(y * y for y in b) ** 0.5
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot / (norm_a * norm_b)


# ── DSL injected-globals factories ───────────────────────────────────────────


def _make_eval_fn(suite_config: SuiteConfig):
    """Return the ``eval()`` configuration function for script injection."""

    def eval_fn(  # noqa: A001
        *,
        repeat: int = 1,
        threshold: int = 1,
        model: Optional[str] = None,
        judge_model: Optional[str] = None,
        delay: float = 1.0,
    ):
        suite_config.repeat = repeat
        suite_config.threshold = threshold
        suite_config.model = model
        suite_config.judge_model = judge_model
        suite_config.delay = delay

    return eval_fn


def _make_step_fn():
    """Return the ``step()`` / ``question()`` / ``response_to()`` factory."""

    def step_fn(text=None, image=None, audio=None, **kwargs):
        return StepContext(text=text, image=image, audio=audio, **kwargs)

    return step_fn


def _make_expect_fn():
    """Return the ``expect()`` function for script injection."""

    def expect_fn(value):
        ctx = _tls.ctx

        if ctx.current_step is None:
            raise RuntimeError(
                "expect() must be called inside a 'with step():' block"
            )

        response = ctx.current_response or ""
        check: Dict[str, Any] = {}

        if isinstance(value, str):
            matched = bool(re.search(value, response))
            check = {"type": "regexp", "pattern": value, "passed": matched}
            if not matched:
                check["reason"] = f"Pattern {value!r} not found in response"

        elif callable(value):
            if getattr(value, "_is_judge", False):
                judge_prompt = value._judge_prompt
                if judge_prompt is None:
                    judge_prompt = (
                        ctx.case_docstring
                        or "Does the response meet quality standards?"
                    )
                passed, reason = _run_judge(ctx, response, judge_prompt)
                check = {
                    "type": "judge",
                    "prompt": judge_prompt,
                    "passed": passed,
                }
                if reason:
                    check["reason"] = reason

            elif getattr(value, "_is_similar_to", False):
                from common.search import _embed_query

                try:
                    ref_vec = _embed_query(value._reference_text)
                    resp_vec = _embed_query(response[:2000])
                    similarity = _cosine_similarity(ref_vec, resp_vec)
                    passed = similarity >= value._threshold
                    check = {
                        "type": "similar_to",
                        "reference": value._reference_text,
                        "threshold": value._threshold,
                        "similarity": round(similarity, 4),
                        "passed": passed,
                    }
                    if not passed:
                        check["reason"] = (
                            f"Similarity {similarity:.4f} < "
                            f"threshold {value._threshold}"
                        )
                except Exception as e:
                    check = {
                        "type": "similar_to",
                        "passed": False,
                        "reason": str(e),
                    }

            else:
                # User-supplied callable
                try:
                    result = value(response)
                    if isinstance(result, tuple) and len(result) == 2:
                        passed, reason = result
                        passed = bool(passed)
                    else:
                        passed = bool(result)
                        reason = None
                    check = {"type": "callable", "passed": passed}
                    if reason:
                        check["reason"] = str(reason)
                except Exception as e:
                    check = {
                        "type": "callable",
                        "passed": False,
                        "reason": str(e),
                    }

        else:
            raise TypeError(
                f"expect() value must be a string or callable, "
                f"got {type(value).__name__}"
            )

        ctx.current_step._checks.append(check)

    return expect_fn


def _make_assume_fn():
    """Return the ``assume()`` function for script injection."""

    def assume_fn(text: str):
        ctx = _tls.ctx
        _send_assume(ctx, text)

    return assume_fn


def _make_similar_to_fn():
    """Return the ``similar_to()`` factory for script injection."""

    def similar_to_fn(text: str, threshold: float):
        def _checker(response: str):
            pass  # never called directly; handled inside expect_fn

        _checker._is_similar_to = True
        _checker._reference_text = text
        _checker._threshold = threshold
        return _checker

    return similar_to_fn


def _make_judge_fn():
    """Return the ``judge()`` factory for script injection."""

    def judge_fn(prompt: Optional[str] = None):
        def _checker(response: str):
            pass  # never called directly; handled inside expect_fn

        _checker._is_judge = True
        _checker._judge_prompt = prompt
        return _checker

    return judge_fn


# ── Script parsing ────────────────────────────────────────────────────────────


def find_eval_script(cortex_path: str) -> Optional[Path]:
    """Return the path to ``cortex/chat/eval.py``, or ``None`` if not found."""
    if not cortex_path:
        return None
    p = Path(cortex_path) / "chat" / "eval.py"
    return p if p.exists() else None


def parse_eval_script(script_path: Path) -> ParsedSuite:
    """Parse an ``eval.py`` script and return its suite config and case names.

    Runs the script with no-op DSL globals so that ``eval()`` configuration
    is captured and function definitions are collected without making any LLM
    calls or side effects.
    """
    source = script_path.read_text()
    code = compile(source, str(script_path), "exec")

    suite_config = SuiteConfig()

    class _NopCM:
        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

    module_globals: Dict[str, Any] = {
        "__builtins__": __builtins__,
        "eval": _make_eval_fn(suite_config),  # noqa: A001
        "step": lambda *a, **kw: _NopCM(),
        "question": lambda *a, **kw: _NopCM(),
        "response_to": lambda *a, **kw: _NopCM(),
        "expect": lambda *a, **kw: None,
        "assume": lambda *a, **kw: None,
        "similar_to": lambda t, th: (lambda r: True),
        "judge": lambda p=None: (lambda r: True),
    }

    exec(code, module_globals)  # noqa: S102

    suite_name: Optional[str] = module_globals.get("__doc__")

    cases: List[Tuple[str, Optional[str]]] = []
    for name, obj in module_globals.items():
        if (
            not name.startswith("_")
            and callable(obj)
            and hasattr(obj, "__code__")
            and obj.__code__.co_filename == str(script_path)
        ):
            cases.append((name, obj.__doc__))

    return ParsedSuite(
        suite_name=suite_name,
        config=suite_config,
        cases=cases,
    )


# ── Case execution ────────────────────────────────────────────────────────────


def _execute_case(
    script_path: Path,
    case_name: str,
    ctx: _CaseContext,
) -> None:
    """Execute a single case function with real DSL globals.

    Re-compiles the script so that case functions are bound to the live DSL
    implementations (``step``, ``expect``, etc.) rather than the no-op stubs
    used during parsing.
    """
    source = script_path.read_text()
    code = compile(source, str(script_path), "exec")

    module_globals: Dict[str, Any] = {
        "__builtins__": __builtins__,
        "eval": lambda **kw: None,  # config already parsed; ignore  # noqa: A001
        "step": _make_step_fn(),
        "question": _make_step_fn(),
        "response_to": _make_step_fn(),
        "expect": _make_expect_fn(),
        "assume": _make_assume_fn(),
        "similar_to": _make_similar_to_fn(),
        "judge": _make_judge_fn(),
    }

    exec(code, module_globals)  # noqa: S102

    case_fn = module_globals.get(case_name)
    if case_fn is None:
        raise ValueError(f"Case '{case_name}' not found in {script_path}")

    _tls.ctx = ctx
    try:
        case_fn()
    finally:
        if hasattr(_tls, "ctx"):
            del _tls.ctx


# ── Suite runner ──────────────────────────────────────────────────────────────


def run_eval_suite(
    script_path: Path,
    providers_state: dict,
    case_filter: Optional[str] = None,
    cancellation_checker: Optional[Callable[[], bool]] = None,
    on_case_start: Optional[Callable[[str, int, int], None]] = None,
    on_case_done: Optional[Callable[[str, dict], None]] = None,
) -> dict:
    """Execute the evaluation suite and return the full result dict.

    Args:
        script_path: Path to ``eval.py``.
        providers_state: Provider discovery state (injected from ``api.py``).
        case_filter: If set, only run the case with this name.
        cancellation_checker: Called before each run; return ``True`` to cancel.
        on_case_start: Called with ``(case_name, index, total)`` when starting.
        on_case_done: Called with ``(case_name, case_result)`` when done.

    Returns:
        Result dict matching the GET endpoint's 200 response shape.

    Raises:
        EvalCancelledError: If cancelled.
    """
    from datetime import datetime, timezone

    suite = parse_eval_script(script_path)
    default_provider = providers_state.get("default_provider", "default")

    cases_to_run = suite.cases
    if case_filter:
        cases_to_run = [(n, d) for n, d in suite.cases if n == case_filter]
        if not cases_to_run:
            raise ValueError(f"Case '{case_filter}' not found in eval suite")

    started_at = datetime.now(timezone.utc).isoformat()
    case_results = []
    total = len(cases_to_run)

    for idx, (case_name, case_docstring) in enumerate(cases_to_run):
        if cancellation_checker and cancellation_checker():
            raise EvalCancelledError("Evaluation cancelled")

        if on_case_start:
            on_case_start(case_name, idx, total)

        repeat = suite.config.repeat
        threshold = suite.config.threshold

        runs: List[Dict] = []
        passing_runs = 0

        case_error: Optional[str] = None

        for run_idx in range(repeat):
            if cancellation_checker and cancellation_checker():
                raise EvalCancelledError("Evaluation cancelled")

            conversation_id = f"eval-{uuid.uuid4()}"

            ctx = _CaseContext(
                providers_state=providers_state,
                suite_config=suite.config,
                case_docstring=case_docstring,
                conversation_id=conversation_id,
                cancellation_checker=cancellation_checker,
            )

            try:
                _execute_case(script_path, case_name, ctx)
            except _EvalRateLimitError:
                logger.error(
                    "Case '%s' (run %d) hit a rate limit", case_name, run_idx + 1
                )
                case_error = "Rate limit exceeded — try again later."
                break
            except EvalCancelledError:
                raise
            except Exception as e:
                logger.exception(
                    "Case '%s' (run %d) raised an error", case_name, run_idx + 1
                )
                case_error = str(e)
                break

            # Flatten all step checks into this run's check list
            run_checks: List[Dict] = []
            for step_res in ctx.step_results:
                run_checks.extend(step_res["checks"])

            run_passed = all(s["passed"] for s in ctx.step_results)
            runs.append({"run": run_idx + 1, "checks": run_checks})
            if run_passed:
                passing_runs += 1

        if case_error is not None:
            case_result = {
                "id": case_name,
                "status": "error",
                "error": case_error,
                "runs": runs,
                "passing_runs": passing_runs,
                "threshold": threshold,
            }
        else:
            case_passed = passing_runs >= threshold
            case_result = {
                "id": case_name,
                "status": "pass" if case_passed else "fail",
                "runs": runs,
                "passing_runs": passing_runs,
                "threshold": threshold,
            }
        case_results.append(case_result)

        if on_case_done:
            on_case_done(case_name, case_result)

    completed_at = datetime.now(timezone.utc).isoformat()
    passed = sum(1 for c in case_results if c["status"] == "pass")
    failed = len(case_results) - passed

    return {
        "suite": suite.suite_name,
        "provider": default_provider,
        "started_at": started_at,
        "completed_at": completed_at,
        "passed": passed,
        "failed": failed,
        "total": len(case_results),
        "cases": case_results,
    }
