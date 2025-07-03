"""
Web layer configuration for SpaceNote.

Configuration specific to the web server and HTTP interface.
Core-specific configuration is handled separately in core/config.py
"""

from pydantic_settings import BaseSettings


class WebConfig(BaseSettings):
    """Configuration for web layer functionality."""

    # Web server
    host: str = "127.0.0.1"
    port: int = 3000
    session_secret_key: str

    # Web-specific settings
    cors_origins: list[str] = []
    debug: bool = False

    model_config = {
        "env_file": ".env",
        "env_prefix": "SPACENOTE_",
        "extra": "ignore",
    }
