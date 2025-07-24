from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel

from spacenote.core.app import App
from spacenote.core.user.models import SessionId
from spacenote.web.class_based_view import cbv
from spacenote.web.deps import get_app, get_session_id

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


@cbv(router)
class AuthApi:
    """API endpoints for authentication."""

    app: App = Depends(get_app)
    session_id: SessionId | None = Depends(get_session_id)

    @router.post("/auth/login")
    async def login(self, request: Request, login_data: LoginRequest) -> LoginResponse:
        """Authenticate user and create session."""
        user_agent = request.headers.get("user-agent")
        ip_address = request.client.host if request.client else None

        session_id = await self.app.login(login_data.username, login_data.password, user_agent, ip_address)
        if not session_id:
            raise HTTPException(status_code=401, detail="Invalid username or password")

        return LoginResponse(session_id=session_id, user_id=login_data.username)

    @router.post("/auth/change-password")
    async def change_password(self, data: ChangePasswordRequest) -> dict[str, str]:
        """Change password for current user."""
        if not self.session_id:
            raise HTTPException(status_code=401, detail="Not authenticated")

        try:
            await self.app.change_password(self.session_id, data.current_password, data.new_password)
        except ValueError as e:
            # Check if it's specifically about incorrect password
            error_msg = str(e)
            if "incorrect" in error_msg.lower() or "invalid" in error_msg.lower():
                raise HTTPException(status_code=401, detail="Current password is incorrect") from e
            raise HTTPException(status_code=400, detail=error_msg) from e
        else:
            return {"message": "Password changed successfully"}
