# ACTIVE PROMPT DSL SCRIPT
# This file is the agent's system message and response logic.
# See agent_stem/src/startup/PROVIDERS.md for provider configuration.

"""You are a helpful AI assistant. Answer questions clearly and concisely.
If you do not know the answer, say so rather than guessing."""

with MessageHistory(3):
    response = prompt()
