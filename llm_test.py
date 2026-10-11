import requests
import subprocess
import shutil
import time
import platform


OLLAMA_URL = "http://127.0.0.1:11434"
MODEL = "qwen2.5:7b"


def check_ollama_installed():
    """Check if Ollama is installed on the system."""
    return shutil.which("ollama") is not None


def install_ollama():
    """Install Ollama using Homebrew."""
    print("Ollama is not installed. Installing Ollama...")

    if platform.system()!= "Darwin":
        raise RuntimeError(
            "Automatic installation is currently configured for macOS only."
        )

    if shutil.which("brew") is None:
        raise RuntimeError(
            "Homebrew is not installed. Please install Homebrew first."
        )

    subprocess.run(
        ["brew", "install", "ollama"],
        check=True
    )

    print("Ollama installed successfully.")


def is_ollama_running():
    """Check if the Ollama server is running."""
    try:
        response =requests.get(OLLAMA_URL, timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        return False


def start_ollama():
    """Start the Ollama server if it is not already running."""
    if is_ollama_running():
        print("Ollama is already running.")
        return

    print("Starting Ollama...")

    subprocess.Popen(
        ["ollama","serve"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    # Give Ollama a few seconds to start
    for _ in range(10):
        if is_ollama_running():
            print("Ollama is running.")
            return
        time.sleep(1)

    raise RuntimeError("Ollama failed to start.")


def check_model():
    """Check if the Qwen model is available."""
    result =subprocess.run(
        ["ollama","list"],
        capture_output=True,
        text=True,
        check=True
    )

    if MODEL in result.stdout:
        print(f"{MODEL} is already installed.")
        return

    print(f"{MODEL} is not installed. Downloading...")
    subprocess.run(
        ["ollama","pull", MODEL],
        check=True
    )

    print(f"{MODEL} downloaded successfully.")


def query_qwen(prompt):
    """Send a prompt to Qwen through the Ollama API."""
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False
    }

    print("Sending request to Qwen...")
    start = time.time()

    response = requests.post(
        f"{OLLAMA_URL}/api/generate",
        json=payload,
        timeout=120
    )

    print(
        f"Response received in "
        f"{time.time() - start:.1f} seconds"
    )

    response.raise_for_status()

    data = response.json()

    return data["response"]


def main():
    """Set up Ollama and test the Qwen model."""

    # Check/install Ollama
    if check_ollama_installed():
        print("Ollama is installed.")
    else:
        install_ollama()

    # Start Ollama if necessary
    start_ollama()

    # Make sure Qwen is available
    check_model()

    # Test Qwen
    prompt = "Say hello in one sentence."
    result = query_qwen(prompt)

    print("\n--- Qwen Response ---")
    print(result)


if __name__ == "__main__":
    main()