from typing import Any, Dict, List

from ..config import get_settings
from ..prompts.interview_prompts import InterviewPromptManager
from ..prompts.verification_prompts import VerificationPromptManager


class InterviewFlow:
    def __init__(self):
        self.settings = get_settings()
        self.interview_manager = InterviewPromptManager(self.settings)
        self.verification_manager = VerificationPromptManager(self.settings)
        self.sessions: Dict[str, Any] = {}

    def start_interview(self, session_id: str):
        """Start a new interview session."""
        self.sessions[session_id] = self.interview_manager.create_interview_session(
            session_id
        )
        return self.sessions[session_id]

    def process_response(
        self,
        session_id: str,
        user_input: str,
        chat_history: List[Dict[str, str]] = None,
    ):
        """Process a candidate's response."""
        # Run the interview chain
        interview_response = self.interview_manager.run_interview(
            session_id=session_id,
            candidate_response=user_input,
            chat_history=chat_history,
        )

        # Run verification if we have previous responses
        if chat_history:
            verification_result = self.verification_manager.chain.invoke(
                {"previous_responses": chat_history, "current_response": user_input},
                config={
                    "tags": ["verification", session_id],
                    "metadata": {
                        "session_id": session_id,
                        "response_type": "verification",
                    },
                },
            )

            return {
                "interview_response": interview_response,
                "verification_result": verification_result,
            }

        return {"interview_response": interview_response}
