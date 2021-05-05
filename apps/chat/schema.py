from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel


class CreatedByEnum(str, Enum):
    operator = "operator"
    user = "user"


class ChatIn(BaseModel):
    phone: str
    message: str
    created_by: CreatedByEnum
    created_at: datetime


class ChatOut(BaseModel):
    phone: str
    message: str
    tags: Optional[List[str]]
    team: Optional[str]
    close_chat: Optional[bool]
