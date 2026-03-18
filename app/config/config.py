import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Configuration class to load environment variables."""

    # database url
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    if DATABASE_URL is None:
        raise ValueError("DATABASE_URL environment variable is not set")

    # api settings
    API: str = "/api"
    V1_API: str = "/v1"
    UI_API: str = "/ui"

    # auth settings
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    if SECRET_KEY is None:
        raise ValueError("SECRET_KEY environment variable is not set")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", default=30)
    )
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(
        os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", default=7)
    )

    # embedding settings
    EMBEDDING_MODEL_NAME: str = "sentence-transformers/multi-qa-mpnet-base-dot-v1"
    EMBEDDING_BATCH_SIZE: int = int(os.getenv("EMBEDDING_BATCH_SIZE", default=64))
