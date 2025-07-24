# SpaceNote Frontend Architecture

**Status**: Active development
**Location**: `/frontend`
**Port**: `SPACENOTE_FRONTEND_PORT` (default: 3002)

SpaceNote's modern frontend implementation built with React and TypeScript. This provides a clean, responsive user interface for managing spaces and notes.

**Goals:**
- Modern React architecture
- Type-safe development with TypeScript
- Optimized bundle size and performance
- Clean state management patterns
- Responsive, accessible UI components

### Technology Stack

**Core Framework:**
- TypeScript 5.8+ for type safety
- React 19 for UI components
- Vite 7 for build tooling and development server

**State Management:**
- Zustand 5.0 for application state management

**HTTP & API:**
- Ky 1.x for HTTP requests with built-in retry logic

**Forms & Validation:**
- React Hook Form 7 for performant form handling
- Zod 4 for schema validation and TypeScript integration

**UI Components:**
- Tailwind CSS 4 for utility-first styling
- shadcn/ui components built on Radix UI primitives

**Rich Text:**
- TipTap 3 for markdown editing with WYSIWYG interface


## Development Strategy

SpaceNote uses a modern single-page application (SPA) architecture built with React. The backend provides a comprehensive REST API that serves the frontend application.

## API Design

SpaceNote uses an **HTTP API approach** rather than strict REST for better simplicity and developer experience.

### API Design Philosophy

- **HTTP API over REST**: Prioritizes simplicity and short URLs over strict REST compliance
- **Query parameters for context**: Uses `space_id`, `filter_id`, `note_id` parameters with `_id` suffix for consistency
- **Entity-based routing**: Each major entity (`notes`, `spaces`, `attachments`) has its own router
- **Mandatory context**: All operations require appropriate context (e.g., `space_id` for notes)

### Endpoint Structure
```
# Spaces management
GET    /api/spaces                      # List user's spaces
GET    /api/spaces/{space_id}           # Get space details (includes filters)

# Notes operations
GET    /api/notes?space_id={id}         # List notes in space
GET    /api/notes?space_id={id}&filter_id={filter}&page=1
POST   /api/notes?space_id={id}         # Create note
GET    /api/notes/{note_id}?space_id={id}  # Get note details
PUT    /api/notes/{note_id}?space_id={id}  # Update note
DELETE /api/notes/{note_id}?space_id={id}  # Delete note

# Comments operations (future)
GET    /api/comments?space_id={id}&note_id={note}  # List comments
POST   /api/comments?space_id={id}&note_id={note}  # Create comment

# Attachments operations (future)  
GET    /api/attachments?space_id={id}   # List space attachments
GET    /api/attachments?space_id={id}&note_id={note}  # Note attachments
```

**Benefits of this approach:**
- **Shorter URLs**: `/api/notes?space_id=my-tasks` vs `/api/spaces/my-tasks/notes`
- **Clear separation**: Each entity has its own router file
- **Flexible parameters**: Easy to add filtering, pagination, sorting
- **Consistent naming**: All ID parameters use `_id` suffix

### Authentication
Session-based authentication with header:
```
X-Session-ID: <session-id>
```

### Response Format
```typescript
interface ApiResponse<T> {
  data: T
  meta?: {
    total?: number
    page?: number
    limit?: number
  }
}
```
