# llava_compatibility.py
# This file provides compatibility between different LLaVA versions
# It addresses the "cannot import name 'LlavaLlamaForCausalLM'" error

import sys
import os


def patch_llava_imports():
    """
    Patch the LLaVA imports to ensure compatibility between different versions.
    This is required because LLaVA-CLI-with-multiple-images might be using
    import paths that don't match the current LLaVA structure.
    """
    try:
        # Try to import from current structure
        from llava.model.language_model.llava_llama import (
            LlavaLlamaForCausalLM,
        )
        from llava.model import LlavaForConditionalGeneration

        # If we got here, we need to add compatibility layer
        sys.modules["llava.model.LlavaLlamaForCausalLM"] = (
            LlavaLlamaForCausalLM
        )

        # Patch the direct import
        if "llava.model" in sys.modules:
            setattr(
                sys.modules["llava.model"],
                "LlavaLlamaForCausalLM",
                LlavaLlamaForCausalLM,
            )

        print("✓ Successfully patched LLaVA imports")
        return True
    except ImportError as e:
        print(f"⚠️ Could not patch LLaVA imports: {e}")
        return False


def fix_llava_multi_images():
    """
    Modify the llava-multi-images.py script to use our compatibility layer.
    This is needed if patching at runtime doesn't work.
    """
    script_paths = [
        "./llava/llava-multi-images.py",
        "/app/llava/llava-multi-images.py",
        "/llava/llava-multi-images.py",
        "llava-multi-images.py",
    ]

    script_path = None
    for path in script_paths:
        if os.path.exists(path):
            script_path = path
            break

    if not script_path:
        print("⚠️ Could not find llava-multi-images.py")
        return False

    # Read the script
    with open(script_path, "r") as f:
        content = f.read()

    # Add our compatibility import at the top
    if "import llava_compatibility" not in content:
        modified_content = (
            "# Import compatibility layer\n"
            "import llava_compatibility\n"
            "llava_compatibility.patch_llava_imports()\n\n"
        ) + content

        # Write back the modified script
        with open(script_path, "w") as f:
            f.write(modified_content)

        print(
            f"✓ Successfully modified {script_path} to use compatibility layer"
        )
        return True

    return True  # Already patched


if __name__ == "__main__":
    # This can be run directly to patch the llava-multi-images.py script
    if patch_llava_imports():
        fix_llava_multi_images()
    else:
        print("Failed to apply compatibility patches")
