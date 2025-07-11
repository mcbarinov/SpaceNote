"""
Core configuration for SpaceNote.

Configuration specific to the core business logic layer.
Web-specific configuration is handled separately in web/config.py
"""

from pydantic_settings import BaseSettings


class CoreConfig(BaseSettings):
    """Configuration for core SpaceNote functionality."""

    # Database
    database_url: str

    # File Storage
    attachments_path: str

    # Logging
    debug: bool

    # Web Interface
    base_url: str

    model_config = {
        "env_file": ".env",
        "env_prefix": "SPACENOTE_",
        "extra": "ignore",
    }
