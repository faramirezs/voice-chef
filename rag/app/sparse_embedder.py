import logging
from typing import Iterable

from fastembed import SparseTextEmbedding
from qdrant_client.http.models import SparseVector

logger = logging.getLogger("voice-chef.rag")


class SparseEmbedder:
    """BM25 sparse-vector generator via fastembed.

    Used in tandem with the dense Embedder for hybrid retrieval — the
    dense vectors carry semantic meaning, the sparse BM25 vectors carry
    keyword/term-frequency signal. Qdrant fuses results via Reciprocal
    Rank Fusion at query time.
    """

    def __init__(
        self,
        model_name: str = "Qdrant/bm25",
        cache_dir: str | None = "/root/.cache/huggingface/fastembed",
    ) -> None:
        logger.info("loading sparse embedding model: %s", model_name)
        self.model_name = model_name
        kwargs: dict[str, str] = {}
        if cache_dir:
            kwargs["cache_dir"] = cache_dir
        self.model = SparseTextEmbedding(model_name=model_name, **kwargs)
        logger.info("sparse embedding model loaded: %s", model_name)

    def embed(self, text: str) -> SparseVector:
        return _to_sparse_vector(next(iter(self.model.embed([text]))))

    def embed_batch(self, texts: list[str]) -> list[SparseVector]:
        return [_to_sparse_vector(r) for r in self.model.embed(texts)]


def _to_sparse_vector(raw) -> SparseVector:  # type: ignore[no-untyped-def]
    return SparseVector(
        indices=raw.indices.tolist(),
        values=raw.values.tolist(),
    )
