#!/bin/bash
# Red Team AI Agent Installer — Linux / Termux
# Detects platform and installs dependencies

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}[+] Installing Red Team AI Agent...${NC}"

# Detect platform
if [ -d "/data/data/com.termux" ]; then
    echo -e "${YELLOW}[*] Detected Termux (Android)${NC}"
    PKG_MGR="pkg"
    PKG_UPDATE="$PKG_MGR update"
    PYTHON="python"
    PIP="pip"
elif [ -f "/etc/debian_version" ]; then
    echo -e "${YELLOW}[*] Detected Debian/Ubuntu/Kali Linux${NC}"
    PKG_MGR="apt"
    PKG_UPDATE="sudo $PKG_MGR update"
    PYTHON="python3"
    PIP="pip3"
elif command -v pacman &> /dev/null; then
    echo -e "${YELLOW}[*] Detected Arch Linux${NC}"
    PKG_MGR="pacman"
    PKG_UPDATE="sudo $PKG_MGR -Sy"
    PYTHON="python"
    PIP="pip"
else
    echo -e "${YELLOW}[*] Detected generic Linux${NC}"
    PKG_MGR="apt"
    PKG_UPDATE="sudo $PKG_MGR update"
    PYTHON="python3"
    PIP="pip3"
fi

# System dependencies
echo -e "${YELLOW}[*] Installing system dependencies...${NC}"
$PKG_UPDATE
if [ "$PKG_MGR" = "pkg" ]; then
    $PKG_MGR install -y python clang make openssl binutils
elif [ "$PKG_MGR" = "pacman" ]; then
    sudo $PKG_MGR -S --noconfirm python python-pip nmap curl wget
else
    sudo $PKG_MGR install -y python3 python3-pip nmap curl wget dnsutils
fi

# Python dependencies
echo -e "${YELLOW}[*] Installing Python dependencies...${NC}"
$PIP install --upgrade pip
$PIP install requests pyyaml dnspython openai

# Optional: Install additional pentest tools
echo -e "${YELLOW}[*] Installing optional pentest tools...${NC}"
if [ "$PKG_MGR" = "pkg" ]; then
    # Termux-specific tools
    $PKG_MGR install -y nmap hydra sqlmap whatweb wget curl
elif [ "$PKG_MGR" = "apt" ]; then
    sudo $PKG_MGR install -y nmap hydra sqlmap nikto whatweb gobuster dirb wfuzz 2>/dev/null || true
fi

# Create directory structure
mkdir -p {core,modules/{recon,scanning,exploitation,post_exploit,report},utils}

echo -e "${GREEN}[✓] Installation complete!${NC}"
echo -e "${GREEN}[+] Run: python3 main.py -t <target> -o \"<objective>\"${NC}"