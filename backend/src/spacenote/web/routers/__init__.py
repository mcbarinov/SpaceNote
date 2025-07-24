from spacenote.web.routers.auth import router as auth_router
from spacenote.web.routers.notes import router as notes_router
from spacenote.web.routers.spaces import router as spaces_router

__all__ = ["auth_router", "notes_router", "spaces_router"]
