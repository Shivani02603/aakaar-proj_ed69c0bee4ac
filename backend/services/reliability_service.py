from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import HTTPException, status, Depends
from database.models import ReliabilityMetric
from database.config import get_db

class ReliabilityService:
    @staticmethod
    def create_reliability_metric(
        uptime_percentage: float,
        timestamp: str,
        db: Session = Depends(get_db)
    ) -> ReliabilityMetric:
        if uptime_percentage < 0 or uptime_percentage > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uptime percentage must be between 0 and 100."
            )
        
        reliability_metric = ReliabilityMetric(
            uptime_percentage=uptime_percentage,
            timestamp=timestamp
        )
        db.add(reliability_metric)
        db.commit()
        db.refresh(reliability_metric)
        return reliability_metric

    @staticmethod
    def get_reliability_metric_by_id(
        metric_id: UUID,
        db: Session = Depends(get_db)
    ) -> ReliabilityMetric:
        reliability_metric = db.query(ReliabilityMetric).filter(ReliabilityMetric.id == metric_id).first()
        if not reliability_metric:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Reliability metric with ID {metric_id} not found."
            )
        return reliability_metric

    @staticmethod
    def list_all_reliability_metrics(
        db: Session = Depends(get_db)
    ) -> List[ReliabilityMetric]:
        return db.query(ReliabilityMetric).all()

    @staticmethod
    def update_reliability_metric(
        metric_id: UUID,
        db: Session = Depends(get_db),
        uptime_percentage: Optional[float] = None,
        timestamp: Optional[str] = None
    ) -> ReliabilityMetric:
        reliability_metric = db.query(ReliabilityMetric).filter(ReliabilityMetric.id == metric_id).first()
        if not reliability_metric:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Reliability metric with ID {metric_id} not found."
            )
        
        if uptime_percentage is not None:
            if uptime_percentage < 0 or uptime_percentage > 100:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Uptime percentage must be between 0 and 100."
                )
            reliability_metric.uptime_percentage = uptime_percentage
        
        if timestamp is not None:
            reliability_metric.timestamp = timestamp
        
        db.commit()
        db.refresh(reliability_metric)
        return reliability_metric

    @staticmethod
    def delete_reliability_metric(
        metric_id: UUID,
        db: Session = Depends(get_db)
    ) -> None:
        reliability_metric = db.query(ReliabilityMetric).filter(ReliabilityMetric.id == metric_id).first()
        if not reliability_metric:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Reliability metric with ID {metric_id} not found."
            )
        
        db.delete(reliability_metric)
        db.commit()