

from typing import Optional

import chromadb
from chromadb.api.models.Collection import Collection

from app.config.settings import settings
from app.personas.personas import ALL_PERSONAS
from app.utils.embeddings import embed_batch
from app.utils.logger import get_logger

logger = get_logger(__name__)


_client: Optional[chromadb.Client] = None
_collection: Optional[Collection] = None


def get_collection() -> Collection:

    global _client, _collection

    if _collection is not None:
        return _collection

    try:
        logger.info("Initialising ChromaDB in-memory client.")
        _client = chromadb.Client()  # ephemeral / in-memory

        _collection = _client.get_or_create_collection(
            name=settings.CHROMA_COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )

        # Populate only if the collection is empty
        if _collection.count() == 0:
            _populate_collection(_collection)

        logger.info(
            "ChromaDB collection '%s' ready with %d documents.",
            settings.CHROMA_COLLECTION_NAME,
            _collection.count(),
        )
        return _collection

    except Exception as exc:
        logger.error("Failed to initialise ChromaDB: %s", exc)
        raise RuntimeError(f"ChromaDB initialisation error: {exc}") from exc


def _populate_collection(collection: Collection) -> None:
    
    logger.info("Populating ChromaDB with %d persona embeddings.", len(ALL_PERSONAS))

    profiles = [p.full_profile() for p in ALL_PERSONAS]
    ids = [p.id for p in ALL_PERSONAS]

    embeddings = embed_batch(profiles, settings.EMBEDDING_MODEL)

    collection.upsert(
        ids=ids,
        embeddings=embeddings,
        documents=profiles,
        metadatas=[{"name": p.name} for p in ALL_PERSONAS],
    )

    logger.info("Persona embeddings stored successfully.")
