import os
import shutil
import subprocess
import argparse
from pathlib import Path
from huggingface_hub import snapshot_download


def convert_model(model_id, output_dir):
    """
    Download a model from Hugging Face and convert it to TensorFlow.js format
    """
    print(f"Downloading model {model_id}...")

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # First, download the model from Hugging Face Hub
    download_path = snapshot_download(
        repo_id=model_id,
        local_dir="./temp_model",
        local_dir_use_symlinks=False,
    )

    print(f"Model downloaded to {download_path}")

    # Check if we need to install tensorflowjs
    try:
        import tensorflowjs
    except ImportError:
        print("Installing tensorflowjs...")
        subprocess.check_call(["pip", "install", "tensorflowjs"])

    # Convert downloaded model to TensorFlow.js format
    print("Converting model to TensorFlow.js format...")

    # We need to determine what kind of model we're dealing with
    # Look for common model files
    has_pytorch = any(Path(download_path).glob("*.pt")) or any(
        Path(download_path).glob("*.bin")
    )
    has_tf_saved_model = os.path.exists(
        os.path.join(download_path, "saved_model.pb")
    )
    has_keras_h5 = any(Path(download_path).glob("*.h5"))

    if has_pytorch:
        print("Detected PyTorch model. Converting to TensorFlow first...")
        # This may require additional transformers code to convert from PyTorch to TF
        # For simplicity, we'll provide instructions
        print("For PyTorch models, manual conversion steps are needed:")
        print("1. Load the model with transformers")
        print("2. Use model.to_tf() method if available")
        print("3. Save as a TensorFlow SavedModel")
        print("4. Then convert using tensorflowjs_converter")

    elif has_tf_saved_model:
        print("Detected TensorFlow SavedModel format")
        # Convert the SavedModel to TensorFlow.js
        tf_js_path = os.path.join(output_dir, "tfjs_model")
        subprocess.check_call(
            [
                "tensorflowjs_converter",
                "--input_format=tf_saved_model",
                "--output_format=tfjs_layers",
                download_path,
                tf_js_path,
            ]
        )
        print(f"Converted model saved to {tf_js_path}")

    elif has_keras_h5:
        # Find the H5 file
        h5_files = list(Path(download_path).glob("*.h5"))
        if h5_files:
            h5_path = str(h5_files[0])
            print(f"Detected Keras H5 model: {h5_path}")

            # Convert the H5 model to TensorFlow.js
            tf_js_path = os.path.join(output_dir, "tfjs_model")
            subprocess.check_call(
                [
                    "tensorflowjs_converter",
                    "--input_format=keras",
                    h5_path,
                    tf_js_path,
                ]
            )
            print(f"Converted model saved to {tf_js_path}")
    else:
        print(
            "Could not determine model format. Please check the model files manually."
        )
        print(f"Files in the model directory: {os.listdir(download_path)}")

    # Clean up
    print("Cleaning up temporary files...")
    shutil.rmtree("./temp_model", ignore_errors=True)

    print("Conversion process completed.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Convert Hugging Face model to TensorFlow.js format"
    )
    parser.add_argument(
        "--model_id",
        type=str,
        default="TanmayNanda/ishara",
        help="Hugging Face model ID",
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default="./models",
        help="Output directory for the converted model",
    )

    args = parser.parse_args()
    convert_model(args.model_id, args.output_dir)
