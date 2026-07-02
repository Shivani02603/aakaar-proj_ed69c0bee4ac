import os
from typing import List
import openai

# Constants
EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIM = 1536

class EmbeddingClient:
    def __init__(self):
        self.api_key = None

    def _get_client(self):
        if not self.api_key:
            self.api_key = os.getenv("OPENAI_API_KEY")
            if not self.api_key:
                raise ValueError("OPENAI_API_KEY environment variable is not set.")
        return openai.Embedding(api_key=self.api_key)

    def embed_text(self, text: str) -> List[float]:
        client = self._get_client()
        response = client.create(input=[text], model=EMBEDDING_MODEL)
        return response["data"][0]["embedding"]

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        client = self._get_client()
        response = client.create(input=texts, model=EMBEDDING_MODEL)
        return [item["embedding"] for item in response["data"]]

# Module-level function
def get_embedding(texts: List[str]) -> List[List[float]]:
    client = EmbeddingClient()
    return client.embed_batch(texts)