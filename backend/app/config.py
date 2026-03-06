import os
from dotenv import load_dotenv

# Load .env from the backend directory
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))


class Settings:
    """Application settings loaded from environment variables."""

    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///./local.db",
    )

    JWT_SECRET: str = os.getenv(
        "JWT_SECRET",
        "ai-assessment-platform-secret-key-change-in-production",
    )

    SENTRY_DSN: str = os.getenv("SENTRY_DSN", "")

    REDIS_URL: str = os.getenv("REDIS_URL", "")

    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    CORS_ORIGINS: list = [
        origin.strip()
        for origin in os.getenv(
            "CORS_ORIGINS",
            "http://localhost:5173,http://127.0.0.1:5173",
        ).split(",")
        if origin.strip()
    ] or ["*"]

    # Detect SQLite for engine configuration differences
    @property
    def is_sqlite(self) -> bool:
        return self.DATABASE_URL.startswith("sqlite")


settings = Settings()
