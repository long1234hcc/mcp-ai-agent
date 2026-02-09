import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # App Info
    APP_NAME: str = "MCP AI Agent"
    ENV_MODE: str = "dev"
    LOG_LEVEL: str = "INFO"

    # Server Config
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # LLM Provider
    # ANTHROPIC_API_KEY: Optional[str] = None
    GOOGLE_API_KEY: str
    # AGENT_MODEL_ID: str = "claude-3-5-sonnet-20241022"
    AGENT_MODEL_ID: str = "gemini-3-flash-preview"

    # Agent Logic
    AGENT_CONFIDENCE_THRESHOLD: float = 0.7
    AGENT_MAX_RETRIES: int = 2

    # Cấu hình nạp file .env
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore" 
    )

# Singleton Instance
settings = Settings()