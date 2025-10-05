from pydantic_settings import BaseSettings
from src.core.redis_config import redis_


class CelerySettings(BaseSettings):
    main: str = 'worker'
    broker: str = redis_.get_broker()
    backend: str = redis_.get_backend()


celery_ = CelerySettings()
