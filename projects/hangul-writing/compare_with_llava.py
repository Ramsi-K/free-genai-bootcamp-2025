# compare_with_llava.py

import subprocess
import datetime
import os
import sys

# === CONFIG ===
if len(sys.argv) > 2:
    # Accept command line arguments for automated testing or API use
    REF_IMG = sys.argv[1]
    USER_IMG = sys.argv[2]
else:
    # Interactive mode for manual use
    REF_IMG = input("Enter path to reference image (calligraphy): ").strip()
    USER_IMG = input("Enter path to user image (handwriting): ").strip()

OUTPUT_DIR = "llava_output"
PROMPT = (
    "Compare the two handwriting samples. "
    "Give honest feedback like a strict Korean teacher. "
    "Focus on accuracy, stroke style, spacing, and neatness."
)

# === Ensure output directory exists ===
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# === Generate unique output filename for saved concatenated image ===
timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
output_img = os.path.join(OUTPUT_DIR, f"comparison_{timestamp}.png")

# === Find llava-multi-images.py ===
script_paths = [
    "./llava-multi-images.py",               # Current directory
    "/llava/llava-multi-images.py",          # Docker container location
    "../LLaVA/llava-multi-images.py",        # Relative path if in subdirectory
    os.path.expanduser("~/LLaVA/llava-multi-images.py")  # Home directory
]

llava_script = None
for path in script_paths:
    if os.path.exists(path):
        llava_script = path
        break

if not llava_script:
    print("Error: Could not find llava-multi-images.py script")
    sys.exit(1)

# === Run LLaVA CLI script ===
COMMAND = [
    "python",
    llava_script,
    "--load-4bit",
    "--images",
    REF_IMG,
    USER_IMG,
    "--dist-images",
    "100",
    "--concat-strategy",
    "horizontal",
    "--save-image",
    "--prompt",
    PROMPT
]

print("Running LLaVA CLI comparison...")
result = subprocess.getoutput(" ".join(COMMAND))

# === Save/rename the output image ===
default_output_img = "concatenated.png"
if os.path.exists(default_output_img):
    os.rename(default_output_img, output_img)
    print(f"✅ Output image saved to: {output_img}")
else:
    print("⚠️ Expected output image not found.")

# === Print feedback from the model ===
print("\n=== LLaVA Feedback ===")
print(result.strip())
