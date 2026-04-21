# REFERENCE EXAMPLE - Not executed by default
#
# This file demonstrates advanced DSL patterns (Level 12).
# To use it, rename to "prompt.py" or "agent.py"
#
# The DSL loader only looks for:
#   - prompt.py (preferred)
#   - agent.py (fallback)
#
# Keep this file as a reference for advanced techniques.

"""
You are an adaptive reasoning agent that can use tools and adjust your behavior
based on the type of question asked.
"""

# Level 12 - Full hacker mode example
# Dynamic configuration based on input content

# Adjust model and parameters
agent.temperature = 0.3
agent.max_tokens = 1000

# Dynamic routing based on content
if any(word in input_text.lower() for word in ["calculate", "compute", "math"]):
    agent.use_tools("calculator")
    agent.tool_choice = "calculator"

if "http" in input_text or "url" in input_text.lower():
    agent.use_tools("web_search")

# Memory compression for long conversations
if len(message_history) > 10:
    # Keep only recent messages to fit context
    recent_summary = f"[Earlier messages: {len(message_history) - 6} messages summarized]"
    message_history[:] = [
        {"role": "system", "content": recent_summary}
    ] + message_history[-6:]

# Enhanced prompt with context
if message_history:
    context_count = len(message_history)
    print(f"[Context: {context_count} prior messages available]")
    print()

print(f"Task: {input_text}")
