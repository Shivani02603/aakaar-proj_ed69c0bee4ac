import os
import uuid
from sqlalchemy import (
    create_engine,
    Column,
    String,
    Integer,
    Text,
    JSON,
    ForeignKey,
    TIMESTAMP,
    Boolean,
    Index,
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from sqlalchemy.dialects.postgresql import UUID
from pgvector.sqlalchemy import Vector

DATABASE_URL_ENV = "DATABASE_URL"
Base = declarative_base()

# Database engine and session setup
engine = create_engine(
    os.environ[DATABASE_URL_ENV],
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
)
SessionLocal = sessionmaker(bind=engine)

# Document model
class Document(Base):
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    filename = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False)
    file_size = Column(Integer, nullable=False)
    uploaded_at = Column(TIMESTAMP, nullable=False)
    status = Column(String(50), nullable=False)
    storage_path = Column(String(500), nullable=False)

    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Document(id={self.id}, filename={self.filename}, file_type={self.file_type}, file_size={self.file_size}, uploaded_at={self.uploaded_at}, status={self.status}, storage_path={self.storage_path})>"

# DocumentChunk model
class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    meta_data = Column("metadata", JSON, nullable=True)
    embedding = Column(Vector(1536), nullable=False)

    document = relationship("Document", back_populates="chunks")

    def __repr__(self):
        return f"<DocumentChunk(id={self.id}, document_id={self.document_id}, chunk_index={self.chunk_index}, content={self.content}, metadata={self.metadata})>"

    __table_args__ = (
        Index("ix_document_chunks_embedding", embedding, postgresql_using="hnsw"),
    )

# ChatSession model
class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    session_id = Column(String(255), unique=True, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False)
    last_activity = Column(TIMESTAMP, nullable=False)

    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ChatSession(id={self.id}, session_id={self.session_id}, created_at={self.created_at}, last_activity={self.last_activity})>"

# ChatMessage model
class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    session_id = Column(String(255), ForeignKey("chat_sessions.session_id", ondelete="CASCADE"), nullable=False)
    query = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    citations = Column(JSON, nullable=True)
    created_at = Column(TIMESTAMP, nullable=False)

    session = relationship("ChatSession", back_populates="messages")

    def __repr__(self):
        return f"<ChatMessage(id={self.id}, session_id={self.session_id}, query={self.query}, answer={self.answer}, citations={self.citations}, created_at={self.created_at})>"