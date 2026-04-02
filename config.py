"""
Configuration settings for Medical Report Explanation System
This file manages all application settings, API keys, and constants
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base configuration class"""
    
    # Flask Settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    DEBUG = os.getenv('FLASK_ENV', 'development') == 'development'
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 5000))
    
    # OpenAI API Settings
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4-turbo-preview')  # or 'gpt-4'
    OPENAI_MAX_TOKENS = int(os.getenv('OPENAI_MAX_TOKENS', 2000))
    OPENAI_TEMPERATURE = float(os.getenv('OPENAI_TEMPERATURE', 0.7))
    
    # File Upload Settings
    MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', 5 * 1024 * 1024))  # 5MB default
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx'}
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'temp_uploads')
    
    # Project Paths
    BASE_DIR = Path(__file__).parent
    DATA_DIR = BASE_DIR / 'data'
    MEDICAL_TERMS_PATH = DATA_DIR / 'medical_terms.json'
    REFERENCE_RANGES_PATH = DATA_DIR / 'reference_ranges.csv'
    
    # API Settings
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')
    API_RATE_LIMIT = int(os.getenv('API_RATE_LIMIT', 100))  # requests per hour
    
    # AI Prompt Settings
    READING_LEVEL = 8  # 8th grade reading level
    MAX_EXPLANATION_LENGTH = 1500  # words
    INCLUDE_DISCLAIMER = True
    
    # Safety Settings
    ENABLE_DIAGNOSIS = False  # Never allow diagnosis
    ENABLE_TREATMENT_ADVICE = False  # Never allow treatment recommendations
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'app.log')
    
    # Cache Settings (optional - for future enhancement)
    ENABLE_CACHE = os.getenv('ENABLE_CACHE', 'False') == 'True'
    CACHE_TIMEOUT = int(os.getenv('CACHE_TIMEOUT', 3600))  # 1 hour
    
    @staticmethod
    def validate_config():
        """Validate required configuration"""
        if not Config.OPENAI_API_KEY:
            raise ValueError(
                "OPENAI_API_KEY is required. "
                "Please set it in your .env file or environment variables."
            )
        
        # Create necessary directories
        Config.DATA_DIR.mkdir(exist_ok=True)
        if not Config.MEDICAL_TERMS_PATH.exists():
            print(f"Warning: Medical terms file not found at {Config.MEDICAL_TERMS_PATH}")
        if not Config.REFERENCE_RANGES_PATH.exists():
            print(f"Warning: Reference ranges file not found at {Config.REFERENCE_RANGES_PATH}")
        
        return True


class DevelopmentConfig(Config):
    """Development-specific configuration"""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production-specific configuration"""
    DEBUG = False
    TESTING = False
    # In production, always use environment variables
    SECRET_KEY = os.getenv('SECRET_KEY')  # Must be set in production


class TestingConfig(Config):
    """Testing-specific configuration"""
    TESTING = True
    DEBUG = True
    OPENAI_API_KEY = 'test-key'  # Mock key for testing


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config():
    """Get configuration based on environment"""
    env = os.getenv('FLASK_ENV', 'development')
    return config.get(env, config['default'])
