"""
Abstract memory interface for agent memory systems.

This defines the contract that both short-term and long-term memory
implementations must fulfill.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any


class Memory(ABC):
    """
    Abstract base class for agent memory.

    All memory implementations must support:
    - Identity-aware storage (user_id, conversation_id)
    - Recent retrieval (temporal)
    - Semantic retrieval (RAG)
    """

    @abstractmethod
    def add(
        self,
        *,
        user_id: str,
        conversation_id: str,
        item: Dict[str, Any],
    ) -> None:
        """
        Add an item to memory.

        Args:
            user_id: Stable user identifier
            conversation_id: Conversation/session identifier
            item: Memory item (typically contains role, content, etc.)
        """
        pass

    @abstractmethod
    def recent(
        self,
        *,
        user_id: str,
        conversation_id: str,
        k: int,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve the k most recent items for a conversation.

        Args:
            user_id: User identifier
            conversation_id: Conversation identifier
            k: Number of recent items to retrieve

        Returns:
            List of recent memory items, oldest to newest
        """
        pass

    @abstractmethod
    def retrieve(
        self,
        *,
        user_id: str,
        query: str,
        k: int,
    ) -> List[Dict[str, Any]]:
        """
        Semantically retrieve relevant items across all conversations.

        Args:
            user_id: User identifier (for isolation)
            query: Semantic query string
            k: Number of items to retrieve

        Returns:
            List of relevant memory items, sorted by relevance
        """
        pass
