import logging

from sentence_transformers import SentenceTransformer

logger = logging.getLogger("voice-chef.embedding-service")


class Embedder:
    """Thin wrapper around sentence-transformers.

    Loaded once at startup. The vector dimension is determined by the model
    and exposed so qdrant collections can be sized to match.
    """

    def __init__(self, model_name: str) -> None:
        logger.info("loading embedding model: %s", model_name)
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)
        self.dim = int(self.model.get_embedding_dimension())
        logger.info("embedding model loaded: %s, dim=%s", model_name, self.dim)

    def embed(self, text: str) -> list[float]:
        return self.model.encode(text, convert_to_numpy=True).tolist()

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        return self.model.encode(texts, convert_to_numpy=True).tolist()
