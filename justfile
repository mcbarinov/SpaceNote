set dotenv-load

default: dev

clean:
	rm -rf .pytest_cache .ruff_cache .mypy_cache build dist src/*.egg-info

sync:
    uv sync --all-extras

build: clean lint audit test
    uv build

format:
    uv run ruff check --select I --fix src tests scripts
    uv run ruff format src tests scripts

lint *args: format
    #!/usr/bin/env bash
    if [[ " {{args}} " == *" --fix "* ]]; then
        uv run ruff check --fix src tests scripts
    else
        uv run ruff check src tests scripts
    fi
    uv run mypy src

audit:
    uv export --no-dev --all-extras --format requirements-txt --no-emit-project > requirements.txt
    uv run pip-audit -r requirements.txt --disable-pip
    rm requirements.txt
    uv run bandit --silent --recursive --configfile "pyproject.toml" src scripts

test:
    uv run pytest tests

dev:
    uv run python -m watchfiles "python -m spacenote.main" src

agent-start:
    SPACENOTE_PORT=8001 uv run python -m spacenote.main > .agent.log 2>&1 & echo $! > .agent.pid

agent-stop:
    -pkill -F .agent.pid 2>/dev/null || true
    -rm -f .agent.pid .agent.log

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

# Docker commands
docker-build:
    #!/usr/bin/env bash
    set -euo pipefail
    VERSION=$(grep -E '^version = ' pyproject.toml | cut -d'"' -f2)
    
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
    VERSION=$(grep -E '^version = ' pyproject.toml | cut -d'"' -f2)
    
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