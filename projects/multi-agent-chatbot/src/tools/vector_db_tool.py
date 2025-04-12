"""
Vector Database Tool - A tool for interacting with Qdrant vector database

This tool provides functionality for retrieving similar documents
from a Qdrant vector database collection.
"""

import os
from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer


class VectorDBTool:
    """
    A tool for querying the Qdrant vector database
    """

    def __init__(
        self,
        db_url: Optional[str] = None,
        collection_name: str = "korean_language_learning",
        embedding_model: str = "paraphrase-multilingual-mpnet-base-v2",
        max_results: int = 10,
    ):
        """
        Initialize the Vector DB tool

        Args:
            db_url: Qdrant server URL (defaults to QDRANT_HOST and QDRANT_PORT env vars)
            collection_name: Name of the collection to query
            embedding_model: The embedding model to use for queries
            max_results: Maximum number of results to return
        """
        # Use environment variables if db_url not provided
        if db_url is None:
            host = os.environ.get("QDRANT_HOST", "qdrant")
            port = os.environ.get("QDRANT_PORT", "6333")
            db_url = f"http://{host}:{port}"

        self.db_url = db_url
        self.collection_name = collection_name
        self.max_results = max_results

        # Initialize Qdrant client
        self.client = QdrantClient(url=db_url)

        # Load the embedding model
        # Use the same model as in embed_and_upload.py
        device = (
            "cuda"
            if os.environ.get("USE_CUDA", "false").lower() == "true"
            else "cpu"
        )
        self.embedding_model = SentenceTransformer(
            embedding_model, device=device
        )

    def search(
        self, query: str, limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Search the vector database for similar documents

        Args:
            query: The search query
            limit: Maximum number of results (defaults to self.max_results)

        Returns:
            List of matching documents with their metadata and similarity scores
        """
        if limit is None:
            limit = self.max_results

        try:
            # Generate embedding for the query
            query_embedding = self.embedding_model.encode(query)

            # Search the vector database
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding.tolist(),
                limit=limit,
                with_payload=True,
                with_vectors=False,
            )

            # Format the results
            formatted_results = []
            for result in results:
                formatted_results.append(
                    {
                        "text": result.payload.get("text", ""),
                        "metadata": {
                            k: v
                            for k, v in result.payload.items()
                            if k != "text"
                        },
                        "score": result.score,
                    }
                )

            return formatted_results

        except Exception as e:
            print(f"Error searching vector database: {str(e)}")
            return []

    def get_all_collections(self) -> List[str]:
        """
        Get a list of all collections in the database

        Returns:
            List of collection names
        """
        try:
            collections_info = self.client.get_collections()
            return [
                collection.name for collection in collections_info.collections
            ]
        except Exception as e:
            print(f"Error getting collections: {str(e)}")
            return []
