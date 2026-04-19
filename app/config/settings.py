
import os
from pathlib import Path
from dotenv import load_dotenv


load_dotenv()


class Settings:
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    MODEL_NAME: str = os.getenv("MODEL_NAME", "llama3-8b-8192")

    SIMILARITY_THRESHOLD: float = float(os.getenv("SIMILARITY_THRESHOLD", "0.30"))
    EMBEDDING_MODEL: str = os.getenv(
        "EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"
    )

    CHROMA_COLLECTION_NAME: str = os.getenv(
        "CHROMA_COLLECTION_NAME", "persona_embeddings"
    )

    
    MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "3"))

    MAX_POST_CHARS: int = 280

    def validate(self) -> None:
        
        if not self.GROQ_API_KEY:
            raise ValueError(
                "GROQ_API_KEY is not set. Please add it to your .env file."
            )


settings = Settings()
