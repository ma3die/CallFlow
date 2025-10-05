from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Callable
from fastapi import FastAPI
from pydantic_settings import BaseSettings
from loguru import logger

from src.core.settings import HOST, PORT, APP_PATH


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[Any, Any]:
    logger.info("Connect APP")
    await app.onstartup()
    yield
    logger.info("Disconnect APP")


class FastAPIAppSettings(BaseSettings):
    title: str = "CallFlow"
    version: str = "0.1.0"
    lifespan: Callable = lifespan


class UvicornFastAPISettings(BaseSettings):
    app: str = APP_PATH
    host: str = HOST
    port: int = PORT
    reload: bool = True


fastapi_ = FastAPIAppSettings()
uvicorn_ = UvicornFastAPISettings()
