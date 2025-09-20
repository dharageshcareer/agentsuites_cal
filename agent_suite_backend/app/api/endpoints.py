from fastapi import APIRouter, Depends
from sqlalchemy import create_engine, text
from typing import List

from fastapi import UploadFile, File
from app.models.pydantic_models import FeedbackAnalysisResponse
from app.services.instructor_assistant_agent import analyze_feedback_file

from app.models.pydantic_models import Agent, ChatRequest, ChatResponse
from app.core.config import DATABASE_URL
# Import the new ADK-based agent function
from app.services.job_placement_agent_adk import query_agent_adk

router = APIRouter()

# Dependency to get a DB connection
def get_db():
    engine = create_engine(DATABASE_URL)
    with engine.connect() as connection:
        yield connection

@router.get("/agents", response_model=List[Agent])
def list_agents(db=Depends(get_db)):
    """
    Lists all the agents available in the application suite.
    """
    query = text("SELECT agent_id, agent_name, description, schema_name FROM system.agents")
    result = db.execute(query).fetchall()
    agents = [Agent(agent_id=row[0], agent_name=row[1], description=row[2], schema_name=row[3]) for row in result]
    return agents

@router.post("/jobplacement_rag/chat", response_model=ChatResponse)
async def chat_with_job_agent(request: ChatRequest):
    """
    Endpoint to communicate with the Job Placement RAG agent (Google ADK version).
    """
    # Call the new agent function
    agent_response = query_agent_adk(request.user_prompt)
    return ChatResponse(response=agent_response)

@router.post("/instructor_assistant/analyze_feedback", response_model=FeedbackAnalysisResponse)
async def analyze_instructor_feedback_stateless(file: UploadFile = File(...)):
    """
    Accepts a student feedback file (CSV or JSON) and returns an LLM-powered
    analysis containing a summary, sentiment, and actionable suggestions.
    This endpoint is stateless and does not store any data.
    """
    # Read the entire file content into memory as bytes
    file_contents = await file.read()

    # Call the agent service to perform the analysis
    analysis_result = analyze_feedback_file(file_contents, file.filename)

    # Return the result directly to the user
    return analysis_result