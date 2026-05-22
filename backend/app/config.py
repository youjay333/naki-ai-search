from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[1]


class Settings(BaseSettings):
    app_name: str = "naki-ai-search"
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    tavily_api_key: str | None = None
    tavily_max_results: int = Field(default=8, ge=3, le=20)
    tavily_search_depth: str = "advanced"
    tavily_include_raw_content: str | bool = "markdown"

    deepseek_api_key: str | None = None
    deepseek_base_url: str = "https://api.deepseek.com"
    deepseek_model: str = "deepseek-v4-pro"
    deepseek_temperature: float = Field(default=0.2, ge=0, le=2)
    deepseek_max_tokens: int = Field(default=2200, ge=256, le=12000)
    deepseek_reasoning_effort: str = "high"
    deepseek_thinking: str = "enabled"

    request_timeout_seconds: int = Field(default=60, ge=10, le=180)

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
