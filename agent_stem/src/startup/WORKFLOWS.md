# Workflows

Workflows are YAML files that turn an LLM prompt into a typed API endpoint. Each workflow file in `cortex/workflows/` is automatically discovered at startup and registered as a `POST` endpoint.

## File location

```
cortex/
  workflows/
    summarize_text.yaml
    book_metadata_extraction.yaml
    nutrition_information_extraction.yaml
```

Files starting with `_` are ignored. Subdirectories are scanned recursively.

---

## YAML reference

### Required fields

| Field | Type | Description |
|---|---|---|
| `name` | string | Internal identifier. Used in API responses and logs. |
| `path` | string | The URL path for the endpoint, e.g. `/v1/extract-book-metadata` |
| `description` | string | Human-readable description, shown in the OpenAPI docs |
| `output_schema` | object | JSON Schema for the LLM's output (see below) |
| `execution` | object | How the LLM is called (see below) |

### Optional fields

| Field | Type | Description |
|---|---|---|
| `provider` | string | Name of the provider to use. Must match a filename in `cortex/providers/` (without `.yaml`). If omitted, the default provider is used. |
| `timeout` | number | Request timeout in seconds, overrides the provider's timeout |
| `input_requirements` | object | Declares what input content types the endpoint accepts. Used only for documentation and example generation — not validated at runtime. |

---

## `output_schema`

Standard JSON Schema. Two shapes are supported:

**String output** — the LLM returns plain text:

```yaml
output_schema:
  type: string
```

**Object output** — the LLM returns JSON, which is parsed and validated against the schema before returning:

```yaml
output_schema:
  type: object
  properties:
    title:
      type: string
      description: The title of the book.
    author:
      type: string
      description: The author of the book.
    series_number:
      type: integer
  required: [title, author]
```

For object schemas, the system instructs the LLM to return valid JSON and enables JSON mode on providers that support it. The response is validated with `jsonschema` before being returned. If parsing or validation fails, the endpoint returns `400` with the raw LLM response for debugging.

---

## `execution`

Only `type: prompt` is currently supported.

```yaml
execution:
  type: prompt
  prompt: |
    Clean up and summarize the user message in less than 50 words.
```

The prompt becomes the **system message**. The output schema instructions are appended to it automatically — you do not need to describe the output format in the prompt.

For object schemas, the appended instruction shows the LLM a concrete JSON example derived from the schema. For string schemas, it tells the LLM to return plain text with no formatting.

---

## `input_requirements`

Optional. Documents what the endpoint expects. Currently used only for generating the OpenAPI example request body.

```yaml
input_requirements:
  content_types: [image]
  description: Requires one image of a book cover
```

Supported `content_types` values: `text` (default), `image`. When `image` is listed, the generated OpenAPI example uses a multimodal message with a base64-encoded JPEG.

---

## `provider`

Refers to a file in `cortex/providers/` by stem name:

```yaml
provider: vision
# → uses cortex/providers/vision.yaml
```

If omitted, the default provider is used (see provider discovery rules in `providers.py`). This is the standard way to route a workflow to a vision-capable model while keeping a different default for text-only workflows.

---

## `evaluation`

Optional. Adds test cases that can be triggered via `POST /private/evaluate{path}`.

```yaml
evaluation:
  repeat: 2       # how many times to run each case
  threshold: 2    # how many runs must pass for the case to pass
  cases:
    - id: my-test-case
      steps:
        - input:
            image_path: "evaluation/images/my-image.jpeg"
            max_tokens: 2048
          expectations:
            - type: equals
              value:
                calories: 180
                serving_size: 40.0
                unit: g
            - type: oneOf
              values:
                - calories: 180
                  unit: g
                - calories: 180
                  unit: pieces
```

`image_path` is resolved relative to the workflow YAML file. Supported expectation types: `equals`, `contains`, `oneOf`, `regex`, `in_range`, `approx_pct`.

---

## Request format

Every workflow endpoint accepts the same request body:

```json
{
  "messages": [
    {"role": "user", "content": "Your text here"}
  ],
  "temperature": 0.7,
  "max_tokens": 4096,
  "stream": false,
  "stream_format": "sse"
}
```

For image input, use the OpenAI multimodal format:

```json
{
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "type": "image_url",
          "image_url": {"url": "data:image/jpeg;base64,<base64>"}
        }
      ]
    }
  ]
}
```

`model` is accepted but may be ignored if the workflow specifies a `provider`.

---

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

`result` is a string for `output_schema.type: string`, or a parsed JSON object for `output_schema.type: object`.

---

## Streaming

Set `"stream": true` to stream the response. Use `"stream_format"` to choose the wire format (`"sse"` or `"ndjson"`).

For **string** output schemas, content delta chunks are emitted token by token, followed by a final chunk with the full `result`. For **object** output schemas, delta content is suppressed during streaming and the complete parsed JSON is sent as a single final chunk (streaming is only useful here for connection keep-alive, not progressive rendering).

---

## Examples

### Text output

```yaml
name: summarize_text_small
path: /v1/summarize-text
description: Summarizes the given text into a concise summary.

output_schema:
  type: string

execution:
  type: prompt
  prompt: |
    Clean up and summarize the user message in less than 50 words.
```

### Object output with image input and a named provider

```yaml
name: book_metadata_extraction
path: /v1/extract-book-metadata
description: Takes an image of a book cover and extracts the book metadata as JSON.
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
    subtitle:
      type: string
    publisher:
      type: string
    series_title:
      type: string
    series_number:
      type: integer
  required: [title, author]

execution:
  type: prompt
  prompt: |
    The image is a book cover.
    Extract the book metadata and return it as a JSON object.
```

### Object output with evaluation

```yaml
name: nutrition_information_extraction
path: /v1/extract-nutrition-information
description: Takes an image of a packaged food product label and extracts the nutrition information as JSON.
provider: vision

input_requirements:
  content_types: [image]

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

execution:
  type: prompt
  prompt: |
    Extract nutrition facts and return ONLY a JSON object.

evaluation:
  repeat: 2
  threshold: 2
  cases:
    - id: calories-label-180
      steps:
        - input:
            image_path: "evaluation/images/my-label.jpeg"
            max_tokens: 2048
          expectations:
            - type: oneOf
              values:
                - {calories: 180, serving_size: 40.0, unit: g}
                - {calories: 180, serving_size: 2.0, unit: pieces}
```
