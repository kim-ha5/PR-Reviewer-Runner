import requests
import subprocess
import shutil
import time
import platform


OLLAMA_URL= "http://127.0.0.1:11434"
MODEL = "qwen2.5:7b"


def check_ollama_installed():
    """Check if Ollama is installed on the system."""
    return shutil.which("ollama") is not None


def install_ollama():
    """Install Ollama based on the operating system."""
    system = platform.system()

    if system== "Darwin":
        # macOS
        if shutil.which("brew") is None:
            raise RuntimeError(
                "Homebrew is not installed. "
                "Please install Homebrew first."
            )

        print("Installing Ollama on macOS...")
        subprocess.run(
            ["brew", "install", "ollama"],
            check=True
        )

    elif system== "Linux":
        # Linux
        print("Installing Ollama on Linux...")
        subprocess.run(
            [
                "sh",
                "-c",
                "curl -fsSL https://ollama.com/install.sh | sh"
            ],
            check=True
        )

    elif system =="Windows":
        # Windows
        raise RuntimeError(
            "Ollama is not installed.\n"
            "Please install Ollama from:\n"
            "https://ollama.com/download/windows\n"
            "Then run this program again."
        )

    else:
        raise RuntimeError(
            f"Unsupported operating system: {system}"
        )

    print("Ollama installed successfully.")


def is_ollama_running():
    """Check if the Ollama server is running."""
    try:
        response = requests.get(
            OLLAMA_URL,
            timeout=5
        )

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
        ["ollama", "serve"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    # Wait for Ollama to start
    for _ in range(15):
        if is_ollama_running():
            print("Ollama is running.")
            return

        time.sleep(1)

    raise RuntimeError(
        "Ollama failed to start."
    )


def check_model():
    """Check if the Qwen model is installed."""
    result =subprocess.run(
        ["ollama", "list"],
        capture_output=True,
        text=True,
        check=True
    )

    if MODEL in result.stdout:
        print(f"{MODEL} is already installed.")
        return

    print(f"{MODEL} is not installed.")
    print(f"Downloading {MODEL}...")

    subprocess.run(
        ["ollama", "pull", MODEL],
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

    elapsed = time.time() - start

    print(
        f"Response received in {elapsed:.1f} seconds"
    )

    response.raise_for_status()

    data = response.json()

    return data["response"]


def main():
    """Set up Ollama and test the Qwen model."""

    # Check if Ollama is installed
    if check_ollama_installed():
        print("Ollama is installed.")
    else:
        install_ollama()

    # Start Ollama if necessary
    start_ollama()

    # Check if Qwen is installed
    check_model()

    # Test Qwen
    prompt = "Say hello in one sentence."

    result = query_qwen(prompt)

    print("\n--- Qwen Response ---")
    print(result)


if __name__ == "__main__":
    main()