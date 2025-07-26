from spacenote.core.core import Service
from spacenote.core.errors import AccessDeniedError, AuthenticationError
from spacenote.core.user.models import SessionId, User


class AccessService(Service):
    async def get_authenticated_user(self, session_id: SessionId) -> User:
        """Get authenticated user from session ID."""
        user = await self.core.services.session.get_user_by_session(session_id)
        if user is None:
            raise AuthenticationError("Invalid or expired session")
        return user

    async def ensure_space_member(self, session_id: SessionId, space_id: str) -> None:
        """Ensure the authenticated user is a member of the specified space."""
        user = await self.get_authenticated_user(session_id)
        space = self.core.services.space.get_space(space_id)
        if user.id not in space.members:
            raise AccessDeniedError(f"Access denied: user '{user.id}' is not a member of space '{space_id}'")

    async def ensure_admin(self, session_id: SessionId) -> None:
        """Ensure the authenticated user is admin, raise AccessDeniedError if not."""
        user = await self.get_authenticated_user(session_id)
        if user.id != "admin":
            raise AccessDeniedError("Admin privileges required")
