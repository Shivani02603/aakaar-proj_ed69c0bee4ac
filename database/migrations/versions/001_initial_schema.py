"""Initial schema

Revision ID: 001_initial_schema
Revises: 
Create Date: 2023-10-11 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
import uuid
from pgvector.sqlalchemy import Vector

# revision identifiers, used by Alembic.
revision = '001_initial_schema'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Enable pgvector extension
    op.execute("CREATE EXTENSION IF NOT EXISTS vector;")

    # Create documents table
    op.create_table(
        'documents',
        sa.Column('id', sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False),
        sa.Column('filename', sa.String(255), nullable=False),
        sa.Column('file_type', sa.String(50), nullable=False),
        sa.Column('file_size', sa.Integer, nullable=False),
        sa.Column('uploaded_at', sa.TIMESTAMP, nullable=False),
        sa.Column('status', sa.String(50), nullable=False),
        sa.Column('storage_path', sa.String(500), nullable=False),
    )

    # Create document_chunks table
    op.create_table(
        'document_chunks',
        sa.Column('id', sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False),
        sa.Column('document_id', sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey('documents.id', ondelete='CASCADE'), nullable=False),
        sa.Column('chunk_index', sa.Integer, nullable=False),
        sa.Column('content', sa.Text, nullable=False),
        sa.Column('metadata', sa.JSON, nullable=True),
        sa.Column('embedding', Vector(1536), nullable=False),
    )
    op.create_index('ix_document_chunks_embedding', 'document_chunks', ['embedding'], postgresql_using='hnsw')

    # Create chat_sessions table
    op.create_table(
        'chat_sessions',
        sa.Column('id', sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False),
        sa.Column('session_id', sa.String(255), unique=True, nullable=False),
        sa.Column('created_at', sa.TIMESTAMP, nullable=False),
        sa.Column('last_activity', sa.TIMESTAMP, nullable=False),
    )

    # Create chat_messages table
    op.create_table(
        'chat_messages',
        sa.Column('id', sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False),
        sa.Column('session_id', sa.String(255), sa.ForeignKey('chat_sessions.session_id', ondelete='CASCADE'), nullable=False),
        sa.Column('query', sa.Text, nullable=False),
        sa.Column('answer', sa.Text, nullable=False),
        sa.Column('citations', sa.JSON, nullable=True),
        sa.Column('created_at', sa.TIMESTAMP, nullable=False),
    )


def downgrade() -> None:
    # Drop chat_messages table
    op.drop_table('chat_messages')

    # Drop chat_sessions table
    op.drop_table('chat_sessions')

    # Drop document_chunks table
    op.drop_index('ix_document_chunks_embedding', table_name='document_chunks')
    op.drop_table('document_chunks')

    # Drop documents table
    op.drop_table('documents')

    # Disable pgvector extension
    op.execute("DROP EXTENSION IF EXISTS vector;")