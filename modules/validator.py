"""
Input Validator Module for Medical Report Explanation System
Validates and sanitizes user inputs to ensure security and proper format
"""

import re
import logging
from typing import Dict, Tuple, Optional
from config import Config
from modules.utils import ValidationHelper

logger = logging.getLogger(__name__)


class InputValidator:
    """Validate and sanitize all user inputs"""
    
    # Patterns for detecting medical report content
    MEDICAL_PATTERNS = [
        r'\b(WBC|RBC|HGB|HCT|PLT|MCV)\b',  # CBC markers
        r'\b(glucose|cholesterol|triglycerides)\b',  # Common tests
        r'\b(\d+\.?\d*)\s*(mg/dL|mmol/L|g/dL|%)\b',  # Units
        r'\b(normal|abnormal|elevated|decreased|high|low)\b',  # Status words
        r'\b(findings?|impression|clinical|laboratory)\b',  # Report sections
    ]
    
    # Minimum content length for a valid report
    MIN_REPORT_LENGTH = 50
    MAX_REPORT_LENGTH = 50000
    
    def __init__(self):
        """Initialize validator"""
        self.validation_helper = ValidationHelper()
    
    def validate_file_upload(self, file) -> Tuple[bool, Optional[str]]:
        """
        Validate uploaded file
        
        Args:
            file: Flask file object
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check if file exists
        if not file or not file.filename:
            return False, "No file provided"
        
        # Check filename
        filename = file.filename
        if not self.validation_helper.is_valid_file_extension(filename):
            return False, f"Invalid file type. Allowed types: {', '.join(Config.ALLOWED_EXTENSIONS)}"
        
        # Read file to check size (this loads file into memory)
        file.seek(0, 2)  # Seek to end
        file_size = file.tell()
        file.seek(0)  # Reset to beginning
        
        if not self.validation_helper.is_file_size_valid(file_size):
            max_mb = Config.MAX_FILE_SIZE / (1024 * 1024)
            return False, f"File too large. Maximum size: {max_mb}MB"
        
        # Check for empty file
        if file_size == 0:
            return False, "File is empty"
        
        return True, None
    
    def validate_text_content(self, text: str) -> Tuple[bool, Optional[str]]:
        """
        Validate text content of medical report
        
        Args:
            text: Report text
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check if text exists
        if not text or not text.strip():
            return False, "No text content provided"
        
        # Check length
        text_length = len(text)
        if text_length < self.MIN_REPORT_LENGTH:
            return False, f"Text too short. Minimum {self.MIN_REPORT_LENGTH} characters required"
        
        if text_length > self.MAX_REPORT_LENGTH:
            return False, f"Text too long. Maximum {self.MAX_REPORT_LENGTH} characters allowed"
        
        # Check if it looks like a medical report
        if not self._contains_medical_content(text):
            return False, "Content doesn't appear to be a medical report. Please provide a valid medical test report."
        
        # Check for suspicious content
        if self._contains_suspicious_content(text):
            return False, "Content contains suspicious or invalid data"
        
        return True, None
    
    def _contains_medical_content(self, text: str) -> bool:
        """
        Check if text contains medical report indicators
        
        Args:
            text: Text to check
            
        Returns:
            True if medical content detected
        """
        text_lower = text.lower()
        matches = 0
        
        for pattern in self.MEDICAL_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                matches += 1
        
        # Require at least 2 different medical patterns
        return matches >= 2
    
    def _contains_suspicious_content(self, text: str) -> bool:
        """
        Check for suspicious or malicious content
        
        Args:
            text: Text to check
            
        Returns:
            True if suspicious content found
        """
        # Check for script injection attempts
        script_patterns = [
            r'<script',
            r'javascript:',
            r'onerror=',
            r'onclick=',
            r'eval\(',
            r'base64',  # Sometimes used in attacks
        ]
        
        text_lower = text.lower()
        for pattern in script_patterns:
            if pattern in text_lower:
                logger.warning(f"Suspicious content detected: {pattern}")
                return True
        
        # Check for excessive special characters (might indicate obfuscation)
        special_char_ratio = sum(1 for c in text if not c.isalnum() and not c.isspace()) / len(text)
        if special_char_ratio > 0.3:  # More than 30% special characters
            logger.warning(f"Excessive special characters: {special_char_ratio:.2%}")
            return True
        
        return False
    
    def sanitize_text(self, text: str) -> str:
        """
        Sanitize text input
        
        Args:
            text: Raw text
            
        Returns:
            Sanitized text
        """
        # Remove null bytes
        text = text.replace('\x00', '')
        
        # Remove any HTML tags (basic sanitization)
        text = re.sub(r'<[^>]+>', '', text)
        
        # Normalize whitespace
        text = ' '.join(text.split())
        
        # Remove any control characters except newlines and tabs
        text = ''.join(char for char in text if char == '\n' or char == '\t' or not char.isspace() or char == ' ')
        
        return text.strip()
    
    def validate_report_type(self, report_type: str) -> Tuple[bool, Optional[str]]:
        """
        Validate report type parameter
        
        Args:
            report_type: Type of report
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        valid_types = ['blood_test', 'imaging', 'auto']
        
        if not report_type:
            # Default to auto-detect
            return True, None
        
        if report_type.lower() not in valid_types:
            return False, f"Invalid report type. Must be one of: {', '.join(valid_types)}"
        
        return True, None
    
    def detect_report_type(self, text: str) -> str:
        """
        Auto-detect type of medical report
        
        Args:
            text: Report text
            
        Returns:
            'blood_test' or 'imaging'
        """
        text_lower = text.lower()
        
        # Blood test indicators
        blood_test_indicators = [
            'complete blood count', 'cbc', 'wbc', 'rbc', 'hemoglobin',
            'lipid panel', 'cholesterol', 'glucose', 'metabolic panel',
            'bmp', 'cmp', 'liver function', 'kidney function', 'thyroid'
        ]
        
        # Imaging indicators
        imaging_indicators = [
            'x-ray', 'ct scan', 'mri', 'ultrasound', 'mammogram',
            'findings:', 'impression:', 'technique:', 'comparison:',
            'radiology', 'radiologist', 'consolidation', 'opacity'
        ]
        
        blood_score = sum(1 for indicator in blood_test_indicators if indicator in text_lower)
        imaging_score = sum(1 for indicator in imaging_indicators if indicator in text_lower)
        
        if imaging_score > blood_score:
            logger.info(f"Detected imaging report (score: {imaging_score} vs {blood_score})")
            return 'imaging'
        else:
            logger.info(f"Detected blood test report (score: {blood_score} vs {imaging_score})")
            return 'blood_test'
    
    def validate_api_request(self, request_data: Dict) -> Tuple[bool, Optional[str], Dict]:
        """
        Validate complete API request
        
        Args:
            request_data: Request data dictionary
            
        Returns:
            Tuple of (is_valid, error_message, validated_data)
        """
        validated_data = {}
        
        # Check for required fields
        if 'report_text' not in request_data and 'file' not in request_data:
            return False, "Either 'report_text' or 'file' must be provided", {}
        
        # Validate text if provided
        if 'report_text' in request_data:
            text = request_data['report_text']
            
            # Validate text content
            is_valid, error = self.validate_text_content(text)
            if not is_valid:
                return False, error, {}
            
            # Sanitize text
            validated_data['report_text'] = self.sanitize_text(text)
        
        # Validate report type if provided
        report_type = request_data.get('report_type', 'auto')
        is_valid, error = self.validate_report_type(report_type)
        if not is_valid:
            return False, error, {}
        
        validated_data['report_type'] = report_type.lower() if report_type else 'auto'
        
        # Auto-detect report type if set to auto
        if validated_data['report_type'] == 'auto' and 'report_text' in validated_data:
            validated_data['report_type'] = self.detect_report_type(validated_data['report_text'])
        
        # Validate optional parameters
        if 'include_disclaimer' in request_data:
            validated_data['include_disclaimer'] = bool(request_data['include_disclaimer'])
        else:
            validated_data['include_disclaimer'] = Config.INCLUDE_DISCLAIMER
        
        return True, None, validated_data
    
    def validate_health_check(self) -> Dict:
        """
        Validate system health for health check endpoint
        
        Returns:
            Dictionary with health status
        """
        health_status = {
            'status': 'healthy',
            'checks': {}
        }
        
        # Check if API key is configured
        if Config.OPENAI_API_KEY:
            health_status['checks']['openai_api_key'] = 'configured'
        else:
            health_status['checks']['openai_api_key'] = 'missing'
            health_status['status'] = 'unhealthy'
        
        # Check if data files exist
        import os
        if os.path.exists(Config.MEDICAL_TERMS_PATH):
            health_status['checks']['medical_terms'] = 'loaded'
        else:
            health_status['checks']['medical_terms'] = 'missing'
            health_status['status'] = 'degraded'
        
        if os.path.exists(Config.REFERENCE_RANGES_PATH):
            health_status['checks']['reference_ranges'] = 'loaded'
        else:
            health_status['checks']['reference_ranges'] = 'missing'
            health_status['status'] = 'degraded'
        
        return health_status


# Example usage and testing
if __name__ == "__main__":
    validator = InputValidator()
    
    # Test sample blood report
    sample_report = """
    Complete Blood Count (CBC)
    White Blood Cells (WBC): 7.5 × 10^9/L [4.0-11.0]
    Hemoglobin (HGB): 14.5 g/dL [13.5-17.5]
    """
    
    is_valid, error = validator.validate_text_content(sample_report)
    print(f"Validation result: {is_valid}, Error: {error}")
    
    report_type = validator.detect_report_type(sample_report)
    print(f"Detected report type: {report_type}")
