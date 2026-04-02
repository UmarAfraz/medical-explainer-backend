"""
Modules package for Medical Report Explanation System
"""

from modules.parser import ReportParser
from modules.validator import InputValidator
from modules.ai_service import AIExplainer
from modules.formatter import ResponseFormatter
from modules.utils import DataLoader, FileHandler, TextProcessor

__all__ = [
    'ReportParser',
    'InputValidator',
    'AIExplainer',
    'ResponseFormatter',
    'DataLoader',
    'FileHandler',
    'TextProcessor'
]

__version__ = '1.0.0'
