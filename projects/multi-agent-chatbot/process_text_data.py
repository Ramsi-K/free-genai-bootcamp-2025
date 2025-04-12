import os
import random
import re
from pathlib import Path
import json  # Added import

# --- Configuration ---
# Use Path(__file__).parent to make paths relative to the script location
SCRIPT_DIR = Path(__file__).parent
TEXT_FOLDER = SCRIPT_DIR / "data/processed/text"
PROCESSED_FOLDER = (
    SCRIPT_DIR / "data/processed/chunks"
)  # Added processed folder path
OUTPUT_JSONL_FILE = (
    PROCESSED_FOLDER / "processed_chunks.jsonl"
)  # Added output file path
CHUNK_SIZE = 300
CHUNK_OVERLAP = 50
ESTIMATED_CHARS_PER_PAGE = 1500  # Heuristic for page estimation in TXT files


# --- Metadata Assignment Logic ---
def assign_metadata(chunk_data):
    """Assigns persona, tone, TOPIK level, and topic metadata based on heuristics."""
    source = chunk_data.get("source", "").lower()
    text = chunk_data.get("text", "").lower()
    text_source_name = chunk_data.get(
        "text_source", ""
    ).lower()  # Get base name for source checks

    # --- Persona Detection ---
    if "속담" in text or "proverb" in text_source_name:
        persona = "AhjussiGPT"
    elif (
        "김치" in text
        or "food" in text_source_name
        or "recipe" in text_source_name
    ):
        persona = "AhjummaGPT"
    else:
        persona = random.choice(["AhjummaGPT", "AhjussiGPT"])

    # --- Tone Detection ---
    if "습니다" in text or "합니다" in text:
        tone = "Formal"
    elif "해요" in text or "있어요" in text:
        tone = "Polite"
    elif "한다" in text or "이다" in text:
        tone = "Plain"
    else:
        tone = random.choice(
            ["Casual", "Polite", "Formal"]
        )  # Default if specific endings aren't found

    # --- TOPIK Level Heuristic ---
    if "초급" in text_source_name or "beginner" in text_source_name:
        topik_level = "1"
    elif "중급" in text_source_name or "intermediate" in text_source_name:
        topik_level = "3"
    elif "고급" in text_source_name or "advanced" in text_source_name:
        topik_level = "5"
    else:
        # More nuanced check if level isn't in filename
        if any(kw in text for kw in ["어려워요", "complex", "advanced topic"]):
            topik_level = random.choice(["4", "5", "6"])
        elif any(kw in text for kw in ["쉬워요", "easy", "simple sentence"]):
            topik_level = random.choice(["1", "2"])
        else:
            topik_level = random.choice(["1", "2", "3", "4", "5", "6"])

    # --- Topic Classification ---
    if any(kw in text for kw in ["인사", "hello", "greeting", "안녕하세요"]):
        topic = "Greetings"
    elif any(
        kw in text
        for kw in ["음식", "식사", "김치", "ramyeon", "밥", "먹어요", "요리"]
    ):
        topic = "Food"
    elif any(
        kw in text for kw in ["문화", "예절", "전통", "korea", "culture"]
    ):
        topic = "Culture"
    elif any(
        kw in text for kw in ["학교", "공부", "시험", "배워요", "university"]
    ):
        topic = "Education"
    elif any(
        kw in text for kw in ["길", "방향", "여행", "travel", "trip", "가요"]
    ):
        topic = "Travel"
    elif any(
        kw in text for kw in ["건강", "병원", "의사", "아파요", "health"]
    ):
        topic = "Healthcare"
    elif any(
        kw in text
        for kw in ["회사", "일", "비즈니스", "work", "job", "meeting"]
    ):
        topic = "Work"
    else:
        # Fallback based on source if text gives no clues
        if "food" in text_source_name or "recipe" in text_source_name:
            topic = "Food"
        elif "proverb" in text_source_name:
            topic = "Culture"  # Proverbs often relate to culture
        else:
            topic = random.choice(
                ["Greetings", "Culture", "Education", "Work", "Food"]
            )  # Default random topic

    # --- Final Assignment ---
    # Ensure page_num is accessed correctly from the initial chunk_data
    chunk_data["metadata"] = {
        "persona": persona,
        "tone": tone,
        "TOPIK_level": topik_level,
        "topic": topic,
        "text_source": chunk_data.get(
            "text_source", "unknown"
        ),  # Use the base filename here
        "text_page": chunk_data.get(
            "page_num", "-1"
        ),  # Use the estimated page number
    }
    return chunk_data  # Return the modified chunk_data


