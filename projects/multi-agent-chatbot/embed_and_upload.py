import json
import uuid
from pathlib import Path
from qdrant_client import QdrantClient, models
from sentence_transformers import SentenceTransformer
import torch  # To check for GPU availability

# --- Configuration ---
SCRIPT_DIR = Path(__file__).parent
PROCESSED_JSONL_FILE = (
    SCRIPT_DIR / "processed_chunks" / "processed_chunks.jsonl"
)
QDRANT_URL = "http://localhost:6333"  # Or your Qdrant Cloud URL / other host
# QDRANT_API_KEY = "YOUR_API_KEY" # Uncomment and set if using Qdrant Cloud with API key
COLLECTION_NAME = "korean_english_chatbot_data"
# Recommended multilingual model: https://huggingface.co/sentence-transformers/paraphrase-multilingual-mpnet-base-v2
EMBEDDING_MODEL_NAME = "paraphrase-multilingual-mpnet-base-v2"
BATCH_SIZE = 64  # Adjust based on your GPU memory and dataset size

# --- Determine Device for Embedding ---
# Use MPS if available (Apple Silicon), otherwise CUDA if available, else CPU
if torch.backends.mps.is_available():
    DEVICE = "mps"
elif torch.cuda.is_available():
    DEVICE = "cuda"
else:
    DEVICE = "cpu"
print(f"Using device: {DEVICE}")

# --- Initialize Embedding Model ---
try:
    print(f"Loading embedding model: {EMBEDDING_MODEL_NAME}...")
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
    # Uncomment the line below and comment the next one if using API Key
    # client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
    client = QdrantClient(url=QDRANT_URL)
    print("Connected to Qdrant.")
except Exception as e:
    print(f"Error connecting to Qdrant: {e}")
    print("Ensure Qdrant instance is running and accessible.")
    exit()

# --- Create Qdrant Collection ---
try:
    print(f"Checking/Creating Qdrant collection: {COLLECTION_NAME}...")
    client.recreate_collection(  # Use recreate_collection for simplicity, creates if not exists, overwrites if exists
        collection_name=COLLECTION_NAME,
        vectors_config=models.VectorParams(
            size=EMBEDDING_DIM, distance=models.Distance.COSINE
        ),
        # Add HNSW indexing for faster search later if needed:
        # hnsw_config=models.HnswConfigDiff(payload_m=16, m=0) # Example config
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
        # Optionally, add retry logic here
        return 0  # Indicate failure or partial success


print(f"Starting embedding and upload process from {PROCESSED_JSONL_FILE}...")
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
            payload = chunk_data.get("metadata", {})  # Get the nested metadata
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
                    print(f"  Embedding batch of {len(texts)} chunks...")
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
        print(f"  Embedding batch of {len(texts)} chunks...")
        embeddings = model.encode(texts, convert_to_tensor=True, device=DEVICE)
        print(f"  Uploading batch...")
        qdrant_points = [
            models.PointStruct(
                id=p["id"], vector=embeddings[i].tolist(), payload=p["payload"]
            )
            for i, p in enumerate(points_batch)
        ]
        uploaded_count = upload_batch(qdrant_points)
        total_uploaded += uploaded_count
        print(f"  -> Uploaded {uploaded_count} points.")

except FileNotFoundError:
    print(f"Error: Processed chunks file not found at {PROCESSED_JSONL_FILE}")
    print("Please run the 'process_text_data.py' script first.")
except Exception as e:
    print(f"An unexpected error occurred during processing: {e}")

print(f"\nEmbedding and upload process finished.")
print(f"Total lines processed from file: {processed_lines}")
print(f"Total points attempted to upload to Qdrant: {total_uploaded}")
