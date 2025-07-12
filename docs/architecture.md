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
- `IMAGE`: Reference to image attachment (int: attachment_id)

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

### Attachments
Attachments allow users to upload and associate files with notes within a space. Files can be uploaded to a space first and then assigned to specific notes, providing flexibility in file management.

```python
class Attachment(MongoModel):
    id: int  # Auto-incremented within each space
    space_id: str  # Space this attachment belongs to
    filename: str  # Original filename (e.g., "report.pdf")
    content_type: str  # MIME type (e.g., "application/pdf", "image/jpeg")
    size: int  # File size in bytes
    path: str  # Relative path from attachments root
    author: str  # User who uploaded the file
    created_at: datetime  # When file was uploaded
    note_id: int | None = None  # Attached note (None = unassigned)
```

**File Storage Strategy**

Configuration: Attachments root directory specified in `CoreConfig.attachments_path`

File System Structure:
```
{attachments_path}/
  /{space_id}/
    /__unassigned__/           # Files with note_id = None
      filename__{id}.ext
    /{note_id}/                # Files assigned to specific notes
      filename__{id}.ext

{attachments_path}_preview/
  /{space_id}/
    /__unassigned__/           # Image previews for unassigned files
      filename__{id}.ext
    /{note_id}/                # Image previews for assigned files
      filename__{id}.ext
```

File Naming Convention:
- **Format**: `{original_filename}__{attachment_id}.{original_extension}`
- **Example**: `report__42.pdf` (where 42 is the auto-incremented attachment ID)
- **Benefits**: Human-readable + guaranteed uniqueness + easy DB correlation

**Workflow**

Stage 1: Upload to Space
1. User uploads file to space
2. File saved to `/{space_id}/__unassigned__/` directory
3. Attachment record created with `note_id = null`
4. File appears in space's unassigned attachments list

Stage 2: Assign to Note
1. When creating/editing note with ATTACHMENT field
2. User selects from available unassigned attachments
3. File moved from `__unassigned__/` to `/{note_id}/` directory
4. Attachment record updated with `note_id`
5. File now linked to note and displayed in note view

**Database Collections**

Per-Space Collections:
- `{space_id}_attachments` - attachment metadata for each space
- Follows existing pattern of space-isolated collections
- Auto-incremented IDs within each space (like notes and comments)

**Image Previews**

For image attachments, preview files are automatically generated:
- **Storage**: Parallel structure in `{attachments_path}_preview/`
- **Generation**: Automatic background processing on image upload
- **Specifications**: Max 800px width/height, 85% JPEG quality
- **Formats**: JPEG, PNG, WebP, GIF (first frame)
- **Naming**: Mirrors original attachment naming convention
- **Purpose**: Fast loading for web interfaces and external integrations

**IMAGE Field Type**

Specialized field type for displaying images within notes:
- **Value**: `int` (attachment_id referencing image attachment)
- **Validation**: Referenced attachment must exist in same space and be image type
- **Display**: Shows preview thumbnail with click-to-enlarge
- **Selection**: Choose from available image attachments in space
- **Difference from ATTACHMENT**: Optimized for visual display vs general file handling

**Access Control**

- Upload/Download: Space membership required
- Assign/Unassign: Space membership required
- Delete: Space membership required
- Admin: Full access to all attachments

### Telegram Notifications
Telegram notifications enable automatic updates to Telegram channels when events occur in spaces. This allows users to stay informed about space activity without constantly checking the web interface.

**Core Models:**

```python
class TelegramBot(MongoModel):
    id: str = Field(alias="_id")  # Bot name/identifier (e.g., "spacenote-bot")
    token: str  # Telegram Bot API token
    created_at: datetime
```

```python
class TelegramConfig(BaseModel):
    enabled: bool = False
    bot_id: str  # Reference to TelegramBot.id
    channel_id: str  # Telegram channel ID (e.g., "@spacenote_updates" or "-1001234567890")
    templates: Templates

    class Templates(BaseModel):
        new_note: str = "📝 New note in {{space.name}}:\n{{note.title}}\nAuthor: {{note.author}}"
        field_update: str = "✏️ Note updated in {{space.name}}:\n{{note.title}}\nChanges: {{changes}}"
        comment: str = "💬 New comment in {{space.name}}:\n{{note.title}}\nBy {{comment.author}}: {{comment.content}}"
```

**Space Integration:**

```python
class Space(MongoModel):
    # ... existing fields ...
    telegram: TelegramConfig | None = None  # Optional Telegram configuration
```

**Database Collections:**

- `telegram_bots` - Store Telegram bot configurations (admin-only)
- `spaces` - Updated with optional `telegram` field

**Event Triggers:**

Notifications are automatically sent when:
1. **New Note Created**: When a note is created in a space with Telegram enabled
2. **Note Fields Updated**: When note fields are modified in a space with Telegram enabled  
3. **New Comment Added**: When a comment is added to a note in a space with Telegram enabled

**Template Variables:**

Jinja2 templates have access to:
```python
{
    "space": space_object,      # Space information
    "note": note_object,        # Note information
    "comment": comment_object,  # Comment information (for comment events)
    "changes": field_changes,   # Field changes (for update events)
    "author": user_object,      # User who triggered the event
    "url": note_url            # Link back to the note
}
```

**Access Control:**

- **Bot Management**: Admin-only (only the admin user can create/delete bots)
- **Space Configuration**: Space members can configure Telegram settings for their spaces
- **Notifications**: Sent automatically when events occur in spaces with Telegram enabled

**Service Implementation:**

The `TelegramService` handles:
- Bot management (CRUD operations)
- Message sending to channels
- Template rendering with Jinja2
- Event integration with existing services
- Rate limiting and error handling

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