# -*- coding: utf-8
import torch
import torch.nn as nn
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from transformers import AutoProcessor, CLIPVisionModel
from PIL import Image
from huggingface_hub import hf_hub_download
import os
import requests
from io import BytesIO

# Initialise device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


# Define module with a classifier head that maps image features from CLIPVision to the number of classes
class CLIPVisionClassifier(nn.Module):
    def __init__(self, clip_model, num_classes):
        super().__init__()
        self.model = clip_model
        self.classifier = nn.Linear(self.model.config.hidden_size, num_classes)

    def forward(self, pixel_values):
        outputs = self.model(pixel_values=pixel_values)
        image_features = outputs.pooler_output
        logits = self.classifier(image_features)
        return logits


def load_model(model_id="aalof/clipvision-asl-fingerspelling"):
    """
    Load model and processor with trained weights.
    """
    processor = AutoProcessor.from_pretrained(model_id)

    # Load the base CLIP model
    clip_model = CLIPVisionModel.from_pretrained(
        "openai/clip-vit-base-patch32"
    )

    # Initialise the full model (including classifier)
    model = CLIPVisionClassifier(clip_model=clip_model, num_classes=26).to(
        device
    )

    # Download and load the trained weights
    weights_path = hf_hub_download(
        repo_id=model_id, filename="pytorch_model.bin"
    )
    model.load_state_dict(torch.load(weights_path, map_location=device))
    model.eval()

    return model, processor, device


def load_image(image_source):
    """Load an image from a file path, URL, or PIL Image object."""
    if isinstance(image_source, Image.Image):
        return image_source.convert("RGB")

    if isinstance(image_source, str):
        if image_source.startswith("http://") or image_source.startswith(
            "https://"
        ):
            response = requests.get(image_source)
            return Image.open(BytesIO(response.content)).convert("RGB")
        elif os.path.isfile(image_source):
            return Image.open(image_source).convert("RGB")

    raise ValueError(
        "Image source must be a PIL Image object, file path, or URL"
    )


def predict_class(image_source, model=None, processor=None):
    """
    Predict the ASL letter class from an image source (file path, URL, or PIL Image).

    If model and processor are not provided, they will be loaded.
    Returns the predicted letter and confidence score.
    """
    # Load model if not provided
    if model is None or processor is None:
        model, processor, _ = load_model()

    # Define the class names (A-Z)
    class_names = [chr(65 + i) for i in range(26)]  # ASCII values for A-Z
    index2label = {idx: label for idx, label in enumerate(class_names)}

    # Load and preprocess the image
    image = load_image(image_source)
    inputs = processor(images=image, return_tensors="pt", padding=True)
    pixel_values = inputs["pixel_values"].to(device)

    # Make prediction
    with torch.no_grad():
        logits = model(pixel_values=pixel_values)
        predicted_idx = torch.argmax(logits, dim=1).item()
        predicted_letter = index2label[predicted_idx]

        # Get confidence score
        probabilities = torch.nn.functional.softmax(logits, dim=1)[0]
        confidence = (
            probabilities[predicted_idx].item() * 100
        )  # Convert to percentage

    return predicted_letter, confidence


# Predict image class
if __name__ == "__main__":
    # Load the model
    model, processor, device = load_model()

    # Make a prediction
    image_path = input("Enter the path to an ASL fingerspelling image: ")
    if not image_path:
        print("No image path provided. Exiting.")
        exit(1)

    predicted_letter, confidence = predict_class(image_path, model, processor)

    # Display image and predicted class
    image = Image.open(image_path)
    plt.imshow(image)
    plt.axis("off")
    plt.title(f"Predicted: {predicted_letter} (Confidence: {confidence:.2f}%)")
    plt.show()
    print(f"Predicted letter: {predicted_letter}")
    print(f"Confidence: {confidence:.2f}%")
