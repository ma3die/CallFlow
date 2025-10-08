from pydantic_settings import BaseSettings

from src.core.settings import POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_HOST, POSTGRES_PORT


class PostgresSettings(BaseSettings):
    POSTGRES_DB: str = POSTGRES_DB
    POSTGRES_USER: str = POSTGRES_USER
    POSTGRES_PASSWORD: str = POSTGRES_PASSWORD
    POSTGRES_HOST: str = POSTGRES_HOST
    POSTGRES_PORT: int = POSTGRES_PORT

    def get_db_url(self):
        return (f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
                f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}")


postgres_settings = PostgresSettings()
