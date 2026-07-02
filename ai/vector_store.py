import os
from typing import List, Dict
from sqlalchemy.orm import Session
from database.models import DocumentChunk
from database.config import SessionLocal

class VectorStore:
    def __init__(self):
        self.pgvector_url = None

    def _get_pgvector_url(self):
        if not self.pgvector_url:
            self.pgvector_url = os.getenv("PGVECTOR_URL")
            if not self.pgvector_url:
                raise ValueError("PGVECTOR_URL environment variable is not set.")
        return self.pgvector_url

    def upsert(self, id: str, vector: List[float], doc_metadata: Dict):
        with SessionLocal() as session:
            existing_chunk = session.query(DocumentChunk).filter_by(id=id).first()
            if existing_chunk:
                existing_chunk.embedding = vector
                existing_chunk.doc_metadata = doc_metadata
            else:
                new_chunk = DocumentChunk(id=id, embedding=vector, doc_metadata=doc_metadata)
                session.add(new_chunk)
            session.commit()

    def search(self, query_embedding: List[float], top_k: int) -> List[Dict]:
        with SessionLocal() as session:
            results = (
                session.query(DocumentChunk)
                .order_by(DocumentChunk.embedding.cosine_distance(query_embedding))
                .limit(top_k)
                .all()
            )
            return [
                {"id": result.id, "content": result.content, "doc_metadata": result.doc_metadata}
                for result in results
            ]

# Singleton instance
vector_store = VectorStore()