# --- Text Chunking Function ---
def chunk_text_with_metadata(
    filepath: Path, chunk_size: int, chunk_overlap: int
):
    """Reads a text file, chunks it, and generates metadata for each chunk."""
    processed_chunks = []
    try:
        full_text = filepath.read_text(encoding="utf-8")
        filename = filepath.name
        filename_without_ext = filepath.stem
    except Exception as e:
        print(f"Error reading file {filepath}: {e}")
        return []

    start_index = 0
    chunk_index = 0
    while start_index < len(full_text):
        end_index = start_index + chunk_size
        chunk_text = full_text[start_index:end_index]

        # Estimate page number based on the start position of the chunk
        estimated_page = (start_index // ESTIMATED_CHARS_PER_PAGE) + 1

        # Create initial chunk data
        chunk_data = {
            "source": filename,  # Keep original filename with extension as source
            "chunk_id": f"{filename_without_ext}_p{estimated_page}_{chunk_index}",
            "text": chunk_text,
            "text_source": filename_without_ext,  # Base name for metadata logic
            "page_num": str(estimated_page),
        }

        # Assign extra metadata
        chunk_data_with_meta = assign_metadata(chunk_data)

        processed_chunks.append(chunk_data_with_meta)

        # Move to the next chunk start position
        start_index += chunk_size - chunk_overlap
        chunk_index += 1

        # Handle potential infinite loop if overlap >= size (shouldn't happen with validation)
        if chunk_size <= chunk_overlap:
            print(
                "Warning: Chunk overlap is greater than or equal to chunk size. Stopping."
            )
            break
        # Ensure we don't get stuck if the step is zero or negative
        if chunk_size - chunk_overlap <= 0:
            print("Warning: Non-positive step size in chunking. Stopping.")
            break

    return processed_chunks


# --- Main Processing Logic ---
def main():
    """Finds text files, processes them, and saves chunks incrementally to a JSONL file."""
    # Create the processed_chunks directory if it doesn't exist
    PROCESSED_FOLDER.mkdir(
        parents=True, exist_ok=True
    )  # Added directory creation

    if not TEXT_FOLDER.is_dir():
        print(f"Error: Text folder not found at {TEXT_FOLDER}")
        return

    total_chunks_processed = 0
    print(f"Starting processing in folder: {TEXT_FOLDER}")
    print(f"Output will be saved to: {OUTPUT_JSONL_FILE}")

    # Open the output file in write mode to overwrite if it exists
    # Use 'a' mode if you want to append to an existing file
    with open(OUTPUT_JSONL_FILE, "w", encoding="utf-8") as outfile:
        for filepath in TEXT_FOLDER.glob("*.txt"):
            print(f"Processing file: {filepath.name}...")
            chunks = chunk_text_with_metadata(
                filepath, CHUNK_SIZE, CHUNK_OVERLAP
            )
            if chunks:
                for chunk in chunks:
                    # Write each chunk as a JSON line
                    try:
                        json.dump(chunk, outfile, ensure_ascii=False)
                        outfile.write("\n")
                    except Exception as e:
                        print(
                            f"  Error writing chunk to JSONL: {e} - Chunk Data: {chunk}"
                        )
                print(f"  -> Saved {len(chunks)} chunks.")
                total_chunks_processed += len(chunks)
            else:
                print(f"  -> No chunks generated or error processing file.")

    print(f"\nProcessing complete.")
    print(
        f"Total chunks saved to {OUTPUT_JSONL_FILE}: {total_chunks_processed}"
    )

    # Removed the in-memory list and final print example


if __name__ == "__main__":
    main()
