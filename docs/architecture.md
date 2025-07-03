# SpaceNote Architecture

SpaceNote is a flexible note-taking system where users create custom "spaces" for different purposes (task tracking, journals, catalogs, etc.).

## Base Infrastructure

All MongoDB models inherit from `MongoModel`:
```python
class MongoModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True)
```

## Core Concepts

### Users
- Identified by unique username
- Passwords stored as bcrypt hashes
- Admin users can create new accounts
- System auto-creates default admin (`admin`/`admin`) on first startup
- **Scale**: Designed for small teams (up to 10 users)
- **Caching**: All users kept in memory for fast access

```python
class User(BaseModel):
    id: str  # username
    password_hash: str  # bcrypt hashed password
    admin: bool  # admin privileges flag
```

### Spaces
A space is a container with custom fields tailored to a specific use case. Each space defines:
- Unique ID (slug format: "our-tasks", "my-journal")
- Custom fields with types and validation
- Member access control
- UI configuration (list columns)
- **Scale**: Designed for small deployments (up to 100 spaces)
- **Caching**: All spaces kept in memory for fast access

```python
class Space(MongoModel):
    id: str = Field(alias="_id")  # Globally unique slug
    name: str
    members: list[str] = []  # User IDs with full access
    fields: list[SpaceField] = []  # Custom fields (order matters for UI)
    list_columns: list[str] = []  # Fields to display in list view
```

Field configuration:
```python
class SpaceField(BaseModel):
    name: str
    type: FieldType
    required: bool = False
    options: dict[FieldOption, FieldOptionValue] = {}  # Type-specific options
    default: FieldValue = None
```

Field options:
- `VALUES`: Available choices for CHOICE type
- `MIN/MAX`: Constraints for numeric/date fields

### Notes
Core content units in SpaceNote:
- Stored in per-space collections: `{space_id}_notes`
- Auto-incremented integer IDs within each space
- Contains user-defined fields matching space configuration
- Separate collections enable field-specific indexing for performance

```python
class Note(MongoModel):
    id: int  # Auto-incremented within each space
    author: str
    created_at: datetime
    fields: dict[str, FieldValue]  # User-defined fields as defined in Space.fields
```

### Fields
Fields define the structure of notes within a space. Supported field types:
- `STRING`: Plain text
- `MARKDOWN`: Rich text with markdown support
- `BOOLEAN`: True/false values
- `CHOICE`: Select from predefined options
- `TAGS`: Multiple string values for categorization
- `USER`: Reference to space members
- `DATETIME`: Date and time values

## Code Organization

### Project Structure
- **`spacenote/core`**: Application core - the heart of the system
  - Used by all client implementations
  - Contains business logic, models, and services
- **`spacenote/web`**: Web client implementation (FastAPI)
- **Future clients**: CLI, Telegram bot, etc.

### Core Architecture

**Concept-based Organization**:
- Each concept has its own folder: `user/`, `space/`, `note/`, `field/`
- Contains models, services, and related utilities

**Service Pattern**:
- Services handle database access, caching, and business logic
- All services inherit from base `Service` class
- Services access each other through `self.core.services.*`
- Example: `UserService`, `SpaceService`, `NoteService`

**Core Class**:
- Central application context
- Manages service lifecycle and dependencies
- Provides unified access to all services
- Handles database connection and startup/shutdown

**Pure Functions**:
- Stateless logic organized as pure functions
- Example: `user/password.py` for password hashing/validation
- Easier to test and reuse

### App Class - Client Entry Point

The `App` class is the **only** interface clients should use:
- Checks access permissions through `AccessService`
- Manages `current_user` context for all operations
- Provides login/logout functionality (via UserService)
- Delegates to appropriate services after access checks

Example flow:
```python
# Client (web) -> App -> AccessService -> Service -> Database
await app.create_note(current_user, space_id, fields)
```

### Design Decisions

**Caching Strategy**:
- Users and Spaces: Cached in memory (small scale)
- Notes: No caching (potentially large scale)
- Cache updates on every modification

**Access Control**:
- Simple model: space members have full access
- All access permission checks in App layer
- `AccessService` for centralized permission logic

**Session Management**:
- Sessions stored in `UserService`
- Login returns session ID
- Session lookup for authentication

## Technology Stack

### Core Technologies
- **Python**: 3.13+
- **Database**: MongoDB
- **Models**: Pydantic v2
- **Framework**: FastAPI

### Code Quality
- **Linting**: Ruff (actively used)
- **Type Checking**: MyPy (strict typing enforced)
- Full type annotations throughout the codebase