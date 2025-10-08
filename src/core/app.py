from typing import Callable
from fastapi import FastAPI

from src.core.fastapi_config import fastapi_
from src.api.routers import ROUTERS
from onstartup import onstartup


def includer(func: Callable, array: list) -> None:
    for i in array:
        func(i)


app = FastAPI(**fastapi_.model_dump())
app.onstartup = onstartup
includer(app.include_router, ROUTERS)
