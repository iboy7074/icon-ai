#!/usr/bin/env python3
"""
Logging configuration for the Red Team AI Agent.
"""

import logging
import sys
from datetime import datetime


def setup_logger(name: str, level: str = "INFO") -> logging.Logger:
    """Configure and return a logger with consistent formatting."""
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            datefmt='%H:%M:%S'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger