from fastapi import APIRouter, Depends
from pydantic import BaseModel

from spacenote.core.app import App
from spacenote.core.user.models import SessionId
from spacenote.web.class_based_view import cbv
from spacenote.web.deps import get_app, get_session_id

router = APIRouter()


class CreateUserRequest(BaseModel):
    username: str
    password: str


@cbv(router)
class UsersApi:
    """API endpoints for user management (admin only)."""

    app: App = Depends(get_app)
    session_id: SessionId | None = Depends(get_session_id)

    @router.get("/users")
    async def get_users(self) -> list[dict[str, str]]:
        """Get all users (admin only)."""
        if not self.session_id:
            raise ValueError("Not authenticated")

        users = await self.app.get_users(self.session_id)
        return [{"id": user.id} for user in users]

    @router.post("/users")
    async def create_user(self, user_data: CreateUserRequest) -> dict[str, str]:
        """Create a new user (admin only)."""
        if not self.session_id:
            raise ValueError("Not authenticated")

        user = await self.app.create_user(self.session_id, user_data.username, user_data.password)
        return {"id": user.id}
