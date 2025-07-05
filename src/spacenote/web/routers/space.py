from typing import Annotated

from fastapi import APIRouter, Form
from fastapi.responses import HTMLResponse, PlainTextResponse, RedirectResponse
from pydantic import BaseModel

from spacenote.core.field.models import FieldOption, FieldType, SpaceField
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

    @router.get("/{space_id}/export")
    async def export(self, space_id: str) -> PlainTextResponse:
        # Export space data as TOML (includes access verification)
        toml_content = self.app.export_space_as_toml(self.current_user, space_id)

        return PlainTextResponse(content=toml_content, media_type="text/plain")


@cbv(router)
class AdminActionRouter(View):
    class CreateSpaceForm(BaseModel):
        id: str
        name: str

    class CreateFieldForm(BaseModel):
        name: str
        type: FieldType
        required: bool = False
        values: str = ""
        default: str = ""

        def to_model(self) -> SpaceField:
            # Prepare options based on field type
            options = {}

            # For CHOICE type parse values as a list (one per line)
            if self.type == FieldType.CHOICE and self.values:
                values_list = [v.strip() for v in self.values.split("\n") if v.strip()]
                if values_list:
                    options[FieldOption.VALUES] = values_list

            # Handle default value based on field type
            default_value: str | bool | list[str] | None = None
            if self.default:
                if self.type == FieldType.BOOLEAN:
                    default_value = self.default.lower() in ("true", "1", "yes")
                elif self.type == FieldType.TAGS:
                    default_value = [v.strip() for v in self.default.split("\n") if v.strip()]
                else:
                    default_value = self.default.strip()

            return SpaceField(
                name=self.name.strip(),
                type=self.type,
                required=self.required,
                options=options,
                default=default_value,
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

    @router.post("/{space_id}/fields/update-list")
    async def update_list_fields(self, space_id: str, value: Annotated[str, Form()]) -> RedirectResponse:
        field_names = [name.strip() for name in value.strip().split(",") if name.strip()]
        await self.app.update_list_fields(self.current_user, space_id, field_names)
        self.render.flash("List fields updated successfully")
        return redirect(f"/spaces/{space_id}/fields")
