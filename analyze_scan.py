"""
Analyze Scan Module
Combines nmap_scanner.py + the Ollama API.
Flow: run nmap scan -> send raw results to LLM -> LLM returns a structured analysis.
"""

import requests
import json
from nmap_scanner import run_nmap_scan

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "mistral-manual"

# System prompt to keep the analysis output consistent
ANALYSIS_PROMPT_TEMPLATE = """You are a security analyst assistant. Below is the result of an nmap scan against a target.

Your tasks:
1. Summarize which ports and services are open.
2. For each service, note general potential security risks (if any).
3. Provide brief follow-up recommendations.

Answer in a structured format with the following headings:
- PORT & SERVICE SUMMARY
- POTENTIAL RISKS
- RECOMMENDATIONS

Do not add information that is not present in the scan data. If the data is limited, say so.

=== NMAP SCAN RESULTS ===
{scan_output}
=== END OF SCAN RESULTS ===

Analysis:"""


def analyze_with_llm(scan_text: str) -> str:
    """Send scan results to Ollama, return the analysis as a string."""
    prompt = ANALYSIS_PROMPT_TEMPLATE.format(scan_output=scan_text)

    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
    }

    print("[*] Sending scan results to the LLM for analysis...")
    print("[*] (This may take tens of seconds depending on your machine's specs)\n")

    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=300)
        response.raise_for_status()
        data = response.json()
        return data.get("response", "(LLM did not return a response)")

    except requests.exceptions.ConnectionError:
        return "[!] Failed to connect to Ollama. Make sure 'ollama serve' is running."
    except requests.exceptions.Timeout:
        return "[!] Timed out waiting for the LLM response."
    except requests.exceptions.HTTPError as e:
        return f"[!] HTTP Error: {e}"
    except json.JSONDecodeError:
        return f"[!] Response is not valid JSON: {response.text}"


def run_full_analysis(target: str = "127.0.0.1") -> dict:
    """
    Full flow: scan -> analyze.
    Returns a dict containing the raw scan result + LLM analysis, ready
    for the next step (generating a docx report).
    """
    scan_result = run_nmap_scan(target=target)
    if not scan_result:
        print("[!] Scan failed, analysis cancelled.")
        return None

    analysis = analyze_with_llm(scan_result["raw_text"])

    print("=" * 60)
    print("LLM ANALYSIS RESULT")
    print("=" * 60)
    print(analysis)

    return {
        "scan_result": scan_result,
        "analysis": analysis,
    }


if __name__ == "__main__":
    run_full_analysis()
