"""
Configuration settings for Premium Care Financial Agent
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Central configuration for the application"""
    
    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4")
    
    # Database Configuration
    DATABASE_PATH = os.getenv("DATABASE_PATH", "data/premium_care.db")
    
    # File Upload Configuration
    MAX_UPLOAD_SIZE_MB = int(os.getenv("MAX_UPLOAD_SIZE_MB", "50"))
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "uploads")
    
    # Analysis Configuration
    MIN_TRANSACTION_AMOUNT = float(os.getenv("MIN_TRANSACTION_AMOUNT", "0.01"))
    ANOMALY_THRESHOLD = float(os.getenv("ANOMALY_THRESHOLD", "2.0"))  # Standard deviations
    RECURRING_THRESHOLD_DAYS = int(os.getenv("RECURRING_THRESHOLD_DAYS", "25"))  # 25-35 days
    
    # Feature Flags
    ENABLE_RECOMMENDATIONS = os.getenv("ENABLE_RECOMMENDATIONS", "true").lower() == "true"
    ENABLE_REAL_TIME_ANALYSIS = os.getenv("ENABLE_REAL_TIME_ANALYSIS", "true").lower() == "true"
    
    # Server Configuration
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", "8000"))
    
    # Security
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    
    @classmethod
    def validate(cls):
        """Validate critical configuration"""
        if not cls.OPENAI_API_KEY:
            print("⚠️  WARNING: OPENAI_API_KEY not set. LLM recommendations will be disabled.")
        
        # Ensure upload folder exists
        os.makedirs(cls.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(os.path.dirname(cls.DATABASE_PATH), exist_ok=True)


# Validate on import
Config.validate()
