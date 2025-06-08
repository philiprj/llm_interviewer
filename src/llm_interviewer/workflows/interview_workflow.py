from typing import Any, Dict

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from ..config.taxonomy import load_taxonomy, validate_taxonomy
from ..models.interview_state import InterviewState
from .nodes import (
    analyze_response,
    analyze_taxonomy_and_select_topic,
    decide_next_step,
    end_interview,
    generate_question,
    move_to_next_topic,
)

INTERVIEW_DOMAINS = load_taxonomy()
assert validate_taxonomy(INTERVIEW_DOMAINS), "Invalid taxonomy"


class InterviewWorkflow:
    def __init__(self):
        self.app = self._create_workflow()

    def _create_workflow(self):
        """Create and compile the interview workflow"""

        workflow = StateGraph(InterviewState)

        # Add nodes
        workflow.add_node("analyze_and_select", analyze_taxonomy_and_select_topic)
        workflow.add_node("generate_question", generate_question)
        workflow.add_node("analyze_response", analyze_response)
        workflow.add_node("next_topic", move_to_next_topic)
        workflow.add_node("end_interview", end_interview)

        # Define edges
        workflow.add_edge(START, "analyze_and_select")
        workflow.add_edge("analyze_and_select", "generate_question")
        workflow.add_edge("generate_question", "analyze_response")

        # Conditional edges for decision making
        workflow.add_conditional_edges(
            "analyze_response",
            decide_next_step,
            {
                "continue_topic": "analyze_and_select",
                "next_topic": "next_topic",
                "end_interview": "end_interview",
            },
        )

        workflow.add_edge("next_topic", "analyze_and_select")
        workflow.add_edge("end_interview", END)

        # Add memory for conversation persistence
        memory = MemorySaver()

        # Compile with interrupt before analyze_response
        return workflow.compile(
            checkpointer=memory, interrupt_before=["analyze_response"]
        )

    def start_interview(self, thread_id: str = "interview_1"):
        """Start a new interview session"""

        initial_state = {
            "taxonomy": INTERVIEW_DOMAINS,
            "messages": [],
            "current_domain": "",
            "current_subdomain": "",
            "current_skill": "",
            "topics_covered": [],
            "questions_asked_current_topic": 0,
            "total_questions_asked": 0,
            "topics_completed": 0,
            "current_evaluation": {},
            "overall_performance": [],
            "should_continue_interview": True,
            "interview_complete": False,
        }

        config = {"configurable": {"thread_id": thread_id}}

        # Run until we hit the interrupt (after generating first question)
        result = self.app.invoke(initial_state, config)

        return result, config

    def continue_interview(self, user_response: str, config: Dict[str, Any]):
        """Continue the interview with a user response"""

        from langchain_core.messages import HumanMessage

        # Get the current state
        current_state = self.app.get_state(config)

        # Add user response to the conversation
        current_state.values["messages"].append(HumanMessage(content=user_response))

        # Update the state with the user's message
        self.app.update_state(config, {"messages": current_state.values["messages"]})

        # Continue execution from where it was interrupted
        result = self.app.invoke(None, config)

        return result

    def get_latest_question(self, state):
        """Extract the latest question from the state"""
        from langchain_core.messages import AIMessage

        questions = [
            msg.content
            for msg in state["messages"]
            if isinstance(msg, AIMessage) and not msg.content.startswith("[INTERNAL]")
        ]

        return questions[-1] if questions else None

    def get_interview_summary(self, state):
        """Extract the interview summary"""
        from langchain_core.messages import AIMessage

        if state.get("interview_complete"):
            ai_messages = [
                msg.content
                for msg in state["messages"]
                if isinstance(msg, AIMessage)
                and not msg.content.startswith("[INTERNAL]")
            ]
            return ai_messages[-1] if ai_messages else None
        return None
