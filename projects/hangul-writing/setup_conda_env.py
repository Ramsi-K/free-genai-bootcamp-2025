import os
import subprocess
import sys
import platform


def check_conda():
    """Check if conda is installed and available in PATH"""
    try:
        subprocess.run(
            ["conda", "--version"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        return False


def create_conda_env():
    """Create and configure the conda environment for the Hangul Writing app"""
    env_name = "hangul-env"

    print(f"Setting up conda environment '{env_name}'...")

    # Check if environment already exists
    result = subprocess.run(
        ["conda", "env", "list"], stdout=subprocess.PIPE, text=True
    )
    if f"{env_name} " in result.stdout:
        print(f"Environment '{env_name}' already exists.")
        user_input = input(
            f"Do you want to update the existing environment? (y/n): "
        )
        if user_input.lower() != "y":
            print("Using existing environment without updates.")
            return env_name
        # Remove existing environment
        print(f"Removing existing environment '{env_name}'...")
        subprocess.run(["conda", "env", "remove", "-n", env_name], check=True)

    # Create new environment with Python 3.10
    print(f"Creating new conda environment '{env_name}' with Python 3.10...")
    subprocess.run(
        ["conda", "create", "-n", env_name, "python=3.10", "-y"], check=True
    )

    # Determine the correct pip to use
    if platform.system() == "Windows":
        pip_path = f"conda run -n {env_name} pip"
    else:
        # Linux/Mac
        pip_path = f"conda run -n {env_name} pip"

    # Install dependencies
    print("Installing required packages...")

    # Core dependencies
    packages = [
        "torch>=2.0.0",
        "transformers>=4.37.0",
        "flask>=2.0.0",
        "flask-cors>=4.0.0",
        "flask-caching>=2.0.0",
        "pillow>=10.0.0",
        "bitsandbytes>=0.41.0",
        "accelerate>=0.26.0",
        "nltk>=3.8",
        "numpy>=1.24.0",
        "scipy>=1.11.0",
        "werkzeug>=2.3.0",
        "sentencepiece>=0.1.99",
        "safetensors>=0.4.0",
        "peft>=0.7.0",
        "opencv-python>=4.8.0",
    ]

    # Install PyTorch with CUDA if available
    print("Checking for CUDA availability...")

    try:
        import torch

        if torch.cuda.is_available():
            cuda_version = torch.version.cuda
            print(f"CUDA is available (version {cuda_version})")
            if platform.system() == "Windows":
                subprocess.run(
                    f"{pip_path} install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118",
                    shell=True,
                    check=True,
                )
            else:
                # Linux/Mac
                subprocess.run(
                    f"{pip_path} install torch torchvision torchaudio",
                    shell=True,
                    check=True,
                )
        else:
            print("CUDA not detected, installing CPU version")
            subprocess.run(
                f"{pip_path} install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu",
                shell=True,
                check=True,
            )
    except:
        print(
            "Could not check CUDA, installing PyTorch without specific CUDA version"
        )
        subprocess.run(
            f"{pip_path} install torch torchvision torchaudio",
            shell=True,
            check=True,
        )

    # Install other dependencies
    for package in packages:
        print(f"Installing {package}...")
        subprocess.run(f"{pip_path} install {package}", shell=True, check=True)

    print("\nSetup completed successfully!")
    print(f"To activate the environment, run: conda activate {env_name}")
    return env_name


def main():
    """Main function to set up the conda environment"""
    if not check_conda():
        print("Conda is not installed or not available in PATH.")
        print("Please install Conda and add it to your PATH.")
        print(
            "You can download Conda from: https://docs.conda.io/en/latest/miniconda.html"
        )
        sys.exit(1)

    env_name = create_conda_env()

    print("\n===== Hangul Calligraphy App Setup Complete =====")
    print(f"Conda environment '{env_name}' is ready!")
    print("\nNext steps:")
    print("1. Activate the environment:        conda activate " + env_name)
    print("2. Download the LLaVA model:        python download_model.py")
    print("3. Start app (without Docker):      python server.py")
    print("   OR")
    print("   Start app (with Docker):         docker-compose up -d")
    print(
        "\nImportant: Downloading and using the LLaVA model requires significant disk space and RAM/GPU memory."
    )


if __name__ == "__main__":
    main()
