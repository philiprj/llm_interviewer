import os
from datetime import datetime

import streamlit as st

# Set up environment
if "OPENAI_API_KEY" not in os.environ:
    st.error("Please set OPENAI_API_KEY environment variable")
    st.stop()

from llm_interviewer.config.taxonomy import INTERVIEW_DOMAINS
from llm_interviewer.workflows.interview_workflow import InterviewWorkflow

# Page configuration
st.set_page_config(
    page_title="AI Technical Interviewer",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize session state
if "interview_workflow" not in st.session_state:
    st.session_state.interview_workflow = InterviewWorkflow()

if "interview_started" not in st.session_state:
    st.session_state.interview_started = False

if "interview_state" not in st.session_state:
    st.session_state.interview_state = None

if "interview_config" not in st.session_state:
    st.session_state.interview_config = None

if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []

# Initialize text area content session state
if "current_response" not in st.session_state:
    st.session_state.current_response = ""

# Sidebar
with st.sidebar:
    st.title("🤖 AI Technical Interviewer")
    st.markdown("---")

    # Interview controls
    st.subheader("Interview Controls")

    if not st.session_state.interview_started:
        if st.button("Start Interview", type="primary", use_container_width=True):
            thread_id = f"interview_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            result, config = st.session_state.interview_workflow.start_interview(
                thread_id
            )

            st.session_state.interview_state = result
            st.session_state.interview_config = config
            st.session_state.interview_started = True

            # Get the first question
            question = st.session_state.interview_workflow.get_latest_question(result)
            if question:
                st.session_state.conversation_history.append(
                    {
                        "role": "interviewer",
                        "content": question,
                        "timestamp": datetime.now(),
                    }
                )

            st.rerun()
    else:
        if st.button("Reset Interview", type="secondary", use_container_width=True):
            # Reset all session state
            for key in [
                "interview_started",
                "interview_state",
                "interview_config",
                "conversation_history",
                "current_response",
            ]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

    st.markdown("---")

    # Interview progress
    if st.session_state.interview_started and st.session_state.interview_state:
        st.subheader("Progress")
        state = st.session_state.interview_state

        # Progress metrics
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Topics", f"{state.get('topics_completed', 0)}/2")
        with col2:
            st.metric("Questions", state.get("total_questions_asked", 0))

        # Current topic
        if state.get("current_domain"):
            st.info(
                f"**Current Topic:**\n{state['current_domain']} - {state['current_subdomain']}"
            )

        # Performance so far
        if state.get("overall_performance"):
            st.subheader("Performance")
            for eval_data in state["overall_performance"]:
                score = eval_data["quality_score"]
                st.metric(
                    f"Topic {len(state['overall_performance'])}",
                    f"{score:.2f}/1.0",
                    delta=None,
                )

# Main content
st.title("AI Technical Interviewer")
st.markdown("*Test your knowledge with an AI-powered technical interview*")

if not st.session_state.interview_started:
    # Welcome screen
    st.markdown("## Welcome!")
    st.markdown("""
    This AI interviewer will assess your technical knowledge through a structured conversation.
    
    **How it works:**
    1. The AI will ask you technical questions based on a predefined taxonomy
    2. You'll provide detailed responses
    3. Your answers will be evaluated and the AI will adapt accordingly
    4. The interview covers up to 2 main topics with up to 3 questions each
    
    **Topics covered:**
    - LLM Architecture & Theory
    - LLM Development & Applications
    
    Click "Start Interview" in the sidebar to begin!
    """)

    # Show taxonomy
    with st.expander("📋 View Interview Taxonomy"):
        st.json(INTERVIEW_DOMAINS)

