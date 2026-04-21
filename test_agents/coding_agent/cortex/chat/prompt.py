"""You are an expert coding assistant powered by Mistral Codestral.

You write clear, correct, and idiomatic code. Always wrap code samples in
markdown code blocks with the appropriate language tag.
"""

# Use _override to inject a focused coding system prompt and pass the
# user message through unchanged.  This demonstrates the _override DSL
# feature documented in agent_stem/src/common/DSL.md.
_override = {
    "messages": [
        {
            "role": "system",
            "content": __doc__,
        },
        {
            "role": "user",
            "content": input_text,
        },
    ],
}
