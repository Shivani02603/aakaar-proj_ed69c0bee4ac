from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import List
from datetime import datetime
from sqlalchemy.orm import Session
from database.models import ChatMessage, ChatSession
from database.config import get_db

router = APIRouter(tags=["Performance"])

# Pydantic schemas
class PerformanceMetricsResponse(BaseModel):
    average_response_time: float = Field(..., description="Average response time in seconds")
    max_response_time: float = Field(..., description="Maximum response time in seconds")
    min_response_time: float = Field(..., description="Minimum response time in seconds")
    total_queries: int = Field(..., description="Total number of queries processed")
    timestamp: datetime = Field(..., description="Timestamp of the metrics calculation")

# Service function to calculate performance metrics
def calculate_performance_metrics(db: Session) -> PerformanceMetricsResponse:
    try:
        # Fetch all chat messages to calculate metrics
        messages = db.query(ChatMessage).all()
        if not messages:
            return PerformanceMetricsResponse(
                average_response_time=0.0,
                max_response_time=0.0,
                min_response_time=0.0,
                total_queries=0,
                timestamp=datetime.utcnow(),
            )

        response_times = []
        for message in messages:
            session = db.query(ChatSession).filter(ChatSession.session_id == message.session_id).first()
            if session:
                response_time = (message.created_at - session.created_at).total_seconds()
                response_times.append(response_time)

        return PerformanceMetricsResponse(
            average_response_time=sum(response_times) / len(response_times),
            max_response_time=max(response_times),
            min_response_time=min(response_times),
            total_queries=len(messages),
            timestamp=datetime.utcnow(),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating performance metrics: {str(e)}",
        )

# Endpoint to get performance metrics
@router.get("/metrics", response_model=PerformanceMetricsResponse)
async def get_performance_metrics(db: Session = Depends(get_db)):
    """
    Get performance metrics including average response time, max response time,
    min response time, and total queries processed.
    """
    return calculate_performance_metrics(db)