"""
Configuration management for the Medical Diagnostics System.
Handles environment variables, API keys, and system settings.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from typing import Optional

# Project root directory
PROJECT_ROOT = Path(__file__).parent

# Load environment variables from .env file if it exists
ENV_FILE = PROJECT_ROOT / ".env"
if ENV_FILE.exists():
    load_dotenv(dotenv_path=ENV_FILE)


class Config:
    """Configuration class for managing system settings."""
    
    # API Keys
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    HUGGINGFACEHUB_API_TOKEN: Optional[str] = os.getenv("HUGGINGFACEHUB_API_TOKEN")
    
    # Model defaults
    DEFAULT_HF_MODEL: str = "meta-llama/Llama-3.2-3B-Instruct"
    DEFAULT_OLLAMA_MODEL: str = "llama3.2"
    DEFAULT_OPENAI_MODEL: str = "gpt-4-turbo"
    
    # Directories
    MEDICAL_REPORTS_DIR: Path = PROJECT_ROOT / "Medical Reports"
    RESULTS_DIR: Path = PROJECT_ROOT / "results"
    
    # Validation
    MIN_REPORT_LENGTH: int = 100
    
    @classmethod
    def get_env_file_path(cls) -> Optional[Path]:
        """Get the path to the .env file if it exists."""
        return ENV_FILE if ENV_FILE.exists() else None
    
    @classmethod
    def ensure_directories(cls) -> None:
        """Ensure required directories exist."""
        cls.RESULTS_DIR.mkdir(exist_ok=True)
        cls.MEDICAL_REPORTS_DIR.mkdir(exist_ok=True)
    
    @classmethod
    def validate_api_keys(cls, use_huggingface: bool = False) -> bool:
        """
        Validate that required API keys are present.
        
        Args:
            use_huggingface: Whether to validate Hugging Face token
            
        Returns:
            True if required API keys are present, False otherwise
        """
        if use_huggingface:
            return cls.HUGGINGFACEHUB_API_TOKEN is not None
        else:
            return cls.OPENAI_API_KEY is not None

