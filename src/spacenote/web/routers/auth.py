from typing import Annotated

from fastapi import APIRouter, Depends, Form, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel

from spacenote.core.app import App
from spacenote.core.user.models import SessionId
from spacenote.web.class_based_view import cbv
from spacenote.web.deps import get_app, get_render, get_session_id
from spacenote.web.render import Render
from spacenote.web.utils import redirect

router: APIRouter = APIRouter(prefix="")


class LoginForm(BaseModel):
    username: str
    password: str


@cbv(router)
class Auth:
    app: App = Depends(get_app)
    render: Render = Depends(get_render)
    session_id: SessionId | None = Depends(get_session_id)

    @router.get("/", response_model=None)
    async def index(self) -> RedirectResponse:
        return redirect("/login")

    @router.get("/login", response_model=None)
    async def login_page(self) -> HTMLResponse | RedirectResponse:
        if self.session_id:
            return redirect("/notes")

        return await self.render.html("login.j2")

    @router.post("/login", response_model=None)
    async def login(
        self, request: Request, response: Response, form: Annotated[LoginForm, Form()]
    ) -> HTMLResponse | RedirectResponse:
        user_agent = request.headers.get("user-agent")
        ip_address = request.client.host if request.client else None

        session_id = await self.app.login(form.username, form.password, user_agent, ip_address)
        if not session_id:
            return await self.render.html("login.j2", error="Invalid username or password")

        response = RedirectResponse(url="/notes", status_code=302)
        response.set_cookie(
            key="session_id",
            value=session_id,
            httponly=True,
            secure=False,  # Set to True in production with HTTPS
            samesite="lax",
            max_age=30 * 24 * 60 * 60,  # 30 days to match session duration
        )
        return response

    @router.get("/logout", response_model=None)
    @router.post("/logout", response_model=None)
    async def logout(self, request: Request) -> RedirectResponse:
        session_id = request.cookies.get("session_id")
        if session_id:
            await self.app.logout(SessionId(session_id))
        response = RedirectResponse(url="/login", status_code=302)
        response.delete_cookie(key="session_id")
        return response
