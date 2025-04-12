"""
Vector Database Tool that connects to Qdrant for RAG functionality
"""

import os
import json
import uuid
from typing import Dict, List, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.http import models
from sentence_transformers import SentenceTransformer
import torch


class VectorDBTool:
    def __init__(
        self,
        db_url: str = None,
        collection_name: str = "korean_language_learning",
        embedding_dimension: int = 768,
        max_results: int = 10,
    ):
        # Handle Docker environment variables if specified
        self.db_url = db_url or os.getenv("QDRANT_HOST", "localhost")
        self.db_port = int(os.getenv("QDRANT_PORT", "6333"))
        self.collection_name = collection_name
        self.embedding_dimension = embedding_dimension
        self.max_results = max_results

        # Determine device for embedding
        if torch.cuda.is_available():
            self.device = "cuda"
        elif torch.backends.mps.is_available():  # Apple Silicon
            self.device = "mps"
        else:
            self.device = "cpu"
        print(f"Using device: {self.device} for embeddings")

        # Initialize embedding model - multilingual for Korean support
        self.model = SentenceTransformer(
            "paraphrase-multilingual-mpnet-base-v2", device=self.device
        )

        # Connect to Qdrant
        self.client = QdrantClient(
            url=f"http://{self.db_url}", port=self.db_port
        )

        # Ensure collection exists
        self._ensure_collection_exists()

    def _ensure_collection_exists(self):
        """Create the collection if it doesn't exist"""
        collections = self.client.get_collections().collections
        collection_names = [collection.name for collection in collections]

        if self.collection_name not in collection_names:
            print(f"Creating collection: {self.collection_name}")
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=self.model.get_sentence_embedding_dimension(),
                    distance=models.Distance.COSINE,
                ),
            )

    def query(
        self,
        query_text: str,
        filter_by: Optional[Dict[str, Any]] = None,
        limit: int = None,
    ) -> List[Dict]:
        """
        Query the vector database for similar documents

        Args:
            query_text: The text to find similar documents for
            filter_by: Optional filters to apply to the search (metadata fields)
            limit: Maximum number of results to return

        Returns:
            List of documents with their metadata and similarity scores
        """
        # Generate embedding for the query
        query_vector = self.model.encode(query_text).tolist()

        # Create search filter if provided
        search_filter = None
        if filter_by:
            filter_conditions = []
            for key, value in filter_by.items():
                filter_conditions.append(
                    models.FieldCondition(
                        key=f"metadata.{key}",
                        match=models.MatchValue(value=value),
                    )
                )
            search_filter = models.Filter(must=filter_conditions)

        # Execute the search
        search_results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=limit or self.max_results,
            query_filter=search_filter,
        )

        # Format and return the results
        results = []
        for result in search_results:
            item = {
                "id": result.id,
                "score": result.score,
                "text": result.payload.get("text", ""),
                "metadata": {
                    k: v for k, v in result.payload.items() if k != "text"
                },
            }
            results.append(item)

        return results

    def add_document(self, text: str, metadata: Dict = None) -> str:
        """
        Add a document to the vector database

        Args:
            text: The text content to add
            metadata: Additional metadata to store with the document

        Returns:
            The ID of the added document
        """
        # Generate embedding
        vector = self.model.encode(text).tolist()

        # Create a unique ID
        point_id = str(uuid.uuid4())

        # Prepare payload
        payload = {"text": text}
        if metadata:
            payload.update(metadata)

        # Add the document to the collection
        self.client.upsert(
            collection_name=self.collection_name,
            points=[
                models.PointStruct(id=point_id, vector=vector, payload=payload)
            ],
        )

        return point_id

    def add_documents_from_jsonl(self, jsonl_path: str) -> int:
        """
        Add documents from a JSONL file to the vector database

        Args:
            jsonl_path: Path to the JSONL file

        Returns:
            Number of documents added
        """
        count = 0

        batch_size = 100  # Process in batches for efficiency
        batch_points = []

        with open(jsonl_path, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    data = json.loads(line.strip())

                    # Extract text and metadata
                    text = data.get("text", "")
                    if not text:
                        continue

                    # Generate embedding
                    vector = self.model.encode(text).tolist()

                    # Extract metadata if available
                    metadata = data.get("metadata", {})

                    # Create payload
                    payload = {"text": text}
                    if metadata:
                        payload["metadata"] = metadata

                    # Use existing ID or generate one
                    point_id = data.get("chunk_id", str(uuid.uuid4()))

                    # Add to batch
                    batch_points.append(
                        models.PointStruct(
                            id=point_id, vector=vector, payload=payload
                        )
                    )

                    count += 1

                    # Process batch when size threshold reached
                    if len(batch_points) >= batch_size:
                        self.client.upsert(
                            collection_name=self.collection_name,
                            points=batch_points,
                        )
                        batch_points = []
                        print(f"Added {count} documents so far...")

                except json.JSONDecodeError:
                    print(f"Skipping invalid JSON line: {line[:50]}...")
                except Exception as e:
                    print(f"Error processing line: {e}")

        # Process any remaining items in the last batch
        if batch_points:
            self.client.upsert(
                collection_name=self.collection_name, points=batch_points
            )

        return count
