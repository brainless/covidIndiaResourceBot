from datetime import datetime
import orjson as json
from typing import Optional

from utils.cache import redis


class ChatState(object):
    current_step: Optional[str]
    has_sent_current_step_message: bool
    looking_for: Optional[str]
    location: Optional[str]
    spo2_level: Optional[int]
    operator_has_replied: Optional[bool]
    last_response_at: Optional[datetime]

    def __init__(self):
        self.current_step = None
        self.has_sent_current_step_message = False
        self.looking_for = None
        self.looking_for = None
        self.spo2_level = None
        self.operator_has_replied = False
        self.last_response_at = None

    def dumps(self):
        return json.dumps(self, default=lambda o: o.__dict__)

    @classmethod
    def loads(cls, data: str):
        data = json.loads(data)
        chat_state = ChatState()
        for key, val in data.items():
            setattr(chat_state, key, val)

        return chat_state


async def get_chat_state(phone_number: str, cache: redis) -> ChatState:
    chat_state = await cache.get(phone_number)

    if chat_state is None:
        chat_state = ChatState()
    else:
        chat_state = ChatState.loads(chat_state)

    return chat_state


async def set_chat_state(phone_number: str, chat_state: ChatState, cache: redis):
    await cache.set(phone_number, chat_state.dumps())


def get_next_message(
        current_message: str,
        config: dict,
        chat_state: ChatState
):
    response_message = None
    if chat_state.operator_has_replied:
        return response_message, chat_state

    if chat_state.current_step is None:
        chat_state.current_step = config["start_at"]

    step_config = config["steps"][chat_state.current_step]

    if not chat_state.has_sent_current_step_message:
        response_message = step_config["message"]

    for message_parser in step_config["allowed_parsers"]:
        try:
            message_parser(current_message, **step_config["variables"])
        except ValueError:
            pass

    return response_message, chat_state
