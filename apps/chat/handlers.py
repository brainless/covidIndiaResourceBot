from typing import Mapping
from fastapi import APIRouter, Depends, BackgroundTasks

from utils.cache import redis, get_redis
from .schema import ChatIn, ChatOut
from .flow import get_next_message
from .state import get_chat_state, set_chat_state
from .tpf_flow import flow_config


chat_router = APIRouter()


@chat_router.post("", response_model=ChatOut)
async def handle_incoming_chat(
        data: ChatIn,
        bg_tasks: BackgroundTasks,
        cache: redis = Depends(get_redis)
) -> Mapping:
    chat_state = await get_chat_state(
        phone_number=data.phone,
        cache=cache
    )
    next_message, updated_chat_state = get_next_message(
        config=flow_config,
        current_message=data.message,
        created_by=data.created_by,
        chat_state=chat_state
    )
    bg_tasks.add_task(set_chat_state, data.phone, updated_chat_state, cache)

    return {
        "phone": data.phone,
        "message": next_message,
        "team": None,
        "tags": [],
        "close_chat": False
    }
