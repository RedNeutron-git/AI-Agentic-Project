"""
Nmap Scanner Module
Runs an nmap scan against a target (default: localhost), saving the raw
results in XML format (easy to parse) as well as plain text (to send to the LLM).
"""

import subprocess
import datetime
import os

# ==== CONFIGURATION ====
TARGET = "127.0.0.1"          # localhost, as agreed at the start
SCAN_ARGS = ["-sV", "-sC"]    # service/version detection + default scripts
OUTPUT_DIR = "scan_results"


def run_nmap_scan(target: str = TARGET, extra_args: list = None) -> dict:
    """
    Run an nmap scan and return the result as a dict:
    - raw_text: plain text output (to send to the LLM, more compact)
    - xml_path: path to the XML file (for structured parsing later if needed)
    - timestamp: when the scan was run
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    xml_output = os.path.join(OUTPUT_DIR, f"scan_{timestamp}.xml")

    args = ["nmap"] + (extra_args or SCAN_ARGS) + ["-oX", xml_output, "-oN", "-", target]

    print(f"[*] Running scan against {target}...")
    print(f"[*] Command: {' '.join(args)}\n")

    try:
        result = subprocess.run(
            args,
            capture_output=True,
            text=True,
            timeout=300,  # 5 min max, a localhost scan should be much faster
        )

        if result.returncode != 0:
            print(f"[!] Nmap exited with error code {result.returncode}")
            print(f"[!] stderr: {result.stderr}")

        raw_text = result.stdout

        print("[+] Scan complete.")
        print(f"[+] XML results saved to: {xml_output}\n")

        return {
            "raw_text": raw_text,
            "xml_path": xml_output,
            "timestamp": timestamp,
            "target": target,
        }

    except subprocess.TimeoutExpired:
        print("[!] Scan timed out (over 5 minutes). Try a more specific/faster scan.")
        return None
    except FileNotFoundError:
        print("[!] Command 'nmap' not found. Make sure nmap is installed.")
        return None


if __name__ == "__main__":
    scan_result = run_nmap_scan()
    if scan_result:
        print("=" * 60)
        print("RAW OUTPUT (to be sent to the LLM):")
        print("=" * 60)
        print(scan_result["raw_text"])