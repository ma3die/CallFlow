from fastapi import FastAPI
from src.core.fastapi_config import fastapi_
from onstartup import onstartup

app = FastAPI(**fastapi_.model_dump())
app.onstartup = onstartup
