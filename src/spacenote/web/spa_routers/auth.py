from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel

from spacenote.core.app import App
from spacenote.core.user.models import SessionId
from spacenote.web.class_based_view import cbv
from spacenote.web.deps import get_app, get_session_id

router: APIRouter = APIRouter(prefix="/new-api")


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    session_id: str
    user: dict[str, str]


class LogoutResponse(BaseModel):
    success: bool


class MeResponse(BaseModel):
    user: dict[str, str] | None


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


class ChangePasswordResponse(BaseModel):
    success: bool


@cbv(router)
class SpaAuth:
    """Auth endpoints that don't require authentication (or handle optional authentication)."""

    app: App = Depends(get_app)
    session_id: SessionId | None = Depends(get_session_id)

    @router.post("/auth/login")
    async def login(self, request: Request, response: Response, login_data: LoginRequest) -> LoginResponse:
        user_agent = request.headers.get("user-agent")
        ip_address = request.client.host if request.client else None

        session_id = await self.app.login(login_data.username, login_data.password, user_agent, ip_address)
        if not session_id:
            raise HTTPException(status_code=401, detail="Invalid username or password")

        user = await self.app.get_user_by_session(SessionId(session_id))
        if not user:
            raise HTTPException(status_code=401, detail="Authentication failed")

        response.set_cookie(
            key="session_id",
            value=session_id,
            httponly=True,
            secure=False,  # Set to True in production with HTTPS
            samesite="lax",
            max_age=30 * 24 * 60 * 60,  # 30 days to match session duration
        )

        return LoginResponse(session_id=session_id, user={"id": user.id})

    @router.post("/auth/logout")
    async def logout(self, response: Response) -> LogoutResponse:
        if self.session_id:
            await self.app.logout(self.session_id)
        response.delete_cookie(key="session_id")
        return LogoutResponse(success=True)

    @router.get("/auth/me")
    async def me(self) -> MeResponse:
        if not self.session_id:
            return MeResponse(user=None)

        user = await self.app.get_user_by_session(self.session_id)
        if not user:
            return MeResponse(user=None)

        return MeResponse(user={"id": user.id})

    @router.post("/auth/change-password")
    async def change_password(self, request_data: ChangePasswordRequest) -> ChangePasswordResponse:
        if not self.session_id:
            raise HTTPException(status_code=401, detail="Not authenticated")

        try:
            await self.app.change_password(self.session_id, request_data.current_password, request_data.new_password)
            return ChangePasswordResponse(success=True)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e)) from e
        except Exception as e:
            raise HTTPException(status_code=500, detail="Failed to change password") from e
