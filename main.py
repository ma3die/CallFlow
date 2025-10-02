from src.core.fastapi_config import uvicorn_
import uvicorn

if __name__ == '__main__':
    uvicorn.run(**uvicorn_.model_dump())