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
from PIL import Image
from io import BytesIO
from transformers import pipeline, BitsAndBytesConfig


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

    Returns:
        tuple: (feedback_text, output_image_path)
    """
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
            # Set up the quantization config for 4-bit loading
            print("Setting up quantization config...")
            quantization_config = BitsAndBytesConfig(
                load_in_4bit=True, bnb_4bit_compute_dtype=torch.float16
            )

            # Load the LLaVA model with the transformers pipeline
            print(f"Loading LLaVA model {model_id}...")
            pipe = pipeline(
                "image-to-text",
                model=model_id,
                model_kwargs={"quantization_config": quantization_config},
            )

        # Load the LLaVA model with the transformers pipeline
        # print(f"Loading LLaVA model {model_id}...")
        # pipe = pipeline(
        #     "image-to-text",
        #     model=model_id,
        #     model_kwargs={"quantization_config": quantization_config},
        # )

        # Prepare the prompt for handwriting comparison
        prompt = (
            "USER: <image>\n"
            "You are a Korean calligraphy teacher evaluating a student's handwriting. "
            "The image on the left is the reference calligraphy, and the image on the right "
            "is the student's handwriting. Compare them and provide specific feedback on: "
            "1. Stroke accuracy and proportion, "
            "2. Character balance and spacing, "
            "3. Overall visual harmony. "
            "Be detailed but encouraging, like a supportive but slightly sassy Korean ahjumma. "
            "Limit your response to 150 words.\n"
            "ASSISTANT:"
        )

        print("Analyzing handwriting...")
        outputs = pipe(
            concatenated_image,
            prompt=prompt,
            generate_kwargs={"max_new_tokens": 300},
        )
        feedback = outputs[0]["generated_text"]

        return feedback, output_image_path

    except Exception as e:
        print(f"Error in compare_with_llava: {str(e)}")
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

    args = parser.parse_args()

    feedback, image_path = compare_with_llava(
        args.reference,
        args.user,
        model_id=args.model,
        output_dir=args.output_dir,
    )

    print("\n=== Handwriting Analysis ===\n")
    print(feedback)
    print(f"\nComparison image saved to: {image_path}")
