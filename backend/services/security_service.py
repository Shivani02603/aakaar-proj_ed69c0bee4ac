from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import HTTPException, status, Depends
from database.models import Document
from database.config import get_db
from cryptography.fernet import Fernet
import os

class SecurityService:
    # Generate encryption key (should be securely stored in a real application)
    ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", Fernet.generate_key())
    cipher_suite = Fernet(ENCRYPTION_KEY)

    @staticmethod
    def encrypt_data(data: str) -> str:
        """Encrypts data using Fernet symmetric encryption."""
        try:
            encrypted_data = SecurityService.cipher_suite.encrypt(data.encode())
            return encrypted_data.decode()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error encrypting data: {str(e)}"
            )

    @staticmethod
    def decrypt_data(encrypted_data: str) -> str:
        """Decrypts data using Fernet symmetric encryption."""
        try:
            decrypted_data = SecurityService.cipher_suite.decrypt(encrypted_data.encode())
            return decrypted_data.decode()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error decrypting data: {str(e)}"
            )

    @staticmethod
    def create_document(db: Session, filename: str, file_type: str, file_size: int, storage_path: str) -> Document:
        """Creates a new document with encrypted storage path."""
        try:
            encrypted_storage_path = SecurityService.encrypt_data(storage_path)
            new_document = Document(
                filename=filename,
                file_type=file_type,
                file_size=file_size,
                uploaded_at=None,  # Assume this is set automatically by the DB
                status="uploaded",
                storage_path=encrypted_storage_path
            )
            db.add(new_document)
            db.commit()
            db.refresh(new_document)
            return new_document
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error creating document: {str(e)}"
            )

    @staticmethod
    def get_document_by_id(db: Session, document_id: UUID) -> Document:
        """Fetches a document by its ID and decrypts the storage path."""
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        try:
            document.storage_path = SecurityService.decrypt_data(document.storage_path)
            return document
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error decrypting document storage path: {str(e)}"
            )

    @staticmethod
    def list_all_documents(db: Session) -> List[Document]:
        """Lists all documents with decrypted storage paths."""
        documents = db.query(Document).all()
        try:
            for document in documents:
                document.storage_path = SecurityService.decrypt_data(document.storage_path)
            return documents
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error decrypting document storage paths: {str(e)}"
            )

    @staticmethod
    def update_document(db: Session, document_id: UUID, filename: Optional[str] = None, file_type: Optional[str] = None, file_size: Optional[int] = None, storage_path: Optional[str] = None) -> Document:
        """Updates a document's details and re-encrypts the storage path if updated."""
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        try:
            if filename:
                document.filename = filename
            if file_type:
                document.file_type = file_type
            if file_size:
                document.file_size = file_size
            if storage_path:
                document.storage_path = SecurityService.encrypt_data(storage_path)
            db.commit()
            db.refresh(document)
            return document
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error updating document: {str(e)}"
            )

    @staticmethod
    def delete_document(db: Session, document_id: UUID) -> None:
        """Deletes a document by its ID."""
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        try:
            db.delete(document)
            db.commit()
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error deleting document: {str(e)}"
            )