from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import Column, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import Session, relationship
from sqlalchemy.ext.declarative import declarative_base
from uuid import uuid4
from datetime import datetime
from database.config import get_db
from backend.routers.auth import get_current_user

Base = declarative_base()

class ChatSession(Base):
    __tablename__ = "chat_sessions"
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    title = Column(String, default="New Chat")
    created_at = Column(DateTime, default=datetime.utcnow)

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    session_id = Column(String, ForeignKey("chat_sessions.id"), nullable=False)
    role = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class SessionCreate(BaseModel):
    title: str = "New Chat"

class SessionResponse(BaseModel):
    id: str
    user_id: str
    title: str
    created_at: datetime

class MessageCreate(BaseModel):
    role: str
    content: str

class MessageResponse(BaseModel):
    id: str
    session_id: str
    role: str
    content: str
    created_at: datetime

router = APIRouter(tags=["Sessions"])

@router.get("/")
async def list_sessions(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    sessions = db.query(ChatSession).filter(ChatSession.user_id == current_user.id).order_by(ChatSession.created_at.desc()).all()
    return [{"id": session.id, "user_id": session.user_id, "title": session.title, "created_at": session.created_at} for session in sessions]

@router.post("/", response_model=SessionResponse)
async def create_session(session_data: SessionCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    new_session = ChatSession(user_id=current_user.id, title=session_data.title)
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    return {"id": new_session.id, "user_id": new_session.user_id, "title": new_session.title, "created_at": new_session.created_at}

@router.delete("/{session_id}")
async def delete_session(session_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    session = db.query(ChatSession).filter(ChatSession.id == session_id, ChatSession.user_id == current_user.id).first()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found or not owned by user")
    db.delete(session)
    db.commit()
    return {"detail": "Session deleted successfully"}

@router.get("/{session_id}/messages")
async def list_messages(session_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    session = db.query(ChatSession).filter(ChatSession.id == session_id, ChatSession.user_id == current_user.id).first()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found or not owned by user")
    messages = db.query(ChatMessage).filter(ChatMessage.session_id == session_id).order_by(ChatMessage.created_at.asc()).all()
    return [{"id": message.id, "session_id": message.session_id, "role": message.role, "content": message.content, "created_at": message.created_at} for message in messages]

@router.post("/{session_id}/messages", response_model=MessageResponse)
async def append_message(session_id: str, message_data: MessageCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    session = db.query(ChatSession).filter(ChatSession.id == session_id, ChatSession.user_id == current_user.id).first()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found or not owned by user")
    new_message = ChatMessage(session_id=session_id, role=message_data.role, content=message_data.content)
    db.add(new_message)
    db.commit()
    db.refresh(new_message)
    return {"id": new_message.id, "session_id": new_message.session_id, "role": new_message.role, "content": new_message.content, "created_at": new_message.created_at}