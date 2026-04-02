"""
Utility functions for Medical Report Explanation System
Helper functions for file handling, data loading, and common operations
"""

import os
import json
import pandas as pd
import PyPDF2
import docx
import logging
from pathlib import Path
from typing import Dict, List, Optional, Union
from config import Config

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FileHandler:
    """Handle file reading operations for different file types"""
    
    @staticmethod
    def read_text_file(file_path: str) -> str:
        """
        Read a plain text file
        
        Args:
            file_path: Path to the text file
            
        Returns:
            Content of the file as string
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            logger.error(f"Error reading text file: {e}")
            raise
    
    @staticmethod
    def read_pdf_file(file_path: str) -> str:
        """
        Read a PDF file and extract text
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Extracted text from PDF
        """
        try:
            text = ""
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text += page.extract_text()
            return text
        except Exception as e:
            logger.error(f"Error reading PDF file: {e}")
            raise
    
    @staticmethod
    def read_docx_file(file_path: str) -> str:
        """
        Read a Word document file
        
        Args:
            file_path: Path to the DOCX file
            
        Returns:
            Extracted text from document
        """
        try:
            doc = docx.Document(file_path)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            return text
        except Exception as e:
            logger.error(f"Error reading DOCX file: {e}")
            raise
    
    @staticmethod
    def read_file(file_path: str) -> str:
        """
        Read any supported file type
        
        Args:
            file_path: Path to the file
            
        Returns:
            Extracted text content
        """
        file_extension = Path(file_path).suffix.lower()
        
        if file_extension == '.txt':
            return FileHandler.read_text_file(file_path)
        elif file_extension == '.pdf':
            return FileHandler.read_pdf_file(file_path)
        elif file_extension == '.docx':
            return FileHandler.read_docx_file(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")


class DataLoader:
    """Load and manage reference data"""
    
    _medical_terms = None
    _reference_ranges = None
    
    @classmethod
    def load_medical_terms(cls) -> Dict:
        """
        Load medical terminology database
        
        Returns:
            Dictionary of medical terms and definitions
        """
        if cls._medical_terms is None:
            try:
                with open(Config.MEDICAL_TERMS_PATH, 'r') as file:
                    cls._medical_terms = json.load(file)
                logger.info("Medical terms loaded successfully")
            except Exception as e:
                logger.error(f"Error loading medical terms: {e}")
                cls._medical_terms = {}
        
        return cls._medical_terms
    
    @classmethod
    def load_reference_ranges(cls) -> pd.DataFrame:
        """
        Load reference ranges database
        
        Returns:
            DataFrame with reference ranges for medical tests
        """
        if cls._reference_ranges is None:
            try:
                cls._reference_ranges = pd.read_csv(Config.REFERENCE_RANGES_PATH)
                logger.info("Reference ranges loaded successfully")
            except Exception as e:
                logger.error(f"Error loading reference ranges: {e}")
                cls._reference_ranges = pd.DataFrame()
        
        return cls._reference_ranges
    
    @classmethod
    def get_test_reference(cls, test_name: str, gender: str = 'both', 
                          age_group: str = 'adult') -> Optional[Dict]:
        """
        Get reference range for a specific test
        
        Args:
            test_name: Name of the test (e.g., 'WBC', 'Glucose')
            gender: 'male', 'female', or 'both'
            age_group: Age group (default: 'adult')
            
        Returns:
            Dictionary with reference range info or None
        """
        df = cls.load_reference_ranges()
        
        # Try to find exact match
        result = df[
            (df['test_name'] == test_name) & 
            (df['gender'] == gender) & 
            (df['age_group'] == age_group)
        ]
        
        # If no match, try with 'both' gender
        if result.empty and gender != 'both':
            result = df[
                (df['test_name'] == test_name) & 
                (df['gender'] == 'both') & 
                (df['age_group'] == age_group)
            ]
        
        if not result.empty:
            return result.iloc[0].to_dict()
        
        return None
    
    @classmethod
    def get_term_definition(cls, term: str, category: str = None) -> Optional[str]:
        """
        Get definition for a medical term
        
        Args:
            term: Medical term to look up
            category: Category to search in (optional)
            
        Returns:
            Definition string or None
        """
        terms = cls.load_medical_terms()
        
        # Search in specific category if provided
        if category and category in terms:
            if term in terms[category]:
                return terms[category][term]
        
        # Search in all categories
        for cat_data in terms.values():
            if isinstance(cat_data, dict):
                if term in cat_data:
                    return cat_data[term]
                # Search nested dictionaries
                for subcategory in cat_data.values():
                    if isinstance(subcategory, dict) and term in subcategory:
                        return subcategory[term]
        
        return None


class TextProcessor:
    """Process and clean text"""
    
    @staticmethod
    def clean_text(text: str) -> str:
        """
        Clean and normalize text
        
        Args:
            text: Raw text
            
        Returns:
            Cleaned text
        """
        # Remove excessive whitespace
        text = ' '.join(text.split())
        
        # Remove special characters that might cause issues
        # But keep medical notation like × and °
        text = text.replace('\x00', '')  # Remove null bytes
        
        return text.strip()
    
    @staticmethod
    def extract_sections(text: str, section_keywords: List[str]) -> Dict[str, str]:
        """
        Extract sections from medical report
        
        Args:
            text: Full report text
            section_keywords: List of section headers to look for
            
        Returns:
            Dictionary with section names and content
        """
        sections = {}
        lines = text.split('\n')
        current_section = 'header'
        sections[current_section] = []
        
        for line in lines:
            line_upper = line.strip().upper()
            
            # Check if line is a section header
            is_section = False
            for keyword in section_keywords:
                if keyword.upper() in line_upper:
                    current_section = keyword.lower()
                    sections[current_section] = []
                    is_section = True
                    break
            
            # Add line to current section
            if not is_section:
                sections[current_section].append(line)
        
        # Join lines in each section
        return {k: '\n'.join(v).strip() for k, v in sections.items() if v}
    
    @staticmethod
    def truncate_text(text: str, max_length: int = 1500, 
                     preserve_sentences: bool = True) -> str:
        """
        Truncate text to maximum length
        
        Args:
            text: Text to truncate
            max_length: Maximum length in characters
            preserve_sentences: Try to end at sentence boundary
            
        Returns:
            Truncated text
        """
        if len(text) <= max_length:
            return text
        
        if preserve_sentences:
            # Find last sentence boundary before max_length
            truncated = text[:max_length]
            last_period = truncated.rfind('.')
            if last_period > max_length * 0.8:  # At least 80% of max length
                return truncated[:last_period + 1]
        
        return text[:max_length] + "..."


class ValidationHelper:
    """Helper functions for validation"""
    
    @staticmethod
    def is_valid_file_extension(filename: str) -> bool:
        """
        Check if file extension is allowed
        
        Args:
            filename: Name of the file
            
        Returns:
            True if extension is allowed
        """
        if '.' not in filename:
            return False
        extension = filename.rsplit('.', 1)[1].lower()
        return extension in Config.ALLOWED_EXTENSIONS
    
    @staticmethod
    def is_file_size_valid(file_size: int) -> bool:
        """
        Check if file size is within limits
        
        Args:
            file_size: Size of file in bytes
            
        Returns:
            True if size is acceptable
        """
        return file_size <= Config.MAX_FILE_SIZE
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Sanitize filename to prevent security issues
        
        Args:
            filename: Original filename
            
        Returns:
            Sanitized filename
        """
        # Remove path components
        filename = os.path.basename(filename)
        
        # Remove or replace dangerous characters
        dangerous_chars = ['..', '/', '\\', '\x00']
        for char in dangerous_chars:
            filename = filename.replace(char, '_')
        
        return filename


