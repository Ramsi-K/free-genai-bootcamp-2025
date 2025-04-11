"""
Simple LLaVA handwriting comparison using Hugging Face transformers pipeline
with image concatenation functionality from the llava-multi-images.py script.

This script provides a streamlined way to compare handwriting images using LLaVA
without the complexity of cloning repositories or setting up complex environments.
"""

import argparse
import torch
import requests
import os
import json
import sys
from PIL import Image
from io import BytesIO
from transformers import pipeline, BitsAndBytesConfig
from huggingface_hub import InferenceClient


# Image concatenation functions from llava-multi-images.py
def concatenate_images_horizontal(images, dist_images):
    """Concatenate images horizontally with a specified distance between them."""
    # calc total width of imgs + dist between them
    total_width = sum(img.width for img in images) + dist_images * (
        len(images) - 1
    )
    # calc max height from imgs
    height = max(img.height for img in images)

    # create new img with calculated dimensions, white bg
    new_img = Image.new("RGB", (total_width, height), (255, 255, 255))

    # init var to track current width pos
    current_width = 0
    for img in images:
        # paste img in new_img at current width
        new_img.paste(img, (current_width, 0))
        # update current width for next img
        current_width += img.width + dist_images

    return new_img


def load_image(image_file):
    """Load an image from a file path or URL."""
    if image_file.startswith("http://") or image_file.startswith("https://"):
        response = requests.get(image_file)
        image = Image.open(BytesIO(response.content)).convert("RGB")
    else:
        image = Image.open(image_file).convert("RGB")
    return image


def upload_to_imgbb(image_path, imgbb_api_key):
    """
    Upload an image to ImgBB and return the URL.

    Args:
        image_path (str): Path to the image file
        imgbb_api_key (str): ImgBB API key

    Returns:
        str: URL of the uploaded image
    """
    print(f"Uploading image {image_path} to ImgBB...")
    try:
        with open(image_path, "rb") as f:
            encoded_image = f.read()
        response = requests.post(
            "https://api.imgbb.com/1/upload",
            params={"key": imgbb_api_key, "expiration": 600},
            files={"image": encoded_image},
        )
        if response.status_code == 200:
            result = response.json()
            # Check if the upload was successful and extract the display_url
            if result.get("success") and "data" in result:
                # Use display_url as it's typically the best quality and direct link
                image_url = result["data"]["display_url"]
                print(f"Upload successful. Image URL: {image_url}")
                return image_url
            else:
                raise Exception(
                    f"Upload response did not contain expected data: {result}"
                )
        else:
            raise Exception(
                f"Upload failed with status code {response.status_code}: {response.text}"
            )
    except Exception as e:
        print(f"Error uploading to ImgBB: {str(e)}")
        raise


def load_llava_model(model_id="llava-hf/llava-1.5-7b-hf"):
    """
    Load the LLaVA model using HuggingFace Transformers pipeline.

    Args:
        model_id (str): HuggingFace model ID for LLaVA

    Returns:
        pipeline: HuggingFace pipeline for image-to-text
    """
    print(f"Loading LLaVA model {model_id}...")

    # Check for GPU
    device = "cuda" if torch.cuda.is_available() else "cpu"
    if device == "cuda":
        print(f"Using GPU: {torch.cuda.get_device_name(0)}")
    else:
        print("GPU not available, using CPU (this will be slow)")

    # Set up the quantization config for 4-bit loading
    quantization_config = BitsAndBytesConfig(
        load_in_4bit=True, bnb_4bit_compute_dtype=torch.float16
    )

    # Load the pipeline
    pipe = pipeline(
        "image-to-text",
        model=model_id,
        device_map="auto",
        model_kwargs={"quantization_config": quantization_config},
    )

    return pipe


