import json
import uuid
import os
import argparse
from pathlib import Path
from qdrant_client import QdrantClient, models
from sentence_transformers import SentenceTransformer
import torch  # To check for GPU availability


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Embed text chunks and upload to Qdrant using GPU acceleration"
    )
    parser.add_argument(
        "--jsonl_file",
        type=str,
        default="processed_chunks/processed_chunks.jsonl",
        help="Path to the JSONL file with text chunks",
    )
    parser.add_argument(
        "--collection",
        type=str,
        default="korean_language_learning",
        help="Qdrant collection name",
    )
    parser.add_argument(
        "--qdrant_host",
        type=str,
        default=os.environ.get("QDRANT_HOST", "qdrant"),
        help="Qdrant host address",
    )
    parser.add_argument(
        "--qdrant_port",
        type=str,
        default=os.environ.get("QDRANT_PORT", "6333"),
        help="Qdrant port",
    )
    parser.add_argument(
        "--batch_size", type=int, default=64, help="Batch size for embeddings"
    )
    parser.add_argument(
        "--force_cpu",
        action="store_true",
        help="Force CPU usage even if GPU is available",
    )

    args = parser.parse_args()

    # --- Configuration ---
    SCRIPT_DIR = Path(__file__).parent
    PROCESSED_JSONL_FILE = SCRIPT_DIR / args.jsonl_file
    QDRANT_URL = f"http://{args.qdrant_host}:{args.qdrant_port}"
    COLLECTION_NAME = args.collection
    # Recommended multilingual model: https://huggingface.co/sentence-transformers/paraphrase-multilingual-mpnet-base-v2
    EMBEDDING_MODEL_NAME = "paraphrase-multilingual-mpnet-base-v2"
    BATCH_SIZE = (
        args.batch_size
    )  # Adjust based on your GPU memory and dataset size

    # --- Determine Device for Embedding ---
    # Use MPS if available (Apple Silicon), otherwise CUDA if available, else CPU
    if args.force_cpu:
        DEVICE = "cpu"
    elif torch.cuda.is_available():
        DEVICE = "cuda"
    elif torch.backends.mps.is_available():
        DEVICE = "mps"
    else:
        DEVICE = "cpu"

    print(f"Using device: {DEVICE} for embeddings")
    if DEVICE == "cuda":
        print(f"GPU: {torch.cuda.get_device_name(0)}")
        print(f"CUDA Version: {torch.version.cuda}")

    # --- Initialize Embedding Model ---
    try:
        print(
            f"Loading embedding model: {EMBEDDING_MODEL_NAME} on {DEVICE}..."
        )
        # Load the model onto the chosen device
        model = SentenceTransformer(EMBEDDING_MODEL_NAME, device=DEVICE)
        print("Embedding model loaded successfully.")
    except Exception as e:
        print(f"Error loading embedding model: {e}")
        print(
            "Please ensure 'sentence-transformers' and 'torch' (with CUDA/MPS if applicable) are installed."
        )
        exit()

    # Get the embedding dimension from the model
    EMBEDDING_DIM = model.get_sentence_embedding_dimension()
    print(f"Embedding dimension: {EMBEDDING_DIM}")

    # --- Initialize Qdrant Client ---
    try:
        print(f"Connecting to Qdrant at {QDRANT_URL}...")
        client = QdrantClient(url=QDRANT_URL)
        print("Connected to Qdrant.")
    except Exception as e:
        print(f"Error connecting to Qdrant: {e}")
        print("Ensure Qdrant instance is running and accessible.")
        exit()

    # --- Create Qdrant Collection ---
    try:
        print(f"Checking/Creating Qdrant collection: {COLLECTION_NAME}...")
        client.recreate_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=models.VectorParams(
                size=EMBEDDING_DIM, distance=models.Distance.COSINE
            ),
            # Add optimized HNSW indexing for faster search
            hnsw_config=models.HnswConfigDiff(m=16, ef_construct=200),
        )
        print(f"Collection '{COLLECTION_NAME}' ensured.")
    except Exception as e:
        print(f"Error creating Qdrant collection: {e}")
        exit()

    # --- Process and Upload Chunks ---
    def upload_batch(batch_points):
        if not batch_points:
            return 0
        try:
            client.upsert(
                collection_name=COLLECTION_NAME,
                points=batch_points,
                wait=True,  # Wait for operation to complete for more reliable counting
            )
            return len(batch_points)
        except Exception as e:
            print(f"Error uploading batch to Qdrant: {e}")
            return 0  # Indicate failure or partial success

    print(
        f"Starting GPU-accelerated embedding and upload process from {PROCESSED_JSONL_FILE}..."
    )
    points_batch = []
    total_uploaded = 0
    processed_lines = 0

    try:
        with open(PROCESSED_JSONL_FILE, "r", encoding="utf-8") as infile:
            for line in infile:
                processed_lines += 1
                try:
                    chunk_data = json.loads(line.strip())
                except json.JSONDecodeError:
                    print(
                        f"Warning: Skipping malformed JSON line {processed_lines}"
                    )
                    continue

                text_to_embed = chunk_data.get("text")
                payload = chunk_data.get(
                    "metadata", {}
                )  # Get the nested metadata
                payload["source"] = chunk_data.get(
                    "source"
                )  # Add original source filename
                payload["text"] = (
                    text_to_embed  # Include the original text in the payload
                )

                # Use a deterministic UUID based on chunk_id if available, otherwise random
                point_id = chunk_data.get("chunk_id")
                if not point_id:
                    print(
                        f"Warning: Missing 'chunk_id' in line {processed_lines}. Generating random UUID."
                    )
                    point_id = str(uuid.uuid4())
                else:
                    # Create a UUID based on the chunk_id for potential idempotency
                    point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, point_id))

                if text_to_embed:
                    # Add data to batch (embedding happens just before upload)
                    points_batch.append(
                        {
                            "id": point_id,
                            "text": text_to_embed,  # Store text temporarily for batch embedding
                            "payload": payload,
                        }
                    )

                    if len(points_batch) >= BATCH_SIZE:
                        # Embed the texts in the current batch
                        texts = [p["text"] for p in points_batch]
                        print(
                            f"  Embedding batch of {len(texts)} chunks using {DEVICE}..."
                        )

                        # Use GPU acceleration here
                        if DEVICE == "cuda":
                            with torch.cuda.amp.autocast():  # Use mixed precision for faster GPU embedding
                                embeddings = model.encode(
                                    texts,
                                    convert_to_tensor=True,
                                    device=DEVICE,
                                )
                        else:
                            embeddings = model.encode(
                                texts, convert_to_tensor=True, device=DEVICE
                            )

                        print(f"  Uploading batch...")

                        # Prepare PointStructs for upload
                        qdrant_points = [
                            models.PointStruct(
                                id=p["id"],
                                vector=embeddings[
                                    i
                                ].tolist(),  # Convert tensor row to list
                                payload=p["payload"],
                            )
                            for i, p in enumerate(points_batch)
                        ]

                        uploaded_count = upload_batch(qdrant_points)
                        total_uploaded += uploaded_count
                        print(
                            f"  -> Uploaded {uploaded_count} points. Total uploaded: {total_uploaded}"
                        )
                        points_batch = []  # Clear the batch

                else:
                    print(
                        f"Warning: Skipping line {processed_lines} due to missing 'text' field."
                    )

        # Upload any remaining points in the last batch
        if points_batch:
            print("Processing final batch...")
            texts = [p["text"] for p in points_batch]
            print(
                f"  Embedding batch of {len(texts)} chunks using {DEVICE}..."
            )

            # Use GPU acceleration here too
            if DEVICE == "cuda":
                with torch.cuda.amp.autocast():  # Use mixed precision
                    embeddings = model.encode(
                        texts, convert_to_tensor=True, device=DEVICE
                    )
            else:
                embeddings = model.encode(
                    texts, convert_to_tensor=True, device=DEVICE
                )

            print(f"  Uploading batch...")
            qdrant_points = [
                models.PointStruct(
                    id=p["id"],
                    vector=embeddings[i].tolist(),
                    payload=p["payload"],
                )
                for i, p in enumerate(points_batch)
            ]
            uploaded_count = upload_batch(qdrant_points)
            total_uploaded += uploaded_count
            print(f"  -> Uploaded {uploaded_count} points.")

    except FileNotFoundError:
        print(
            f"Error: Processed chunks file not found at {PROCESSED_JSONL_FILE}"
        )
        print("Please run the 'process_text_data.py' script first.")
    except Exception as e:
        print(f"An unexpected error occurred during processing: {e}")

    print(f"\nGPU-accelerated embedding and upload process finished.")
    print(f"Total lines processed from file: {processed_lines}")
    print(f"Total points attempted to upload to Qdrant: {total_uploaded}")
    print(f"These were embedded using: {DEVICE}")


if __name__ == "__main__":
    main()
