# src/__init__.py
"""
BIG-IP Receiver Configuration API Service

A FastAPI-based service for managing BIG-IP receiver configurations through a REST API.
"""

__version__ = "1.0.0"
__author__ = "F5 DevCentral"
__description__ = "API Service for managing BIG-IP receiver configurations"

from .config_handler import ConfigHandler
from .main import app

__all__ = ["ConfigHandler", "app"]