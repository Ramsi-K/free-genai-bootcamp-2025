#!/usr/bin/env python3
"""
Script to populate Qdrant with processed chunks from JSONL files
"""

import os
import argparse
from pathlib import Path
from src.tools.vector_db import VectorDBTool


def main():
    parser = argparse.ArgumentParser(
        description="Populate Qdrant with processed chunks"
    )
    parser.add_argument(
        "--jsonl_file",
        type=str,
        default="data/processed/chunks/processed_chunks.jsonl",
        help="Path to the JSONL file containing processed chunks",
    )
    parser.add_argument(
        "--collection",
        type=str,
        default="korean_language_learning",
        help="Qdrant collection name to use",
    )
    parser.add_argument(
        "--host",
        type=str,
        default=os.environ.get("QDRANT_HOST", "localhost"),
        help="Qdrant host address",
    )
    parser.add_argument(
        "--port",
        type=str,
        default=os.environ.get("QDRANT_PORT", "6333"),
        help="Qdrant port",
    )

    args = parser.parse_args()

    # Ensure the file exists
    jsonl_path = Path(args.jsonl_file)
    if not jsonl_path.exists():
        print(f"Error: File {jsonl_path} does not exist.")
        return

    # Initialize VectorDBTool
    print(f"Connecting to Qdrant at {args.host}:{args.port}")
    vector_db = VectorDBTool(db_url=args.host, collection_name=args.collection)

    # Add documents from the JSONL file
    print(f"Adding documents from {jsonl_path}...")
    count = vector_db.add_documents_from_jsonl(str(jsonl_path))

    print(
        f"Successfully added {count} documents to Qdrant collection '{args.collection}'."
    )

    # Print a short message on how to query the database
    print("\nYou can now query your data using the VectorDBTool:")
    print(
        "  1. Make sure your chatbot is properly configured to connect to Qdrant"
    )
    print("  2. Run the bot with `python main.py`")
    print(
        "  3. The agents will automatically query the database when relevant"
    )


if __name__ == "__main__":
    main()
