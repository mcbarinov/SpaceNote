from fastapi import APIRouter, Depends, HTTPException
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
            raise HTTPException(status_code=401, detail="Not authenticated")

        try:
            users = await self.app.get_users(self.session_id)
            return [{"id": user.id} for user in users]
        except PermissionError as e:
            raise HTTPException(status_code=403, detail="Admin access required") from e

    @router.post("/users")
    async def create_user(self, user_data: CreateUserRequest) -> dict[str, str]:
        """Create a new user (admin only)."""
        if not self.session_id:
            raise HTTPException(status_code=401, detail="Not authenticated")

        try:
            user = await self.app.create_user(self.session_id, user_data.username, user_data.password)
        except PermissionError as e:
            raise HTTPException(status_code=403, detail="Admin access required") from e
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e)) from e
        else:
            return {"id": user.id}
