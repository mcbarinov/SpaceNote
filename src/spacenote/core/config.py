"""
Core configuration for SpaceNote.

Configuration specific to the core business logic layer.
Web-specific configuration is handled separately in web/config.py
"""

from pydantic_settings import BaseSettings


class CoreConfig(BaseSettings):
    """Configuration for core SpaceNote functionality."""

    # Database
    database_url: str = "mongodb://localhost:27017/spacenote"

    # Logging
    debug: bool = False

    model_config = {
        "env_file": ".env",
        "env_prefix": "SPACENOTE_",
        "extra": "ignore",
    }
