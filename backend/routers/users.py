from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from uuid import UUID
from database.config import get_db
from backend.routers.auth import get_current_user

router = APIRouter(tags=["Users"])

class User(BaseModel):
    id: UUID
    username: str
    email: EmailStr
    created_at: str

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    username: str | None = None
    email: EmailStr | None = None

@router.get("/")
async def list_users(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    users = db.query(User).all()
    return [{"id": user.id, "username": user.username, "email": user.email, "created_at": user.created_at} for user in users]

@router.get("/{user_id}")
async def get_user(user_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return {"id": user.id, "username": user.username, "email": user.email, "created_at": user.created_at}

@router.put("/{user_id}")
async def update_user(user_id: UUID, user_data: UserUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if user_data.username:
        user.username = user_data.username
    if user_data.email:
        user.email = user_data.email
    db.commit()
    db.refresh(user)
    return {"id": user.id, "username": user.username, "email": user.email, "created_at": user.created_at}

@router.delete("/{user_id}")
async def delete_user(user_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    db.delete(user)
    db.commit()
    return {"detail": "User deleted successfully"}