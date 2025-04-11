# -*- coding: utf-8
import torch
import torch.nn as nn
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from transformers import AutoProcessor, CLIPVisionModel
from PIL import Image
from huggingface_hub import hf_hub_download

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


def classify_image(image_path, model, processor, device):
    """
    Classify image using the trained model.
    """
    class_names = sorted(
        [
            "A",
            "B",
            "C",
            "D",
            "E",
            "F",
            "G",
            "H",
            "I",
            "J",
            "K",
            "L",
            "M",
            "N",
            "O",
            "P",
            "Q",
            "R",
            "S",
            "T",
            "U",
            "V",
            "W",
            "X",
            "Y",
            "Z",
        ]
    )
    index2label = {
        idx: label for idx, label in enumerate(class_names)
    }  # Recreate the label mapping (A-Z)

    # Load and preprocess the image
    image = Image.open(image_path).convert("RGB")
    inputs = processor(images=image, return_tensors="pt", padding=True)
    pixel_values = inputs["pixel_values"].to(device)

    # Make prediction
    with torch.no_grad():
        logits = model(pixel_values=pixel_values)
        predicted_idx = torch.argmax(logits, dim=1).item()
        predicted_class = index2label[predicted_idx]

        # Get probabilities for all classes
        probabilities = torch.nn.functional.softmax(logits, dim=1)[0]
        confidence = probabilities[predicted_idx].item()

    return predicted_class, confidence


# Predict image class
if __name__ == "__main__":
    # Load the model
    model, processor, device = load_model()

    # Make a prediction
    image_path = ""
    predicted_letter, confidence = classify_image(
        image_path, model, processor, device
    )

    # Display image and predicted class
    image = Image.open(image_path)
    plt.imshow(image)
    plt.axis("off")
    plt.show()
    print(f"Predicted class: {predicted_letter}")
    print(f"Confidence: {confidence:.2%}")
