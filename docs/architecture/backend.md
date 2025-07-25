# SpaceNote Backend Architecture

## Technology Stack

- **Language**: Python 3.13+
- **Database**: MongoDB
- **Models**: Pydantic v2 with strict validation
- **Web Framework**: FastAPI
- **Type Checking**: MyPy with strict mode
- **Linting**: Ruff

## Base Infrastructure

All MongoDB models inherit from a common base:

```python
class MongoModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True)
```

This provides:
- Automatic field aliasing for MongoDB's `_id` field
- Support for MongoDB-specific types
- Consistent configuration across all models

## Project Structure

```
spacenote/
├── core/               # Application core (shared by all clients)
│   ├── user/          # User management
│   ├── space/         # Space management
│   ├── note/          # Note operations
│   ├── field/         # Field validation and types
│   ├── filter/        # Filter logic
│   ├── comment/       # Comment system
│   ├── attachment/    # File management
│   ├── telegram/      # Telegram integration
│   └── access/        # Access control
├── web/               # Web layer (FastAPI)
│   └── routers/      # API endpoints
└── scripts/          # Utility scripts
```

## Core Architecture

### Concept-Based Organization

Each domain concept has its own module containing:
- **Models**: Pydantic models for data structures
- **Service**: Business logic and database operations
- **Utilities**: Pure functions for stateless operations

Example structure:
```
user/
├── __init__.py
├── models.py      # User, UserCreate, UserUpdate models
├── service.py     # UserService class
└── password.py    # Pure functions for password operations
```

### Service Layer Pattern

Services handle all business logic and data access:

```python
class UserService(Service):
    def __init__(self, core: "Core"):
        super().__init__(core)
        self._users_cache: dict[str, User] = {}
        self._sessions: dict[str, str] = {}  # session_id -> user_id
    
    async def get_user(self, user_id: str) -> User | None:
        # Check cache first
        if user_id in self._users_cache:
            return self._users_cache[user_id]
        # Load from database if needed
        ...
```

**Service Responsibilities:**
- Database operations (CRUD)
- Caching management
- Business logic enforcement
- Cross-service coordination via `self.core.services.*`

**Service Access Rules:**
- Services ONLY access other services through `self.core.services.*`
- Never pass services as parameters to functions
- Services are singletons managed by Core

### Core Class

The Core class is the central orchestrator:

```python
class Core:
    def __init__(self, config: CoreConfig):
        self.config = config
        self.db: Database = None
        self.services = ServiceRegistry()
    
    async def startup(self):
        # Initialize database connection
        # Create service instances
        # Load caches
        
    async def shutdown(self):
        # Cleanup resources
```

**Core Responsibilities:**
- Service lifecycle management
- Database connection handling
- Configuration management
- Startup/shutdown orchestration

### App Class - Client Interface

The App class is the ONLY interface clients should use:

```python
class App:
    def __init__(self, core: Core):
        self._core = core
        
    async def create_note(
        self, 
        current_user: User,
        space_id: str,
        fields: dict[str, Any]
    ) -> Note:
        # 1. Check access permissions (App's only real responsibility)
        await self._core.services.access.ensure_space_member(current_user, space_id)
        
        # 2. Delegate everything else to service
        return await self._core.services.note.create_note(
            space_id, current_user.id, fields
        )
```

**App Layer Responsibilities:**
- Access control enforcement (primary responsibility)
- User context management
- Direct delegation to services (no business logic)

**Request Flow:**
```
Client Request → App (access check) → Domain Service (validation + logic) → Database
                  ↓
              Response
```

**Design Principle:**
- App layer: Only access control, then delegate
- Service layer: All business logic, validation, and data operations

### Pure Functions

Stateless business logic is organized as pure functions:

```python
# field/validators.py
def validate_note_fields(
    space: Space, 
    fields: dict[str, Any]
) -> dict[str, Any]:
    # Pure validation logic
    # No service access
    # No side effects
```

