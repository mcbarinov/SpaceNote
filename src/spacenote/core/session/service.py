import secrets
from datetime import UTC, datetime, timedelta, timezone
from typing import Any

import structlog
from pymongo import ASCENDING
from pymongo.asynchronous.database import AsyncDatabase

from spacenote.core.core import Service
from spacenote.core.errors import NotFoundError
from spacenote.core.session.models import Session
from spacenote.core.user.models import SessionId, User

logger = structlog.get_logger(__name__)


class SessionService(Service):
    """Service for managing user sessions."""

    SESSION_DURATION_DAYS = 30

    def __init__(self, database: AsyncDatabase[dict[str, Any]]) -> None:
        super().__init__(database)
        self._collection = database.get_collection("sessions")
        self._session_cache: dict[SessionId, User] = {}

    async def create_session(self, user_id: str, user_agent: str | None = None, ip_address: str | None = None) -> SessionId:
        """Create a new session for a user."""
        log = logger.bind(user_id=user_id, action="create_session")

        now = datetime.now(UTC)
        session_data = {
            "_id": secrets.token_urlsafe(32),
            "user_id": user_id,
            "created_at": now,
            "last_used": now,
            "expires_at": now + timedelta(days=self.SESSION_DURATION_DAYS),
            "user_agent": user_agent,
            "ip_address": ip_address,
        }

        session = Session.model_validate(session_data)
        await self._collection.insert_one(session.to_dict())

        session_id = SessionId(session.id)
        log.debug("session_created", session_id=session_id)
        return session_id

    async def get_session(self, session_id: str) -> Session | None:
        """Get session by ID and update last_used timestamp."""
        session_data = await self._collection.find_one_and_update(
            {"_id": session_id, "expires_at": {"$gt": datetime.now(UTC)}},
            {"$set": {"last_used": datetime.now(UTC)}},
        )

        if session_data is None:
            return None

        return Session.model_validate(session_data)

    async def get_user_sessions(self, user_id: str) -> list[Session]:
        """Get all active sessions for a user."""
        cursor = self._collection.find({"user_id": user_id, "expires_at": {"$gt": datetime.now(UTC)}}).sort("last_used", -1)

        return await Session.list_cursor(cursor)

    async def delete_session(self, session_id: str) -> None:
        """Delete a specific session."""
        log = logger.bind(session_id=session_id, action="delete_session")

        result = await self._collection.delete_one({"_id": session_id})
        if result.deleted_count == 0:
            log.warning("session_not_found")
            raise NotFoundError(f"Session '{session_id}' not found")

        # Clear from cache
        self.invalidate_session_cache(SessionId(session_id))

        log.debug("session_deleted")

    async def delete_user_sessions(self, user_id: str) -> int:
        """Delete all sessions for a user."""
        log = logger.bind(user_id=user_id, action="delete_user_sessions")

        result = await self._collection.delete_many({"user_id": user_id})

        # Clear sessions from cache
        sessions_to_remove = [sid for sid, user in self._session_cache.items() if user.id == user_id]
        for session_id in sessions_to_remove:
            del self._session_cache[session_id]

        log.debug("user_sessions_deleted", count=result.deleted_count)

        return result.deleted_count

    async def get_user_by_session(self, session_id: SessionId) -> User | None:
        """Get user by session ID using cache."""
        # Check cache first
        if session_id in self._session_cache:
            return self._session_cache[session_id]

        # Get session from database
        session = await self.get_session(session_id)
        if session is None:
            return None

        # Get user from UserService and cache it
        user = self.core.services.user.get_user(session.user_id)
        self._session_cache[session_id] = user

        return user

    def invalidate_session_cache(self, session_id: SessionId) -> None:
        """Remove session from cache."""
        self._session_cache.pop(session_id, None)

    def invalidate_user_session_cache(self, user_id: str) -> None:
        """Remove all sessions for a user from cache."""
        sessions_to_remove = [sid for sid, user in self._session_cache.items() if user.id == user_id]
        for session_id in sessions_to_remove:
            del self._session_cache[session_id]

    async def cleanup_expired_sessions(self) -> int:
        """Remove expired sessions. This is called periodically."""
        result = await self._collection.delete_many(
            {"expires_at": {"$lt": datetime.now(timezone.utc)}}  # noqa: UP017
        )

        if result.deleted_count > 0:
            logger.debug("expired_sessions_cleaned", count=result.deleted_count)

        return result.deleted_count

    async def on_start(self) -> None:
        """Initialize service on application startup."""
        # Create TTL index for automatic session expiration
        await self._collection.create_index([("expires_at", ASCENDING)], expireAfterSeconds=0)

        # Index for user_id to speed up user session queries
        await self._collection.create_index([("user_id", ASCENDING)])

        logger.debug("session_service_started")
