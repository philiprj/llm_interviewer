"""Tests for interview state management."""

from langchain_core.messages import AIMessage, HumanMessage

from src.llm_interviewer.models.interview_state import InterviewState


class TestInterviewState:
    """Test the InterviewState TypedDict structure."""

    def test_interview_state_structure(self):
        """Test that InterviewState has the expected structure."""
        # Since InterviewState is a TypedDict, we test by creating valid instances
        sample_state = {
            "taxonomy": {"domains": []},
            "messages": [],
            "current_domain": "Test Domain",
            "current_subdomain": "Test Subdomain",
            "current_skill": "Test Skill",
            "topics_covered": [],
            "questions_asked_current_topic": 0,
            "total_questions_asked": 0,
            "topics_completed": 0,
            "current_evaluation": {},
            "overall_performance": [],
            "should_continue_interview": True,
            "interview_complete": False,
        }

        # This should not raise any errors
        state: InterviewState = sample_state
        assert state["current_domain"] == "Test Domain"
        assert state["should_continue_interview"] is True

    def test_state_with_messages(self):
        """Test state with actual message objects."""
        messages = [HumanMessage(content="Hello"), AIMessage(content="Hi there!")]

        state: InterviewState = {
            "taxonomy": {"domains": []},
            "messages": messages,
            "current_domain": "LLM Architecture",
            "current_subdomain": "Model Architecture",
            "current_skill": "Transformer Architecture",
            "topics_covered": [
                {"domain": "LLM Development", "subdomain": "Prompt Engineering"}
            ],
            "questions_asked_current_topic": 2,
            "total_questions_asked": 5,
            "topics_completed": 1,
            "current_evaluation": {
                "quality_score": 0.8,
                "demonstrates_knowledge": True,
            },
            "overall_performance": [{"topic": "Prompt Engineering", "score": 0.75}],
            "should_continue_interview": True,
            "interview_complete": False,
        }

        assert len(state["messages"]) == 2
        assert state["messages"][0].content == "Hello"
        assert state["total_questions_asked"] == 5
        assert len(state["topics_covered"]) == 1

    def test_state_completion_flags(self):
        """Test interview completion state management."""
        # Active interview state
        active_state: InterviewState = {
            "taxonomy": {},
            "messages": [],
            "current_domain": "Test",
            "current_subdomain": "Test",
            "current_skill": "Test",
            "topics_covered": [],
            "questions_asked_current_topic": 1,
            "total_questions_asked": 1,
            "topics_completed": 0,
            "current_evaluation": {},
            "overall_performance": [],
            "should_continue_interview": True,
            "interview_complete": False,
        }

        assert active_state["should_continue_interview"] is True
        assert active_state["interview_complete"] is False

        # Completed interview state
        completed_state: InterviewState = {
            "taxonomy": {},
            "messages": [],
            "current_domain": "Test",
            "current_subdomain": "Test",
            "current_skill": "Test",
            "topics_covered": [],
            "questions_asked_current_topic": 3,
            "total_questions_asked": 6,
            "topics_completed": 2,
            "current_evaluation": {},
            "overall_performance": [],
            "should_continue_interview": False,
            "interview_complete": True,
        }

        assert completed_state["should_continue_interview"] is False
        assert completed_state["interview_complete"] is True

    def test_performance_tracking(self):
        """Test performance tracking data structures."""
        state: InterviewState = {
            "taxonomy": {},
            "messages": [],
            "current_domain": "LLM Architecture",
            "current_subdomain": "Model Architecture",
            "current_skill": "Attention Mechanisms",
            "topics_covered": [
                {
                    "domain": "LLM Development",
                    "subdomain": "Prompt Engineering",
                    "skill": "Chain-of-thought",
                }
            ],
            "questions_asked_current_topic": 2,
            "total_questions_asked": 4,
            "topics_completed": 1,
            "current_evaluation": {
                "quality_score": 0.85,
                "demonstrates_knowledge": True,
                "areas_of_strength": ["Clear explanations"],
                "areas_for_improvement": ["More examples needed"],
            },
            "overall_performance": [
                {
                    "domain": "LLM Development",
                    "subdomain": "Prompt Engineering",
                    "average_score": 0.75,
                    "questions_answered": 2,
                }
            ],
            "should_continue_interview": True,
            "interview_complete": False,
        }

        # Verify structure
        assert len(state["topics_covered"]) == 1
        assert state["topics_covered"][0]["domain"] == "LLM Development"
        assert state["current_evaluation"]["quality_score"] == 0.85
        assert len(state["overall_performance"]) == 1
        assert state["overall_performance"][0]["average_score"] == 0.75
