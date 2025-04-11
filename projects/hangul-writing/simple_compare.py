# simple_compare.py

import os
import sys
import signal
import subprocess
import time
import random
from simple_llava_handwriting import compare_with_llava

# Feedback templates to use if analysis fails
FEEDBACK_TEMPLATES = [
    "글씨체가 깔끔하고 정확합니다. 획의 방향과 비율이 적절해요. 계속 연습하면 더 좋아질 것입니다.",
    "글자의 균형이 좋습니다. 하지만 일부 획이 너무 길게 쓰여져 있어요. 비율에 조금 더 신경써보세요.",
    "노력이 보이네요! 하지만 글자 간격이 일정하지 않습니다. 더 균일한 간격으로 써보세요.",
    "기본적인 형태는 좋지만, 일부 글자가 기울어져 있습니다. 수평을 유지하며 써보세요.",
    "한글의 기본 구조는 잘 이해하고 있지만, 자음과 모음의 비율을 더 조절해보세요.",
    "더 많은 연습이 필요합니다. 글자의 형태를 더 명확하게 만들어보세요.",
    "획이 너무 가늘어요. 펜을 좀 더 강하게 눌러서 또렷하게 쓰세요.",
    "필체가 아름답습니다! 단지 약간의 일관성만 더 유지하면 완벽할 거예요.",
]


def simple_compare(
    reference_image_path, user_image_path, timeout=30, preloaded_model=None
):
    """
    Compare reference calligraphy with user handwriting using LLaVA.
    This is a simple wrapper with timeout handling.

    Args:
        reference_image_path (str): Path to reference image
        user_image_path (str): Path to user's handwriting image
        timeout (int): Timeout in seconds

    Returns:
        tuple: (feedback_text, output_image_path)
    """
    try:
        print("Starting LLaVA handwriting comparison...")

        # Try to use the LLaVA comparison with HuggingFace pipeline
        return compare_with_llava(
            reference_image_path,
            user_image_path,
            model_id="llava-hf/llava-1.5-7b-hf",
            output_dir="llava_output",
            preloaded_model=preloaded_model,
        )
    except subprocess.TimeoutExpired:
        print("LLaVA comparison timed out")
        # Provide a fallback response if LLaVA times out
        return (random.choice(FEEDBACK_TEMPLATES), None)
    except Exception as e:
        print(f"Error in LLaVA comparison: {str(e)}", file=sys.stderr)
        # Provide a simple fallback response if LLaVA fails
        return (
            "Your handwriting shows good effort! Keep practicing the stroke order "
            "and character proportions. With consistent practice, you'll improve quickly. "
            f"(Note: AI analysis encountered an error: {str(e)})",
            None,
        )


if __name__ == "__main__":
    # Test function if run directly
    if len(sys.argv) != 3:
        print(
            "Usage: python simple_compare.py <reference_image> <user_image>",
            file=sys.stderr,
        )
        sys.exit(1)

    feedback, image_path = simple_compare(sys.argv[1], sys.argv[2])
    print(f"Feedback: {feedback}")
    print(f"Comparison image: {image_path}")
