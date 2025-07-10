# Claude Code Agent Instructions

This file contains technical instructions specifically for the Claude Code agent. Project architecture and general documentation should be found in `docs/architecture.md`.

## Required Reading

When starting work on this project, you MUST read:
1. This file (`CLAUDE.md`) - for Claude Code agent-specific instructions
2. `docs/architecture.md` - for project architecture and general information

Both files are mandatory reading. The architecture file contains information for both humans and other AI agents.

## Content Guidelines

- **No duplication**: Never duplicate information between `CLAUDE.md` and `docs/architecture.md`
- `CLAUDE.md`: Technical instructions for Claude Code agent only
- `docs/architecture.md`: Project architecture, design decisions, and general documentation

## Language Requirements

All content must be in English:
- Code comments
- Documentation
- Git commit messages
- Any other written content

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
- `just dev` - Start development server (human use only)

### AI Agent Operations
- `just agent-start` - Start AI agent
- `just agent-stop` - Stop AI agent

## Template Writing Guidelines

Since we are in the prototyping phase:
- Use Pico CSS framework
- Minimize HTML tags - use as few as possible
- Minimize CSS classes - use as few as possible
- Focus on functionality over aesthetics
- Beauty and polish will come later - prioritize minimalism now

## Error Handling Guidelines

When writing web route handlers:
- Only add try/catch blocks if error handling is critically important
- Let exceptions bubble up to FastAPI's default error handling
- The App class will handle business logic errors and access control
- Services will raise appropriate exceptions that FastAPI will handle
- Follow minimalism principle during prototyping phase

## Documentation Writing Guidelines

When writing `docs/architecture.md`:
- Write concisely, only what matters
- No unnecessary filler content
- Focus on essential information only