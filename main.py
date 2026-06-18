#!/usr/bin/env python3
"""
Red Team AI Agent — Main Entry Point
Cross-platform: Linux, Windows, Termux
"""

import os
import sys
import json
import yaml
import argparse
import logging
from datetime import datetime
from core.agent import RedTeamAgent
from utils.platform import PlatformDetector

def load_config(config_path: str) -> dict:
    """Load YAML configuration file."""
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    
    # Environment variable overrides
    if os.environ.get("OPENAI_API_KEY"):
        config.setdefault("llm", {})["api_key"] = os.environ["OPENAI_API_KEY"]
    if os.environ.get("TARGET"):
        config["target"] = os.environ["TARGET"]
    
    return config

def banner():
    """Display cool banner."""
    print(r"""
    ╔══════════════════════════════════════════════╗
    ║         RED TEAM AI AGENT v2.0              ║
    ║   Autonomous Penetration Testing Framework   ║
    ║   Linux | Windows | Termux                   ║
    ╚══════════════════════════════════════════════╝
    """)

def main():
    parser = argparse.ArgumentParser(
        description="Red Team AI Agent - Autonomous Penetration Testing",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("-t", "--target", help="Target IP or domain")
    parser.add_argument("-o", "--objective", default="Perform comprehensive penetration test",
                       help="Penetration testing objective")
    parser.add_argument("-c", "--config", default="config.yaml",
                       help="Configuration file path")
    parser.add_argument("-v", "--verbose", action="store_true",
                       help="Verbose output (DEBUG logging)")
    parser.add_argument("--list-tools", action="store_true",
                       help="List available tools and exit")
    parser.add_argument("--platform-info", action="store_true",
                       help="Show platform detection info and exit")
    parser.add_argument("--interactive", action="store_true",
                       help="Run in interactive (step-by-step) mode")
    
    args = parser.parse_args()
    banner()
    
    # Show platform info
    detector = PlatformDetector()
    if args.platform_info:
        info = detector.get_info()
        print(json.dumps(info, indent=2))
        return
    
    # Load config
    config = load_config(args.config)
    if args.target:
        config["target"] = args.target
    if args.verbose:
        config["log_level"] = "DEBUG"
    config["interactive"] = args.interactive
    
    # Show available tools
    if args.list_tools:
        from core.tool_registry import ToolRegistry
        registry = ToolRegistry(config, detector)
        print("\n[+] Available Tools:")
        for name, info in registry.list_all().items():
            status = "✓" if info["available"] else "✗"
            print(f"   {status} {name:20s} - {info['description']}")
        return
    
    # Validate target
    if not config.get("target"):
        print("[!] Error: No target specified. Use -t TARGET or set TARGET env var.")
        sys.exit(1)
    
    # Create output directory
    output_dir = config.get("output_dir", "./reports")
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize and run agent
    print(f"\n[+] Target: {config['target']}")
    print(f"[+] Platform: {detector.detected_os}")
    print(f"[+] Objective: {args.objective}")
    print(f"[+] Starting engagement at {datetime.now().isoformat()}\n")
    
    agent = RedTeamAgent(config)
    results = agent.run(args.objective)
    
    # Save report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_target = config["target"].replace("/", "_").replace(":", "_")
    report_file = os.path.join(output_dir, f"report_{safe_target}_{timestamp}.md")
    
    with open(report_file, "w") as f:
        f.write(results.get("full_report", str(results)))
    
    print(f"\n[✓] Engagement complete.")
    print(f"[+] Report saved to: {report_file}")
    print(f"[+] Findings: {len(results.get('findings', []))}")
    print(f"[+] Iterations: {results.get('iterations', 0)}")

if __name__ == "__main__":
    main()