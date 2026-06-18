#!/usr/bin/env python3
"""
Tool Registry — Manages all pentest tools across platforms.
Discovers available tools at runtime and provides unified execution.
"""

import shutil
import subprocess
import logging
import os
from typing import Dict, Any, List, Optional, Callable
from utils.platform import PlatformDetector

class ToolRegistry:
    """
    Dynamic tool registry that discovers tools on the system.
    Maps abstract tool names to platform-specific commands.
    """
    
    def __init__(self, config: Dict[str, Any], platform: PlatformDetector):
        self.logger = logging.getLogger("ToolRegistry")
        self.platform = platform
        self.config = config
        self.target = config.get("target", "")
        self.tools = {}
        self._discover_tools()
        
    def _discover_tools(self):
        """Auto-discover available tools on the current platform."""
        # Core recon tools
        self._register("nmap", ["nmap"], "Network Mapper - port scanning & service detection")
        self._register("ping", ["ping"], "ICMP echo for host discovery")
        self._register("traceroute", ["traceroute", "tracert"], "Route tracing")
        
        # DNS enumeration
        self._register("dnsrecon", ["dnsrecon"], "DNS enumeration tool")
        self._register("dnsenum", ["dnsenum"], "DNS enumeration")
        self._register("host", ["host"], "DNS lookup utility")
        self._register("dig", ["dig"], "DNS lookup utility")
        self._register("nslookup", ["nslookup"], "DNS lookup")
        
        # Web tools
        self._register("curl", ["curl"], "HTTP requests")
        self._register("wget", ["wget"], "HTTP download")
        self._register("whatweb", ["whatweb"], "Web technology fingerprinting")
        self._register("nikto", ["nikto", "nikto.pl"], "Web server scanner")
        self._register("gobuster", ["gobuster"], "Directory/file brute-forcing")
        self._register("dirb", ["dirb"], "Directory brute-forcing")
        self._register("wfuzz", ["wfuzz"], "Web fuzzer")
        self._register("sqlmap", ["sqlmap"], "SQL injection automation")
        
        # Exploitation
        self._register("msfconsole", ["msfconsole"], "Metasploit Framework")
        self._register("searchsploit", ["searchsploit"], "Exploit-DB search")
        self._register("hydra", ["hydra"], "Password brute-forcing")
        self._register("john", ["john", "john-ng"], "John the Ripper password cracker")
        self._register("hashcat", ["hashcat"], "GPU-accelerated password cracking")
        
        # Utility
        self._register("python3", ["python3", "python"], "Python interpreter")
        self._register("bash", ["bash", "sh"], "Shell interpreter")
        self._register("powershell", ["powershell", "pwsh"], "PowerShell")
        self._register("ssh", ["ssh"], "SSH client")
        self._register("nc", ["nc", "ncat"], "Netcat - raw network communication")
        
        # Post-exploitation
        self._register("socat", ["socat"], "Swiss-army knife for networking")
        
        available = [name for name, info in self.tools.items() if info["available"]]
        self.logger.info(f"Discovered {len(available)} available tools: {available}")
    
    def _register(self, name: str, binaries: List[str], description: str):
        """Register a tool and check if it's available on this system."""
        found_path = None
        for binary in binaries:
            path = shutil.which(binary)
            if path:
                found_path = path
                break
        
        self.tools[name] = {
            "name": name,
            "binaries": binaries,
            "description": description,
            "available": found_path is not None,
            "path": found_path,
            "platforms": self._get_supported_platforms(binaries)
        }
    
    def _get_supported_platforms(self, binaries: List[str]) -> List[str]:
        """Determine which platforms a tool supports."""
        platforms = []
        for binary in binaries:
            if binary in ["powershell", "pwsh", "tracert"]:
                platforms.append("windows")
            if binary in ["ping", "host", "dig", "nslookup"]:
                platforms.append("all")
            platforms.append("linux")
            platforms.append("termux")
        return list(set(platforms))
    
    def list_tools(self) -> List[str]:
        """List all available (found on system) tool names."""
        return [name for name, info in self.tools.items() if info["available"]]
    
    def list_all(self) -> Dict[str, Any]:
        """List all registered tools with availability status."""
        return self.tools
    
    def execute(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool with given parameters.
        
        Args:
            tool_name: Name of the registered tool
            params: Dict of parameters (args, target, ports, etc.)
            
        Returns:
            Dict with success status, stdout, stderr, and any findings
        """
        if tool_name not in self.tools:
            return {"success": False, "error": f"Unknown tool: {tool_name}"}
        
        tool = self.tools[tool_name]
        if not tool["available"]:
            # Install if possible
            install_result = self._install_tool(tool_name)
            if not install_result["success"]:
                return {
                    "success": False,
                    "error": f"Tool '{tool_name}' not available and couldn't be installed",
                    "install_help": install_result.get("message", "")
                }
        
        # Build command
        cmd = self._build_command(tool_name, params)
        
        self.logger.info(f"Executing: {' '.join(cmd)}")
        
        try:
            timeout = params.get("timeout", self.config.get("tool_timeout", 60))
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            output = result.stdout
            if result.stderr:
                self.logger.debug(f"Stderr: {result.stderr[:500]}")
            
            # Auto-analyze output for findings
            finding = self._extract_finding(tool_name, output)
            
            return {
                "success": result.returncode == 0,
                "returncode": result.returncode,
                "stdout": output,
                "stderr": result.stderr,
                "finding": finding,
                "command": " ".join(cmd)
            }
            
        except subprocess.TimeoutExpired:
            return {"success": False, "error": f"Command timed out after {timeout}s", "finding": None}
        except FileNotFoundError:
            return {"success": False, "error": f"Tool '{tool_name}' binary not found", "finding": None}
        except Exception as e:
            return {"success": False, "error": str(e), "finding": None}
    
    def _build_command(self, tool_name: str, params: Dict[str, Any]) -> List[str]:
        """Build the command line for a specific tool and parameters."""
        target = params.get("target", self.target)
        args = params.get("args", "")
        ports = params.get("ports", "")
        
        cmd_map = {
            "nmap": self._cmd_nmap,
            "ping": lambda: ["ping", "-c", "3" if self.platform.is_unix() else "-n", "1", target],
            "gobuster": lambda: ["gobuster", "dir", "-u", target, "-w", 
                                 params.get("wordlist", "/usr/share/wordlists/dirb/common.txt")],
            "nikto": lambda: ["nikto", "-h", target],
            "hydra": lambda: ["hydra", "-l", params.get("username", "admin"),
                              "-P", params.get("wordlist", "/usr/share/wordlists/rockyou.txt"),
                              target, params.get("service", "ssh")],
            "sqlmap": lambda: ["sqlmap", "-u", target, "--batch", "--banner"],
            "whatweb": lambda: ["whatweb", target],
            "curl": lambda: ["curl", "-s", "-k", target],
            "dig": lambda: ["dig", target, params.get("type", "ANY")],
        }
        
        builder = cmd_map.get(tool_name)
        if builder:
            return builder()
        
        # Default: tool + target + extra args
        tool_path = self.tools[tool_name]["path"]
        cmd = [tool_path, target] if target else [tool_path]
        if args:
            cmd.extend(args.split())
        return cmd
    
    def _cmd_nmap(self) -> List[str]:
        """Build nmap command based on target and params."""
        params = {}  # would come from caller context
        cmd = ["nmap", "-sV", "-sC", "-O", "--reason"]
        target = params.get("target", self.target)
        ports = params.get("ports", "")
        if ports:
            cmd.extend(["-p", ports])
        cmd.append(target)
        return cmd
    
    def _extract_finding(self, tool_name: str, output: str) -> Optional[Dict[str, Any]]:
        """Extract security findings from tool output."""
        findings_keywords = {
            "nmap": ["open", "vulnerable", "CVE-"],
            "nikto": ["vulnerability", "warning", "CVE-", "OSVDB-"],
            "sqlmap": ["identified", "injectable", "parameter"],
            "hydra": ["password found", "login:", "successful"],
            "gobuster": ["Found", "Status: 200", "Status: 403"],
        }
        
        keywords = findings_keywords.get(tool_name, [])
        for kw in keywords:
            if kw.lower() in output.lower():
                lines = [l.strip() for l in output.split("\n") if kw.lower() in l.lower()]
                return {
                    "tool": tool_name,
                    "type": "potential_finding",
                    "detail": lines[:5],
                    "raw_snippet": output[:500]
                }
        return None
    
    def _install_tool(self, tool_name: str) -> Dict[str, Any]:
        """Attempt to install a missing tool."""
        install_commands = {
            "nmap": self._install_pkg("nmap"),
            "nikto": self._install_pkg("nikto"),
            "gobuster": self._install_pkg("gobuster"),
            "hydra": self._install_pkg("hydra"),
            "sqlmap": self._install_pkg("sqlmap"),
            "whatweb": self._install_pkg("whatweb"),
            "dnsrecon": self._install_pkg("dnsrecon"),
            "john": self._install_pkg("john"),
        }
        
        cmd = install_commands.get(tool_name)
        if not cmd:
            return {"success": False, "message": f"No auto-install recipe for '{tool_name}'"}
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            if result.returncode == 0:
                # Re-discover
                self._discover_tools()
                return {"success": True, "message": f"Installed {tool_name}"}
            return {"success": False, "message": result.stderr}
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    def _install_pkg(self, pkg: str) -> List[str]:
        """Get platform-specific install command."""
        if self.platform.is_termux():
            return ["pkg", "install", pkg, "-y"]
        elif self.platform.is_debian():
            return ["sudo", "apt", "install", pkg, "-y"]
        elif self.platform.is_arch():
            return ["sudo", "pacman", "-S", pkg, "--noconfirm"]
        elif self.platform.is_windows():
            return ["winget", "install", pkg] if pkg in ["nmap"] else ["echo", f"Install {pkg} manually on Windows"]
        else:
            return ["sudo", "apt", "install", pkg, "-y"]a