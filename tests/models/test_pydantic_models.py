"""Tests for Pydantic models."""

import pytest
from pydantic import ValidationError

from src.llm_interviewer.models.pydantic_models import (
    Question,
    ResponseEvaluation,
    TopicSelection,
)


class TestTopicSelection:
    """Test the TopicSelection model."""

    def test_valid_topic_selection(self):
        """Test creating a valid TopicSelection."""
        topic = TopicSelection(
            selected_topic="LLM Architecture",
            selected_subdomain="Model Architecture",
            selected_skill="Transformer Architecture",
            reasoning="This is a fundamental concept to assess",
        )

        assert topic.selected_topic == "LLM Architecture"
        assert topic.selected_subdomain == "Model Architecture"
        assert topic.selected_skill == "Transformer Architecture"
        assert topic.reasoning == "This is a fundamental concept to assess"

    def test_missing_required_fields(self):
        """Test validation fails when required fields are missing."""
        with pytest.raises(ValidationError):
            TopicSelection(
                selected_topic="LLM Architecture",
                # Missing other required fields
            )

    def test_empty_strings_allowed(self):
        """Test that empty strings are allowed for all fields."""
        topic = TopicSelection(
            selected_topic="", selected_subdomain="", selected_skill="", reasoning=""
        )
        assert topic.selected_topic == ""

    def test_serialization(self):
        """Test model serialization to dict."""
        topic = TopicSelection(
            selected_topic="Test Topic",
            selected_subdomain="Test Subdomain",
            selected_skill="Test Skill",
            reasoning="Test reasoning",
        )

        serialized = topic.model_dump()
        expected = {
            "selected_topic": "Test Topic",
            "selected_subdomain": "Test Subdomain",
            "selected_skill": "Test Skill",
            "reasoning": "Test reasoning",
        }
        assert serialized == expected


class TestQuestion:
    """Test the Question model."""

    def test_valid_question(self):
        """Test creating a valid Question."""
        question = Question(
            question="What is attention mechanism?",
            topic_focus="Understanding of attention in transformers",
            difficulty_level="Intermediate",
        )

        assert question.question == "What is attention mechanism?"
        assert question.topic_focus == "Understanding of attention in transformers"
        assert question.difficulty_level == "Intermediate"

    def test_difficulty_levels(self):
        """Test different difficulty levels."""
        difficulty_levels = ["Beginner", "Intermediate", "Advanced"]

        for level in difficulty_levels:
            question = Question(
                question="Test question",
                topic_focus="Test focus",
                difficulty_level=level,
            )
            assert question.difficulty_level == level

    def test_json_serialization(self):
        """Test JSON serialization and deserialization."""
        question = Question(
            question="Test question",
            topic_focus="Test focus",
            difficulty_level="Beginner",
        )

        # Test serialization
        json_str = question.model_dump_json()
        assert isinstance(json_str, str)

        # Test deserialization
        question_restored = Question.model_validate_json(json_str)
        assert question_restored.question == question.question
        assert question_restored.topic_focus == question.topic_focus
        assert question_restored.difficulty_level == question.difficulty_level


class TestResponseEvaluation:
    """Test the ResponseEvaluation model."""

    def test_valid_evaluation(self):
        """Test creating a valid ResponseEvaluation."""
        evaluation = ResponseEvaluation(
            quality_score=0.85,
            demonstrates_knowledge=True,
            areas_of_strength=["Clear explanation", "Good examples"],
            areas_for_improvement=["Could add more detail"],
            should_continue_topic=True,
            reasoning="Good understanding but needs more depth",
        )

        assert evaluation.quality_score == 0.85
        assert evaluation.demonstrates_knowledge is True
        assert len(evaluation.areas_of_strength) == 2
        assert len(evaluation.areas_for_improvement) == 1
        assert evaluation.should_continue_topic is True

    def test_quality_score_bounds(self):
        """Test quality score validation."""
        # Valid scores
        for score in [0.0, 0.5, 1.0]:
            evaluation = ResponseEvaluation(
                quality_score=score,
                demonstrates_knowledge=True,
                areas_of_strength=[],
                areas_for_improvement=[],
                should_continue_topic=False,
                reasoning="Test",
            )
            assert evaluation.quality_score == score

        # Test edge cases - Pydantic doesn't enforce 0-1 bounds by default
        # but we can test that it accepts floats
        evaluation = ResponseEvaluation(
            quality_score=1.5,  # This will be accepted unless we add validators
            demonstrates_knowledge=True,
            areas_of_strength=[],
            areas_for_improvement=[],
            should_continue_topic=False,
            reasoning="Test",
        )
        assert evaluation.quality_score == 1.5

    def test_empty_lists(self):
        """Test that empty lists are valid for strength/improvement areas."""
        evaluation = ResponseEvaluation(
            quality_score=0.5,
            demonstrates_knowledge=False,
            areas_of_strength=[],
            areas_for_improvement=[],
            should_continue_topic=False,
            reasoning="No clear understanding demonstrated",
        )

        assert evaluation.areas_of_strength == []
        assert evaluation.areas_for_improvement == []

    def test_boolean_flags(self):
        """Test boolean field behavior."""
        # Test True values
        evaluation = ResponseEvaluation(
            quality_score=0.8,
            demonstrates_knowledge=True,
            areas_of_strength=["Good"],
            areas_for_improvement=[],
            should_continue_topic=True,
            reasoning="Continue with topic",
        )
        assert evaluation.demonstrates_knowledge is True
        assert evaluation.should_continue_topic is True

        # Test False values
        evaluation.demonstrates_knowledge = False
        evaluation.should_continue_topic = False
        assert evaluation.demonstrates_knowledge is False
        assert evaluation.should_continue_topic is False
