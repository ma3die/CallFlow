from pydantic_settings import BaseSettings

from src.core.settings import REDIS_HOST, REDIS_PORT


class RedisSettings(BaseSettings):
    REDIS_HOST: str = REDIS_HOST
    REDIS_PORT: int = REDIS_PORT

    def get_backend(self) -> str:
        return f'redis://{self.REDIS_HOST}:{self.REDIS_PORT}/1'

    def get_broker(self) -> str:
        return f'redis://{self.REDIS_HOST}:{self.REDIS_PORT}/2'


redis_ = RedisSettings()
