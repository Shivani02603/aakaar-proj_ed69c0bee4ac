from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional
from sqlalchemy.orm import Session
from database.models import Document, ChatSession
from database.config import get_db

router = APIRouter(tags=["Scalability"])

# Pydantic schemas for request and response
class ScalabilityStatsResponse(BaseModel):
    concurrent_users_supported: int = Field(..., description="Number of concurrent users supported by the system")
    current_active_sessions: int = Field(..., description="Number of currently active chat sessions")
    total_documents_uploaded: int = Field(..., description="Total number of documents uploaded to the system")
    total_chat_sessions: int = Field(..., description="Total number of chat sessions created in the system")

# Service function to calculate scalability stats
def calculate_scalability_stats(db: Session) -> ScalabilityStatsResponse:
    try:
        # Query the database for required stats
        total_documents = db.query(Document).count()
        total_chat_sessions = db.query(ChatSession).count()
        active_sessions = db.query(ChatSession).filter(ChatSession.last_activity.isnot(None)).count()

        # Assuming the system supports 50 concurrent users as per NFR-002
        concurrent_users_supported = 50

        return ScalabilityStatsResponse(
            concurrent_users_supported=concurrent_users_supported,
            current_active_sessions=active_sessions,
            total_documents_uploaded=total_documents,
            total_chat_sessions=total_chat_sessions,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating scalability stats: {str(e)}",
        )

# Endpoint to get scalability stats
@router.get("/scalability/stats", response_model=ScalabilityStatsResponse)
def get_scalability_stats(db: Session = Depends(get_db)):
    """
    Get scalability statistics for the system.
    """
    return calculate_scalability_stats(db)