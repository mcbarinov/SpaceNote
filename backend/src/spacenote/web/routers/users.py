from fastapi import APIRouter
from pydantic import BaseModel

from spacenote.web.deps import AppDep, SessionIdDep

router = APIRouter()


class CreateUserRequest(BaseModel):
    username: str
    password: str


@router.get("/users")
async def get_users(app: AppDep, session_id: SessionIdDep) -> list[dict[str, str]]:
    """Get all users (admin only)."""
    users = await app.get_users(session_id)
    return [{"id": user.id} for user in users]


@router.post("/users")
async def create_user(user_data: CreateUserRequest, app: AppDep, session_id: SessionIdDep) -> dict[str, str]:
    """Create a new user (admin only)."""
    user = await app.create_user(session_id, user_data.username, user_data.password)
    return {"id": user.id}
