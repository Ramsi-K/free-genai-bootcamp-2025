import os
import torch
import tensorflow as tf
import subprocess
from pathlib import Path
from huggingface_hub import snapshot_download
from transformers import (
    AutoModelForImageClassification,
    TFAutoModelForImageClassification,
)


def convert_ishara_model(output_dir="./models/ishara_tfjs"):
    """
    Specifically convert the TanmayNanda/ishara model to TensorFlow.js format
    """
    model_id = "TanmayNanda/ishara"
    print(f"Processing {model_id} model...")

    # Create output directories
    os.makedirs(output_dir, exist_ok=True)
    temp_dir = "./temp_ishara_model"
    os.makedirs(temp_dir, exist_ok=True)

    try:
        # 1. Download the model from Hugging Face
        print(f"Downloading model from Hugging Face: {model_id}")
        download_path = snapshot_download(
            repo_id=model_id, local_dir=temp_dir, local_dir_use_symlinks=False
        )

        print(f"Model downloaded to {download_path}")

        # 2. Check if it's a PyTorch model (most likely)
        if any(Path(download_path).glob("*.bin")):
            print("Detected PyTorch model. Converting to TensorFlow...")

            # 3. Load PyTorch model using transformers
            pytorch_model = AutoModelForImageClassification.from_pretrained(
                download_path
            )

            # 4. Convert to TensorFlow model
            tf_model_path = os.path.join(temp_dir, "tf_model")
            tf_model = TFAutoModelForImageClassification.from_pretrained(
                download_path, from_pt=True
            )

            # 5. Save as TensorFlow SavedModel
            print(f"Saving TensorFlow model to {tf_model_path}")
            tf_model.save_pretrained(tf_model_path)

            # 6. Convert to TensorFlow.js format
            print("Converting to TensorFlow.js format...")

            # Make sure tensorflowjs is installed
            try:
                import tensorflowjs
            except ImportError:
                subprocess.check_call(["pip", "install", "tensorflowjs"])

            # Convert using tensorflowjs_converter
            subprocess.check_call(
                [
                    "tensorflowjs_converter",
                    "--input_format=tf_saved_model",
                    "--output_format=tfjs_graph_model",
                    tf_model_path,
                    output_dir,
                ]
            )

            print(f"Model successfully converted to TensorFlow.js format!")
            print(f"Output saved to: {output_dir}")

            # Create a metadata.json file with class mapping
            create_metadata_file(download_path, output_dir)

        else:
            print(
                "Model format not recognized as PyTorch. Please check the model structure."
            )
            print(f"Files in model directory: {os.listdir(download_path)}")

    finally:
        # Clean up temporary files
        print("Cleaning up temporary files...")
        import shutil

        shutil.rmtree(temp_dir, ignore_errors=True)


def create_metadata_file(model_path, output_dir):
    """Create a metadata.json file with information about the model"""
    import json

    # Try to extract label information from the model's config file
    try:
        with open(os.path.join(model_path, "config.json"), "r") as f:
            config = json.load(f)

        # Extract label mapping if available
        id2label = config.get("id2label", {})

        metadata = {
            "model_name": "ishara-asl-detection",
            "version": "1.0",
            "description": "ASL Fingerspelling detection model converted from TanmayNanda/ishara",
            "input_shape": [
                1,
                224,
                224,
                3,
            ],  # Typical image input shape, adjust if needed
            "labels": id2label,
        }

        with open(os.path.join(output_dir, "metadata.json"), "w") as f:
            json.dump(metadata, f, indent=2)

        print("Created metadata.json with label information")

    except Exception as e:
        print(f"Error creating metadata file: {e}")


if __name__ == "__main__":
    convert_ishara_model()
