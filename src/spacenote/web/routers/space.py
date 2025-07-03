from typing import Annotated

from fastapi import APIRouter, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel

from spacenote.core.field.models import FieldType, SpaceField
from spacenote.web.class_based_view import cbv
from spacenote.web.deps import View
from spacenote.web.utils import redirect

router: APIRouter = APIRouter(prefix="/spaces")


@cbv(router)
class SpacePageRouter(View):
    @router.get("/")
    async def index(self) -> HTMLResponse:
        spaces = self.app.get_spaces_by_member(self.current_user)
        return await self.render.html("spaces/index.j2", spaces=spaces)

    @router.get("/create")
    async def create(self) -> HTMLResponse:
        return await self.render.html("spaces/create.j2")

    @router.get("/{space_id}/fields")
    async def fields(self, space_id: str) -> HTMLResponse:
        space = self.app.get_space(self.current_user, space_id)
        return await self.render.html("spaces/fields/index.j2", space=space)

    @router.get("/{space_id}/fields/create")
    async def create_field(self, space_id: str) -> HTMLResponse:
        space = self.app.get_space(self.current_user, space_id)
        return await self.render.html("spaces/fields/create.j2", space=space)


@cbv(router)
class AdminActionRouter(View):
    class CreateSpaceForm(BaseModel):
        id: str
        name: str

    class CreateFieldForm(BaseModel):
        name: str
        type: FieldType
        required: bool = False
        values: str
        default: str

        def to_model(self) -> SpaceField:
            return SpaceField(
                name=self.name.strip(),
                type=self.type,
                required=self.required,
                values=self.values.strip() if self.values else None,
                default=self.default.strip() if self.default else None,
            )

    @router.post("/create")
    async def create_space(self, form: Annotated[CreateSpaceForm, Form()]) -> RedirectResponse:
        space = await self.app.create_space(self.current_user, form.id, form.name)
        self.render.flash(f"Space '{space.id}' created successfully")
        return redirect("/spaces")

    @router.post("/{space_id}/fields/create")
    async def create_field(self, space_id: str, form: Annotated[CreateFieldForm, Form()]) -> RedirectResponse:
        await self.app.add_field(self.current_user, space_id, form.to_model())
        return redirect(f"/spaces/{space_id}/fields")
