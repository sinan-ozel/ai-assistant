"""
Prompt compilation utilities.

Builds LLM prompts from:
- System instructions
- Retrieved context
- Conversation history
- User input
"""

from typing import List, Dict, Any


def build_prompt(
    system: str,
    history: List[Dict[str, Any]],
    retrieved: List[Dict[str, Any]],
    user_input: str,
) -> List[Dict[str, str]]:
    """
    Build a prompt for the LLM.

    Args:
        system: System instruction
        history: Recent conversation messages
        retrieved: Semantically retrieved context
        user_input: Current user message

    Returns:
        List of messages in OpenAI format
    """
    messages = [{"role": "system", "content": system}]

    # Add retrieved context as system messages
    for item in retrieved:
        context_text = item.get("text", str(item))
        messages.append({
            "role": "system",
            "content": f"Relevant context: {context_text}"
        })

    # Add conversation history
    for msg in history:
        # Extract role and content, handling different formats
        if "role" in msg and "content" in msg:
            messages.append({
                "role": msg["role"],
                "content": msg["content"],
            })

    # Add current user input
    messages.append({"role": "user", "content": user_input})

    return messages
