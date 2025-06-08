from typing import Annotated, Any, Dict, List, TypedDict

from langchain_core.messages import BaseMessage


class InterviewState(TypedDict):
    # Core interview data
    taxonomy: Dict[str, Any]
    messages: Annotated[List[BaseMessage], "Chat history"]

    # Topic tracking
    current_domain: str
    current_subdomain: str
    current_skill: str
    topics_covered: List[Dict[str, str]]

    # Progress tracking
    questions_asked_current_topic: int
    total_questions_asked: int
    topics_completed: int

    # Evaluation data
    current_evaluation: Dict[str, Any]
    overall_performance: List[Dict[str, Any]]

    # Flow control
    should_continue_interview: bool
    interview_complete: bool
