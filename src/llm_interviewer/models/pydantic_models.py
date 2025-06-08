from typing import List

from pydantic import BaseModel, Field


class TopicSelection(BaseModel):
    selected_topic: str = Field(description="The topic/domain selected for questioning")
    selected_subdomain: str = Field(description="The specific subdomain to focus on")
    selected_skill: str = Field(description="The specific skill to assess")
    reasoning: str = Field(
        description="Why this topic was selected for the current context"
    )


class Question(BaseModel):
    question: str = Field(description="The interview question to ask")
    topic_focus: str = Field(
        description="What specific aspect this question is testing"
    )
    difficulty_level: str = Field(description="Beginner, Intermediate, or Advanced")


class ResponseEvaluation(BaseModel):
    quality_score: float = Field(
        description="Score between 0-1 representing response quality"
    )
    demonstrates_knowledge: bool = Field(
        description="Whether the response shows adequate knowledge"
    )
    areas_of_strength: List[str] = Field(description="What the candidate did well")
    areas_for_improvement: List[str] = Field(description="Areas that could be better")
    should_continue_topic: bool = Field(
        description="Whether to ask another question on this topic"
    )
    reasoning: str = Field(description="Detailed reasoning for the evaluation")
