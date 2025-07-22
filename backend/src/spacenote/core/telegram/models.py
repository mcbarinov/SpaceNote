from datetime import datetime

from pydantic import BaseModel, Field

from spacenote.core.db import MongoModel


class TelegramBot(MongoModel):
    id: str = Field(alias="_id")  # Bot name/identifier (e.g., "spacenote-bot")
    token: str  # Telegram Bot API token
    created_at: datetime


class TelegramConfig(BaseModel):
    enabled: bool = False
    bot_id: str  # Reference to TelegramBot.id
    channel_id: str  # Telegram channel ID (e.g., "@spacenote_updates" or "-1001234567890")
    templates: "Templates"

    class Templates(BaseModel):
        new_note: str = (
            "📝 New note in {{space.name|escape_html}}\nNote #{{note.id}}\nAuthor: {{note.author|escape_html}}\n\n🔗 {{url}}"
        )
        field_update: str = (
            "✏️ Note updated in {{space.name|escape_html}}\nNote #{{note.id}}\nAuthor: {{note.author|escape_html}}\n\n🔗 {{url}}"
        )
        comment: str = (
            "💬 New comment in {{space.name|escape_html}}\n"
            "Note #{{note.id}}\n"
            "By {{comment.author|escape_html}}: {{comment.content|escape_html}}\n\n"
            "🔗 {{url}}"
        )
