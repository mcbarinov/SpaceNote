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
- **Single admin system**: Only the user with id "admin" has administrative privileges
- System auto-creates default admin (`admin`/`admin`) on first startup
- Regular users can only be created by the admin
- **Scale**: Designed for small teams (up to 10 users)
- **Caching**: All users kept in memory for fast access

```python
class User(BaseModel):
    id: str  # username (id == "admin" indicates the administrator)
    password_hash: str  # bcrypt hashed password
    session_id: str | None  # current session identifier
```

### Spaces
A space is a container with custom fields tailored to a specific use case. Each space defines:
- Unique ID (slug format: "our-tasks", "my-journal")
- Custom fields with types and validation
- Member access control
- UI configuration (list columns)
- Filters for custom views
- **Scale**: Designed for small deployments (up to 100 spaces)
- **Caching**: All spaces kept in memory for fast access

```python
class Space(MongoModel):
    id: str = Field(alias="_id")  # Globally unique slug
    name: str
    members: list[str] = []  # User IDs with full access
    fields: list[SpaceField] = []  # Custom fields (order matters for UI)
    list_columns: list[str] = []  # Fields to display in list view
    filters: list[Filter] = []  # Filter definitions for this space
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

### Filters
Filters enable custom views of notes with specific conditions, sorting, and field display:
- Stored as part of space configuration
- Each filter has unique ID within the space
- Apply complex conditions with various operators
- Custom sorting and field display per filter

```python
class Filter(BaseModel):
    id: str  # unique identifier: "urgent-tasks", "my-drafts"
    title: str  # human-readable: "Urgent Tasks", "My Drafts"
    description: str = ""
    conditions: list[FilterCondition]  # filtering logic
    sort: list[str] = []  # ["-created_at", "priority"]
    list_fields: list[str] = []  # additional display columns
```

Supported operators:
- **Comparison**: `eq`, `ne`, `gt`, `gte`, `lt`, `lte`
- **Text**: `contains`, `startswith`, `endswith`
- **List**: `in` (has any), `all` (has all)

Filter logic stored as pure functions in `core/filter/`:
- `mongo.py`: Query building and sorting
- `validators.py`: Filter validation

### Comments
Comments enable threaded discussions on notes:
- Stored in per-space collections: `{space_id}_comments`
- Support nested replies via parent_id
- Notes track comment count and last comment timestamp

```python
class Comment(MongoModel):
    id: str  # Auto-incremented within each space
    note_id: int  # Reference to parent note
    author: str  # User ID
    content: str  # Comment text
    created_at: datetime
    edited_at: datetime | None = None
    parent_id: str | None = None  # For nested comments
```

## Code Organization

### Project Structure
- **`spacenote/core`**: Application core - the heart of the system
  - Used by all client implementations
  - Contains business logic, models, and services
- **`spacenote/web`**: Web client implementation (FastAPI)
- **Future clients**: CLI, Telegram bot, etc.

### Core Architecture

**Concept-based Organization**:
- Each concept has its own folder: `user/`, `space/`, `note/`, `field/`, `filter/`
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
- Admin determination: `user.id == "admin"` (single admin system)
- `ensure_admin()` method in AccessService enforces admin-only operations

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