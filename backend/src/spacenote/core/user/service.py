from typing import Any

import structlog
from pymongo.asynchronous.database import AsyncDatabase

from spacenote.core.core import Service
from spacenote.core.errors import NotFoundError, ValidationError
from spacenote.core.user.models import User
from spacenote.core.user.password import hash_password, validate_password_strength, verify_password

logger = structlog.get_logger(__name__)


class UserService(Service):
    """Service for managing users with in-memory caching."""

    def __init__(self, database: AsyncDatabase[dict[str, Any]]) -> None:
        super().__init__(database)
        self._collection = database.get_collection("users")
        self._users: dict[str, User] = {}

    def get_user(self, id: str) -> User:
        """Get user by ID from cache."""
        if id not in self._users:
            raise NotFoundError(f"User '{id}' not found")
        return self._users[id]

    def user_exists(self, id: str) -> bool:
        """Check if a user exists by ID."""
        return id in self._users

    def get_users(self) -> list[User]:
        """Get all users from cache."""
        return list(self._users.values())

    async def create_user(self, id: str, password: str) -> User:
        """Create a new user with hashed password."""
        log = logger.bind(user_id=id, action="create_user")

        if self.user_exists(id):
            log.warning("user_already_exists")
            raise ValidationError(f"User with ID '{id}' already exists")

        user_data = {"_id": id, "password_hash": hash_password(password)}
        await self._collection.insert_one(User.model_validate(user_data).to_dict())
        await self.update_cache(id)

        log.debug("user_created")
        return self.get_user(id)

    async def change_password(self, user_id: str, old_password: str, new_password: str) -> None:
        """Change password for a user after verifying old password."""
        validate_password_strength(new_password)
        user = self.get_user(user_id)

        if not verify_password(old_password, user.password_hash):
            raise ValidationError("Current password is incorrect")

        updated = {"password_hash": hash_password(new_password)}
        await self._collection.update_one({"_id": user_id}, {"$set": updated})
        await self.update_cache(user_id)

    async def ensure_admin_user_exists(self) -> None:
        if not self.user_exists("admin"):
            await self.create_user("admin", "admin")

    def verify_password(self, username: str, password: str) -> bool:
        """Verify user password."""
        log = logger.bind(username=username, action="verify_password")
        log.debug("password_verification_attempt")

        if not self.user_exists(username):
            log.warning("verification_failed", reason="user_not_found")
            return False

        try:
            user = self.get_user(username)
            if not verify_password(password, user.password_hash):
                log.warning("verification_failed", reason="invalid_password")
                return False
        except NotFoundError:
            log.warning("verification_failed", reason="user_not_found")
            return False
        else:
            log.debug("password_verified")
            return True

    async def update_cache(self, id: str | None = None) -> None:
        """Reload users cache from database."""
        if id is not None:  # update a specific user
            user = await self._collection.find_one({"_id": id})
            if user is None:
                del self._users[id]
            self._users[id] = User.model_validate(user)
        else:  # update all users
            users = await User.list_cursor(self._collection.find())
            self._users = {user.id: user for user in users}

    async def on_start(self) -> None:
        """Initialize service on application startup."""
        await self.update_cache()
        await self.ensure_admin_user_exists()
        logger.debug("user_service_started", user_count=len(self._users))