class ResponseHelper:
    """Helper functions for formatting responses"""
    
    @staticmethod
    def create_success_response(data: Dict, message: str = "Success") -> Dict:
        """
        Create standardized success response
        
        Args:
            data: Response data
            message: Success message
            
        Returns:
            Formatted response dictionary
        """
        return {
            'success': True,
            'message': message,
            'data': data
        }
    
    @staticmethod
    def create_error_response(error: str, status_code: int = 400) -> tuple:
        """
        Create standardized error response
        
        Args:
            error: Error message
            status_code: HTTP status code
            
        Returns:
            Tuple of (response_dict, status_code)
        """
        return {
            'success': False,
            'error': error
        }, status_code
    
    @staticmethod
    def add_disclaimer(explanation: str) -> str:
        """
        Add medical disclaimer to explanation
        
        Args:
            explanation: Generated explanation
            
        Returns:
            Explanation with disclaimer
        """
        disclaimer = """
        
⚠️ IMPORTANT DISCLAIMER:
This explanation is for educational purposes only and is not medical advice. 
It does not replace professional medical consultation. Always discuss your 
results with your healthcare provider, who can provide personalized medical 
advice based on your complete health history.

This system uses AI and may not be 100% accurate. Do not make medical 
decisions based solely on this information.
        """
        return explanation + disclaimer


# Convenience function to initialize data
def initialize_data():
    """Load all reference data at startup"""
    logger.info("Initializing data...")
    DataLoader.load_medical_terms()
    DataLoader.load_reference_ranges()
    logger.info("Data initialization complete")


if __name__ == "__main__":
    # Test utilities
    initialize_data()
    print("Utilities module loaded successfully")