def process_feedback_with_ollama(feedback, ollama_host=None):
    """
    Process LLaVA feedback through Ollama to get an ahjumma-style response.

    Args:
        feedback (str): The original feedback from LLaVA
        ollama_host (str): Host URL for Ollama API

    Returns:
        str: Ahjumma-style feedback
    """
    if not ollama_host:
        ollama_host = os.environ.get("OLLAMA_HOST", "http://localhost:11434")

    model = "kimjk/llama3.2-korean"  # Default model, good for Korean

    prompt = f"""
    You're a spicy Korean auntie (AhjummaGPT). Someone just gave the following handwriting feedback to a student:

    {feedback}

    Now, you want to respond like a proper ahjumma:
    - React to the feedback with sass, like you're gossiping about your neighbor's son who failed calligraphy class
    - Mix in a few Korean interjections like "aigoo", "mwo ya~", or "ottoke"
    - Use mostly English but throw in Hangul here and there to add flavor
    - Add a couple over-the-top emojis like 💅🔥🤦‍♀️
    - Keep it short (1-3 lines)

    Be funny, a little judgy, but still warm-hearted. Your goal is to roast *with love*.
    """

    try:
        # Try using the Ollama API
        try:
            print(
                f"Sending feedback to Ollama at {ollama_host} for ahjumma transformation..."
            )
            response = requests.post(
                f"{ollama_host}/api/generate",
                json={"model": model, "prompt": prompt, "stream": False},
                timeout=30,
            )

            if response.status_code == 200:
                result = response.json()
                ahjumma_feedback = result.get("response", "").strip()
                print("Received ahjumma response from Ollama")
                return ahjumma_feedback
            else:
                print(
                    f"Error from Ollama API: {response.status_code} - {response.text}"
                )
                return feedback  # Return original feedback if Ollama fails

        except (requests.RequestException, json.JSONDecodeError) as e:
            print(f"API error when calling Ollama: {e}. Falling back to CLI.")

            # Fallback to CLI method (for local development)
            try:
                command = f'ollama run {model} "{prompt}"'
                ahjumma_feedback = subprocess.getoutput(command).strip()
                return ahjumma_feedback
            except Exception as cli_error:
                print(f"CLI error: {cli_error}")
                return feedback  # Return original feedback if CLI fails

    except Exception as e:
        print(f"Error processing feedback with Ollama: {e}")
        return feedback  # Return original feedback on error


def compare_with_llava_hf_api(
    reference_image_path,
    user_image_path,
    model_id="llava-hf/llava-1.5-7b-hf",
    save_image=True,
    output_dir=None,
    imgbb_api_key=None,
    hf_api_key=None,
    hf_provider="nebius",  # Changed default to nebius
):
    """
    Compare reference calligraphy with user handwriting using the LLaVA model via HF Inference API.

    Args:
        reference_image_path (str): Path to reference image
        user_image_path (str): Path to user's handwriting image
        model_id (str): Hugging Face model ID for LLaVA
        save_image (bool): Whether to save the concatenated image
        output_dir (str): Directory to save the output image
        imgbb_api_key (str): ImgBB API key for image hosting
        hf_api_key (str): HuggingFace API key for inference
        hf_provider (str): HuggingFace provider, e.g., 'hf', 'nebius'

    Returns:
        tuple: (feedback_text, output_image_path)
    """
    if not imgbb_api_key:
        imgbb_api_key = os.environ.get("IMGBB_API_KEY")

    if not hf_api_key:
        hf_api_key = os.environ.get("HF_API_KEY")

    if not imgbb_api_key or not hf_api_key:
        raise ValueError(
            "ImgBB API key and HuggingFace API key are required. Set them as parameters or as environment variables."
        )

    try:
        print(
            f"Loading images from {reference_image_path} and {user_image_path}"
        )

        # Create output directory if specified
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

        # Load the images
        reference_image = load_image(reference_image_path)
        user_image = load_image(user_image_path)

        # Resize images to similar heights for better comparison
        target_height = min(reference_image.height, user_image.height, 600)
        ref_aspect = reference_image.width / reference_image.height
        user_aspect = user_image.width / user_image.height

        reference_image = reference_image.resize(
            (int(target_height * ref_aspect), target_height)
        )
        user_image = user_image.resize(
            (int(target_height * user_aspect), target_height)
        )

        # Concatenate the images horizontally
        concatenated_image = concatenate_images_horizontal(
            [reference_image, user_image], dist_images=50
        )

        # Save the concatenated image if requested
        output_image_path = None
        if save_image:
            import uuid

            image_id = str(uuid.uuid4())[:8]
            output_file = f"concatenated_{image_id}.jpg"
            if output_dir:
                output_image_path = os.path.join(output_dir, output_file)
            else:
                output_image_path = output_file
            concatenated_image.save(output_image_path)
            print(f"Saved concatenated image to {output_image_path}")

        # Upload image to ImgBB
        image_url = upload_to_imgbb(output_image_path, imgbb_api_key)
        print(f"Uploaded image to ImgBB: {image_url}")

        # Use HuggingFace Inference API
        print(
            f"Sending request to HuggingFace Inference API for model {model_id} using provider {hf_provider}..."
        )

        # Force using nebius provider for LLaVA
        client = InferenceClient(
            provider="nebius",  # Always use nebius for LLaVA
            api_key=hf_api_key,
        )

        # Prepare the prompt for handwriting comparison
        prompt = (
            "You are a Korean calligraphy teacher evaluating a student's handwriting. "
            "The image on the left is the reference calligraphy, and the image on the right "
            "is the student's handwriting. Compare them and provide specific feedback on: "
            "1. Stroke accuracy and proportion, "
            "2. Character balance and spacing, "
            "3. Overall visual harmony. "
            "Be detailed but encouraging, like a supportive but slightly sassy Korean ahjumma. "
            "Limit your response to 150 words."
        )

        # Create the messages with embedded image URL
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": image_url}},
                ],
            }
        ]

        # Call the API
        try:
            completion = client.chat.completions.create(
                model=model_id,
                messages=messages,
                max_tokens=300,
            )
            llava_feedback = completion.choices[0].message.content

            # Process the LLaVA feedback through Ollama for ahjumma-style response
            ollama_host = os.environ.get(
                "OLLAMA_HOST", "http://localhost:11434"
            )
            feedback = process_feedback_with_ollama(
                llava_feedback, ollama_host
            )

        except Exception as api_error:
            print(f"Error from HuggingFace API: {str(api_error)}")
            print("API response may contain more details about the error")
            raise

        return feedback, output_image_path

    except Exception as e:
        print(f"Error in compare_with_llava_hf_api: {str(e)}")
        return f"Error analyzing handwriting: {str(e)}", None


