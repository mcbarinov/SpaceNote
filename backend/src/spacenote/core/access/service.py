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

    def ensure_space_member(self, space_id: str, member: str) -> None:
        space = self.core.services.space.get_space(space_id)
        if member not in space.members:
            raise AccessDeniedError(f"Access denied: user '{member}' is not a member of space '{space_id}'")

    def ensure_admin(self, user_id: str) -> None:
        """Ensure the user is admin, raise AccessDeniedError if not."""
        if user_id != "admin":
            raise AccessDeniedError("Admin privileges required")
