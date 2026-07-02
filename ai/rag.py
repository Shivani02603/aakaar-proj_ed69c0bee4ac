import os
from .embeddings import get_embedding
from ai.vector_store import VectorStore
import google.generativeai as genai

vector_store = VectorStore()

async def retrieve_context(query: str, top_k: int, session_id: str, user_id: str):
    query_embedding = get_embedding(query)
    results = vector_store.search(query_embedding, top_k=top_k)
    return results

async def answer_question(query: str, session_id: str, user_id: str) -> dict:
    context_chunks = await retrieve_context(query, top_k=5, session_id=session_id, user_id=user_id)
    if not context_chunks:
        return {'answer': "I don't know.", 'sources': []}

    context_text = "\n".join(chunk['text'] for chunk in context_chunks)
    sources = [{'filename': chunk['metadata']['source_filename'], 'location': chunk['metadata']['page_or_row']} for chunk in context_chunks]

    prompt = f"Answer the following question based on the context provided:\n\nContext:\n{context_text}\n\nQuestion: {query}\n\nAnswer:"
    api_key = os.getenv('GOOGLE_GEMINI_API_KEY')
    if not api_key:
        raise ValueError("Google Gemini API key not found in environment variables.")
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.0-flash')
    response = model.generate_content(prompt)
    answer = response.text

    return {'answer': answer, 'sources': sources}