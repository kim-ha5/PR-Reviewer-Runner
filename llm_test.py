import requests
import time

url = "http://127.0.0.1:11434/api/generate"

payload = {
    "model": "qwen2.5:7b",
    "prompt": "Say hello in one sentence.",
    "stream": False
}

print("Sending request to Qwen...")
start =time.time()

response= requests.post(
    url,
    json=payload,
    timeout=120
)

print(f"Response received in {time.time() - start:.1f} seconds")

response.raise_for_status()

data = response.json()

print("\n--- Qwen Response ---")
print(data["response"])