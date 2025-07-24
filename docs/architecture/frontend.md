# SpaceNote Frontend Architecture

## Frontend (Main Implementation)

**Status**: Active development
**Location**: `/frontend`
**Port**: `SPACENOTE_FRONTEND_PORT` (default: 3002)

This is the primary frontend implementation being developed for SpaceNote. It represents a clean, modern approach to building the user interface with lessons learned from previous implementations.

**Goals:**
- Clean architecture from ground up
- Improved state management patterns
- Better TypeScript usage
- Optimized bundle size
- Modern React patterns

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


## Legacy Web (Server-Side Rendering)

**Status**: Maintained alongside main frontend
**Location**: `spacenote/web/`
**Port**: `SPACENOTE_PORT` (default: 3000)

The legacy web implementation uses server-side rendering and provides a fully functional SpaceNote experience without JavaScript dependencies.

**Technology Stack:**
- FastAPI for routing and API endpoints
- Jinja2 templates for HTML generation
- Pico CSS for semantic, minimal styling
- Vanilla JavaScript for progressive enhancement

**Architecture Principles:**
- Server-side rendering for simplicity and performance
- Progressive enhancement approach
- Minimal JavaScript usage
- Semantic HTML with Pico CSS styling

**Template Guidelines:**
- Use Pico CSS semantic classes
- Keep templates simple and readable
- Minimize custom CSS
- Focus on functionality over aesthetics during prototyping

**Development Commands:**
```bash
# Legacy web only
just dev

# Backend + legacy web
just dev-all
```

## Development Strategy

### Dual Frontend Approach
SpaceNote provides two frontend implementations:
- **Frontend**: Modern SPA with full JavaScript functionality
- **Legacy**: Server-rendered pages with progressive enhancement

### API Compatibility
Both implementations share the same backend API:
- RESTful endpoints for data operations
- Session-based authentication
- Consistent error handling
- Same business logic validation

### Migration Path
Users can choose their preferred interface:
- Power users may prefer the modern frontend
- Users preferring simplicity may use legacy web
- Both will be maintained long-term

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

## Build and Deployment

### Frontend Development
```bash
cd frontend/
npm run dev          # Development server
npm run build        # Production build
npm run type-check   # TypeScript validation
npm run lint         # Code quality checks
```

### Production Optimization
- Tree shaking for minimal bundle size
- Asset optimization and compression
- Critical CSS extraction
- Service worker for offline capability

### Future Considerations

If the application grows in complexity, consider adding:
- **React Query** for advanced server state management, caching, and optimistic updates
- **Real-time updates** with WebSockets for collaborative features
- **Advanced caching strategies** for improved performance

