# Claude Code Agent Instructions

This file contains technical instructions specifically for the Claude Code agent. Project architecture and general documentation should be found in the `docs/architecture/` directory.

## Required Reading

When starting work on this project, you MUST read:
1. This file (`CLAUDE.md`) - for Claude Code agent-specific instructions
2. `docs/architecture/concepts.md` - for core concepts and high-level overview
3. `docs/architecture/backend.md` - for backend architecture details
4. `docs/architecture/frontend.md` - for frontend implementation details

All files are mandatory reading. The architecture files contain information for both humans and other AI agents.

## Content Guidelines

- **No duplication**: Never duplicate information between `CLAUDE.md` and architecture docs
- `CLAUDE.md`: Technical instructions for Claude Code agent only
- `docs/architecture/`: Project architecture, design decisions, and general documentation


## Language Requirements

All content must be in English:
- Code comments
- Documentation
- Git commit messages
- Any other written content

## Communication Language

**ALWAYS communicate in English only**, regardless of the language used by the user. All responses must be in English.

## Current Project State

**Phase**: Prototyping
- We can modify any data structures as needed
- Breaking changes are acceptable
- We are NOT writing tests at this stage
- Focus is on rapid iteration and exploration


## Code Quality Checks

After making any code changes, you MUST run linters to ensure code quality:
- Run `just lint` to check for linting and type errors
- Fix any issues before considering the task complete
- This includes both ruff (linting) and mypy (type checking)

## Comment Guidelines

**DO NOT write meaningless comments that simply restate what the code does.**

Bad examples:
```python
# Verify user is admin
if not current_user.admin:
    raise PermissionError("Only administrators can export spaces")
# Export space data
return self._core.services.space.export_as_json(space_id)
```

**Only write comments when they provide additional context or explain WHY something is done:**

Good examples:
```python
# Late import to avoid circular dependency with module X
from module.x import SomeClass

# Using exponential backoff to handle rate limits
time.sleep(2 ** attempt)
```

**The code should be self-explanatory. Comments should explain business logic, not implementation details.**

## Import Guidelines

**All imports MUST be at the top of the file** in the standard Python import order:
1. Standard library imports
2. Third-party imports
3. Local application imports

**Exception**: Late imports are only allowed to resolve circular dependency issues and MUST include a comment explaining why:
```python
# Late import to avoid circular dependency with module X
from module.x import SomeClass
```

**Never** use late imports for convenience or performance reasons without a clear circular dependency issue.

## Project Commands

### Human Development
- `just dev` - Start backend development server (human use only)
- `just dev-all` - Start backend and frontend servers
- `just frontend-dev` - Start frontend development server on port 3002

### AI Agent Operations
- `just agent-start` - Start AI agent servers (backend: 8001)
- `just agent-stop` - Stop AI agent servers

## API Router Structure

SpaceNote has a single React frontend that communicates with the backend via API routes:

- **Frontend (React/SPA)** - `frontend/`
  - Modern React SPA on port 3002
  - API routes are in `web/routers/` 
  - Create new router files like `web/routers/spaces.py` for new API endpoints
  - These routes should follow RESTful patterns as described in architecture docs

When implementing new API endpoints, always create them in `web/routers/`.

## Frontend Import Guidelines

**MANDATORY: Use path aliases for all cross-directory imports.**

SpaceNote has path aliases configured (`@/*` → `./src/*`). Always use them for clean, maintainable code.

### Import Rules

**✅ REQUIRED - Use Path Aliases:**
```typescript
import { Button } from "@/components/ui/button"
import { useSpacesStore } from "@/stores/spacesStore"
import type { Note } from "@/lib/api/notes"
import { formatFieldValue } from "@/lib/formatters"
```

**✅ ALLOWED - Relative for Same Directory:**
```typescript
import { FieldsTable } from "./components/FieldsTable"
import { utils } from "./helpers"
```

**❌ FORBIDDEN - Deep Relative Paths:**
```typescript
import { Button } from "../../../components/ui/button"      // Never do this
import { formatters } from "../../../../lib/formatters"     // Never do this
```

### Why This Matters

- **Maintainability**: Moving files won't break imports
- **Readability**: `@/lib/api` is clearer than `../../../lib/api`
- **IDE Support**: Better autocomplete and navigation
- **Industry Standard**: Expected by all React/TypeScript developers

**When creating new components, always use `@/` imports for anything outside the current directory.**


## Error Handling Guidelines

When writing web route handlers:
- Only add try/catch blocks if error handling is critically important
- Let exceptions bubble up to FastAPI's default error handling
- The App class will handle business logic errors and access control
- Services will raise appropriate exceptions that FastAPI will handle
- Follow minimalism principle during prototyping phase

## Service Access Guidelines

**CRITICAL RULE**: Services can ONLY be accessed through `core.services.*` objects:

- ✅ **Correct**: `self.core.services.attachment.get_attachment()`
- ❌ **FORBIDDEN**: Passing services as parameters to pure functions
- ❌ **FORBIDDEN**: `validate_note_fields(space, fields, attachment_service=service)`

**Pure functions** (in modules like `field/validators.py`) must:
- Work only with simple data types (strings, dicts, models)
- Never receive services as parameters
- Never access `self.core` or any service objects
- Be truly "pure" - same input always produces same output

**Service layer** responsibilities:
- Access other services through `self.core.services.*`
- Handle business logic that requires service interactions
- Call pure functions with prepared data

## Documentation Writing Guidelines

When writing architecture documentation:
- Write concisely, only what matters
- No unnecessary filler content
- Focus on essential information only