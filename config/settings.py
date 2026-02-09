"""
Configuration management using pydantic-settings.
Loads configuration from environment variables and .env file.
For Streamlit Cloud, secrets are loaded in app.py before importing this module.
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """
    Centralized configuration for the multi-agent research application.
    All settings can be overridden via environment variables.
    """

    # API Keys (required)
    ANTHROPIC_API_KEY: str
    TAVILY_API_KEY: str

    # Model Configuration
    CLAUDE_MODEL: str = "claude-opus-4-6"
    CLAUDE_TEMPERATURE: float = 0.7
    CLAUDE_MAX_TOKENS: int = 4000

    # Workflow Configuration
    MAX_SEARCH_RESULTS: int = 10
    MAX_REVISION_ITERATIONS: int = 2
    QUALITY_THRESHOLD: float = 0.8

    # Timeouts (seconds)
    SEARCH_TIMEOUT: int = 30
    LLM_TIMEOUT: int = 60

    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
