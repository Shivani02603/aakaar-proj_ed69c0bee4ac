from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime
from database.models import Document, ChatSession
from database.config import get_db

router = APIRouter(tags=["Reliability"])

# Pydantic schemas
class ReliabilityMetrics(BaseModel):
    uptime_percentage: float = Field(..., ge=0, le=100, description="Percentage of uptime during business hours")
    last_downtime: Optional[datetime] = Field(None, description="Timestamp of the last downtime event")
    downtime_duration_minutes: Optional[int] = Field(None, ge=0, description="Duration of the last downtime in minutes")

class ReliabilityMetricsResponse(BaseModel):
    id: UUID
    uptime_percentage: float
    last_downtime: Optional[datetime]
    downtime_duration_minutes: Optional[int]

class ReliabilityMetricsCreate(BaseModel):
    uptime_percentage: float = Field(..., ge=0, le=100, description="Percentage of uptime during business hours")
    last_downtime: Optional[datetime] = Field(None, description="Timestamp of the last downtime event")
    downtime_duration_minutes: Optional[int] = Field(None, ge=0, description="Duration of the last downtime in minutes")

class ReliabilityMetricsUpdate(BaseModel):
    uptime_percentage: Optional[float] = Field(None, ge=0, le=100, description="Percentage of uptime during business hours")
    last_downtime: Optional[datetime] = Field(None, description="Timestamp of the last downtime event")
    downtime_duration_minutes: Optional[int] = Field(None, ge=0, description="Duration of the last downtime in minutes")

# Routes
@router.get("/reliability/metrics", response_model=List[ReliabilityMetricsResponse])
def get_reliability_metrics(db: Session = Depends(get_db)):
    try:
        metrics = db.query(ChatSession).all()  # Replace ChatSession with the actual reliability metrics model
        return metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/reliability/metrics/{id}", response_model=ReliabilityMetricsResponse)
def get_reliability_metric(id: UUID, db: Session = Depends(get_db)):
    try:
        metric = db.query(ChatSession).filter(ChatSession.id == id).first()  # Replace ChatSession with the actual reliability metrics model
        if not metric:
            raise HTTPException(status_code=404, detail="Reliability metric not found")
        return metric
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/reliability/metrics", response_model=ReliabilityMetricsResponse, status_code=status.HTTP_201_CREATED)
def create_reliability_metric(metric: ReliabilityMetricsCreate, db: Session = Depends(get_db)):
    try:
        new_metric = ChatSession(**metric.dict())  # Replace ChatSession with the actual reliability metrics model
        db.add(new_metric)
        db.commit()
        db.refresh(new_metric)
        return new_metric
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/reliability/metrics/{id}", response_model=ReliabilityMetricsResponse)
def update_reliability_metric(id: UUID, metric: ReliabilityMetricsUpdate, db: Session = Depends(get_db)):
    try:
        existing_metric = db.query(ChatSession).filter(ChatSession.id == id).first()  # Replace ChatSession with the actual reliability metrics model
        if not existing_metric:
            raise HTTPException(status_code=404, detail="Reliability metric not found")
        for key, value in metric.dict(exclude_unset=True).items():
            setattr(existing_metric, key, value)
        db.commit()
        db.refresh(existing_metric)
        return existing_metric
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/reliability/metrics/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_reliability_metric(id: UUID, db: Session = Depends(get_db)):
    try:
        metric = db.query(ChatSession).filter(ChatSession.id == id).first()  # Replace ChatSession with the actual reliability metrics model
        if not metric:
            raise HTTPException(status_code=404, detail="Reliability metric not found")
        db.delete(metric)
        db.commit()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))