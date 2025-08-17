from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):  # type: ignore
    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")
    openai_api_base: str = Field(default="https://api.openai.com/v1", alias="OPENAI_API_BASE")
    embeddings_model: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2", alias="EMBEDDINGS_MODEL"
    )
    llm_provider: str = Field(default="openai", alias="LLM_PROVIDER")
    llm_model: str = Field(default="gpt-4o-mini", alias="LLM_MODEL")

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
