"""Tests for Settings configuration."""

import os
from unittest.mock import patch

import pytest

from src.llm_interviewer.config.settings import Settings


class TestSettings:
    """Test the Settings configuration class."""

    def test_default_settings(self):
        """Test default settings values."""
        settings = Settings()

        assert settings.model_provider == "openai"
        assert settings.model_name == "gpt-4o"
        assert settings.temperature == 0.05
        assert settings.max_topics == 2
        assert settings.max_questions_per_topic == 3
        assert settings.langchain_tracing_v2 is False
        assert settings.environment == "development"

    def test_custom_settings_development(self):
        """Test creating settings with custom values in development."""
        settings = Settings(
            model_provider="anthropic",
            model_name="claude-2",
            temperature=0.1,
            max_topics=3,
            max_questions_per_topic=5,
            environment="development",  # Use development to avoid validation
        )

        assert settings.model_provider == "anthropic"
        assert settings.model_name == "claude-2"
        assert settings.temperature == 0.1
        assert settings.max_topics == 3
        assert settings.max_questions_per_topic == 5
        assert settings.environment == "development"

    def test_custom_settings_production_with_key(self):
        """Test creating settings with custom values in production with required key."""
        settings = Settings(
            model_provider="anthropic",
            model_name="claude-2",
            temperature=0.1,
            max_topics=3,
            max_questions_per_topic=5,
            environment="production",
            anthropic_api_key="test-key",  # Provide required key
        )

        assert settings.model_provider == "anthropic"
        assert settings.model_name == "claude-2"
        assert settings.temperature == 0.1
        assert settings.max_topics == 3
        assert settings.max_questions_per_topic == 5
        assert settings.environment == "production"
        assert settings.anthropic_api_key == "test-key"

    def test_llm_performance_settings(self):
        """Test LLM performance related settings."""
        settings = Settings(
            llm_timeout=60,
            llm_max_retries=5,
            enable_llm_caching=False,
            enable_prompt_optimization=False,
        )

        assert settings.llm_timeout == 60
        assert settings.llm_max_retries == 5
        assert settings.enable_llm_caching is False
        assert settings.enable_prompt_optimization is False

    def test_langsmith_settings(self):
        """Test LangSmith configuration settings."""
        settings = Settings(
            langchain_tracing_v2=True,
            langchain_api_key="test-key",
            langchain_project="test-project",
            langchain_endpoint="https://test.endpoint.com",
        )

        assert settings.langchain_tracing_v2 is True
        assert settings.langchain_api_key == "test-key"
        assert settings.langchain_project == "test-project"
        assert settings.langchain_endpoint == "https://test.endpoint.com"

    @patch.dict(
        os.environ,
        {
            "model_provider": "google",  # lowercase to match pydantic-settings behavior
            "model_name": "gemini-pro",
            "temperature": "0.2",
            "max_topics": "4",
        },
    )
    def test_environment_variable_override(self):
        """Test that environment variables override defaults."""
        settings = Settings()

        assert settings.model_provider == "google"
        assert settings.model_name == "gemini-pro"
        assert settings.temperature == 0.2
        assert settings.max_topics == 4

    def test_production_validation_openai_missing_key(self):
        """Test production validation fails without OpenAI key."""
        with pytest.raises(
            ValueError, match="OPENAI_API_KEY is required in production"
        ):
            Settings(environment="production", model_provider="openai")

    def test_production_validation_anthropic_missing_key(self):
        """Test production validation fails without Anthropic key."""
        with pytest.raises(
            ValueError, match="ANTHROPIC_API_KEY is required in production"
        ):
            Settings(environment="production", model_provider="anthropic")

    def test_production_validation_success_with_keys(self):
        """Test production validation succeeds with required keys."""
        settings = Settings(
            environment="production", model_provider="openai", openai_api_key="test-key"
        )
        assert settings.environment == "production"
        assert settings.openai_api_key == "test-key"

    def test_development_no_validation(self):
        """Test development environment doesn't require API keys."""
        settings = Settings(environment="development", model_provider="openai")
        assert settings.environment == "development"
        assert settings.openai_api_key is None

    @patch.dict(os.environ, {}, clear=True)
    def test_langsmith_environment_setup(self):
        """Test LangSmith environment variable setup."""
        Settings(
            langchain_tracing_v2=True,
            langchain_api_key="test-langsmith-key",
            langchain_project="test-project",
        )

        # The post_init should set environment variables
        assert os.environ.get("LANGCHAIN_TRACING_V2") == "true"
        assert os.environ.get("LANGCHAIN_API_KEY") == "test-langsmith-key"
        assert os.environ.get("LANGCHAIN_PROJECT") == "test-project"

    def test_temperature_bounds(self):
        """Test temperature accepts valid float values."""
        # Test valid temperature values
        for temp in [0.0, 0.5, 1.0, 2.0]:
            settings = Settings(temperature=temp)
            assert settings.temperature == temp

    def test_integer_settings_validation(self):
        """Test integer settings accept valid values."""
        settings = Settings(
            max_topics=5, max_questions_per_topic=10, llm_timeout=120, llm_max_retries=3
        )

        assert settings.max_topics == 5
        assert settings.max_questions_per_topic == 10
        assert settings.llm_timeout == 120
        assert settings.llm_max_retries == 3

    def test_case_sensitive_environment_variables(self):
        """Test that case-sensitive environment variables work correctly."""
        with patch.dict(
            os.environ,
            {
                "model_provider": "google",  # exact case match
                "MODEL_PROVIDER": "anthropic",
            },
        ):
            settings = Settings()
            # Should use lowercase version since that matches the field name
            assert settings.model_provider == "google"

    def test_google_provider_settings(self):
        """Test settings with Google provider (no validation required)."""
        settings = Settings(
            model_provider="google",
            model_name="gemini-pro",
            environment="production",  # Google doesn't require API key validation
        )

        assert settings.model_provider == "google"
        assert settings.model_name == "gemini-pro"
        assert settings.environment == "production"
