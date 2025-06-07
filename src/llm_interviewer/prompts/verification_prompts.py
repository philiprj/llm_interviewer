from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage, SystemMessage
from langchain.schema.output_parser import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough


class VerificationPromptManager:
    def __init__(self, settings):
        self.llm = ChatOpenAI(
            model_name=settings.model_name,
            temperature=settings.temperature,
            max_tokens=settings.max_tokens,
        )

        # Define the verification prompt
        self.verification_prompt = ChatPromptTemplate.from_messages(
            [
                SystemMessage(
                    content="""You are an AI interviewer verifying candidate responses.
            Your role is to:
            1. Check for consistency with previous answers
            2. Identify any contradictions
            3. Evaluate the depth of understanding
            4. Provide a confidence score for the verification"""
                ),
                HumanMessage(
                    content="""Previous responses: {previous_responses}
            Current response: {current_response}
            Please verify the consistency and accuracy of the current response."""
                ),
            ]
        )

        # Create the chain
        self.chain = (
            {
                "previous_responses": RunnablePassthrough(),
                "current_response": RunnablePassthrough(),
            }
            | self.verification_prompt
            | self.llm
            | StrOutputParser()
        )
