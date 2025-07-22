set dotenv-load

# Import sub-justfiles
import "backend/justfile" as backend
import "frontend/justfile" as frontend

# Default to showing available commands
default:
    @just --list

# Backend shortcuts (most commonly used)
dev: backend-dev
lint: backend-lint
test: backend-test
build: backend-build

# Database operations (shared)
db-reset:
    #!/usr/bin/env bash
    set -euo pipefail
    DB_NAME=$(echo "$SPACENOTE_DATABASE_URL" | sed 's/.*\///')
    echo "⚠️  This will completely DROP the '$DB_NAME' database!"
    echo "📊 Database URL: $SPACENOTE_DATABASE_URL"
    echo "All data will be lost permanently."
    read -p "Are you sure? (y/N): " confirm
    if [ "$confirm" = "y" ] || [ "$confirm" = "Y" ]; then
        mongosh --eval "db.getSiblingDB('$DB_NAME').dropDatabase()" "$SPACENOTE_DATABASE_URL"
        echo "✅ Database '$DB_NAME' has been dropped"
    else
        echo "❌ Operation cancelled"
    fi

# Docker operations
docker-build:
    #!/usr/bin/env bash
    set -euo pipefail
    VERSION=$(grep -E '^version = ' backend/pyproject.toml | cut -d'"' -f2)
    
    # Remove existing builder and create fresh one
    docker buildx rm spacenote-builder 2>/dev/null || true
    docker buildx create --name spacenote-builder --use
    
    # Build for multiple platforms
    docker buildx build --platform linux/amd64,linux/arm64 \
        -t spacenote:latest -t spacenote:$VERSION \
        --load .
    
    echo "✅ Built spacenote:latest and spacenote:$VERSION for linux/amd64 and linux/arm64"

docker-deploy:
    #!/usr/bin/env bash
    set -euo pipefail
    VERSION=$(grep -E '^version = ' backend/pyproject.toml | cut -d'"' -f2)
    
    # Check if working directory is clean
    if ! git diff --quiet || ! git diff --cached --quiet; then
        echo "❌ Working directory has uncommitted changes. Please commit or stash them first."
        exit 1
    fi
    
    # Remove existing builder and create fresh one
    docker buildx rm spacenote-builder 2>/dev/null || true
    docker buildx create --name spacenote-builder --use
    
    # Build and push multi-platform images directly to registry
    echo "Building and pushing multi-platform images..."
    docker buildx build --platform linux/amd64,linux/arm64 \
        -t ghcr.io/mcbarinov/spacenote:latest \
        -t ghcr.io/mcbarinov/spacenote:$VERSION \
        --push .
    
    echo "✅ Successfully deployed to ghcr.io/mcbarinov/spacenote (latest and $VERSION) for linux/amd64 and linux/arm64"
    
    # Create and push Git tag
    echo "Creating Git tag v$VERSION..."
    git tag -a "v$VERSION" -m "Release v$VERSION"
    git push origin "v$VERSION"
    
    echo "✅ Git tag v$VERSION created and pushed"

# Quick access to both development servers
dev-all:
    @echo "Starting backend and frontend development servers..."
    @echo "Backend: http://localhost:3000"
    @echo "Frontend: http://localhost:5173"
    @echo "Press Ctrl+C to stop both servers"
    @trap 'kill 0' INT; just backend-dev & just frontend-dev & wait

# AI agent commands
agent-start:
    just backend-agent-start
    just frontend-agent-start
    @echo "✅ AI agent servers started (backend: 8001, frontend: 8002)"

agent-stop:
    just backend-agent-stop
    just frontend-agent-stop
    @echo "✅ AI agent servers stopped"