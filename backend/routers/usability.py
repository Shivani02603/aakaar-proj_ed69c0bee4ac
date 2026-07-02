from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional
from sqlalchemy.orm import Session
from uuid import UUID
from database.models import Document, ChatSession
from database.config import get_db

router = APIRouter(tags=["Usability"])

# Pydantic schemas for request and response
class UsabilityFeedbackBase(BaseModel):
    id: UUID
    feedback: str
    created_at: Optional[str] = None

class UsabilityFeedbackCreate(BaseModel):
    feedback: str

class UsabilityFeedbackUpdate(BaseModel):
    feedback: Optional[str] = None

class UsabilityFeedbackResponse(UsabilityFeedbackBase):
    class Config:
        orm_mode = True

# Mock database table for usability feedback
class UsabilityFeedback:
    def __init__(self, id: UUID, feedback: str, created_at: str):
        self.id = id
        self.feedback = feedback
        self.created_at = created_at

# In-memory storage for usability feedback (mock implementation)
usability_feedback_storage = []

# Route to get all usability feedback
@router.get("/usability/feedback", response_model=List[UsabilityFeedbackResponse])
def get_usability_feedback(db: Session = Depends(get_db)):
    return usability_feedback_storage

# Route to get a specific usability feedback by ID
@router.get("/usability/feedback/{feedback_id}", response_model=UsabilityFeedbackResponse)
def get_usability_feedback_by_id(feedback_id: UUID, db: Session = Depends(get_db)):
    feedback = next((f for f in usability_feedback_storage if f.id == feedback_id), None)
    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usability feedback with ID {feedback_id} not found.",
        )
    return feedback

# Route to create new usability feedback
@router.post("/usability/feedback", response_model=UsabilityFeedbackResponse, status_code=status.HTTP_201_CREATED)
def create_usability_feedback(feedback_data: UsabilityFeedbackCreate, db: Session = Depends(get_db)):
    from uuid import uuid4
    from datetime import datetime

    new_feedback = UsabilityFeedback(
        id=uuid4(),
        feedback=feedback_data.feedback,
        created_at=datetime.utcnow().isoformat(),
    )
    usability_feedback_storage.append(new_feedback)
    return new_feedback

# Route to update usability feedback by ID
@router.put("/usability/feedback/{feedback_id}", response_model=UsabilityFeedbackResponse)
def update_usability_feedback(feedback_id: UUID, feedback_data: UsabilityFeedbackUpdate, db: Session = Depends(get_db)):
    feedback = next((f for f in usability_feedback_storage if f.id == feedback_id), None)
    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usability feedback with ID {feedback_id} not found.",
        )
    if feedback_data.feedback:
        feedback.feedback = feedback_data.feedback
    return feedback

# Route to delete usability feedback by ID
@router.delete("/usability/feedback/{feedback_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_usability_feedback(feedback_id: UUID, db: Session = Depends(get_db)):
    global usability_feedback_storage
    feedback = next((f for f in usability_feedback_storage if f.id == feedback_id), None)
    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usability feedback with ID {feedback_id} not found.",
        )
    usability_feedback_storage = [f for f in usability_feedback_storage if f.id != feedback_id]
    return None