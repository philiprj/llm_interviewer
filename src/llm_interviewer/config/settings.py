import os
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # API Keys - Required in production
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    google_api_key: Optional[str] = None

    # Model settings
    model_provider: str = "openai"  # One of: openai, anthropic, google
    model_name: str = "gpt-4"  # e.g. gpt-4, claude-2, gemini-pro
    temperature: float = 0.05

    # Interview settings
    max_topics: int = 2
    max_questions_per_topic: int = 3

    # Environment
    environment: str = "development"  # development, production

    class Config:
        env_file = ".env" if os.path.exists(".env") else None
        extra = "ignore"
        # Case sensitive environment variables
        case_sensitive = True

    def model_post_init(self, __context) -> None:
        """Validate required settings for production"""
        if self.environment == "production":
            if not self.openai_api_key and self.model_provider == "openai":
                raise ValueError("OPENAI_API_KEY is required in production")
            if not self.anthropic_api_key and self.model_provider == "anthropic":
                raise ValueError("ANTHROPIC_API_KEY is required in production")


settings = Settings()
