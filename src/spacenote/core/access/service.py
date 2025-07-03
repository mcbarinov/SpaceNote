from spacenote.core.core import Service
from spacenote.core.errors import AccessDeniedError


class AccessService(Service):
    def ensure_space_member(self, space_id: str, member: str) -> None:
        space = self.core.services.space.get_space(space_id)
        if member not in space.members:
            raise AccessDeniedError(f"Access denied: user '{member}' is not a member of space '{space_id}'")
