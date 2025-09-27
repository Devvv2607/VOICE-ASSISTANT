"""
Configuration module for Jarvis AI Assistant.
Handles environment variables and application settings.
"""

import os
from dotenv import load_dotenv
from typing import Dict, Optional

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration class for Jarvis AI Assistant."""
    
    def __init__(self):
        """Initialize configuration with environment variables."""
        # API Keys
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')
        self.news_api_key = os.getenv('NEWS_API_KEY')
        self.serp_api_key = os.getenv('SERP_API_KEY')
        
        # Email Configuration
        self.email_config = {
            'user': os.getenv('EMAIL_USER'),
            'password': os.getenv('EMAIL_PASSWORD'),
            'imap_server': os.getenv('EMAIL_IMAP_SERVER', 'imap.gmail.com'),
            'smtp_server': os.getenv('EMAIL_SMTP_SERVER', 'smtp.gmail.com')
        }
        
        # Assistant Settings
        self.wake_words = ['hey jarvis', 'jarvis', 'hey davis', 'davis']
        self.tts_rate = 180
        self.tts_volume = 0.9
        
        # Google Calendar Scopes
        self.calendar_scopes = ['https://www.googleapis.com/auth/calendar']
        self.calendar_credentials_file = 'credentials.json'
        self.calendar_token_file = 'token.pickle'
    
    def is_llm_configured(self) -> bool:
        """Check if LLM is properly configured."""
        return bool(self.gemini_api_key)
    
    def is_email_configured(self) -> bool:
        """Check if email is properly configured."""
        return bool(self.email_config['user'] and self.email_config['password'])
    
    def get_email_config(self) -> Dict[str, Optional[str]]:
        """Get email configuration."""
        return self.email_config.copy()
    
    def validate_config(self) -> Dict[str, bool]:
        """Validate configuration and return status."""
        return {
            'llm': self.is_llm_configured(),
            'email': self.is_email_configured(),
            'news_api': bool(self.news_api_key),
            'calendar_credentials': os.path.exists(self.calendar_credentials_file)
        }

# Global configuration instance
config = Config()