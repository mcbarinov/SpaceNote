class UserError(Exception):
    """Base class for user-related errors."""


class NotFoundError(UserError):
    def __init__(self, message: str = "Document not found") -> None:
        super().__init__(message)


class AccessDeniedError(UserError):
    """Raised when a user tries to access a resource they do not have permission for."""


class AdminRequiredError(AccessDeniedError):
    """Raised when an admin action is required but the user is not an admin."""

    def __init__(self, message: str = "Admin privileges required") -> None:
        super().__init__(message)
