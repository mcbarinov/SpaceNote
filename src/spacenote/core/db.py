from typing import Any, Self

from pydantic import BaseModel, ConfigDict
from pymongo.asynchronous.cursor import AsyncCursor


class MongoModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True)

    def to_dict(self) -> dict[str, Any]:
        """Convert the model to a dictionary."""
        return self.model_dump(by_alias=True)

    @classmethod
    async def list_cursor(cls, cursor: AsyncCursor[dict[str, Any]]) -> list[Self]:
        """Iterate over an AsyncCursor and return a list of model instances."""
        return [cls.model_validate(item) async for item in cursor]
