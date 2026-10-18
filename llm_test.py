import argparse
import json
import requests
import subprocess
import shutil
import time
import platform
from pathlib import Path


OLLAMA_URL = "http://127.0.0.1:11434"
MODEL = "qwen2.5:7b"
DEFAULT_PROMPT = Path("prompts/test-prompt.md")
DEFAULT_FINDINGS = Path("codeql-findings.json")
DEFAULT_SOURCE = Path("testing_code.py")
DEFAULT_OUTPUT = Path("findings/llm-review.json")
DEFAULT_MARKDOWN_OUTPUT = Path("findings/llm-review.md")


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
        timeout=None
    )

    elapsed = time.time() - start

    print(
        f"Response received in {elapsed:.1f} seconds"
    )

    response.raise_for_status()

    data = response.json()

    return data["response"]


def parse_review(result, finding_count):
    """Parse and validate the model's one-explanation-per-finding response."""
    cleaned = result.strip()
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        if len(lines) < 3 or not lines[-1].strip().startswith("```"):
            raise ValueError("Qwen returned an incomplete JSON code fence.")
        cleaned = "\n".join(lines[1:-1]).strip()

    try:
        review = json.loads(cleaned)
    except json.JSONDecodeError as error:
        raise ValueError("Qwen did not return valid JSON.") from error

    if not isinstance(review, list) or len(review) != finding_count:
        raise ValueError(
            "Qwen must return exactly one review object per CodeQL finding."
        )

    indices = []
    for item in review:
        if not isinstance(item, dict):
            raise ValueError("Every Qwen review must be a JSON object.")
        if not isinstance(item.get("finding_index"), int):
            raise ValueError("Every review must have an integer finding_index.")
        if not isinstance(item.get("explanation"), str) or not item["explanation"].strip():
            raise ValueError("Every review must have a non-empty explanation.")
        if not isinstance(item.get("impact"), str) or not item["impact"].strip():
            raise ValueError("Every review must have a non-empty impact.")
        indices.append(item["finding_index"])

    if sorted(indices) != list(range(finding_count)):
        raise ValueError(
            "Qwen review indices must contain every CodeQL finding exactly once."
        )

    return review


def load_prompt(template_path, findings_path, source_path):
    """Build the LLM prompt from CodeQL findings and the vulnerable source."""
    if not template_path.is_file():
        raise FileNotFoundError(f"Prompt file not found: {template_path}")
    if not findings_path.is_file():
        raise FileNotFoundError(
            f"CodeQL findings file not found: {findings_path}. "
            "Run CodeQL and scripts/extract_output.py first."
        )
    if not source_path.is_file():
        raise FileNotFoundError(f"Source file not found: {source_path}")

    try:
        findings = json.loads(findings_path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as error:
        raise ValueError(
            f"CodeQL findings are not valid JSON: {findings_path}"
        ) from error

    if not isinstance(findings, list):
        raise ValueError("CodeQL findings must be a JSON array.")
    if not findings:
        raise ValueError("CodeQL produced no findings to explain.")

    prompt = template_path.read_text(encoding="utf-8")
    return prompt.replace(
        "{{codeql_result}}",
        json.dumps(findings, indent=2, ensure_ascii=False),
    ).replace(
        "{{source_code}}",
        source_path.read_text(encoding="utf-8"),
    )


def main():
    """Explain CodeQL findings with Ollama."""
    parser = argparse.ArgumentParser(
        description="Send CodeQL findings and source code to Ollama."
    )
    parser.add_argument(
        "--findings",
        type=Path,
        default=DEFAULT_FINDINGS,
        help="JSON file produced by scripts/extract_output.py",
    )
    parser.add_argument(
        "--source",
        type=Path,
        default=DEFAULT_SOURCE,
        help="Source file referenced by the CodeQL findings",
    )
    parser.add_argument(
        "--prompt",
        type=Path,
        default=DEFAULT_PROMPT,
        help="Prompt template containing {{codeql_result}} and {{source_code}}",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="JSON file for the validated per-finding review",
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=DEFAULT_MARKDOWN_OUTPUT,
        help="Markdown file containing the raw model response",
    )
    args = parser.parse_args()

    # Check if Ollama is installed
    if check_ollama_installed():
        print("Ollama is installed.")
    else:
        install_ollama()

    # Start Ollama if necessary
    start_ollama()

    # Check if Qwen is installed
    check_model()

    prompt = load_prompt(args.prompt, args.findings, args.source)
    findings = json.loads(args.findings.read_text(encoding="utf-8-sig"))

    result = query_qwen(prompt)
    review = parse_review(result, len(findings))

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(review, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.write_text(result.rstrip() + "\n", encoding="utf-8")

    print("\n--- Qwen Response ---")
    print(result)


if __name__ == "__main__":
    main()