"""
Settings and Configuration Management

Handles environment variables and configuration for the Research Agent.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from typing import Optional

class Settings:
    """
    Configuration settings for the Research Agent.
    
    Loads settings from environment variables and .env file.
    """
    
    def __init__(self, env_file: Optional[str] = None):
        """
        Initialize settings.
        
        Args:
            env_file: Optional path to .env file
        """
        
        # Load environment variables
        if env_file:
            load_dotenv(env_file)
        else:
            # Try to find .env file in current directory or parent directories
            current_dir = Path.cwd()
            for path in [current_dir] + list(current_dir.parents):
                env_path = path / '.env'
                if env_path.exists():
                    load_dotenv(env_path)
                    break
        
        # IO Intelligence API Configuration
        self.io_api_key = os.getenv('IO_API_KEY')
        self.io_base_url = os.getenv('IO_BASE_URL', 'https://api.io.net/v1')
        self.io_models_endpoint = os.getenv('IO_MODELS_ENDPOINT', '/models')
        self.io_agents_endpoint = os.getenv('IO_AGENTS_ENDPOINT', '/agents')
        
        # Agent Configuration
        self.max_sources = int(os.getenv('MAX_SOURCES', '10'))
        self.output_format = os.getenv('OUTPUT_FORMAT', 'markdown')
        self.research_depth = os.getenv('RESEARCH_DEPTH', 'standard')
        self.enable_streaming = os.getenv('ENABLE_STREAMING', 'true').lower() == 'true'
        
        # HTTP Configuration
        self.user_agent = os.getenv('USER_AGENT', 'IOResearchAgent/1.0')
        self.request_timeout = int(os.getenv('REQUEST_TIMEOUT', '30'))
        self.max_retries = int(os.getenv('MAX_RETRIES', '3'))
        
        # Model Configuration
        self.default_model = os.getenv('DEFAULT_MODEL', 'gpt-3.5-turbo')
        self.max_tokens = int(os.getenv('MAX_TOKENS', '2000'))
        self.temperature = float(os.getenv('TEMPERATURE', '0.3'))
        
        # Development mode flag
        self.use_mock_api = os.getenv('USE_MOCK_API', 'false').lower() == 'true'
        
        # Real data settings
        self.use_real_data = os.getenv('USE_REAL_DATA', 'true').lower() == 'true'
        self.force_real_data = os.getenv('FORCE_REAL_DATA', 'true').lower() == 'true'
        
        # Validate required settings
        self._validate_settings()
    
    def _validate_settings(self):
        """Validate that required settings are present."""
        
        if not self.io_api_key:
            raise ValueError(
                "IO_API_KEY is required. Please set it in your environment variables or .env file."
            )
        
        if self.max_sources <= 0:
            raise ValueError("MAX_SOURCES must be a positive integer.")
        
        if self.output_format not in ['markdown', 'json', 'txt']:
            raise ValueError("OUTPUT_FORMAT must be one of: markdown, json, txt")
        
        if self.research_depth not in ['quick', 'standard', 'detailed']:
            raise ValueError("RESEARCH_DEPTH must be one of: quick, standard, detailed")
    
    def to_dict(self) -> dict:
        """Convert settings to dictionary."""
        
        return {
            'io_api_key': '***' if self.io_api_key else None,  # Hide API key
            'io_base_url': self.io_base_url,
            'max_sources': self.max_sources,
            'output_format': self.output_format,
            'research_depth': self.research_depth,
            'enable_streaming': self.enable_streaming,
            'user_agent': self.user_agent,
            'request_timeout': self.request_timeout,
            'max_retries': self.max_retries,
            'default_model': self.default_model,
            'max_tokens': self.max_tokens,
            'temperature': self.temperature,
        }
    
    def __repr__(self) -> str:
        """String representation of settings."""
        
        return f"Settings({self.to_dict()})"