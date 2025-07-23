# SpaceNote Core Concepts

SpaceNote is a flexible note-taking system where users create custom "spaces" for different purposes (task tracking, journals, catalogs, etc.).

## Core Philosophy

SpaceNote is designed primarily for individuals who need flexible, customizable note organization for their personal notes. It can also serve small teams. Rather than imposing rigid structures, it allows users to define their own data schemas through "spaces" - each tailored to specific use cases.

## Scale & Design Principles

- **Personal-first design**: Optimized for individual users and their personal notes
- **Small-scale focus**: Can support up to 10 users when used by teams
- **Performance through simplicity**: In-memory caching for frequently accessed data
- **Flexibility over complexity**: Custom fields instead of fixed schemas
- **Privacy by default**: Space-based access control

## Core Concepts

### Users

The foundation of SpaceNote's identity and access system.

- **Identity**: Each user has a unique username serving as their ID
- **Authentication**: Passwords stored as bcrypt hashes
- **Single Admin**: Only the user with id="admin" has administrative privileges
- **User Creation**: Regular users can only be created by the admin
- **Scale**: Optimized for individual use, supports up to 10 users with full in-memory caching

The system auto-creates a default admin account (admin/admin) on first startup.

### Spaces

Spaces are customizable containers that define how notes are structured and organized.

**Key Characteristics:**
- **Unique ID**: Slug format (e.g., "our-tasks", "my-journal")
- **Custom Schema**: Define fields specific to the use case
- **Access Control**: Member-based permissions
- **UI Customization**: Configure list views and filters
- **Scale**: Designed for up to 100 spaces per deployment

**Use Case Examples:**
- Task tracker with priority, status, assignee fields
- Personal journal with mood, weather, location fields
- Product catalog with price, category, stock fields
- Meeting notes with attendees, action items, decisions fields

### Notes

The core content units within each space.

**Structure:**
- **Per-Space Storage**: Each space has its own notes collection
- **Auto-ID**: Integer IDs auto-incremented within each space
- **Flexible Fields**: Content matches the space's field definitions
- **Metadata**: Author and creation timestamp always included

**Design Rationale:**
- Separate collections enable field-specific indexing
- Integer IDs provide simple, readable references
- Schema flexibility allows spaces to evolve independently

### Fields

Fields define the data structure within a space.

**Available Field Types:**
- `STRING`: Plain text for titles, names, descriptions
- `MARKDOWN`: Rich text with formatting support
- `BOOLEAN`: Yes/no, true/false values
- `CHOICE`: Single selection from predefined options
- `TAGS`: Multiple values for categorization
- `USER`: Reference to space members for assignment
- `DATETIME`: Date and time values with timezone
- `IMAGE`: Visual content via attachment reference

**Field Configuration:**
- Required/optional designation
- Default values
- Type-specific constraints (min/max, allowed values)
- Display order for UI rendering

### Filters

Filters provide custom views of notes within a space.

**Capabilities:**
- **Complex Conditions**: Combine multiple criteria with various operators
- **Custom Sorting**: Define display order (newest first, by priority, etc.)
- **Field Selection**: Choose which fields to display in list view
- **Saved Views**: Store commonly used filters for quick access

**Operator Support:**
- Comparison: `eq`, `ne`, `gt`, `gte`, `lt`, `lte`
- Text matching: `contains`, `startswith`, `endswith`
- List operations: `in` (has any), `all` (has all)

### Comments

Enable collaborative discussions on notes.

**Features:**
- **Threaded Discussions**: Support for nested replies
- **Real-time Updates**: Note comment counts update automatically
- **Edit History**: Track when comments are modified
- **Per-Space Storage**: Comments isolated by space for performance

### Attachments

File management system integrated with notes.

**Two-Stage Workflow:**

1. **Upload to Space**: Files uploaded and stored as "unassigned"
2. **Assign to Note**: Link files to specific notes when needed

**Benefits:**
- Upload files before creating notes
- Reuse files across multiple notes
- Manage space-wide file library
- Automatic image preview generation

**Storage Strategy:**
- Human-readable filenames with unique IDs
- Organized directory structure by space and note
- Separate preview storage for images

### Telegram Notifications

Real-time updates to Telegram channels for space activity.

**Event Types:**
- New note creation
- Note field updates
- New comments

**Features:**
- Customizable message templates
- Per-space configuration
- Admin-managed bot tokens
- Jinja2 template support for rich formatting

## Access Control Model

SpaceNote uses a simple, effective permission system:

- **Admin**: Full system access (user with id="admin")
- **Space Members**: Full access to their spaces
- **Non-Members**: No access to space content

This model prioritizes simplicity and clear boundaries over granular permissions.

## Data Isolation

Each space maintains separate MongoDB collections for:
- Notes: `{space_id}_notes`
- Comments: `{space_id}_comments`
- Attachments: `{space_id}_attachments`

Benefits:
- Performance: Queries don't cross space boundaries
- Indexing: Optimize for each space's unique fields
- Scalability: Easy to shard by space if needed
- Security: Clear data isolation between spaces