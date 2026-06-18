"""Red Team AI Agent — Core modules for autonomous penetration testing."""

from .agent import RedTeamAgent
from .llm_interface import LLMInterface
from .tool_registry import ToolRegistry

__version__ = "2.0.0"
__all__ = ["RedTeamAgent", "LLMInterface", "ToolRegistry"]