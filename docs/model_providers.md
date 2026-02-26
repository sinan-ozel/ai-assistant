# Model Provider Configuration

TL;DR: You can simply set up the environmental variable `MISTRAL_API_KEY`.
If you do so, this will use Mistral endpoints, and the built-in providers will be available, as below.
Alternatively, you can create a YAML file (or multiple YAML files) under `providers/` folder in your "cortex".
Each one of these are just keyword arguments to a `litellm.conversation` call, so


## Default Provider Selection Rules

The agent follows a priority-based system to determine the default provider. The rules are evaluated in order, and the first one that succeeds becomes the default provider.

### Priority 1: Custom `default.yaml`

**Location:** `cortex/providers/default.yaml` (mounted volume)

If a `default.yaml` file exists in your mounted cortex providers directory, it will be used as the default provider.

- **Validation:** The provider is tested during startup with a test call
- **On Failure:** The application will log an error and crash
- **Use Case:** When you want to explicitly define your own default provider configuration

**Example - OpenAI:**
```yaml
api_base: https://api.openai.com/v1
model: gpt-4
api_key: ${OPENAI_API_KEY}
```

**Example: Self-Hosted Ollama on Localhost:**
```yaml
api_base: http://localhost:11434
model: ollama/gemma3:270m
```

**Example: Self-Hosted llama.cpp on Localhost:**
```yaml
api_base: http://localhost:8080/v1
model: openai/qwen3-vl:2b-q4km
api_key: dummy
timeout: 150
```

### Priority 2: DEFAULT_PROVIDER Matching Custom Provider

**Location:** `cortex/providers/${DEFAULT_PROVIDER}.yaml` (mounted volume)

**Environment Variable:** `DEFAULT_PROVIDER`

If the `DEFAULT_PROVIDER` environment variable is set and matches a file in your custom providers directory, that provider will be used as the default.

- **Validation:** The provider is tested during startup with a test call
- **On Failure:** The application will log an error and crash
- **Use Case:** When you have multiple custom providers and want to select one as default via environment variable

**Example:**
```bash
export DEFAULT_PROVIDER=local_gemma3_270m
# This will use cortex/providers/local_gemma3_270m.yaml as default
```

**Note:** All provider files in `cortex/providers/` will be registered and available for use, regardless of which one is the default.

### Priority 3: Single Custom Provider

**Location:** `cortex/providers/` (mounted volume)

**Condition:** Only one provider file exists in the custom providers directory

If there is exactly one YAML file in your custom providers directory, and no explicit default has been set via the methods above, the agent will automatically use this single provider as the default.

- **Validation:** The provider is tested during startup with a test call
- **On Failure:** The application will log a warning and continue to check other priority rules
- **Use Case:** Simplified setup when you have only one custom provider - no need to name it `default.yaml` or set `DEFAULT_PROVIDER`

**Example:**
```bash
# Your cortex/providers/ directory contains only:
# - vision.yaml

# The agent will automatically use vision.yaml as the default provider
```

### Priority 4: DEFAULT_PROVIDER Matching Built-in Provider

**Condition:** Only checked if no custom provider matches the DEFAULT_PROVIDER value

**Environment Variable:** `DEFAULT_PROVIDER`

If the `DEFAULT_PROVIDER` environment variable is set and matches a built-in provider (after checking for custom providers), the agent will use that provider.

- **Location:** `agent_stem/default/providers/${DEFAULT_PROVIDER}.yaml`
- **Validation:** The provider is tested during startup with a test call
- **On Failure:**
  - If the provider file doesn't exist: logs an error and crashes, listing available custom and built-in providers
  - If validation fails: logs an error but continues to Priority 4
- **Error Details:** If the provider fails or doesn't exist, the error message will:
  - List available custom provider names (if any)
  - List available built-in provider names
  - Explain how to create a custom provider via `cortex/providers/default.yaml`
  - Clarify that provider file properties are keyword arguments to LiteLLM

**Example:**
```bash
export DEFAULT_PROVIDER=mistral-small
```

**Built-in Providers:**
- `large` - Large language model
- `small` - Small/efficient language model
- `default` - Default Mistral model
- `vision` - Vision-capable model
- `coding` - Code-optimized model
- `reasoning` - Reasoning-optimized model
- `evaluation` - Evaluation/judge model for use in evaluation
- `instruction-following` - Instruction-following models.

Note that you do not have to use these, they are just provided to be a focal point.
For simpler workflows and agents, simply set up `default.yaml`, or just `your_preferred_label.yaml`,
but if you use your own name, set `DEFAULT_PROVIDER`=`your_preferred_label`

### Priority 5: Fallback to Built-in Default

**Location:** `agent_stem/default/providers/default.yaml`

If none of the above rules provide a working provider, the agent falls back to the built-in `default.yaml` provider configuration.

