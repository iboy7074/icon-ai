# icon-ai
##Red Team AI Agent — Cross-Platform (Linux, Windows, Termux)
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

#### Linux (Kali/Ubuntu/Debian/Arch)

```bash
git clone https://github.com/your-org/redteam-ai-agent.git
cd redteam-ai-agent
chmod +x install.sh
./install.sh
