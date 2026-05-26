# Agent Evaluation DSL

The evaluation DSL lets you write test cases for your agent in plain Python, placed at
`cortex/chat/eval.py` — right next to `prompt.py`.

## Quick start

```python
"""My agent evaluation suite."""

eval(repeat=2, threshold=1)


def greets_user():
    with question("Hello!"):
        expect(r"(?i)hello|hi|hey")


def answers_math():
    with question("What is 2 + 2?"):
        expect(r"\b4\b|four")
```

Start a run:

```bash
curl -X POST http://localhost:8000/private/v1/agent/evaluate
```

Poll for results:

```bash
curl http://localhost:8000/private/v1/agent/evaluate
```

---

## The `eval.py` file

Place it at `cortex/chat/eval.py`. No imports, no boilerplate.

The **module docstring** becomes the suite name.  
`eval(...)` at module level sets suite-wide configuration.  
Every **function whose name does not start with `_`** is collected as a test case, in
definition order.

```python
"""Nutrition label extraction suite."""

eval(repeat=3, threshold=2)


def greeting_basic():
    with step("Hello!"):
        expect("hello")
        expect(r"hell[o0]")
        expect(similar_to("a warm greeting", 0.8))


def calories_label():
    """The response must identify 180 calories and a valid serving size."""
    with step("How many calories does this have?"):
        expect("180")
        expect(judge())         # prompt defaults to the docstring above


def multi_turn_memory():
    assume("My name is Alice.")
    with question("What is my name?"):
        expect("Alice")
    with response_to("What city do I live in?"):
        expect(judge("Should admit it does not know — not invent a city."))


def _helper():
    # Starts with _ — never collected as a case.
    return "some/shared/value"
```

---

## Injected globals

No imports are required inside `eval.py`. The following names are always available:

| Name | Description |
|---|---|
| `eval(...)` | Suite-level configuration |
| `step(text?, image?, audio?, **kwargs)` | Context manager: send a turn, collect checks |
| `question(...)` | Alias for `step` |
| `response_to(...)` | Alias for `step` |
| `expect(value)` | Attach a check to the enclosing step |
| `assume(text)` | Send a turn, discard the response |
| `similar_to(text, threshold)` | Embedding cosine-similarity checker |
| `judge(prompt?)` | LLM-as-judge checker |

Any standard Python — imports, variables, loops, conditionals — also works inside the file.

---

## `eval()` — suite configuration

```python
eval(
    repeat=3,           # how many times to run each case
    threshold=2,        # minimum passing runs required
    model=None,         # override the agent model for this suite
    judge_model=None,   # model used for judge() calls; defaults to agent model
)
```

Defaults are `repeat=1`, `threshold=1`.

---

## Cases

Any module-level function whose name does **not** start with `_` is a test case.
The function name (with underscores) is used as the case ID in the report.

```python
def it_greets_politely():   # case ID: "it_greets_politely"
    ...

def _build_prompt(n):       # not a case
    ...
```

Case functions may call any Python code. The DSL primitives are ordinary functions that
compose naturally with loops, conditionals, and helper functions.

---

## Steps — `step()`, `question()`, `response_to()`

All three are identical. Each sends one turn to the agent. Subsequent steps within the
same case continue the same conversation, so multi-turn memory is tested naturally.

```python
with step("What is the capital of France?"):
    expect("Paris")

with question("What is the capital of France?"):   # reads as Q&A
    expect("Paris")

with response_to("My name is Alice. What is it?"):  # reads as conversation
    expect("Alice")
```

Arguments:

```python
step(text="...", image="path/to/image", audio="path/to/audio", max_tokens=1024)
```

> **Note:** `image` and `audio` arguments are not yet supported in the Python DSL.
> Use the YAML-based workflow evaluation for image inputs.

---

## `assume()` — conversation setup without evaluation

Sends a turn to the agent and discards the response. Use it to establish context
before the evaluated steps.

```python
def followup_context():
    assume("My name is Alice.")
    assume("I live in Montreal.")
    with question("What city am I in?"):
        expect("Montreal")
```

---

## `expect()` — three check types

### String → regexp match

```python
expect("Paris")               # substring: passes if "Paris" appears anywhere
expect(r"\b\d{3}\b")          # passes if a 3-digit number appears
expect(r"(?i)hello")          # case-insensitive match
```

### Callable → call with response, pass if truthy

```python
def valid_json(response):
    import json
    try:
        json.loads(response)
        return True
    except Exception:
        return False, "response was not valid JSON"

expect(valid_json)
expect(lambda r: len(r) > 20)
```

The callable receives the response string. If it returns a `(bool, reason)` tuple,
the reason appears in the report on failure.

### `similar_to(text, threshold)` → embedding similarity

Passes if the cosine similarity between the response embedding and the reference text
embedding is ≥ `threshold`. Uses the in-process fastembed model.

```python
expect(similar_to("a polite refusal", 0.82))
```

### `judge(prompt?)` → LLM-as-judge

Sends the response to a judge model with a grading prompt. Passes if the verdict is
affirmative.

```python
expect(judge("Did the agent correctly identify the calorie count?"))
```

If called with no argument, the judge prompt is taken from the **case function's
docstring**:

```python
def calories_label():
    """The response must identify 180 calories and a serving size in grams."""
    with step("How many calories?"):
        expect(judge())   # uses the docstring above
```

The judge model is selected in this order:
1. `judge_model=` from `eval()`
2. A provider named `evaluation` in `cortex/providers/`
3. The `DEFAULT_PROVIDER` environment variable
4. The `default` provider

---

## HTTP API

At most one evaluation run is active at a time.

### `POST /private/v1/agent/evaluate`

Starts a run. Returns `202 Accepted` or `409 Conflict` if a run is already active.

```bash
# Run all cases
curl -X POST http://localhost:8000/private/v1/agent/evaluate

# Run a single case
curl -X POST http://localhost:8000/private/v1/agent/evaluate \
  -H "Content-Type: application/json" \
  -d '{"case": "calories_label"}'
```

### `GET /private/v1/agent/evaluate`

Returns results from the last completed run, or a progress snapshot if running.

```bash
curl http://localhost:8000/private/v1/agent/evaluate
```

Status codes: `200` (results), `202` (still running — retry after a few seconds), `404` (no run yet).

### `DELETE /private/v1/agent/evaluate`

Cancels the in-progress run after the current step completes.

```bash
curl -X DELETE http://localhost:8000/private/v1/agent/evaluate
```

---

## Example result

```json
{
  "suite": "Nutrition label extraction suite",
  "provider": "default",
  "started_at": "2025-04-01T14:00:00Z",
  "completed_at": "2025-04-01T14:01:43Z",
  "passed": 2,
  "failed": 1,
  "total": 3,
  "cases": [
    {
      "id": "greeting_basic",
      "status": "pass",
      "runs": [
        { "run": 1, "checks": [{ "type": "regexp", "pattern": "hello", "passed": true }] },
        { "run": 2, "checks": [{ "type": "regexp", "pattern": "hello", "passed": true }] }
      ],
      "passing_runs": 2,
      "threshold": 1
    }
  ]
}
```
