# Red Team AI Agent Installer — Windows
# Requires: Python 3.8+, winget (optional)

Write-Host "[+] Installing Red Team AI Agent for Windows..." -ForegroundColor Green

# Check Python
try {
    $pyVersion = python --version
    Write-Host "[*] Found $pyVersion" -ForegroundColor Yellow
} catch {
    Write-Host "[!] Python not found. Installing..." -ForegroundColor Red
    # Try winget
    try {
        winget install Python.Python.3.12
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine")
    } catch {
        Write-Host "[!] Please install Python from https://python.org" -ForegroundColor Red
        exit 1
    }
}

# Install Python packages
Write-Host "[*] Installing Python dependencies..." -ForegroundColor Yellow
pip install --upgrade pip
pip install requests pyyaml dnspython openai

# Optional: Install Windows pentest tools
Write-Host "[*] Optional: Install nmap for Windows?" -ForegroundColor Yellow
Write-Host "    winget install nmap" -ForegroundColor Gray
Write-Host "    Download from: https://nmap.org/download.html" -ForegroundColor Gray

# Create directory structure
New-Item -ItemType Directory -Force -Path core, modules\recon, modules\scanning, modules\exploitation, modules\post_exploit, modules\report, utils | Out-Null

Write-Host "[✓] Installation complete!" -ForegroundColor Green
Write-Host "[+] Run: python main.py -t <target>" -ForegroundColor Green