else:
    # Interview in progress
    if st.session_state.interview_state and not st.session_state.interview_state.get(
        "interview_complete"
    ):
        # Current question
        if st.session_state.conversation_history:
            latest_question = st.session_state.conversation_history[-1]
            if latest_question["role"] == "interviewer":
                st.markdown("### 🤖 Interviewer Question:")
                st.markdown(f"*{latest_question['content']}*")

        # Response input
        st.markdown("### 💭 Your Response:")
        user_response = st.text_area(
            "Please provide a detailed response:",
            height=200,
            placeholder="Type your answer here...",
            value=st.session_state.current_response,
            key="response_input",
        )

        # Update session state with current text area value
        st.session_state.current_response = user_response

        if st.button(
            "Submit Response", type="primary", disabled=not user_response.strip()
        ):
            if user_response.strip():
                # Add user response to history
                st.session_state.conversation_history.append(
                    {
                        "role": "candidate",
                        "content": user_response,
                        "timestamp": datetime.now(),
                    }
                )

                st.session_state.current_response = ""

                # Continue interview
                with st.spinner("AI is evaluating your response..."):
                    result = st.session_state.interview_workflow.continue_interview(
                        user_response, st.session_state.interview_config
                    )
                    st.session_state.interview_state = result

                # Check if interview is complete
                if result.get("interview_complete"):
                    summary = st.session_state.interview_workflow.get_interview_summary(
                        result
                    )
                    if summary:
                        st.session_state.conversation_history.append(
                            {
                                "role": "interviewer",
                                "content": summary,
                                "timestamp": datetime.now(),
                            }
                        )
                else:
                    # Get next question
                    question = st.session_state.interview_workflow.get_latest_question(
                        result
                    )
                    if question:
                        st.session_state.conversation_history.append(
                            {
                                "role": "interviewer",
                                "content": question,
                                "timestamp": datetime.now(),
                            }
                        )

                st.rerun()

    elif st.session_state.interview_state and st.session_state.interview_state.get(
        "interview_complete"
    ):
        # Interview complete
        st.success("🎉 Interview Complete!")

        # Show final summary
        if st.session_state.conversation_history:
            final_summary = st.session_state.conversation_history[-1]
            if final_summary["role"] == "interviewer":
                st.markdown("### 📊 Final Results:")
                st.markdown(final_summary["content"])

        # Detailed performance breakdown
        state = st.session_state.interview_state
        if state.get("overall_performance"):
            st.markdown("### 📈 Detailed Performance")

            for i, eval_data in enumerate(state["overall_performance"], 1):
                with st.expander(
                    f"Question {i}: {eval_data['topic']} (Score: {eval_data['quality_score']:.2f}/1.0)"
                ):
                    col1, col2 = st.columns(2)

                    with col1:
                        st.markdown("**Question:**")
                        st.write(eval_data["question"])

                        st.markdown("**Your Response:**")
                        st.write(eval_data["response"])

                    with col2:
                        st.markdown("**Evaluation:**")
                        st.write(f"**Score:** {eval_data['quality_score']:.2f}/1.0")
                        st.write(
                            f"**Demonstrates Knowledge:** {'✅' if eval_data['demonstrates_knowledge'] else '❌'}"
                        )

                        if eval_data["areas_of_strength"]:
                            st.markdown("**Strengths:**")
                            for strength in eval_data["areas_of_strength"]:
                                st.write(f"• {strength}")

                        if eval_data["areas_for_improvement"]:
                            st.markdown("**Areas for Improvement:**")
                            for improvement in eval_data["areas_for_improvement"]:
                                st.write(f"• {improvement}")

                        st.markdown("**Reasoning:**")
                        st.write(eval_data["reasoning"])

# Conversation history (always visible if interview started)
if st.session_state.interview_started and st.session_state.conversation_history:
    with st.expander("💬 Conversation History", expanded=False):
        for entry in st.session_state.conversation_history:
            role_emoji = "🤖" if entry["role"] == "interviewer" else "👤"
            role_name = "Interviewer" if entry["role"] == "interviewer" else "You"

            st.markdown(
                f"**{role_emoji} {role_name}** *({entry['timestamp'].strftime('%H:%M:%S')})*"
            )
            st.markdown(entry["content"])
            st.markdown("---")
