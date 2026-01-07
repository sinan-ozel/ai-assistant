"""
Qdrant-backed long-term (semantic) memory implementation.

Provides:
- Vector embeddings for semantic retrieval
- User-scoped, cross-conversation memory
- Metadata filtering
"""

import uuid
from typing import List, Dict, Any, Callable
from qdrant_client import QdrantClient
from qdrant_client.models import (
    VectorParams,
    Distance,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
)
from .memory import Memory


class QdrantLongTermMemory(Memory):
    """
    Long-term memory backed by Qdrant vector database.

    Stores facts/observations with embeddings for semantic retrieval.
    Retrieval is user-scoped but cross-conversation.
    """

    def __init__(
        self,
        collection: str,
        embedding_fn: Callable[[str], List[float]],
        qdrant_host: str = "qdrant",
        qdrant_port: int = 6333,
        vector_size: int = 1536,
    ):
        """
        Initialize Qdrant long-term memory.

        Args:
            collection: Qdrant collection name
            embedding_fn: Function that takes text and returns vector
            qdrant_host: Qdrant server hostname
            qdrant_port: Qdrant server port
            vector_size: Embedding dimension
        """
        self.collection = collection
        self.embed = embedding_fn
        self.vector_size = vector_size

        # Connect to Qdrant
        self.client = QdrantClient(host=qdrant_host, port=qdrant_port)

        # Create collection if it doesn't exist
        try:
            self.client.get_collection(collection_name=collection)
        except Exception:
            self.client.create_collection(
                collection_name=collection,
                vectors_config=VectorParams(
                    size=vector_size,
                    distance=Distance.COSINE,
                ),
            )

    def add(
        self,
        *,
        user_id: str,
        conversation_id: str,
        item: Dict[str, Any],
    ) -> None:
        """
        Add an item to long-term memory with embedding.

        The item must contain a 'text' field for embedding.
        Conversation ID is stored but retrieval is user-scoped.
        """
        if "text" not in item:
            raise ValueError("Item must contain 'text' field for embedding")

        # Generate embedding
        vector = self.embed(item["text"])

        # Prepare payload with metadata
        payload = {
            "user_id": user_id,
            "conversation_id": conversation_id,
            **item,
        }

        # Store in Qdrant
        self.client.upsert(
            collection_name=self.collection,
            points=[
                PointStruct(
                    id=str(uuid.uuid4()),
                    vector=vector,
                    payload=payload,
                )
            ],
        )

    def recent(
        self,
        *,
        user_id: str,
        conversation_id: str,
        k: int,
    ) -> List[Dict[str, Any]]:
        """
        Long-term memory does not support temporal retrieval.

        Returns empty list. Use short-term memory for recent messages.
        """
        return []

    def retrieve(
        self,
        *,
        user_id: str,
        query: str,
        k: int,
    ) -> List[Dict[str, Any]]:
        """
        Semantically retrieve relevant items for a user.

        Searches across all conversations for this user.
        """
        # Generate query embedding
        vector = self.embed(query)

        # Search with user_id filter
        hits = self.client.search(
            collection_name=self.collection,
            query_vector=vector,
            limit=k,
            query_filter=Filter(
                must=[
                    FieldCondition(
                        key="user_id",
                        match=MatchValue(value=user_id),
                    )
                ]
            ),
        )

        return [hit.payload for hit in hits]
