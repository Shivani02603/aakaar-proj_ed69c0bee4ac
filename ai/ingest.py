import os
import tempfile
from typing import List
from fastapi import UploadFile
from pypdf import PdfReader
import tiktoken
from .embeddings import get_embedding

def chunk(text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> List[dict]:
    enc = tiktoken.get_encoding('cl100k_base')
    tokens = enc.encode(text)
    chunks = []
    start = 0
    n_tokens = len(tokens)
    while start < n_tokens:
        end = min(start + chunk_size, n_tokens)
        chunk_tokens = tokens[start:end]
        chunk_text = enc.decode(chunk_tokens)
        chunks.append(chunk_text)
        start += chunk_size - chunk_overlap
    return chunks

async def ingest_pdf(file: UploadFile, session_id: str, user_id: str):
    contents = await file.read()
    original_filename = file.filename or "uploaded_file.pdf"
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(original_filename)[1]) as tmp:
        tmp.write(contents)
        tmp.flush()
        file_path = tmp.name

    try:
        reader = PdfReader(file_path)
        all_chunks = []
        for page_index, page in enumerate(reader.pages):
            text = page.extract_text()
            if not text:
                continue
            page_chunks = chunk(text)
            for i, chunk_text in enumerate(page_chunks):
                metadata = {
                    'source_filename': original_filename,
                    'chunk_index': i,
                    'total_chunks': len(page_chunks),
                    'page_or_row': f"Page {page_index + 1}"
                }
                embedding = get_embedding(chunk_text)
                all_chunks.append({'text': chunk_text, 'embedding': embedding, 'metadata': metadata})
        return all_chunks
    finally:
        os.remove(file_path)