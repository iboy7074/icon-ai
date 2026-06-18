#!/usr/bin/env python3
"""
Safe command execution with timeout, output capture, and error handling.
Cross-platform compatible.
"""

import subprocess
import logging
import os
import signal
import tempfile
from typing import Optional, Tuple, List

logger = logging.getLogger("Executor")


def run_command(cmd: List[str], timeout: int = 60, shell: bool = False,
                capture: bool = True, cwd: Optional[str] = None) -> dict:
    """
    Execute a system command safely with timeout.
    
    Args:
        cmd: Command as list of strings (e.g., ["nmap", "-sV", "target"])
        timeout: Max execution time in seconds
        shell: Use shell=True (caution: security risk)
        capture: Capture stdout/stderr
        cwd: Working directory
        
    Returns:
        dict with success, stdout, stderr, returncode, error
    """
    try:
        result = subprocess.run(
            cmd,
            capture_output=capture,
            text=True,
            timeout=timeout,
            shell=shell,
            cwd=cwd
        )
        return {
            "success": result.returncode == 0,
            "returncode": result.returncode,
            "stdout": result.stdout or "",
            "stderr": result.stderr or "",
            "error": None
        }
    except subprocess.TimeoutExpired:
        logger.warning(f"Command timed out after {timeout}s: {' '.join(cmd[:3])}...")
        return {"success": False, "returncode": -1, "stdout": "", "stderr": "", 
                "error": f"TIMEOUT after {timeout}s"}
    except FileNotFoundError:
        return {"success": False, "returncode": -1, "stdout": "", "stderr": "",
                "error": f"Command not found: {cmd[0]}"}
    except Exception as e:
        logger.error(f"Execution error: {e}")
        return {"success": False, "returncode": -1, "stdout": "", "stderr": "",
                "error": str(e)}