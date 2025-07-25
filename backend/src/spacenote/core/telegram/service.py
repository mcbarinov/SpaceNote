import html
from datetime import UTC, datetime
from typing import Any

import httpx
import structlog
from jinja2 import BaseLoader, Environment
from pymongo.asynchronous.database import AsyncDatabase

from spacenote.core.core import Service
from spacenote.core.errors import NotFoundError, ValidationError
from spacenote.core.telegram.models import TelegramBot

logger = structlog.get_logger(__name__)


class TelegramService(Service):
    """Service for managing Telegram bots and notifications."""

    def __init__(self, database: AsyncDatabase[dict[str, Any]]) -> None:
        super().__init__(database)
        self._collection = database.get_collection("telegram_bots")
        self._jinja_env = Environment(loader=BaseLoader(), autoescape=False)  # noqa: S701
        # Add custom filter for HTML escaping
        self._jinja_env.filters["escape_html"] = lambda text: html.escape(str(text)) if text else ""

    async def create_bot(self, id: str, token: str) -> TelegramBot:
        """Create a new Telegram bot."""
        log = logger.bind(bot_id=id, action="create_bot")

        if await self.bot_exists(id):
            log.warning("bot_already_exists")
            raise ValidationError(f"Bot with ID '{id}' already exists")

        bot = TelegramBot(
            id=id,
            token=token,
            created_at=datetime.now(UTC),
        )

        await self._collection.insert_one(bot.model_dump(by_alias=True))
        log.info("bot_created")
        return bot

    async def get_bot(self, id: str) -> TelegramBot:
        """Get bot by ID."""
        doc = await self._collection.find_one({"_id": id})
        if not doc:
            raise NotFoundError(f"Bot '{id}' not found")
        return TelegramBot(**doc)

    async def bot_exists(self, id: str) -> bool:
        """Check if a bot exists by ID."""
        count = await self._collection.count_documents({"_id": id})
        return count > 0

    async def get_bots(self) -> list[TelegramBot]:
        """Get all bots."""
        docs = await self._collection.find().to_list(None)
        return [TelegramBot(**doc) for doc in docs]

    async def delete_bot(self, id: str) -> None:
        """Delete a bot."""
        log = logger.bind(bot_id=id, action="delete_bot")

        result = await self._collection.delete_one({"_id": id})
        if result.deleted_count == 0:
            raise NotFoundError(f"Bot '{id}' not found")

        log.info("bot_deleted")

    def render_template(self, template: str, context: dict[str, Any]) -> str:
        """Render a Jinja2 template with the given context."""
        template_obj = self._jinja_env.from_string(template)
        return template_obj.render(context)

    async def send_notification(self, bot_id: str, channel_id: str, message: str, note_url: str | None = None) -> None:
        """Send a notification to a Telegram channel."""
        log = logger.bind(bot_id=bot_id, channel_id=channel_id, action="send_notification")

        # Get bot to verify it exists
        bot = await self.get_bot(bot_id)

        # Send message via Telegram Bot API
        url = f"https://api.telegram.org/bot{bot.token}/sendMessage"
        payload = {
            "chat_id": channel_id,
            "text": message,
            "parse_mode": "HTML",
            "disable_web_page_preview": False,
        }

        # Add inline keyboard with link button if URL is provided (skip for localhost)
        if note_url and not any(host in note_url for host in ["localhost", "127.0.0.1"]):
            payload["reply_markup"] = {"inline_keyboard": [[{"text": "View Note 🔗", "url": note_url}]]}

        try:
            async with httpx.AsyncClient() as client:
                log.debug("telegram_request", payload=payload)
                response = await client.post(url, json=payload)
                if response.status_code != 200:
                    error_body = response.text
                    log.error("telegram_error_response", status=response.status_code, body=error_body)
                response.raise_for_status()
                result = response.json()
                log.info("notification_sent", message=message[:200], telegram_response=result)
        except httpx.HTTPError as e:
            status_code = getattr(e, "response", None)
            status_code = getattr(status_code, "status_code", None) if status_code else None
            log.exception("telegram_api_error", error=str(e), status_code=status_code)
            raise
        except Exception as e:
            log.exception("notification_failed", error=str(e))
            raise
