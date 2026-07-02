from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import HTTPException, status, Depends
from database.models import ScalabilityMetric
from database.config import get_db

class ScalabilityService:
    @staticmethod
    def create_scalability_metric(
        metric_name: str,
        metric_value: float,
        db: Session = Depends(get_db),
        description: Optional[str] = None
    ) -> ScalabilityMetric:
        scalability_metric = ScalabilityMetric(
            metric_name=metric_name,
            metric_value=metric_value,
            description=description
        )
        db.add(scalability_metric)
        db.commit()
        db.refresh(scalability_metric)
        return scalability_metric

    @staticmethod
    def get_scalability_metric_by_id(
        metric_id: UUID,
        db: Session = Depends(get_db)
    ) -> ScalabilityMetric:
        scalability_metric = db.query(ScalabilityMetric).filter(ScalabilityMetric.id == metric_id).first()
        if not scalability_metric:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Scalability metric with ID {metric_id} not found."
            )
        return scalability_metric

    @staticmethod
    def list_all_scalability_metrics(
        db: Session = Depends(get_db)
    ) -> List[ScalabilityMetric]:
        return db.query(ScalabilityMetric).all()

    @staticmethod
    def update_scalability_metric(
        metric_id: UUID,
        db: Session = Depends(get_db),
        metric_name: Optional[str] = None,
        metric_value: Optional[float] = None,
        description: Optional[str] = None
    ) -> ScalabilityMetric:
        scalability_metric = db.query(ScalabilityMetric).filter(ScalabilityMetric.id == metric_id).first()
        if not scalability_metric:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Scalability metric with ID {metric_id} not found."
            )
        if metric_name is not None:
            scalability_metric.metric_name = metric_name
        if metric_value is not None:
            scalability_metric.metric_value = metric_value
        if description is not None:
            scalability_metric.description = description
        db.commit()
        db.refresh(scalability_metric)
        return scalability_metric

    @staticmethod
    def delete_scalability_metric(
        metric_id: UUID,
        db: Session = Depends(get_db)
    ) -> None:
        scalability_metric = db.query(ScalabilityMetric).filter(ScalabilityMetric.id == metric_id).first()
        if not scalability_metric:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Scalability metric with ID {metric_id} not found."
            )
        db.delete(scalability_metric)
        db.commit()