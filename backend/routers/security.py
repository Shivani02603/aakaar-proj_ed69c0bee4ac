from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional
from sqlalchemy.orm import Session
from uuid import UUID
from database.models import Document
from database.config import get_db
from cryptography.fernet import Fernet
import os

# Initialize encryption key
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", Fernet.generate_key())
cipher_suite = Fernet(ENCRYPTION_KEY)

# APIRouter for security
router = APIRouter(tags=["Security"])

# Pydantic schemas
class DocumentBase(BaseModel):
    id: UUID
    filename: str
    file_type: str
    file_size: int
    uploaded_at: str
    status: str
    storage_path: str

class EncryptedDocumentResponse(BaseModel):
    id: UUID
    filename: str
    file_type: str
    file_size: int
    uploaded_at: str
    status: str
    encrypted_storage_path: str

class EncryptionRequest(BaseModel):
    document_id: UUID

class DecryptionRequest(BaseModel):
    encrypted_storage_path: str

# Utility functions for encryption and decryption
def encrypt_data(data: str) -> str:
    return cipher_suite.encrypt(data.encode()).decode()

def decrypt_data(data: str) -> str:
    return cipher_suite.decrypt(data.encode()).decode()

# Route to list all documents with encrypted storage paths
@router.get("/security/documents", response_model=List[EncryptedDocumentResponse])
def list_encrypted_documents(db: Session = Depends(get_db)):
    documents = db.query(Document).all()
    if not documents:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No documents found."
        )
    encrypted_documents = [
        EncryptedDocumentResponse(
            id=doc.id,
            filename=doc.filename,
            file_type=doc.file_type,
            file_size=doc.file_size,
            uploaded_at=doc.uploaded_at.isoformat(),
            status=doc.status,
            encrypted_storage_path=encrypt_data(doc.storage_path)
        )
        for doc in documents
    ]
    return encrypted_documents

# Route to encrypt a document's storage path
@router.post("/security/encrypt", response_model=EncryptedDocumentResponse)
def encrypt_document(request: EncryptionRequest, db: Session = Depends(get_db)):
    document = db.query(Document).filter(Document.id == request.document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found."
        )
    encrypted_storage_path = encrypt_data(document.storage_path)
    return EncryptedDocumentResponse(
        id=document.id,
        filename=document.filename,
        file_type=document.file_type,
        file_size=document.file_size,
        uploaded_at=document.uploaded_at.isoformat(),
        status=document.status,
        encrypted_storage_path=encrypted_storage_path
    )

# Route to decrypt a document's storage path
@router.post("/security/decrypt", response_model=DocumentBase)
def decrypt_document(request: DecryptionRequest, db: Session = Depends(get_db)):
    try:
        decrypted_storage_path = decrypt_data(request.encrypted_storage_path)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid encrypted storage path."
        )
    document = db.query(Document).filter(Document.storage_path == decrypted_storage_path).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found."
        )
    return DocumentBase(
        id=document.id,
        filename=document.filename,
        file_type=document.file_type,
        file_size=document.file_size,
        uploaded_at=document.uploaded_at.isoformat(),
        status=document.status,
        storage_path=document.storage_path
    )