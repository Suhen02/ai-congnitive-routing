
from typing import List

from app.config.settings import settings
from app.utils.embeddings import embed_text
from app.utils.logger import get_logger
from app.vectorstore.db import get_collection

logger = get_logger(__name__)


def route_post_to_bots(
    post_content: str,
    threshold: float = settings.SIMILARITY_THRESHOLD,
) -> List[str]:
 
   
    if not post_content or not post_content.strip():
        logger.warning("route_post_to_bots called with empty post content.")
        raise ValueError("post_content must be a non-empty string.")

    logger.info("Routing post (len=%d chars) | threshold=%.2f", len(post_content), threshold)

   
    try:
        post_embedding = embed_text(post_content, settings.EMBEDDING_MODEL)
    except RuntimeError as exc:
        logger.error("Failed to embed post: %s", exc)
        raise

   
    try:
        collection = get_collection()
        results = collection.query(
            query_embeddings=[post_embedding],
            n_results=collection.count(),
            include=["distances", "metadatas"],
        )
    except Exception as exc:
        logger.error("ChromaDB query failed: %s", exc)
        raise RuntimeError(f"Vector store query error: {exc}") from exc

   
    # ChromaDB with cosine space returns distances in [0, 2];
    # similarity = 1 - (distance / 2)  →  maps to [0, 1]
    ids: List[str] = results["ids"][0]
    distances: List[float] = results["distances"][0]

    matched: List[str] = []

    for bot_id, dist in zip(ids, distances):
        similarity = 1.0 - (dist / 2.0)
        logger.info(
            "  Persona %-20s | cosine_dist=%.4f | similarity=%.4f | match=%s",
            bot_id,
            dist,
            similarity,
            similarity >= threshold,
        )
        if similarity >= threshold:
            matched.append(bot_id)

    if matched:
        logger.info("Matched personas: %s", matched)
    else:
        logger.info("No personas exceeded the threshold of %.2f.", threshold)

    return matched
