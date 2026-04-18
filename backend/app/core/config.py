from pathlib import Path
from functools import lru_cache

from pydantic import AliasChoices
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


ROOT_ENV_FILE = Path(__file__).resolve().parents[3] / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(ROOT_ENV_FILE),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "AI Engineering Assessment Platform"
    environment: str = Field(default="development", alias="ENVIRONMENT")
    debug: bool = Field(default=False, alias="DEBUG")

    api_prefix: str = Field(default="/api", alias="API_PREFIX")
    frontend_url: str = Field(default="http://localhost:5173", alias="FRONTEND_URL")
    cors_origins: list[str] = Field(
        default_factory=lambda: ["http://localhost:5173", "http://127.0.0.1:5173"],
        alias="CORS_ORIGINS",
    )

    database_url: str = Field(alias="DATABASE_URL")
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")

    jwt_secret_key: str = Field(
        validation_alias=AliasChoices("SECRET_KEY", "JWT_SECRET_KEY"),
    )
    jwt_algorithm: str = Field(
        validation_alias=AliasChoices("ALGORITHM", "JWT_ALGORITHM"),
    )
    jwt_access_token_minutes: int = Field(
        validation_alias=AliasChoices(
            "ACCESS_TOKEN_EXPIRE_MINUTES",
            "JWT_ACCESS_TOKEN_MINUTES",
        ),
    )

    request_rate_limit_per_minute: int = Field(
        default=120,
        alias="REQUEST_RATE_LIMIT_PER_MINUTE",
    )
    evaluation_rate_limit_per_minute: int = Field(
        default=20,
        alias="EVALUATION_RATE_LIMIT_PER_MINUTE",
    )

    assessment_timeout_minutes: int = Field(default=60, alias="ASSESSMENT_TIMEOUT_MINUTES")
    default_sequence_mode: str = Field(default="fixed", alias="DEFAULT_SEQUENCE_MODE")
    simulation_seed: int = Field(default=11, alias="SIMULATION_SEED")

    log_level: str = Field(default="INFO", alias="LOG_LEVEL")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
