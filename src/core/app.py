from fastapi import FastAPI

from src.core.fastapi_config import fastapi_
from src.callflow.router import router as router_callflow
from onstartup import onstartup

app = FastAPI(**fastapi_.model_dump())
app.onstartup = onstartup
app.include_router(router_callflow)
