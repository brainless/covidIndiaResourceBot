import orjson as json
from typing import Mapping
from fastapi import APIRouter, Depends, status

from utils.cache import redis, get_redis
from .schema import ChatIn, ChatOut
from .flow import get_next_message


chat_router = APIRouter()


@chat_router.post("", response_model=ChatOut)
async def handle_incoming_chat(
        data: ChatIn,
        cache: redis = Depends(get_redis)
) -> Mapping:
    chat_state = await cache.get(data.phone)

    if chat_state is None:
        chat_state = {}
    else:
        chat_state = json.loads(chat_state)

    return {
        "phone": data.phone,
        "message": get_next_message(**chat_state),
        "team": None,
        "tags": []
    }
