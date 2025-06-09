import json
from typing import Literal

from langchain.globals import set_llm_cache
from langchain_community.cache import InMemoryCache
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.tracers import LangChainTracer
from langsmith import Client

from ..config.settings import settings
from ..models.interview_state import InterviewState
from ..models.pydantic_models import Question, ResponseEvaluation, TopicSelection

# Initialize LangSmith client
langsmith_client = Client() if settings.langchain_tracing_v2 else None

# Enable caching if configured
if settings.enable_llm_caching:
    set_llm_cache(InMemoryCache())


# Enhanced LLM initialization with tracing
def create_llm_with_tracing(run_name: str, tags: list | None = None):
    """Create LLM instance with proper tracing and callbacks"""
    callbacks = []

    if settings.langchain_tracing_v2:
        tracer = LangChainTracer(
            project_name=settings.langchain_project, tags=tags or []
        )
        callbacks.append(tracer)

    if settings.model_provider == "openai":
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(
            temperature=settings.temperature,
            model=settings.model_name,
            request_timeout=settings.llm_timeout,
            max_retries=settings.llm_max_retries,
            callbacks=callbacks,
            tags=tags,
        )
    elif settings.model_provider == "anthropic":
        from langchain_anthropic import ChatAnthropic

        return ChatAnthropic(
            temperature=settings.temperature,
            model=settings.model_name,
            timeout=settings.llm_timeout,
            max_retries=settings.llm_max_retries,
            callbacks=callbacks,
            tags=tags,
        )


# Create specialized LLMs with tags
topic_selector_llm = create_llm_with_tracing(
    "topic_selection", tags=["topic_selection", "interview_flow"]
).with_structured_output(TopicSelection)

question_generator_llm = create_llm_with_tracing(
    "question_generation", tags=["question_generation", "interview_flow"]
).with_structured_output(Question)

evaluator_llm = create_llm_with_tracing(
    "response_evaluation", tags=["evaluation", "interview_flow"]
).with_structured_output(ResponseEvaluation)


def analyze_taxonomy_and_select_topic(state: InterviewState) -> InterviewState:
    """Step 1: Analyze taxonomy and identify topic for question"""

    system_prompt = """You are an expert technical interviewer. Analyze the provided skills taxonomy and conversation history to select the most appropriate topic for the next question.

    Consider:
    1. What topics have already been covered
    2. The candidate's demonstrated skill level so far
    3. Logical progression of topics
    4. Areas that need deeper exploration

    Select a domain, subdomain, and specific skill that would provide the most valuable assessment data."""

    taxonomy_str = json.dumps(state["taxonomy"], indent=2)
    topics_covered_str = json.dumps(state["topics_covered"], indent=2)

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(
            content=f"""
        Skills Taxonomy:
        {taxonomy_str}

        Topics Already Covered:
        {topics_covered_str}

        Total Questions Asked: {state["total_questions_asked"]}
        Topics Completed: {state["topics_completed"]}

        Select the next topic to explore."""
        ),
    ]

    topic_selection = topic_selector_llm.invoke(messages)

    return {
        **state,
        "current_domain": topic_selection.selected_topic,
        "current_subdomain": topic_selection.selected_subdomain,
        "current_skill": topic_selection.selected_skill,
        "messages": state["messages"]
        + [
            AIMessage(
                content=f"[INTERNAL] Selected topic: {topic_selection.selected_topic} - {topic_selection.selected_subdomain} - {topic_selection.selected_skill}. Reasoning: {topic_selection.reasoning}"
            )
        ],
    }


def generate_question(state: InterviewState) -> InterviewState:
    """Step 2: Create a question for user"""

    system_prompt = """You are an expert technical interviewer. Generate a thoughtful, targeted question based on the selected topic and the candidate's conversation history.

    The question should:
    1. Test both theoretical knowledge and practical application
    2. Be appropriate for the candidate's demonstrated skill level
    3. Allow for meaningful follow-up
    4. Be clear and unambiguous
    5. Encourage detailed responses"""

    recent_messages = (
        state["messages"][-6:] if len(state["messages"]) > 6 else state["messages"]
    )
    conversation_context = "\n".join(
        [
            f"{msg.__class__.__name__}: {msg.content}"
            for msg in recent_messages
            if not msg.content.startswith("[INTERNAL]")
        ]
    )

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(
            content=f"""
        Current Topic Focus:
        - Domain: {state["current_domain"]}
        - Subdomain: {state["current_subdomain"]}
        - Skill: {state["current_skill"]}

        Questions asked on this topic: {state["questions_asked_current_topic"]}

        Recent conversation context:
        {conversation_context}

        Generate an appropriate interview question."""
        ),
    ]

    question_obj = question_generator_llm.invoke(messages)

    return {
        **state,
        "messages": state["messages"] + [AIMessage(content=question_obj.question)],
        "questions_asked_current_topic": state["questions_asked_current_topic"] + 1,
        "total_questions_asked": state["total_questions_asked"] + 1,
    }


