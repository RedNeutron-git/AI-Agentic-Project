# Pentest AI Agent

A modular, local-first AI agent framework for penetration testing workflows — powered by a self-hosted LLM (Mistral, via Ollama). Built to be extended with additional security tools over time. No API costs, no data leaves the machine.

## About This Project

This project is a personal learning exercise to explore how AI agents work in practice — combining a locally-hosted LLM with real security tooling to automate recon, analysis, and reporting workflows. It's part of an ongoing journey into AI security and MLSecOps, built step by step from scratch to understand each moving part: model hosting, API integration, and tool orchestration.

The goal is to keep this **modular** — each security tool (Nmap, and eventually others like Nuclei, Nikto, etc.) plugs into the same core LLM analysis pipeline, rather than building a one-off script per tool.

**Disclaimer:** This tool is for authorized testing and educational purposes only. Only run scans against systems you own or have explicit permission to test.

## Features

- Local LLM (Mistral 7B via Ollama) as the reasoning engine — 100% offline inference, zero API cost
- Modular tool integration — currently supports Nmap, designed to accept additional recon/scanning tools
- Structured LLM analysis: summary, potential risks, recommendations
- Consistent output pipeline, ready to extend into report generation (`.docx`, etc.)

## Prerequisites

- Kali Linux (or any Debian-based distro)
- Python 3
- Security tools as needed per module (e.g. Nmap for the recon module)
- ~8GB RAM available (for running the Mistral 7B model)

## Setup Instructions

```bash
# Download Ollama
curl -fsSL -o ollama-linux-amd64.tar.zst https://ollama.com/download/ollama-linux-amd64.tar.zst

# Make sure zstd is installed (required to extract .tar.zst)
sudo apt install zstd

# Extract & install Ollama
sudo tar -xf ollama-linux-amd64.tar.zst -C /usr

# Start Ollama server
ollama serve
```

```bash
# Download the GGUF model manually (browser recommended for stability)
# Source: https://huggingface.co/bartowski/Mistral-7B-Instruct-v0.3-GGUF/resolve/main/Mistral-7B-Instruct-v0.3-Q4_K_M.gguf

# Create Modelfile
cat > Modelfile << 'EOF'
FROM /path/to/Mistral-7B-Instruct-v0.3-Q4_K_M.gguf
EOF

# Import the model into Ollama
ollama create mistral-manual -f Modelfile
```

```bash
# Set up Python virtual environment
python3 -m venv venv-module
source venv-module/bin/activate
pip install requests

# To exit the virtual environment later:
deactivate
```

## Usage

```bash
# 1. Test the connection to Ollama
python3 test_ollama.py

# 2. Run the Nmap recon module standalone
python3 nmap_scanner.py

# 3. Run the full flow: recon module + LLM analysis
python3 analyze_scan.py
```

## License

MIT License

## Credit

Built by **RedNeutron**
