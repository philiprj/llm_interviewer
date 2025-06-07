from typing import Any, Dict

from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import HumanMessage, SystemMessage
from langchain.schema.output_parser import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough
from langchain_openai import ChatOpenAI
from langsmith import Client


class InterviewPromptManager:
    def __init__(self, settings):
        self.client = Client()
        self.llm = ChatOpenAI(
            model_name=settings.model_name,
            temperature=settings.temperature,
            max_tokens=settings.max_tokens,
        )

        # Define the base interview prompt
        self.interview_prompt = ChatPromptTemplate.from_messages(
            [
                SystemMessage(
                    content="""You are an AI interviewer conducting a technical interview.
            Your role is to:
            1. Evaluate technical accuracy
            2. Identify knowledge gaps
            3. Ask relevant follow-up questions
            4. Maintain a professional and constructive tone"""
                ),
                MessagesPlaceholder(variable_name="chat_history"),
                HumanMessage(content="{candidate_response}"),
            ]
        )

        # Create the chain
        self.chain = (
            {
                "chat_history": RunnablePassthrough(),
                "candidate_response": RunnablePassthrough(),
            }
            | self.interview_prompt
            | self.llm
            | StrOutputParser()
        )

    def create_interview_session(self, session_id: str):
        """Create a new interview session in LangSmith."""
        return self.client.create_project(
            project_name=f"interview_session_{session_id}",
            description="Technical interview session",
        )

    def run_interview(
        self, session_id: str, candidate_response: str, chat_history: list = None
    ):
        """Run the interview chain with LangSmith tracking."""
        chat_history = chat_history or []

        # Run the chain with LangSmith tracking
        result = self.chain.invoke(
            {"chat_history": chat_history, "candidate_response": candidate_response},
            config={
                "tags": ["interview", session_id],
                "metadata": {"session_id": session_id, "response_type": "interview"},
            },
        )

        return result
