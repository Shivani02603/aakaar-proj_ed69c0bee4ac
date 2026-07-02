import uuid
from datetime import datetime
from database.models import Document, DocumentChunk, ChatSession, ChatMessage, SessionLocal

def seed_data():
    session = SessionLocal()
    try:
        # Seed Documents
        document1 = Document(
            id=uuid.uuid4(),
            filename="example1.pdf",
            file_type="pdf",
            file_size=1024,
            uploaded_at=datetime.now(),
            status="processed",
            storage_path="/storage/documents/example1.pdf"
        )
        document2 = Document(
            id=uuid.uuid4(),
            filename="example2.txt",
            file_type="txt",
            file_size=512,
            uploaded_at=datetime.now(),
            status="processed",
            storage_path="/storage/documents/example2.txt"
        )
        document3 = Document(
            id=uuid.uuid4(),
            filename="example3.docx",
            file_type="docx",
            file_size=2048,
            uploaded_at=datetime.now(),
            status="uploaded",
            storage_path="/storage/documents/example3.docx"
        )
        session.add_all([document1, document2, document3])
        session.commit()

        # Seed DocumentChunks
        chunk1 = DocumentChunk(
            id=uuid.uuid4(),
            document_id=document1.id,
            chunk_index=0,
            content="This is the first chunk of example1.pdf.",
            metadata={"page": 1},
            embedding=[0.1] * 1536
        )
        chunk2 = DocumentChunk(
            id=uuid.uuid4(),
            document_id=document1.id,
            chunk_index=1,
            content="This is the second chunk of example1.pdf.",
            metadata={"page": 2},
            embedding=[0.2] * 1536
        )
        chunk3 = DocumentChunk(
            id=uuid.uuid4(),
            document_id=document2.id,
            chunk_index=0,
            content="This is the first chunk of example2.txt.",
            metadata={"line": 1},
            embedding=[0.3] * 1536
        )
        session.add_all([chunk1, chunk2, chunk3])
        session.commit()

        # Seed ChatSessions
        session1 = ChatSession(
            id=uuid.uuid4(),
            session_id=str(uuid.uuid4()),
            created_at=datetime.now(),
            last_activity=datetime.now()
        )
        session2 = ChatSession(
            id=uuid.uuid4(),
            session_id=str(uuid.uuid4()),
            created_at=datetime.now(),
            last_activity=datetime.now()
        )
        session3 = ChatSession(
            id=uuid.uuid4(),
            session_id=str(uuid.uuid4()),
            created_at=datetime.now(),
            last_activity=datetime.now()
        )
        session.add_all([session1, session2, session3])
        session.commit()

        # Seed ChatMessages
        message1 = ChatMessage(
            id=uuid.uuid4(),
            session_id=session1.session_id,
            query="What is the capital of France?",
            answer="The capital of France is Paris.",
            citations=None,
            created_at=datetime.now()
        )
        message2 = ChatMessage(
            id=uuid.uuid4(),
            session_id=session1.session_id,
            query="What is the population of Paris?",
            answer="The population of Paris is approximately 2.1 million.",
            citations=None,
            created_at=datetime.now()
        )
        message3 = ChatMessage(
            id=uuid.uuid4(),
            session_id=session2.session_id,
            query="What is the tallest mountain in the world?",
            answer="The tallest mountain in the world is Mount Everest.",
            citations=None,
            created_at=datetime.now()
        )
        session.add_all([message1, message2, message3])
        session.commit()

    except Exception as e:
        session.rollback()
        print(f"Error seeding data: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    seed_data()