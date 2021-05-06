from typing import Mapping
from datetime import datetime
from fastapi import APIRouter, Depends, BackgroundTasks, status

from utils.cache import redis, get_redis
from .schema import ChatIn, ChatOut, ChatReset
from .flow import get_next_message
from .state import get_chat_state_and_variables, set_chat_state, delete_chat_state
from .tpf_flow import flow_config


chat_router = APIRouter()


@chat_router.delete("", status_code=status.HTTP_200_OK)
async def handle_incoming_chat(
        data: ChatReset,
        cache: redis = Depends(get_redis)
) -> Mapping:
    await delete_chat_state(
        phone_number=data.phone,
        cache=cache
    )

    return {
        "status": "deleted"
    }


@chat_router.post("")
async def handle_incoming_chat(
        data: ChatIn,
        bg_tasks: BackgroundTasks,
        cache: redis = Depends(get_redis)
) -> Mapping:
    chat_state, chat_variables = await get_chat_state_and_variables(
        phone_number=data.phone,
        cache=cache,
        flow_config=flow_config
    )

    next_message, updated_chat_state = get_next_message(
        flow_config=flow_config,
        created_by=data.created_by,
        current_message=data.message,
        chat_state=chat_state,
        chat_variables=chat_variables
    )
    updated_chat_state.last_response_at = datetime.utcnow()
    bg_tasks.add_task(set_chat_state, data.phone, updated_chat_state, cache)

    return {
        "phone": data.phone,
        "message": next_message,
        "close_chat": False,
        **chat_variables.to_dict()
    }
