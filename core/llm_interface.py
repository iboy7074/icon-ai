#!/usr/bin/env python3
"""
LLM Interface — Abstraction layer for multiple LLM backends.
Supports OpenAI, Ollama (local), Anthropic, and any OpenAI-compatible API.
"""

import json
import logging
import requests
from typing import Dict, Any, Optional, List

class LLMInterface:
    """
    Multi-backend LLM interface for the red team agent.
    
    Supported backends:
    - openai: OpenAI API (GPT-4, GPT-4o, etc.)
    - ollama: Local Ollama (Llama, Mistral, CodeLlama, etc.)
    - openai_compatible: Any OpenAI-compatible endpoint
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.logger = logging.getLogger("LLMInterface")
        self.backend = config.get("backend", "openai").lower()
        self.model = config.get("model", "gpt-4")
        self.api_key = config.get("api_key", "")
        self.api_url = config.get("api_url", "")
        self.temperature = config.get("temperature", 0.2)
        self.max_tokens = config.get("max_tokens", 4096)
        
        # System prompt for red team agent behavior
        self.system_prompt = """You are RedTeamAI, an autonomous penetration testing agent.
You conduct authorized security assessments. Your capabilities include:
- Reconnaissance (nmap, subfinder, amass, dns enumeration)
- Vulnerability scanning (nikto, nuclei, whatweb)
- Exploitation (metasploit, sqlmap, custom exploits)
- Post-exploitation (privilege escalation, lateral movement)
- Web application testing (sqlmap, dirb, gobuster, xss)
- Wireless testing (aircrack-ng, reaver)
- Password attacks (hydra, john, hashcat)
- Reporting and documentation

You must reason step-by-step about what action to take next based on previous results.
Always output valid JSON with keys: type, tool, params, reasoning."""
        
    def query(self, prompt: str, system_override: Optional[str] = None) -> str:
        """Send a query to the LLM and return the response text."""
        system = system_override or self.system_prompt
        
        if self.backend == "openai":
            return self._query_openai(system, prompt)
        elif self.backend == "ollama":
            return self._query_ollama(system, prompt)
        elif self.backend == "openai_compatible":
            return self._query_openai_compatible(system, prompt)
        else:
            raise ValueError(f"Unsupported backend: {self.backend}")
    
    def reason(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Use LLM to reason about the current state and decide next action.
        Returns a structured action plan.
        """
        prompt = f"""
        Current context:
        - Objective: {context.get('objective', 'No objective set')}
        - Target: {context.get('target', 'Unknown')}
        - Platform: {context.get('platform', 'Unknown')}
        - Available tools: {', '.join(context.get('tools_available', []))}
        
        Recent history (last 5 actions):
        {json.dumps(context.get('history', [])[-5:], indent=2)}
        
        Current findings:
        {json.dumps(context.get('findings', []), indent=2)}
        
        Decide the next action. Respond ONLY with valid JSON:
        {{
            "type": "run_tool" | "analyze" | "write_exploit" | "final_answer",
            "tool": "tool_name" (if type is run_tool),
            "params": {{"arg1": "value1", ...}},
            "reasoning": "Why this action makes sense",
            "language": "python" | "bash" | "powershell" (if type is write_exploit)
        }}
        
        If the objective is complete, use type "final_answer" with a summary.
        """
        
        response = self.query(prompt)
        
        try:
            # Try to extract JSON from response (handle markdown code blocks)
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0].strip()
            else:
                json_str = response.strip()
            
            return json.loads(json_str)
        except (json.JSONDecodeError, IndexError):
            self.logger.warning(f"Failed to parse LLM response as JSON: {response[:200]}...")
            return {"type": "analyze", "data": response, "reasoning": "Parse raw response"}
    
    def _query_openai(self, system: str, prompt: str) -> str:
        """Query OpenAI API."""
        try:
            import openai
            client = openai.OpenAI(api_key=self.api_key)
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            return response.choices[0].message.content
        except ImportError:
            self.logger.warning("openai package not installed, using requests directly")
            return self._query_openai_rest(system, prompt)
    
    def _query_openai_rest(self, system: str, prompt: str) -> str:
        """Fallback: query OpenAI via REST."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt}
            ],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }
        resp = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers, json=data, timeout=60
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]
    
    def _query_ollama(self, system: str, prompt: str) -> str:
        """Query local Ollama instance."""
        url = self.api_url or "http://localhost:11434/api/generate"
        data = {
            "model": self.model,
            "system": system,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": self.temperature
            }
        }
        resp = requests.post(url, json=data, timeout=120)
        resp.raise_for_status()
        return resp.json()["response"]
    
    def _query_openai_compatible(self, system: str, prompt: str) -> str:
        """Query any OpenAI-compatible API."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt}
            ],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }
        resp = requests.post(self.api_url, headers=headers, json=data, timeout=60)
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]