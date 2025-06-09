"""Pytest configuration and shared fixtures."""

import json
import tempfile
from pathlib import Path
from typing import Any, Dict

import pytest


@pytest.fixture
def sample_taxonomy() -> Dict[str, Any]:
    """Sample taxonomy data for testing."""
    return {
        "domains": [
            {
                "name": "Test Domain",
                "subdomains": [
                    {
                        "name": "Test Subdomain",
                        "core_skills": [
                            {
                                "name": "Test Skill",
                                "knowledge_areas": ["Area 1", "Area 2"],
                                "practical_applications": ["App 1", "App 2"],
                            }
                        ],
                    }
                ],
            }
        ]
    }


@pytest.fixture
def temp_taxonomy_file(sample_taxonomy):
    """Create a temporary taxonomy file for testing."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(sample_taxonomy, f)
        temp_path = f.name

    yield temp_path

    # Cleanup
    Path(temp_path).unlink(missing_ok=True)


@pytest.fixture
def invalid_taxonomy_file():
    """Create a temporary invalid taxonomy file for testing."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        f.write("invalid json content")
        temp_path = f.name

    yield temp_path

    # Cleanup
    Path(temp_path).unlink(missing_ok=True)
