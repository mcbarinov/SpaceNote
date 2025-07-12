from typing import NewType

from pydantic import Field

from spacenote.core.db import MongoModel

SessionId = NewType("SessionId", str)


class User(MongoModel):
    id: str = Field(alias="_id")  # username
    password_hash: str  # password_hash
