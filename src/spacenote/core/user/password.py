"""
Password utilities for authentication.

This module contains pure functions for password hashing and verification.
These functions have no external dependencies and are easily testable.
"""

import bcrypt


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.

    Args:
        password: Plain text password to hash

    Returns:
        Hashed password as string
    """
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    """
    Verify a password against a hash.

    Args:
        password: Plain text password to verify
        password_hash: Stored password hash

    Returns:
        True if password matches hash, False otherwise
    """
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))


def validate_password_strength(password: str) -> None:
    """
    Validate password meets minimum requirements.

    Args:
        password: Password to validate

    Raises:
        ValueError: If password doesn't meet requirements
    """
    if len(password) < 4:
        raise ValueError("Password must be at least 4 characters long")
