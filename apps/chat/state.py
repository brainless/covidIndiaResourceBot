from datetime import datetime
from typing import Optional

import orjson as json

from utils.cache import redis


class ChatState(object):
    current_step: Optional[str]
    has_sent_current_step_message: bool
    looking_for: Optional[str]
    location: Optional[str]
    spo2_level: Optional[int]
    operator_has_replied: Optional[bool]
    tried_this_step: 0
    last_response_at: Optional[datetime]

    def __init__(self):
        self.current_step = None
        self.has_sent_current_step_message = False
        self.looking_for = None
        self.looking_for = None
        self.spo2_level = None
        self.operator_has_replied = False
        self.tried_this_step = 0
        self.last_response_at = None

    def dumps(self):
        return json.dumps(self, default=lambda o: o.__dict__)

    def loads(self, data: str):
        data = json.loads(data)
        for key, val in data.items():
            setattr(self, key, val)


async def get_chat_state(phone_number: str, cache: redis) -> ChatState:
    chat_state_cached = await cache.get(phone_number)
    chat_state = ChatState()

    if chat_state_cached is not None:
        chat_state.loads(chat_state_cached)

    return chat_state


async def set_chat_state(phone_number: str, chat_state: ChatState, cache: redis):
    await cache.set(phone_number, chat_state.dumps())