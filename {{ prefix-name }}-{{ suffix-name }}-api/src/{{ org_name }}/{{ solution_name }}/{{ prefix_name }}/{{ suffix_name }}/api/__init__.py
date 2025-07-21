"""
{{ PrefixName }}{{ SuffixName }} REST API Module

This module provides the FastAPI application factory and core API functionality.
"""

from .app import create_app
from .config import Settings

__all__ = ["create_app", "Settings"] 