def compare_with_llava(
    reference_image_path,
    user_image_path,
    model_id="llava-hf/llava-1.5-7b-hf",
    save_image=True,
    output_dir=None,
    preloaded_model=None,
):
    """
    Compare reference calligraphy with user handwriting using the LLaVA model via HF pipeline.

    Args:
        reference_image_path (str): Path to reference image
        user_image_path (str): Path to user's handwriting image
        model_id (str): Hugging Face model ID for LLaVA
        save_image (bool): Whether to save the concatenated image
        output_dir (str): Directory to save the output image
        preloaded_model: Optional preloaded pipeline model

    Returns:
        tuple: (feedback_text, output_image_path)
    """
    # If environment variables are set for API keys, use the API version
    imgbb_api_key = os.environ.get("IMGBB_API_KEY")
    hf_api_key = os.environ.get("HF_API_KEY")

    if imgbb_api_key and hf_api_key:
        print("Using HuggingFace Inference API for LLaVA")
        return compare_with_llava_hf_api(
            reference_image_path,
            user_image_path,
            model_id=model_id,
            save_image=save_image,
            output_dir=output_dir,
            imgbb_api_key=imgbb_api_key,
            hf_api_key=hf_api_key,
        )

    # Otherwise use the local version
    try:
        print(
            f"Loading images from {reference_image_path} and {user_image_path}"
        )

        # Create output directory if specified
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

        # Load the images
        reference_image = load_image(reference_image_path)
        user_image = load_image(user_image_path)

        # Resize images to similar heights for better comparison
        target_height = min(reference_image.height, user_image.height, 600)
        ref_aspect = reference_image.width / reference_image.height
        user_aspect = user_image.width / user_image.height

        reference_image = reference_image.resize(
            (int(target_height * ref_aspect), target_height)
        )
        user_image = user_image.resize(
            (int(target_height * user_aspect), target_height)
        )

        # Concatenate the images horizontally
        concatenated_image = concatenate_images_horizontal(
            [reference_image, user_image], dist_images=50
        )

        # Save the concatenated image if requested
        output_image_path = None
        if save_image:
            import uuid

            image_id = str(uuid.uuid4())[:8]
            output_file = f"concatenated_{image_id}.jpg"
            if output_dir:
                output_image_path = os.path.join(output_dir, output_file)
            else:
                output_image_path = output_file
            concatenated_image.save(output_image_path)
            print(f"Saved concatenated image to {output_image_path}")

        # Use the preloaded model if provided, otherwise load a new one
        if preloaded_model is not None:
            print("Using pre-loaded LLaVA model")
            pipe = preloaded_model
        else:
            pipe = load_llava_model(model_id)

        # Prepare the prompt for handwriting comparison
        prompt = (
            "USER: <image>\n"
            "You are a Calligraphy teacher evaluating a student's handwriting. "
            "The image on the left is the reference calligraphy, and the image on the right "
            "is the student's handwriting. Compare them and provide specific feedback on: "
            "1. Stroke accuracy and proportion, "
            "2. Character balance and spacing, "
            "3. Overall visual harmony. "
            "Be detailed."
            "Your response must be in English only."
            "Limit your response to 150 words.\n"
            "ASSISTANT:"
        )

        print("Analyzing handwriting...")
        outputs = pipe(
            concatenated_image,
            prompt=prompt,
            generate_kwargs={"max_new_tokens": 300},
        )
        llava_feedback = outputs[0]["generated_text"]

        # Process the LLaVA feedback through Ollama for ahjumma-style response
        ollama_host = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
        feedback = process_feedback_with_ollama(llava_feedback, ollama_host)

        return feedback, output_image_path

    except Exception as e:
        print(f"Error in compare_with_llava: {str(e)}")
        return f"Error analyzing handwriting: {str(e)}", None


# Alternative method using chat-style input format for newer LLaVA models
def compare_with_llava_chat(
    reference_image_path,
    user_image_path,
    model_id="llava-hf/llava-v1.5-7b",
    save_image=True,
    output_dir=None,
    preloaded_model=None,
):
    """
    Compare images using the chat-style input format for newer LLaVA models.

    Args:
        reference_image_path (str): Path to reference image
        user_image_path (str): Path to user's handwriting image
        model_id (str): Hugging Face model ID
        save_image (bool): Whether to save the concatenated image
        output_dir (str): Directory to save the output image
        preloaded_model: Optional preloaded pipeline model

    Returns:
        tuple: (feedback_text, output_image_path)
    """
    # If environment variables are set for API keys, use the API version
    imgbb_api_key = os.environ.get("IMGBB_API_KEY")
    hf_api_key = os.environ.get("HF_API_KEY")

    if imgbb_api_key and hf_api_key:
        print("Using HuggingFace Inference API for LLaVA")
        return compare_with_llava_hf_api(
            reference_image_path,
            user_image_path,
            model_id=model_id,
            save_image=save_image,
            output_dir=output_dir,
            imgbb_api_key=imgbb_api_key,
            hf_api_key=hf_api_key,
        )

    try:
        # Load and concatenate images as in the original function
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

        # Load the images
        reference_image = load_image(reference_image_path)
        user_image = load_image(user_image_path)

        # Resize images to similar heights for better comparison
        target_height = min(reference_image.height, user_image.height, 600)
        ref_aspect = reference_image.width / reference_image.height
        user_aspect = user_image.width / user_image.height

        reference_image = reference_image.resize(
            (int(target_height * ref_aspect), target_height)
        )
        user_image = user_image.resize(
            (int(target_height * user_aspect), target_height)
        )

        # Concatenate the images horizontally
        concatenated_image = concatenate_images_horizontal(
            [reference_image, user_image], dist_images=50
        )

        # Save the concatenated image if requested
        output_image_path = None
        if save_image:
            import uuid

            image_id = str(uuid.uuid4())[:8]
            output_file = f"concatenated_{image_id}.jpg"
            if output_dir:
                output_image_path = os.path.join(output_dir, output_file)
            else:
                output_image_path = output_file
            concatenated_image.save(output_image_path)
            print(f"Saved concatenated image to {output_image_path}")

        # Use the preloaded model if provided, otherwise load a new one
        if preloaded_model is not None:
            print("Using pre-loaded LLaVA model")
            pipe = preloaded_model
        else:
            # Use image-text-to-text pipeline for chat models
            print(f"Loading LLaVA model {model_id}...")
            quantization_config = BitsAndBytesConfig(
                load_in_4bit=True, bnb_4bit_compute_dtype=torch.float16
            )

            pipe = pipeline(
                "image-text-to-text",  # Use this task for chat-style models
                model=model_id,
                device_map="auto",
                model_kwargs={"quantization_config": quantization_config},
            )

        # Create message format for chat models
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "image": concatenated_image,
                    },
                    {
                        "type": "text",
                        "text": (
                            "You are a Korean calligraphy teacher evaluating a student's handwriting. "
                            "The image on the left is the reference calligraphy, and the image on the right "
                            "is the student's handwriting. Compare them and provide specific feedback on: "
                            "1. Stroke accuracy and proportion, "
                            "2. Character balance and spacing, "
                            "3. Overall visual harmony. "
                            "Be detailed but encouraging, like a supportive but slightly sassy Korean ahjumma. "
                            "Limit your response to 150 words."
                        ),
                    },
                ],
            }
        ]

        print("Analyzing handwriting...")
        outputs = pipe(
            text=messages, max_new_tokens=300, return_full_text=False
        )

        if isinstance(outputs, list) and len(outputs) > 0:
            llava_feedback = outputs[0]["generated_text"]

            # Process the LLaVA feedback through Ollama for ahjumma-style response
            ollama_host = os.environ.get(
                "OLLAMA_HOST", "http://localhost:11434"
            )
            feedback = process_feedback_with_ollama(
                llava_feedback, ollama_host
            )

            return feedback, output_image_path
        else:
            return "Error: Unexpected model output format", output_image_path

    except Exception as e:
        print(f"Error in compare_with_llava_chat: {str(e)}")
        return f"Error analyzing handwriting: {str(e)}", None


