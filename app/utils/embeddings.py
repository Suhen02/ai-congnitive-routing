from functools import lru_cache
from typing import List

from app.utils.logger import get_logger

logger = get_logger(__name__)


@lru_cache(maxsize=1)
def _load_model(model_name: str):
    
    from sentence_transformers import SentenceTransformer  

    logger.info("Loading embedding model: %s", model_name)
    return SentenceTransformer(model_name)


def embed_text(text: str, model_name: str) -> List[float]:

    if not text or not text.strip():
        raise ValueError("embed_text received empty or whitespace-only input.")

    try:
        model = _load_model(model_name)
        vector = model.encode(text, normalize_embeddings=True)
        logger.debug("Embedded %d chars → vector dim=%d", len(text), len(vector))
        return vector.tolist()
    except Exception as exc:
        logger.error("Embedding generation failed: %s", exc)
        raise RuntimeError(f"Failed to generate embedding: {exc}") from exc


def embed_batch(texts: List[str], model_name: str) -> List[List[float]]:
  
    if not texts:
        raise ValueError("embed_batch received an empty list.")

    try:
        model = _load_model(model_name)
        vectors = model.encode(texts, normalize_embeddings=True)
        logger.debug("Batch embedded %d texts", len(texts))
        return [v.tolist() for v in vectors]
    except Exception as exc:
        logger.error("Batch embedding failed: %s", exc)
        raise RuntimeError(f"Failed to generate batch embeddings: {exc}") from exc
