# SpaceNote Backend Architecture

## Technology Stack

- **Language**: Python 3.13+
- **Database**: MongoDB
- **Models**: Pydantic v2 with strict validation
- **Web Framework**: FastAPI (legacy web client)
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
├── web/               # Legacy web client (FastAPI + SSR)
│   ├── api/          # New API endpoints
│   └── templates/    # Jinja2 templates
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

### Service Layer

Services raise specific exceptions:
- `ValueError`: Invalid input or state
- `PermissionError`: Access denied
- `KeyError`: Entity not found

### Web Layer

FastAPI handles exceptions automatically:
- Returns appropriate HTTP status codes
- Provides consistent error responses
- Logs errors for debugging

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

## Future Extensibility

The architecture supports multiple clients:
- Current: Legacy web (FastAPI + SSR)
- Planned: CLI client
- Planned: Telegram bot
- Possible: Mobile API

All clients interact through the App class, ensuring consistent behavior and access control.