# Direct usage example
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Compare Korean handwriting using LLaVA"
    )
    parser.add_argument(
        "--reference",
        required=True,
        help="Path to reference calligraphy image",
    )
    parser.add_argument(
        "--user", required=True, help="Path to user's handwriting image"
    )
    parser.add_argument(
        "--model",
        default="llava-hf/llava-1.5-7b-hf",
        help="HuggingFace model ID for LLaVA",
    )
    parser.add_argument(
        "--output-dir",
        default="llava_output",
        help="Directory to save output image",
    )
    parser.add_argument(
        "--chat-format",
        action="store_true",
        help="Use chat format for newer LLaVA models",
    )
    parser.add_argument(
        "--use-api",
        action="store_true",
        help="Use HuggingFace Inference API instead of local model",
    )
    parser.add_argument(
        "--imgbb-key",
        help="ImgBB API key for image hosting (needed for API mode)",
    )
    parser.add_argument(
        "--hf-key",
        help="HuggingFace API key for inference (needed for API mode)",
    )

    args = parser.parse_args()

    # If using API mode, use the HF API implementation
    if args.use_api:
        # Get keys from args or environment variables
        imgbb_key = args.imgbb_key or os.environ.get("IMGBB_API_KEY")
        hf_key = args.hf_key or os.environ.get("HF_API_KEY")

        if not imgbb_key or not hf_key:
            print(
                "Error: ImgBB and HuggingFace API keys are required for API mode"
            )
            print(
                "Set them with --imgbb-key and --hf-key or as environment variables"
            )
            sys.exit(1)

        feedback, image_path = compare_with_llava_hf_api(
            args.reference,
            args.user,
            model_id=args.model,
            output_dir=args.output_dir,
            imgbb_api_key=imgbb_key,
            hf_api_key=hf_key,
        )
    elif args.chat_format:
        feedback, image_path = compare_with_llava_chat(
            args.reference,
            args.user,
            model_id=args.model,
            output_dir=args.output_dir,
        )
    else:
        feedback, image_path = compare_with_llava(
            args.reference,
            args.user,
            model_id=args.model,
            output_dir=args.output_dir,
        )

    print("\n=== Handwriting Analysis ===\n")
    print(feedback)
    print(f"\nComparison image saved to: {image_path}")