- **Validation:** The provider is tested during startup with a test call
- **On API Key Missing:** If the failure is due to a missing API key (e.g., `MISTRAL_API_KEY` not set), the application will log a **warning** (not error) and continue to run in **tools-only mode** without crashing. The warning will explain that abilities are restricted to tools only.
- **On Other Failures:** If the failure is due to other issues (network, invalid configuration, etc.), the application will log an error and crash.
- **Error/Warning Details:** The message will explain:
  - That you need to set up the `MISTRAL_API_KEY` environment variable, OR
  - That you can create your own `cortex/providers/default.yaml` file
  - List of available built-in provider names

**Default Configuration:**
```yaml
api_base: https://api.mistral.ai
model: mistral/mistral-large-2512
api_key: ${MISTRAL_API_KEY}
```

## Running Without a Model (Tools-Only Mode)

If the providers folder is empty and `MISTRAL_API_KEY` is not set, the agent will run in tools-only mode:

- **Behavior:** No language model is available, but tools can still be used
- **Restrictions:** Functions that require LLM capabilities will not be available
- **Warning:** A warning message will be logged at startup explaining the limited functionality
- **Use Case:** Useful for testing tool integrations or running in environments where LLM access is not needed

To enable full LLM capabilities from this state:
1. Set the `MISTRAL_API_KEY` environment variable, OR
2. Create a `cortex/providers/default.yaml` file with your provider configuration

## Creating Custom Providers

### Provider File Format

Provider files are YAML files with configuration that gets passed as keyword arguments to [LiteLLM](https://docs.litellm.ai/).

**Required Fields:**
- `model`: The model identifier (e.g., `gpt-4`, `mistral/mistral-small`)

**Common Fields:**
- `api_base`: Base URL for the API endpoint
- `api_key`: API key (can use `${ENV_VAR}` syntax)
- `max_tokens`: Maximum tokens for responses
- `timeout`: Request timeout in seconds

**Example with Environment Variable:**
```yaml
api_base: https://api.anthropic.com
model: claude-3-opus-20240229
api_key: ${ANTHROPIC_API_KEY}
max_tokens: 4096
```

**Example with Local Model:**
```yaml
api_base: http://localhost:11434
model: ollama/llama2
```

### Disabling a Provider

To disable a provider without deleting the file, add `_enabled: false`:

```yaml
_enabled: false
model: some-model
api_key: ${API_KEY}
```

## Using Providers in Workflows

Once a provider is configured and validated during startup, it can be referenced in your workflows by name.

The default provider is automatically available and can be used without specifying a provider name explicitly.

## Environment Variables

The agent supports environment variable substitution in provider configurations using the `${VAR_NAME}` syntax.

**Example:**
```yaml
model: gpt-4
api_key: ${OPENAI_API_KEY}
api_base: ${OPENAI_BASE_URL}
```

If the environment variable is not set, the original `${VAR_NAME}` string will remain, and the provider will fail API key validation.

## Troubleshooting

### Provider Validation Failed

If a provider fails validation during startup, check:

1. **API Key:** Ensure the required environment variable is set
2. **Network:** Verify the API endpoint is reachable
3. **Model Name:** Confirm the model identifier is correct
4. **API Base:** Check if the `api_base` URL is correct

### No Default Provider

If no default provider can be determined:

1. Create a `cortex/providers/default.yaml` file with your provider configuration
2. OR set the `DEFAULT_PROVIDER` environment variable to select one of your custom providers
3. OR set the `MISTRAL_API_KEY` environment variable to use the built-in default
4. OR set the `DEFAULT_PROVIDER` environment variable to one of the built-in providers

### Multiple Providers Available

If you have multiple provider files in `cortex/providers/`:

- Name one of them `default.yaml` to make it the default
- OR set the `DEFAULT_PROVIDER` environment variable to the name (without `.yaml`) of the provider you want as default
- All providers in the directory will be registered and available for use

## Summary

The default provider selection follows this decision tree:

```
1. Is there cortex/providers/default.yaml?
   YES → Use it (crash if fails)
   NO → Continue to 2

2. Is DEFAULT_PROVIDER env set and matches cortex/providers/${DEFAULT_PROVIDER}.yaml?
   YES → Use it (crash if fails)
   NO → Continue to 3

3. Is DEFAULT_PROVIDER env set and matches agent_stem/default/providers/${DEFAULT_PROVIDER}.yaml?
   YES (file exists) → Try it
      AVAILABLE → Use it
      FAILED → Log error, continue to 4
   YES (file doesn't exist) → Log error and crash (lists available providers)
   NO → Continue to 4

4. Use agent_stem/default/providers/default.yaml
   AVAILABLE → Use it
   FAILED (API key missing) → Log warning, run in tools-only mode (don't crash)
   FAILED (other reason) → Log error and crash
```

This ensures that:
- Custom configurations always take precedence
- Simple single-provider setups work automatically
- Environment-based configuration is supported
- The system can run in tools-only mode when no LLM is configured
- There's always a fallback (with proper error/warning messages)
