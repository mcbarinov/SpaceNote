from multiprocessing import AuthenticationError

from fastapi import APIRouter, Request
from pydantic import BaseModel

from spacenote.web.deps import AppDep, SessionIdDep

router = APIRouter()


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    session_id: str
    user_id: str


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


@router.post("/auth/login")
async def login(request: Request, login_data: LoginRequest, app: AppDep) -> LoginResponse:
    """Authenticate user and create session."""
    user_agent = request.headers.get("user-agent")
    ip_address = request.client.host if request.client else None

    session_id = await app.login(login_data.username, login_data.password, user_agent, ip_address)
    if not session_id:
        raise AuthenticationError("Invalid username or password")

    return LoginResponse(session_id=session_id, user_id=login_data.username)


@router.post("/auth/change-password")
async def change_password(data: ChangePasswordRequest, app: AppDep, session_id: SessionIdDep) -> dict[str, str]:
    """Change password for current user."""
    await app.change_password(session_id, data.current_password, data.new_password)
    return {"message": "Password changed successfully"}
