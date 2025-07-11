from datetime import datetime

from pydantic import Field

from spacenote.core.db import MongoModel


class Session(MongoModel):
    id: str = Field(alias="_id")  # session token
    user_id: str
    created_at: datetime
    last_used: datetime
    expires_at: datetime
    user_agent: str | None = None
    ip_address: str | None = None
