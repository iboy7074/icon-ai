#!/usr/bin/env python3
"""
Red Team AI Agent Core — ReAct (Reasoning + Acting) Loop
Cross-platform: Linux, Windows, Termux
"""

import json
import time
import logging
from typing import Dict, Any, Optional
from core.llm_interface import LLMInterface
from core.tool_registry import ToolRegistry
from utils.platform import PlatformDetector
from utils.logger import setup_logger

class RedTeamAgent:
    """
    Autonomous AI penetration testing agent.
    Uses ReAct (Reasoning + Acting) pattern with LLM for decision making.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = setup_logger("RedTeamAgent", config.get("log_level", "INFO"))
        self.platform = PlatformDetector()
        self.llm = LLMInterface(config.get("llm", {}))
        self.tool_registry = ToolRegistry(config, self.platform)
        self.max_iterations = config.get("max_iterations", 50)
        self.target = config.get("target", "")
        self.session_log = []
        
    def run(self, objective: str) -> Dict[str, Any]:
        """
        Main agent loop: Observe → Think → Act → Observe...
        
        Args:
            objective: The pentest objective (e.g., "enumerate and exploit target 10.0.0.1")
            
        Returns:
            Dict with session results
        """
        self.logger.info(f"Starting red team engagement. Objective: {objective}")
        self.logger.info(f"Platform: {self.platform.detected_os}")
        
        context = {
            "objective": objective,
            "target": self.target,
            "platform": self.platform.detected_os,
            "tools_available": self.tool_registry.list_tools(),
            "history": [],
            "findings": []
        }
        
        for iteration in range(1, self.max_iterations + 1):
            self.logger.info(f"=== Iteration {iteration}/{self.max_iterations} ===")
            
            # Step 1: LLM reasons about next action
            action_plan = self.llm.reason(context)
            
            if action_plan.get("type") == "final_answer":
                self.logger.info("Agent completed objective.")
                break
                
            # Step 2: Execute action
            result = self._execute_action(action_plan)
            
            # Step 3: Update context
            context["history"].append({
                "iteration": iteration,
                "action": action_plan,
                "result": result
            })
            
            if result.get("finding"):
                context["findings"].append(result["finding"])
                
            time.sleep(self.config.get("action_delay", 1))
            
        return self._generate_final_report(context)
    
    def _execute_action(self, action_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single action from the LLM's plan."""
        action_type = action_plan.get("type", "")
        tool_name = action_plan.get("tool", "")
        params = action_plan.get("params", {})
        
        self.logger.debug(f"Executing: {action_type} | Tool: {tool_name}")
        
        if action_type == "run_tool":
            return self.tool_registry.execute(tool_name, params)
        elif action_type == "analyze":
            return self._analyze_results(action_plan.get("data", ""))
        elif action_type == "write_exploit":
            return self._generate_exploit_code(action_plan)
        else:
            return {"success": False, "error": f"Unknown action type: {action_type}"}
    
    def _analyze_results(self, data: str) -> Dict[str, Any]:
        """Use LLM to analyze scan/enum results."""
        prompt = f"Analyze these penetration testing results for vulnerabilities:\n\n{data}\n\nIdentify vulnerabilities, potential exploits, and CVEs."
        analysis = self.llm.query(prompt)
        return {"success": True, "analysis": analysis}
    
    def _generate_exploit_code(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Generate exploit code from LLM specifications."""
        prompt = f"Write a working {plan.get('language', 'python')} exploit for:\n{json.dumps(plan, indent=2)}"
        code = self.llm.query(prompt)
        return {"success": True, "code": code, "language": plan.get("language", "python")}
    
    def _generate_final_report(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate final engagement report."""
        report_prompt = f"""
        Generate a pentest report from this engagement:
        - Objective: {context['objective']}
        - Target: {context['target']}
        - Findings: {json.dumps(context['findings'], indent=2)}
        - Actions taken: {len(context['history'])} iterations
        
        Format: Executive Summary, Technical Findings, Remediations.
        """
        report = self.llm.query(report_prompt)
        return {
            "objective": context["objective"],
            "target": context["target"],
            "iterations": len(context["history"]),
            "findings": context["findings"],
            "full_report": report,
            "session_log": context["history"]
        }