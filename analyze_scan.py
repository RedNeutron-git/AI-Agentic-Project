"""
Analyze Scan Module
Combines nmap_scanner.py + the Ollama API.
Flow: run nmap scan -> send raw results to LLM -> LLM returns a structured
analysis per finding, including OWASP references.
"""

import requests
import json
from nmap_scanner import run_nmap_scan

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "mistral-manual"

# Prompt template to keep the analysis output consistent
ANALYSIS_PROMPT_TEMPLATE = """You are a security analyst assistant. Below is the result of an nmap scan against a target.

Your task: analyze the scan results and identify relevant security findings.

For EACH finding identified, present it in the following format:

---
### [Number]. [Finding Name]

**Description:**
Explain what was found (port, service, version, configuration) briefly and factually.

**Risk:**
Explain the potential security risk of this finding. Include a severity level
(Low/Medium/High/Critical) if it can be assessed from the available data.

**Remediation Recommendation:**
Concrete steps that can be taken to mitigate/fix the issue.

**OWASP Reference:**
The relevant OWASP category (e.g. OWASP Top 10, OWASP ASVS, etc.), if applicable.
If no OWASP reference is relevant for this finding, write "Not applicable".

---

Important rules:
- Only report findings that are actually supported by the scan data. Do not invent findings.
- If the scan results are limited or show no significant risk, state that clearly.
- If there are no findings worth reporting, simply say "No significant findings from this scan result."
- Be concise and to the point, avoid filler content.

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
