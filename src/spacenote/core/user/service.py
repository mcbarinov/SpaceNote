import secrets
from typing import Any

from pymongo.asynchronous.database import AsyncDatabase

from spacenote.core.core import Service
from spacenote.core.errors import NotFoundError
from spacenote.core.user.models import User
from spacenote.core.user.password import hash_password, validate_password_strength, verify_password


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

    def get_user_by_session(self, session_id: str) -> User | None:
        """Get user by session ID from cache."""
        for user in self._users.values():
            if user.session_id == session_id:
                return user
        return None

    def user_exists(self, id: str) -> bool:
        """Check if a user exists by ID."""
        return id in self._users

    def get_users(self) -> list[User]:
        """Get all users from cache."""
        return list(self._users.values())

    async def create_user(self, id: str, password: str) -> User:
        """Create a new user with hashed password."""
        if self.user_exists(id):
            raise ValueError(f"User with ID '{id}' already exists")
        user_data = {"_id": id, "password_hash": hash_password(password), "session_id": None}
        await self._collection.insert_one(User.model_validate(user_data).to_dict())
        await self.update_cache(id)
        return self.get_user(id)

    async def change_password(self, user_id: str, old_password: str, new_password: str) -> None:
        """Change password for a user after verifying old password."""
        validate_password_strength(new_password)
        user = self.get_user(user_id)

        if not verify_password(old_password, user.password_hash):
            raise ValueError("Current password is incorrect")

        updated = {"password_hash": hash_password(new_password), "session_id": None}
        await self._collection.update_one({"_id": user_id}, {"$set": updated})
        await self.update_cache(user_id)

    async def ensure_admin_user_exists(self) -> None:
        if not self.user_exists("admin"):
            await self.create_user("admin", "admin")

    async def login(self, username: str, password: str) -> str | None:
        """Authenticate user and return session ID."""
        if not self.user_exists(username):
            return None
        user = self.get_user(username)
        if not verify_password(password, user.password_hash):
            return None

        session_id = secrets.token_urlsafe(32)
        await self._collection.update_one({"_id": username}, {"$set": {"session_id": session_id}})
        await self.update_cache(username)

        return session_id

    async def logout(self, user_id: str) -> None:
        """Logout user by clearing session ID."""
        if not self.user_exists(user_id):
            raise NotFoundError(f"User '{user_id}' not found")

        await self._collection.update_one({"_id": user_id}, {"$set": {"session_id": None}})
        await self.update_cache(user_id)

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
