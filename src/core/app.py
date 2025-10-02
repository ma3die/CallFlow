from fastapi import FastAPI
from src.core.fastapi_config import fastapi_

app = FastAPI(**fastapi_.model_dump())
