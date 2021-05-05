from fastapi import FastAPI

from utils.cache import get_redis
# from utils.sentry import sentry_init
from utils.config import settings
from apps.chat.handlers import chat_router


origins = [
    "http://localhost:3000"
]

app = FastAPI(root_path=settings.root_path)


@app.on_event("startup")
async def startup():
    await get_redis()
    # sentry_init()


@app.get("/")
async def api_home():
    return {"status": "ok"}


app.include_router(
    chat_router,
    prefix="/chat"
)
