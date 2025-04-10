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
# The prompt will be passed directly to the LLaVA CLI tool after image paths
PROMPT = "Compare the two handwriting samples. Give honest feedback like a strict Korean teacher. Focus on accuracy, stroke style, spacing, and neatness."

# === Ensure output directory exists ===
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# === Generate unique output filename for saved concatenated image ===
timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
output_img = os.path.join(OUTPUT_DIR, f"comparison_{timestamp}.png")

# === Find llava-multi-images.py ===
script_paths = [
    "./llava-multi-images.py",  # Current directory
    "/llava/llava-multi-images.py",  # Docker container location
    "../LLaVA/llava-multi-images.py",  # Relative path if in subdirectory
    os.path.expanduser("~/LLaVA/llava-multi-images.py"),  # Home directory
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
# Format changed: adding the prompt at the end without a flag
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
]

# For debugging
print(f"Running command: {' '.join(COMMAND)}")
print(f"With prompt: {PROMPT}")

# Execute LLaVA with the command and prompt (sending prompt to stdin)
try:
    process = subprocess.Popen(
        COMMAND,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    stdout, stderr = process.communicate(input=PROMPT)
    result = stdout

    if process.returncode != 0:
        print(f"Error occurred (code {process.returncode}):")
        print(f"STDERR: {stderr}")
        result = f"Error: {stderr}"
except Exception as e:
    print(f"Exception running LLaVA: {e}")
    result = f"Exception: {e}"

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
