from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "sqlite:///./pr_racing.db"
    anthropic_api_key: str = ""
    line_channel_secret: str = ""
    line_channel_access_token: str = ""
    secret_key: str = "change-me-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 8

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
