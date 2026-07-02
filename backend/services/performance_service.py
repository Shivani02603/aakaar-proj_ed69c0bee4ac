from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import HTTPException, status, Depends
from database.models import PerformanceMetric
from database.config import get_db

class PerformanceService:
    @staticmethod
    def create_performance_metric(
        metric_name: str,
        value: float,
        db: Session = Depends(get_db),
        description: Optional[str] = None
    ) -> PerformanceMetric:
        performance_metric = PerformanceMetric(
            metric_name=metric_name,
            value=value,
            description=description
        )
        db.add(performance_metric)
        db.commit()
        db.refresh(performance_metric)
        return performance_metric

    @staticmethod
    def get_performance_metric_by_id(
        metric_id: UUID,
        db: Session = Depends(get_db)
    ) -> PerformanceMetric:
        performance_metric = db.query(PerformanceMetric).filter(PerformanceMetric.id == metric_id).first()
        if not performance_metric:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Performance metric with ID {metric_id} not found."
            )
        return performance_metric

    @staticmethod
    def list_all_performance_metrics(
        db: Session = Depends(get_db)
    ) -> List[PerformanceMetric]:
        return db.query(PerformanceMetric).all()

    @staticmethod
    def update_performance_metric(
        metric_id: UUID,
        db: Session = Depends(get_db),
        metric_name: Optional[str] = None,
        value: Optional[float] = None,
        description: Optional[str] = None
    ) -> PerformanceMetric:
        performance_metric = db.query(PerformanceMetric).filter(PerformanceMetric.id == metric_id).first()
        if not performance_metric:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Performance metric with ID {metric_id} not found."
            )
        if metric_name is not None:
            performance_metric.metric_name = metric_name
        if value is not None:
            performance_metric.value = value
        if description is not None:
            performance_metric.description = description
        db.commit()
        db.refresh(performance_metric)
        return performance_metric

    @staticmethod
    def delete_performance_metric(
        metric_id: UUID,
        db: Session = Depends(get_db)
    ) -> None:
        performance_metric = db.query(PerformanceMetric).filter(PerformanceMetric.id == metric_id).first()
        if not performance_metric:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Performance metric with ID {metric_id} not found."
            )
        db.delete(performance_metric)
        db.commit()