from typing import Annotated

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel

from spacenote.core.field.models import FieldOption, FieldType, SpaceField
from spacenote.core.filter.parsing import parse_raw_filter_data
from spacenote.web.class_based_view import cbv
from spacenote.web.deps import SessionView
from spacenote.web.utils import redirect

router: APIRouter = APIRouter(prefix="/spaces")


@cbv(router)
class SpacePageRouter(SessionView):
    @router.get("/")
    async def index(self) -> HTMLResponse:
        spaces = await self.app.get_spaces_by_member(self.session_id)
        return await self.render.html("spaces/index.j2", spaces=spaces)

    @router.get("/create")
    async def create(self) -> HTMLResponse:
        return await self.render.html("spaces/create.j2")

    @router.get("/{space_id}/fields")
    async def fields(self, space_id: str) -> HTMLResponse:
        space = await self.app.get_space(self.session_id, space_id)
        return await self.render.html("spaces/fields/index.j2", space=space)

    @router.get("/{space_id}/fields/create")
    async def create_field(self, space_id: str) -> HTMLResponse:
        space = await self.app.get_space(self.session_id, space_id)
        return await self.render.html("spaces/fields/create.j2", space=space)

    @router.get("/{space_id}/filters")
    async def filters(self, space_id: str) -> HTMLResponse:
        space = await self.app.get_space(self.session_id, space_id)
        return await self.render.html("spaces/filters/index.j2", space=space)

    @router.get("/{space_id}/filters/create")
    async def create_filter(self, space_id: str) -> HTMLResponse:
        space = await self.app.get_space(self.session_id, space_id)
        return await self.render.html("spaces/filters/create.j2", space=space)

    @router.get("/{space_id}/members")
    async def members(self, space_id: str) -> HTMLResponse:
        space = await self.app.get_space(self.session_id, space_id)
        return await self.render.html("spaces/members/index.j2", space=space)

    @router.get("/{space_id}/telegram")
    async def telegram_settings(self, space_id: str) -> HTMLResponse:
        space = await self.app.get_space(self.session_id, space_id)
        bots = await self.app.get_telegram_bots(self.session_id)
        return await self.render.html("spaces/telegram/index.j2", space=space, bots=bots)


@cbv(router)
class SpaceActionRouter(SessionView):
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
        space = await self.app.create_space(self.session_id, form.id, form.name)
        self.render.flash(f"Space '{space.id}' created successfully")
        return redirect("/spaces")

    @router.post("/{space_id}/fields/create")
    async def create_field(self, space_id: str, form: Annotated[CreateFieldForm, Form()]) -> RedirectResponse:
        await self.app.add_field(self.session_id, space_id, form.to_model())
        return redirect(f"/spaces/{space_id}/fields")

    @router.post("/{space_id}/fields/update-list")
    async def update_list_fields(self, space_id: str, value: Annotated[str, Form()]) -> RedirectResponse:
        field_names = [name.strip() for name in value.strip().split(",") if name.strip()]
        await self.app.update_list_fields(self.session_id, space_id, field_names)
        self.render.flash("List fields updated successfully")
        return redirect(f"/spaces/{space_id}/fields")

    @router.post("/{space_id}/fields/update-hidden-create")
    async def update_hidden_create_fields(self, space_id: str, value: Annotated[str, Form()]) -> RedirectResponse:
        field_names = [name.strip() for name in value.strip().split(",") if name.strip()]
        await self.app.update_hidden_create_fields(self.session_id, space_id, field_names)
        self.render.flash("Hidden create fields updated successfully")
        return redirect(f"/spaces/{space_id}/fields")

    @router.post("/{space_id}/filters/create")
    async def create_filter(self, space_id: str, request: Request) -> RedirectResponse:
        form_data = dict(await request.form())
        filter_model = parse_raw_filter_data(form_data)
        await self.app.add_filter(self.session_id, space_id, filter_model)
        self.render.flash(f"Filter '{filter_model.title}' created successfully")
        return redirect(f"/spaces/{space_id}/filters")

    @router.post("/{space_id}/filters/{filter_id}/delete")
    async def delete_filter(self, space_id: str, filter_id: str) -> RedirectResponse:
        await self.app.delete_filter(self.session_id, space_id, filter_id)
        self.render.flash(f"Filter '{filter_id}' deleted successfully")
        return redirect(f"/spaces/{space_id}/filters")

    @router.post("/{space_id}/members/update")
    async def update_members(self, space_id: str, members: Annotated[str, Form()]) -> RedirectResponse:
        # Parse comma-separated usernames
        member_list = [username.strip() for username in members.split(",") if username.strip()]
        await self.app.update_space_members(self.session_id, space_id, member_list)
        self.render.flash("Members updated successfully")
        return redirect(f"/spaces/{space_id}/members")

    @router.post("/{space_id}/telegram")
    async def update_telegram_config(self, space_id: str, request: Request) -> RedirectResponse:
        form_data = dict(await request.form())
        # Convert form data to string dict
        telegram_config = {k: str(v) for k, v in form_data.items()}
        await self.app.update_space_telegram_config(self.session_id, space_id, telegram_config)
        self.render.flash("Telegram configuration updated successfully")
        return redirect(f"/spaces/{space_id}/telegram")
