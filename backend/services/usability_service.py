from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import HTTPException, status, Depends
from database.models import UsabilityFeedback
from database.config import get_db

class UsabilityService:
    @staticmethod
    def create_usability_feedback(
        feedback_text: str,
        user_id: Optional[UUID],
        db: Session = Depends(get_db)
    ) -> UsabilityFeedback:
        """
        Create a new usability feedback entry.
        """
        new_feedback = UsabilityFeedback(
            feedback_text=feedback_text,
            user_id=user_id
        )
        db.add(new_feedback)
        db.commit()
        db.refresh(new_feedback)
        return new_feedback

    @staticmethod
    def get_usability_feedback_by_id(
        feedback_id: UUID,
        db: Session = Depends(get_db)
    ) -> UsabilityFeedback:
        """
        Retrieve a usability feedback entry by its ID.
        """
        feedback = db.query(UsabilityFeedback).filter(UsabilityFeedback.id == feedback_id).first()
        if not feedback:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Usability feedback with ID {feedback_id} not found."
            )
        return feedback

    @staticmethod
    def list_all_usability_feedback(
        db: Session = Depends(get_db)
    ) -> List[UsabilityFeedback]:
        """
        List all usability feedback entries.
        """
        feedback_list = db.query(UsabilityFeedback).all()
        return feedback_list

    @staticmethod
    def update_usability_feedback(
        feedback_id: UUID,
        feedback_text: Optional[str] = None,
        user_id: Optional[UUID] = None,
        db: Session = Depends(get_db)
    ) -> UsabilityFeedback:
        """
        Update an existing usability feedback entry.
        """
        feedback = db.query(UsabilityFeedback).filter(UsabilityFeedback.id == feedback_id).first()
        if not feedback:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Usability feedback with ID {feedback_id} not found."
            )
        if feedback_text is not None:
            feedback.feedback_text = feedback_text
        if user_id is not None:
            feedback.user_id = user_id
        db.commit()
        db.refresh(feedback)
        return feedback

    @staticmethod
    def delete_usability_feedback(
        feedback_id: UUID,
        db: Session = Depends(get_db)
    ) -> None:
        """
        Delete a usability feedback entry by its ID.
        """
        feedback = db.query(UsabilityFeedback).filter(UsabilityFeedback.id == feedback_id).first()
        if not feedback:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Usability feedback with ID {feedback_id} not found."
            )
        db.delete(feedback)
        db.commit()