def analyze_response(state: InterviewState) -> InterviewState:
    """Step 4: Analyze user response using system prompt"""

    if not state["messages"] or not isinstance(state["messages"][-1], HumanMessage):
        return state

    user_response = state["messages"][-1].content

    system_prompt = f"""You are an expert technical interviewer evaluating a candidate's response. Analyze the response thoroughly and provide detailed feedback.

    Current Assessment Context:
    - Domain: {state["current_domain"]}
    - Subdomain: {state["current_subdomain"]}
    - Skill: {state["current_skill"]}
    - Question Number on this topic: {state["questions_asked_current_topic"]}

    Evaluate the response for:
    1. Technical accuracy and depth
    2. Practical understanding
    3. Communication clarity
    4. Areas of strength and improvement
    5. Whether additional questions on this topic would be valuable

    Provide a quality score between 0-1 and determine if we should continue with this topic or move on."""

    ai_messages = [
        msg
        for msg in state["messages"]
        if isinstance(msg, AIMessage) and not msg.content.startswith("[INTERNAL]")
    ]
    last_question = (
        ai_messages[-1].content if ai_messages else "No previous question found"
    )

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(
            content=f"""
        Question Asked: {last_question}

        Candidate's Response: {user_response}

        Please evaluate this response."""
        ),
    ]

    evaluation = evaluator_llm.invoke(messages)

    evaluation_data = {
        "question": last_question,
        "response": user_response,
        "quality_score": evaluation.quality_score,
        "demonstrates_knowledge": evaluation.demonstrates_knowledge,
        "areas_of_strength": evaluation.areas_of_strength,
        "areas_for_improvement": evaluation.areas_for_improvement,
        "should_continue_topic": evaluation.should_continue_topic,
        "reasoning": evaluation.reasoning,
        "topic": f"{state['current_domain']} - {state['current_subdomain']} - {state['current_skill']}",
    }

    return {
        **state,
        "current_evaluation": evaluation_data,
        "overall_performance": state["overall_performance"] + [evaluation_data],
        "messages": state["messages"]
        + [
            AIMessage(
                content=f"[INTERNAL] Evaluation complete. Quality score: {evaluation.quality_score:.2f}. Should continue topic: {evaluation.should_continue_topic}"
            )
        ],
    }


def decide_next_step(
    state: InterviewState,
) -> Literal["continue_topic", "next_topic", "end_interview"]:
    """Step 5: Decision logic for interview flow"""

    if state["topics_completed"] >= settings.max_topics:
        return "end_interview"

    if state["questions_asked_current_topic"] >= settings.max_questions_per_topic:
        return "next_topic"

    if state["current_evaluation"]:
        evaluation = state["current_evaluation"]

        if (
            evaluation["quality_score"] < 0.3
            and state["questions_asked_current_topic"] >= 2
        ):
            return "next_topic"

        if evaluation["demonstrates_knowledge"] and evaluation["quality_score"] > 0.7:
            return "next_topic"

        if evaluation["should_continue_topic"]:
            return "continue_topic"

    if state["questions_asked_current_topic"] >= 2:
        return "next_topic"

    return "continue_topic"


def move_to_next_topic(state: InterviewState) -> InterviewState:
    """Step 6: Move onto next topic"""

    completed_topic = {
        "domain": state["current_domain"],
        "subdomain": state["current_subdomain"],
        "skill": state["current_skill"],
        "questions_asked": state["questions_asked_current_topic"],
    }

    return {
        **state,
        "topics_covered": state["topics_covered"] + [completed_topic],
        "topics_completed": state["topics_completed"] + 1,
        "questions_asked_current_topic": 0,
        "current_domain": "",
        "current_subdomain": "",
        "current_skill": "",
        "messages": state["messages"]
        + [
            AIMessage(
                content=f"[INTERNAL] Moving to next topic. Topics completed: {state['topics_completed'] + 1}"
            )
        ],
    }


def end_interview(state: InterviewState) -> InterviewState:
    """Step 7: End interview and provide summary"""

    total_score = sum(
        [eval_data["quality_score"] for eval_data in state["overall_performance"]]
    )
    avg_score = (
        total_score / len(state["overall_performance"])
        if state["overall_performance"]
        else 0
    )

    summary = f"""
    Interview Complete!

    Summary:
    - Topics Covered: {len(state["topics_covered"])}
    - Total Questions Asked: {state["total_questions_asked"]}
    - Average Performance Score: {avg_score:.2f}/1.0

    Performance by Topic:
    """

    for eval_data in state["overall_performance"]:
        summary += f"\n- {eval_data['topic']}: {eval_data['quality_score']:.2f}/1.0"

    return {
        **state,
        "interview_complete": True,
        "should_continue_interview": False,
        "messages": state["messages"] + [AIMessage(content=summary)],
    }
