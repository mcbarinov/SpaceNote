from fastapi import Request
from fastapi.responses import HTMLResponse
from jinja2 import ChoiceLoader, Environment, PackageLoader

from spacenote.core.field.models import FieldType
from spacenote.core.user.models import User


def init_jinja() -> Environment:
    loader = ChoiceLoader([PackageLoader("spacenote.web")])
    env = Environment(loader=loader, autoescape=True, enable_async=True)

    env.filters |= {}  # Custom filters can be added here
    env.globals |= {"field_types": list(FieldType)}  # Custom globals can be added here
    return env


class Render:
    def __init__(self, env: Environment, request: Request, current_user: User | None = None) -> None:
        self.env = env
        self.request = request
        self.current_user = current_user

    async def html(self, template_name: str, **kwargs: object) -> HTMLResponse:
        flash_messages = self.request.session.pop("flash_messages") if "flash_messages" in self.request.session else []

        # Automatically inject current_user into template context
        context = {"flash_messages": flash_messages, "current_user": self.current_user} | kwargs

        html_content = await self.env.get_template(template_name).render_async(context)
        return HTMLResponse(content=html_content, status_code=200)

    def flash(self, message: str, is_error: bool = False) -> None:
        if "flash_messages" not in self.request.session:
            self.request.session["flash_messages"] = []
        self.request.session["flash_messages"].append({"message": message, "error": is_error})
