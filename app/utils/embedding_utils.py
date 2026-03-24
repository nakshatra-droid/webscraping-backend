from sentence_transformers import SentenceTransformer
from app.config.config import Config

embedding_model = None


class EmbeddingUtils:
    """Utility class for managing the embedding model instance globally."""
    @staticmethod
    def preload_model():
        global embedding_model
        embedding_model = SentenceTransformer(Config.EMBEDDING_MODEL_NAME)

    @staticmethod
    def get_embedding_model() -> "SentenceTransformer":
        return embedding_model
