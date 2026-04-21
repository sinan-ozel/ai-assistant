# Workflows

Workflows turn an LLM prompt into a typed POST endpoint. Each YAML file in
`cortex/workflows/` is auto-discovered at startup and registered as an endpoint.

## Quick example

```yaml
# cortex/workflows/summarize_text.yaml
name: summarize_text
path: /v1/summarize-text
description: Summarizes the given text into a concise summary.

output_schema:
  type: string

execution:
  type: prompt
  prompt: |
    Clean up and summarize the user message in less than 50 words.
```

Call it:

```bash
curl -X POST http://localhost:8000/v1/summarize-text \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "Long text to summarize..."}]}'
```

## Structured JSON output

```yaml
name: extract_book_metadata
path: /v1/extract-book-metadata
description: Extracts book metadata from a cover image.
provider: vision

input_requirements:
  content_types: [image]
  description: Requires one image of a book cover

output_schema:
  type: object
  properties:
    title:
      type: string
    author:
      type: string
    publisher:
      type: string
  required: [title, author]

execution:
  type: prompt
  prompt: |
    Extract the book metadata from this cover image. Return only JSON.
```

## YAML reference

### Required fields

| Field | Description |
|---|---|
| `name` | Internal identifier, shown in logs |
| `path` | URL path for the endpoint (e.g. `/v1/my-task`) |
| `description` | Human-readable description, shown in Swagger UI |
| `output_schema` | JSON Schema for the LLM output |
| `execution` | How the LLM is called |

### Optional fields

| Field | Description |
|---|---|
| `provider` | Name of the provider YAML to use (without `.yaml`). Defaults to the default provider. |
| `timeout` | Request timeout in seconds |
| `input_requirements` | Documents accepted input content types (for OpenAPI example generation) |
| `evaluation` | Test cases for the evaluation pipeline |

## Output schema

**String output** — the LLM returns plain text:

```yaml
output_schema:
  type: string
```

**Object output** — the LLM returns JSON, validated before returning:

```yaml
output_schema:
  type: object
  properties:
    calories:
      type: integer
    serving_size:
      type: number
    unit:
      type: string
  required: [calories, serving_size, unit]
```

For object schemas, JSON mode is enabled on providers that support it, and the response
is validated with `jsonschema`. If parsing or validation fails, the endpoint returns `400`
with the raw LLM response for debugging.

## Execution

Only `type: prompt` is currently supported. The `prompt` string becomes the system message.
Output format instructions are appended automatically — do not describe the output format in
your prompt.

```yaml
execution:
  type: prompt
  prompt: |
    Extract nutrition facts from this food label.
    Be precise with numeric values.
```

## Using a named provider

Route a workflow to a specific provider (e.g. a vision-capable model):

```yaml
provider: vision
# → uses cortex/providers/vision.yaml
```

## Evaluation

Add test cases directly to the workflow YAML. Run them via `POST /private/evaluate{path}`.

```yaml
evaluation:
  repeat: 2
  threshold: 2
  cases:
    - id: calorie-label-test
      steps:
        - input:
            image_path: "evaluation/images/label.jpeg"
            max_tokens: 2048
          expectations:
            - type: oneOf
              values:
                - {calories: 180, serving_size: 40.0, unit: g}
                - {calories: 180, serving_size: 2.0, unit: pieces}
```

`image_path` is resolved relative to the workflow YAML file. Supported expectation types:
`equals`, `contains`, `oneOf`, `regex`, `in_range`, `approx_pct`.

## Request format

All workflow endpoints accept the same request body:

```json
{
  "messages": [{"role": "user", "content": "Your text here"}],
  "temperature": 0.7,
  "max_tokens": 4096,
  "stream": false,
  "stream_format": "sse"
}
```

For image input, use the OpenAI multimodal format:

```json
{
  "messages": [{
    "role": "user",
    "content": [{"type": "image_url", "image_url": {"url": "data:image/jpeg;base64,..."}}]
  }]
}
```

## Response format

```json
{
  "result": "...",
  "usage": {
    "prompt_tokens": 56,
    "completion_tokens": 31,
    "total_tokens": 87
  }
}
```

`result` is a string for `output_schema.type: string`, or a parsed JSON object for
`output_schema.type: object`.
