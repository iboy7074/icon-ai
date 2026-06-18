# icon-ai
<div align="center">
  <h1>🤖 Red Team AI Agent</h1>
  <p><strong>Autonomous Penetration Testing Framework</strong></p>
  <p>
    <em>Linux · Windows · Termux (Android)</em>
  </p>
  <p>
    <a href="#-features">Features</a> •
    <a href="#-quick-start">Quick Start</a> •
    <a href="#-architecture">Architecture</a> •
    <a href="#-modules">Modules</a> •
    <a href="#-configuration">Configuration</a> •
    <a href="#-examples">Examples</a> •
    <a href="#-roadmap">Roadmap</a>
  </p>
</div>

---

## 🎯 Overview

**Red Team AI Agent** is an autonomous, LLM-powered penetration testing framework that reasons, plans, and executes real security assessments across **Linux (Kali/Ubuntu/Debian), Windows, and Termux (Android)**.

Instead of being a passive chatbot that suggests commands, this agent **actively runs tools, interprets results, decides next steps, and chains operations**—like a real red team operator, but automated.

It uses a **ReAct (Reasoning + Acting)** loop powered by your choice of LLM backend (OpenAI GPT-4, local Ollama models, or any OpenAI-compatible API) to conduct end-to-end pentests from reconnaissance through exploitation and reporting.

---

## ✨ Features

| Capability | Description |
|---|---|
| **🤖 Autonomous Operation** | LLM-driven planning & execution — no manual intervention needed |
| **🛠️ 20+ Integrated Tools** | nmap, sqlmap, hydra, nikto, gobuster, whatweb, dnsrecon, searchsploit, and more |
| **🌍 Cross-Platform** | Runs natively on Linux, Windows, and Termux (Android) |
| **🔌 Multi-LLM Backend** | OpenAI, Ollama (local), or any OpenAI-compatible API |
| **🔄 Dynamic Tool Discovery** | Auto-detects installed tools; offers to install missing ones |
| **📊 Structured Reporting** | Generates Markdown/HTML pentest reports with findings |
| **🧩 Modular Design** | Plug-in architecture for custom recon, scanning, and exploit modules |
| **📱 Termux-Optimized** | Full functionality on Android devices via Termux |
| **🔓 No Auth Restrictions** | Full exploit generation, reverse shells, C2 code — all authorized |

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+** installed on your system
- **An LLM API key** (OpenAI) or **Ollama** running locally (optional but recommended)

### Installation


###Termux (Android)
```bash
pkg install git python -y
git clone https://github.com/your-org/redteam-ai-agent.git
cd redteam-ai-agent
bash install.sh
```
#### Linux (Kali/Ubuntu/Debian/Arch)


```bash
git clone https://github.com/your-org/redteam-ai-agent.git
cd redteam-ai-agent
chmod +x install.sh
./install.sh
```

### Windows (PowerShell)
```bash
git clone https://github.com/your-org/redteam-ai-agent.git
cd redteam-ai-agent
.\install.ps1
```
### Configure

```bash
# Copy and edit the config
cp config.yaml config.yaml

# Set your API key (or use env var)
export OPENAI_API_KEY="sk-..."
```
### run
```bash
# Basic usage
python3 main.py -t 10.10.10.1 -o "Enumerate all ports, services, and find vulnerabilities"

# Verbose mode
python3 main.py -t example.com -o "Subdomain enumeration + web recon" --verbose

# List available tools on your system
python3 main.py --list-tools

# Show platform info
python3 main.py --platform-info
```
### Architecture
```bash
redteam-ai-agent/
│
├── main.py                      # Entry point — CLI argument parsing & orchestration
├── config.yaml                  # Global configuration
├── install.sh                   # Linux/Termux installer
├── install.ps1                  # Windows installer
├── requirements.txt             # Python dependencies
│
├── core/
│   ├── agent.py                 # ReAct agent loop (Observe → Think → Act → Repeat)
│   ├── llm_interface.py         # LLM abstraction (OpenAI, Ollama, OpenAI-compatible)
│   └── tool_registry.py         # Dynamic tool discovery & execution
│
├── modules/
│   ├── recon/                   # Reconnaissance modules
│   │   └── subdomain_enum.py    # DNS brute-force + crt.sh enumeration
│   ├── scanning/                # Network & web scanning
│   ├── exploitation/            # Exploit generation & execution
│   ├── post_exploit/            # Post-exploitation & pivoting
│   └── report/                  # Report generation
│
└── utils/
    ├── platform.py              # Cross-platform detection (Linux/Win/Termux)
    ├── executor.py              # Safe command execution
    └── logger.py                # Structured logging `
````
    
    
  ### How It Works
```bash
    ┌─────────────┐     ┌──────────────────┐     ┌───────────────┐
│  User sets   │────▶│  Agent ReAct     │────▶│  Tool Registry│
│  Objective   │     │  Loop (LLM)      │     │  (Execution)  │
└─────────────┘     └──────────────────┘     └───────┬───────┘
        ▲                                             │
        │               ┌─────────────────┐           │
        └───────────────│  Results &      │◀──────────┘
                        │  Observations   │
                        └─────────────────┘

```


### Configuration
```bashllm:
  backend: "openai"          # openai | ollama | openai_compatible
  model: "gpt-4"             # or llama3.1, mistral, codellama
  api_key: ""                # or set OPENAI_API_KEY env var
  api_url: ""                # Ollama: http://localhost:11434/api/generate
  temperature: 0.2
  max_tokens: 4096

agent:
  max_iterations: 50
  action_delay: 1            # seconds between actions
  tool_timeout: 120          # seconds per tool execution

output:
  directory: "./reports"
  log_level: "INFO"          # DEBUG | INFO | WARNING | ERROR
  format: "markdown"         # markdown | html
````
### Environment Variables
```bash

Variable	Description
OPENAI_API_KEY	OpenAI API key (overrides config.yaml)
TARGET	Target IP/domain (overrides config.yaml)
```
### 📋 Examples
### Full Engagement — Linux/Kali

## Full Engagement — Linux/Kali
```bash
python main.py -t https://target.com -o "Web app security assessment: identify SQLi, XSS, LFI"
```
## Web Application Test — Termux
```bash
python main.py -t https://target.com -o "Web app security assessment: identify SQLi, XSS, LFI"
```
### Network Reconnaissance — Windows
```bash
python main.py -t 192.168.1.0/24 -o "Discover live hosts, open ports, and running services"
```
### Custom Module Only
```bash
# Run just the subdomain enumeration module
python3 -c "
from modules.recon.subdomain_enum import SubdomainEnumerator
e = SubdomainEnumerator('example.com')
print(e.enumerate_all())
```

#### 🛡️ Authorization
⚠️ /* IMPORTANT: This tool is designed exclusively for authorized security professionals conducting legitimate penetration tests. Users must have explicit written permission to test any target. The HackerAI platform pre-verifies user authorization. Unauthorized use is illegal.

### Supported LLM Backends
```bash
Backend	Model Examples	Setup
OpenAI	GPT-4, GPT-4o, GPT-4-turbo	Set OPENAI_API_KEY env var
Ollama (local)	Llama 3.1, Mistral, CodeLlama, Qwen	ollama pull llama3.1 + set api_url
OpenAI-Compatible	Any API following OpenAI format	Set api_url + api_key
```
### 🗺️ Roadmap


