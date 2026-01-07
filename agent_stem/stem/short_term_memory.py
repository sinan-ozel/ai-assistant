"""
Redis-backed short-term (conversation) memory implementation.

Uses redis-memory's ConversationMemory for:
- Multiprocessing-safe state
- Automatic persistence
- Background sync with resilience
"""

import json
from typing import List, Dict, Any
from redis_memory import ConversationMemory
from .memory import Memory


class RedisShortTermMemory(Memory):
    """
    Short-term memory backed by Redis.

    Stores conversation history with identity isolation.
    Retrieval is conversation-scoped only.
    """

    def __init__(self, redis_host: str = "redis", redis_port: int = 6379):
        """
        Initialize Redis short-term memory.

        Args:
            redis_host: Redis server hostname
            redis_port: Redis server port
        """
        self.redis_host = redis_host
        self.redis_port = redis_port
        # We'll create ConversationMemory instances per conversation

    def _get_conversation_key(self, user_id: str, conversation_id: str) -> str:
        """Generate a unique key for a conversation."""
        return f"{user_id}:{conversation_id}"

    def _get_memory(self, user_id: str, conversation_id: str) -> ConversationMemory:
        """Get or create a ConversationMemory instance."""
        conv_key = self._get_conversation_key(user_id, conversation_id)
        return ConversationMemory(conversation_id=conv_key)

    def add(
        self,
        *,
        user_id: str,
        conversation_id: str,
        item: Dict[str, Any],
    ) -> None:
        """
        Add an item to the conversation history.

        Items are appended to a list in Redis, preserving order.
        """
        mem = self._get_memory(user_id, conversation_id)

        # Get existing messages or initialize empty list
        if not hasattr(mem, "messages"):
            mem.messages = []

        messages = mem.messages
        if not isinstance(messages, list):
            messages = []

        # Append new message with metadata
        messages.append({
            "user_id": user_id,
            "conversation_id": conversation_id,
            **item,
        })

        # Write back to Redis
        mem.messages = messages

    def recent(
        self,
        *,
        user_id: str,
        conversation_id: str,
        k: int,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve the k most recent messages from the conversation.

        Returns messages in chronological order (oldest to newest).
        """
        mem = self._get_memory(user_id, conversation_id)

        # Get messages or return empty list
        if not hasattr(mem, "messages"):
            return []

        messages = mem.messages
        if not isinstance(messages, list):
            return []

        # Return last k messages
        return messages[-k:] if k < len(messages) else messages

    def retrieve(
        self,
        *,
        user_id: str,
        query: str,
        k: int,
    ) -> List[Dict[str, Any]]:
        """
        Short-term memory does not support semantic retrieval.

        Returns empty list. Use long-term memory for RAG.
        """
        return []
