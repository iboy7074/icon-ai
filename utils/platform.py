#!/usr/bin/env python3
"""
Platform Detector — Cross-platform detection for Linux, Windows, Termux.
"""

import os
import sys
import platform
import subprocess
import logging

class PlatformDetector:
    """Detect and provide information about the current platform."""
    
    def __init__(self):
        self.logger = logging.getLogger("PlatformDetector")
        self._detect()
        
    def _detect(self):
        """Detect the current operating system and environment."""
        self.os_name = platform.system().lower()
        self.os_release = platform.release()
        self.machine = platform.machine()
        self.is_termux_env = self._check_termux()
        self.is_wsl = self._check_wsl()
        self.is_docker = self._check_docker()
        
        # Friendly OS name
        if self.is_termux_env:
            self.detected_os = "termux"
        elif self.os_name == "linux":
            if self.is_wsl:
                self.detected_os = "wsl"
            else:
                self.detected_os = "linux"
        elif self.os_name == "windows":
            self.detected_os = "windows"
        elif self.os_name == "darwin":
            self.detected_os = "macos"
        else:
            self.detected_os = self.os_name
        
        self.logger.info(f"Detected platform: {self.detected_os} ({self.os_name} {self.os_release})")
    
    def _check_termux(self) -> bool:
        """Check if running in Termux (Android terminal emulator)."""
        # Termux sets PREFIX environment variable
        prefix = os.environ.get("PREFIX", "")
        if "com.termux" in prefix.lower() or "/data/data/com.termux" in prefix:
            return True
        # Check for Termux-specific files
        if os.path.exists("/data/data/com.termux/files/usr/bin"):
            return True
        return False
    
    def _check_wsl(self) -> bool:
        """Check if running in Windows Subsystem for Linux."""
        try:
            if os.path.exists("/proc/version"):
                with open("/proc/version") as f:
                    return "microsoft" in f.read().lower() or "wsl" in f.read().lower()
        except:
            pass
        return False
    
    def _check_docker(self) -> bool:
        """Check if running inside a Docker container."""
        try:
            if os.path.exists("/.dockerenv"):
                return True
            with open("/proc/1/cgroup") as f:
                return "docker" in f.read()
        except:
            return False
    
    def is_unix(self) -> bool:
        """Check if running on a Unix-like system (Linux, macOS, Termux, WSL)."""
        return self.detected_os in ["linux", "macos", "termux", "wsl"]
    
    def is_windows(self) -> bool:
        """Check if running on native Windows."""
        return self.detected_os == "windows"
    
    def is_termux(self) -> bool:
        """Check if running in Termux."""
        return self.detected_os == "termux"
    
    def is_linux(self) -> bool:
        """Check if running on Linux (not Termux)."""
        return self.detected_os == "linux"
    
    def is_debian(self) -> bool:
        """Check if running on Debian/Ubuntu/Kali."""
        if not self.is_unix():
            return False
        try:
            if os.path.exists("/etc/debian_version"):
                return True
            if os.path.exists("/etc/os-release"):
                with open("/etc/os-release") as f:
                    return "debian" in f.read().lower() or "ubuntu" in f.read().lower() or "kali" in f.read().lower()
        except:
            pass
        return False
    
    def is_arch(self) -> bool:
        """Check if running on Arch Linux."""
        try:
            if os.path.exists("/etc/arch-release"):
                return True
            if os.path.exists("/etc/os-release"):
                with open("/etc/os-release") as f:
                    return "arch" in f.read().lower()
        except:
            pass
        return False
    
    def get_package_manager(self) -> str:
        """Get the recommended package manager."""
        if self.is_termux():
            return "pkg"
        elif self.is_debian():
            return "apt"
        elif self.is_arch():
            return "pacman"
        elif self.is_windows():
            return "winget"
        return "apt"
    
    def get_shell(self) -> str:
        """Get the default shell path."""
        if self.is_windows():
            return "powershell.exe"
        return os.environ.get("SHELL", "/bin/bash")
    
    def get_info(self) -> dict:
        """Get complete platform information."""
        return {
            "os": self.detected_os,
            "os_name": self.os_name,
            "release": self.os_release,
            "arch": self.machine,
            "termux": self.is_termux_env,
            "wsl": self.is_wsl,
            "docker": self.is_docker,
            "package_manager": self.get_package_manager(),
            "shell": self.get_shell(),
            "python": sys.version
        }