from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Oracle — lidos do .env
    ORACLE_USER: str
    ORACLE_APP_PASSWORD: str
    ORACLE_DSN: str          # formato host:porta/service_name
    ORACLE_POOL_MIN: int = 2
    ORACLE_POOL_MAX: int = 10

    # API
    API_ENV: str = "development"
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000


settings = Settings()
