from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from src.app.api.routes import router

app = FastAPI(title="My Python AI App")

app.mount("/static", StaticFiles(directory="src/app/static"), name="static")
app.include_router(router)
