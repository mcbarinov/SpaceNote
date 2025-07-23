"""
Web layer configuration for SpaceNote.

Configuration specific to the web server and HTTP interface.
Core-specific configuration is handled separately in core/config.py
"""

from pydantic_settings import BaseSettings


class WebConfig(BaseSettings):
    """Configuration for web layer functionality."""

    # Web server
    host: str
    port: int
    session_secret_key: str

    # Web-specific settings
    cors_origins: list[str] = []
    debug: bool

    model_config = {
        "env_file": [".env", "../.env"],
        "env_prefix": "SPACENOTE_",
        "extra": "ignore",
    }
