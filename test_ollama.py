"""
Test connection from Python to the Ollama API.
Purpose: verify that we can send a prompt & receive a response from the
mistral-manual model via the API before moving on to more complex agent logic.
"""

import requests
import json

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "mistral-manual"


def test_ollama_connection():
    prompt = "Hi, briefly introduce yourself in 1-2 sentences."

    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,  # False = wait for the full response at once, easier to debug
    }

    print(f"[*] Sending prompt to {MODEL_NAME}...")
    print(f"[*] Prompt: {prompt}\n")

    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=120)
        response.raise_for_status()  # raise an error if status code isn't 200

        data = response.json()
        print("[+] Connection successful!")
        print("[+] Response from model:\n")
        print(data.get("response", "(empty)"))

    except requests.exceptions.ConnectionError:
        print("[!] Failed to connect to Ollama. Make sure 'ollama serve' is running.")
    except requests.exceptions.Timeout:
        print("[!] Timeout. The model may still be loading or taking too long.")
    except requests.exceptions.HTTPError as e:
        print(f"[!] HTTP Error: {e}")
        print(f"[!] Detail: {response.text}")
    except json.JSONDecodeError:
        print("[!] Response is not valid JSON. Raw response:")
        print(response.text)


if __name__ == "__main__":
    test_ollama_connection()
