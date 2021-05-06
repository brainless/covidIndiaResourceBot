from datetime import datetime
from typing import Optional

import orjson as json

from utils.cache import redis


class Cacheable(object):
    def to_dict(self):
        return self.__dict__

    def from_dict(self, data: dict):
        for key, val in data.items():
            setattr(self, key, val)


class ChatState(Cacheable):
    current_step: Optional[str]
    has_sent_current_step_message: bool
    has_operator_replied: Optional[bool]
    tried_this_step: 0
    last_response_at: Optional[datetime]

    def __init__(self):
        self.current_step = None
        self.has_sent_current_step_message = False
        self.has_operator_replied = False
        self.tried_this_step = 0
        self.last_response_at = None

    def dumps(self):
        return json.dumps(self, default=lambda o: o.__dict__)

    def loads(self, data: str):
        data = json.loads(data)
        for key, val in data.items():
            if key != "variables":
                setattr(self, key, val)


async def get_chat_state_and_variables(
        phone_number: str,
        cache: redis,
        flow_config: dict
) -> [ChatState, Cacheable]:
    chat_state_cached = await cache.get(phone_number)

    chat_state = ChatState()
    if "chat_variables_class" in flow_config:
        chat_variables = flow_config["chat_variables_class"]()
    else:
        chat_variables = Cacheable()

    if chat_state_cached is not None:
        chat_state_dict = json.loads(chat_state_cached)
        chat_state.loads(chat_state_cached)

        if "variables" in chat_state_dict:
            chat_variables.load(chat_state_dict["variables"])

    return chat_state, chat_variables


async def set_chat_state(phone_number: str, chat_state: ChatState, cache: redis):
    await cache.set(phone_number, chat_state.dumps())


async def delete_chat_state(phone_number: str, cache: redis):
    await cache.delete(phone_number)
