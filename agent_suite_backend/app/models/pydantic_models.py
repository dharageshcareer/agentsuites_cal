from pydantic import BaseModel, Field
from typing import List, Optional

# ==================================
# Agent Models
# ==================================

class Agent(BaseModel):
    agent_id: int
    agent_name: str
    description: Optional[str] = None
    schema_name: str

    class Config:
        from_attributes = True

# ==================================
# Chat Models
# ==================================

class ChatRequest(BaseModel):
    user_prompt: str

class ChatResponse(BaseModel):
    response: str

# ==================================
# Feedback Analysis Models
# ==================================
class FeedbackAnalysisResponse(BaseModel):
    """Defines the structured response for the feedback analysis agent."""
    summary: str = Field(..., description="A concise summary of the student feedback.")
    sentiment: str = Field(..., description="The overall sentiment of the feedback (e.g., Positive, Negative, Mixed).")
    action_suggestions: List[str] = Field(..., description="A list of 2-3 actionable recommendations for the instructor.")