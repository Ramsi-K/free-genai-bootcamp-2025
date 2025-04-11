import os
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

# Explicitly set the CUDA device (sometimes helps with detection issues)
os.environ["CUDA_VISIBLE_DEVICES"] = "0"


def download_model(model_id, cache_dir):
    model_path = os.path.join(cache_dir, model_id.split("/")[-1])

    # Check if the model already exists
    if os.path.exists(model_path):
        print(f"Model already exists at {model_path}. Skipping download.")
        return

    # Check for GPU and available memory
    gpu_available = torch.cuda.is_available()

    if gpu_available:
        print(f"GPU detected: {torch.cuda.get_device_name(0)}")
        print(
            f"GPU memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB"
        )
    else:
        print(
            "WARNING: No GPU detected! Will attempt to download in CPU mode (very slow)."
        )

    try:
        # Create quantization config based on whether GPU is available
        from transformers import BitsAndBytesConfig

        quantization_config = None

        if gpu_available:
            try:
                quantization_config = BitsAndBytesConfig(
                    load_in_4bit=True, bnb_4bit_compute_dtype=torch.float16
                )
                print("Using 4-bit quantization for GPU")
            except Exception as e:
                print(f"Failed to create quantization config: {e}")
                print("Proceeding without quantization")
        else:
            print("Proceeding without quantization in CPU-only mode")

        # First download the tokenizer
        print(f"Downloading tokenizer for {model_id}...")
        tokenizer = AutoTokenizer.from_pretrained(
            model_id,
            cache_dir=cache_dir,
            use_fast=False,
            trust_remote_code=True,
        )
        print("Tokenizer downloaded successfully.")

        # Save tokenizer locally
        tokenizer_path = os.path.join(
            cache_dir, f"{model_id.split('/')[-1]}-tokenizer"
        )
        tokenizer.save_pretrained(tokenizer_path)
        print(f"Tokenizer saved to {tokenizer_path}")

        # Download the model, with or without quantization based on GPU availability
        print(f"Downloading model {model_id}...")
        print(
            "This may take several minutes depending on your internet connection."
        )

        model_kwargs = {
            "cache_dir": cache_dir,
            "torch_dtype": torch.float16 if gpu_available else torch.float32,
            "trust_remote_code": True,
        }

        # Only add quantization config if available
        if gpu_available and quantization_config:
            model_kwargs["quantization_config"] = quantization_config

        # First try with device_map="auto"
        try:
            print("Attempting to load with device_map='auto'...")
            model_kwargs["device_map"] = "auto"
            model = AutoModelForCausalLM.from_pretrained(
                model_id, **model_kwargs
            )
        except RuntimeError as e:
            if "No GPU found" in str(e) and gpu_available:
                print(
                    "GPU detection issue with device_map='auto'. Trying explicit device map..."
                )
                # Try with explicit device mapping
                model_kwargs["device_map"] = {"": 0}  # Map everything to GPU 0
                try:
                    model = AutoModelForCausalLM.from_pretrained(
                        model_id, **model_kwargs
                    )
                except Exception as inner_e:
                    print(f"Explicit device mapping failed: {inner_e}")
                    print(
                        "Falling back to CPU mode (slow and memory intensive)..."
                    )
                    model_kwargs.pop("device_map", None)
                    if "quantization_config" in model_kwargs:
                        model_kwargs.pop("quantization_config")
                    model = AutoModelForCausalLM.from_pretrained(
                        model_id, **model_kwargs
                    )
            else:
                # If not a GPU detection issue, fall back to CPU
                print(f"Failed with error: {e}")
                print("Falling back to CPU mode...")
                model_kwargs.pop("device_map", None)
                if "quantization_config" in model_kwargs:
                    model_kwargs.pop("quantization_config")
                model = AutoModelForCausalLM.from_pretrained(
                    model_id, **model_kwargs
                )

        print("Model downloaded successfully.")

        # Save model locally
        model_save_path = os.path.join(
            cache_dir, f"{model_id.split('/')[-1]}-model"
        )
        model.save_pretrained(model_save_path)
        print(f"Model saved to {model_save_path}")

        # Free up memory
        del model
        if gpu_available:
            torch.cuda.empty_cache()
        print("Memory cleared")

    except Exception as e:
        print(f"Error downloading model or tokenizer: {e}")
        print("\nTroubleshooting tips:")
        print(
            "1. Check CUDA installation: Run 'python -c \"import torch; print(torch.cuda.is_available())\"'"
        )
        print(
            "2. Update GPU drivers: https://www.nvidia.com/Download/index.aspx"
        )
        print("3. Try installing PyTorch with the correct CUDA version:")
        print(
            "   pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118"
        )
        print("4. Try downloading without quantization:")
        print("   Set use_quantization=False in this script")
        print(
            "5. If your GPU has limited memory (<8GB), try a smaller model or use CPU-only mode"
        )


if __name__ == "__main__":
    model_id = "llava-hf/llava-1.5-7b-hf"
    cache_dir = "cache/models"

    # Ensure cache directory exists
    os.makedirs(cache_dir, exist_ok=True)

    # Download the model and tokenizer
    download_model(model_id, cache_dir)

    print(
        "\nSetup completed. You can now run the server with: python server.py"
    )
    print("Or use Docker Compose with: docker-compose up -d")