**Pure Function Rules:**
- Work with simple data types only
- No service dependencies
- No database access
- Same input always produces same output

## Database Design

### Collection Strategy

Per-space collections for data isolation:
- `spaces` - Space configurations (global)
- `users` - User accounts (global)
- `telegram_bots` - Bot configurations (global)
- `{space_id}_notes` - Notes for each space
- `{space_id}_comments` - Comments for each space
- `{space_id}_attachments` - File metadata for each space

### Auto-Increment IDs

Within each space, entities use auto-incremented integer IDs:

```python
# Simple approach: get the highest existing ID and increment by 1
collection = self.db[f"{space_id}_notes"]
last_item = await collection.find({}).sort("_id", -1).limit(1).to_list(1)
next_id = 1 if not last_item else last_item[0]["_id"] + 1
```

Benefits:
- Human-readable IDs (Note #42)
- Simple references in UI
- Per-space isolation
- No additional counter documents needed

Note: This simple approach works for prototyping but would need atomic operations for high-concurrency production use.

## Caching Strategy

### In-Memory Caches

Small, frequently accessed data is cached:

**Users Cache:**
- All users loaded on startup
- Updated on every modification
- Enables fast authentication checks

**Spaces Cache:**
- All spaces loaded on startup
- Updated on modifications
- Enables fast access control

### No Caching

Large or dynamic data is not cached:
- Notes (potentially thousands per space)
- Comments (high volume, frequent updates)
- Attachments (file metadata changes rarely)

## Access Control

### Simple Permission Model

- **Admin**: User with `id == "admin"` has full access
- **Space Members**: Full access to their spaces
- **Non-Members**: No access

### AccessService Implementation

```python
class AccessService(Service):
    async def ensure_admin(self, user: User) -> None:
        if user.id != "admin":
            raise PermissionError("Admin access required")
    
    async def ensure_space_member(self, user: User, space_id: str) -> None:
        if user.id == "admin":
            return  # Admin has access to everything
            
        space = await self.core.services.space.get_space(space_id)
        if not space or user.id not in space.members:
            raise PermissionError("Space access denied")
```

## Session Management

Sessions are managed in-memory by UserService:

```python
async def login(self, username: str, password: str) -> str:
    user = await self.get_user(username)
    if not user or not verify_password(password, user.password_hash):
        raise ValueError("Invalid credentials")
    
    session_id = generate_session_id()
    self._sessions[session_id] = user.id
    return session_id
```

Benefits:
- Fast session validation
- Simple implementation
- Suitable for small user base

## Error Handling

SpaceNote uses a centralized error handling system that distinguishes between user-facing and internal errors.

### Error Hierarchy

All user-facing errors inherit from the abstract `UserError` base class:

```python
from abc import ABC

class UserError(ABC, Exception):
    """Base class for user-related errors.
    
    All errors that inherit from UserError will have their messages 
    displayed to the user. These errors should not contain any 
    sensitive information.
    """

class ValidationError(UserError):
    """Raised when user input fails validation."""

class AuthenticationError(UserError):
    """Raised when authentication fails."""

class AccessDeniedError(UserError):
    """Raised when access is denied."""

class NotFoundError(UserError):
    """Raised when a requested resource is not found."""
```

### Service Layer

Services raise specific exceptions based on the error type:

**User Errors (inherit from UserError):**
- `ValidationError`: Invalid user input or data validation failures
- `AuthenticationError`: Login failures, invalid sessions
- `AccessDeniedError`: Permission denied, admin privileges required
- `NotFoundError`: Requested resource doesn't exist

**Internal Errors (standard Python exceptions):**
- `ValueError`: Programming errors, internal validation
- `KeyError`: Missing keys in data structures
- `Exception`: Unexpected system errors

### Web Layer Error Handling

The web layer uses a centralized error handler that automatically maps error types to HTTP status codes:

```python
# Single handler for all UserError subclasses
app.add_exception_handler(UserError, user_error_handler)
app.add_exception_handler(Exception, general_exception_handler)
```

**Status Code Mapping:**
- `AuthenticationError` → 401 Unauthorized
- `AccessDeniedError` → 403 Forbidden  
- `NotFoundError` → 404 Not Found
- `ValidationError` → 400 Bad Request
- `Exception` (non-UserError) → 500 Internal Server Error

**Error Response Format:**
```json
{
  "error": "Error Type",
  "detail": "Human-readable error message",
  "status_code": 400
}
```

### Router Implementation

Routers are kept minimal and let errors bubble up to the centralized handlers:

```python
# ✅ CORRECT - Simple, clean router
@router.post("/spaces")
async def create_space(self, request: CreateSpaceRequest) -> Space:
    return await self.app.create_space(self.session_id, request.id, request.name)

# ❌ AVOID - Verbose try/catch blocks
@router.post("/spaces")
async def create_space(self, request: CreateSpaceRequest) -> Space:
    try:
        return await self.app.create_space(self.session_id, request.id, request.name)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except AccessDeniedError as e:
        raise HTTPException(status_code=403, detail=str(e)) from e
```

**Router Guidelines:**
- No try/catch blocks in router methods
- No manual HTTPException creation
- Let the centralized error handler manage all error responses
- Focus on business logic, not error handling

### Benefits

**For Frontend Developers:**
- Consistent API error responses
- Clear error messages for user-facing issues
- Predictable status codes

**For Backend Developers:**
- Simple router implementations
- Easy to add new error types
- Centralized error handling logic
- Internal errors are automatically hidden from users

**Security:**
- User errors show helpful messages
- Internal errors hide sensitive system information
- Automatic logging of unexpected errors

## Development Workflow

### Type Safety

All backend code must pass MyPy strict checks:
```bash
cd backend/
mypy src/ --strict
```

### Code Quality

Ruff enforces consistent style:
```bash
cd backend/
ruff check src/
ruff format src/
```

### Running Linters

After any backend code changes:
```bash
cd backend/
just lint  # Runs both ruff and mypy
```

## Configuration

Configuration via environment variables:

```python
class CoreConfig(BaseSettings):
    mongodb_url: str = "mongodb://localhost:27017"
    database_name: str = "spacenote"
    attachments_path: Path = Path("./attachments")
    
    model_config = SettingsConfigDict(
        env_prefix="SPACENOTE_"
    )
```

## API Router Architecture

### HTTP API Approach

SpaceNote uses an **HTTP API approach** rather than strict REST for the frontend API (`/api/...`):

**Design Philosophy:**
- **Entity-based routing**: Each major entity has its own router file
- **Query parameters for context**: Required parameters like `space_id` passed as query params
- **Shorter URLs**: `/api/notes?space_id=123` vs `/api/spaces/123/notes`
- **Consistent naming**: All ID parameters use `_id` suffix

**Router Organization:**
```
web/routers/
├── __init__.py          # Router registry
├── auth.py             # Authentication endpoints
├── spaces.py           # Space management and filters
├── notes.py            # Note operations
├── attachments.py      # File operations (future)
└── comments.py         # Comment operations (future)
```

**Example API Structure:**
```python
# spaces.py
@router.get("/spaces")                          # List spaces
@router.get("/spaces/{space_id}")               # Space details (includes filters)

# notes.py  
@router.get("/notes")                           # ?space_id=123&filter_id=active
@router.get("/notes/{note_id}")                 # ?space_id=123
```

**Benefits:**
- Clear separation of concerns
- Simpler URLs for frontend developers
- Easy to add filtering/pagination parameters
- Flexible and maintainable

### Security Model

All endpoints use session-based authentication via `X-Session-ID` header. Access control is enforced at the App layer, ensuring that:
- Users can only access spaces they're members of
- Admin users have full access
- Data isolation is maintained between spaces

## Future Extensibility

The architecture supports multiple clients:
- Current: React frontend (SPA)
- Planned: CLI client
- Planned: Telegram bot
- Possible: Mobile API

All clients interact through the App class, ensuring consistent behavior and access control.