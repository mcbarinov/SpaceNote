lint-frontend:
    just --justfile ./frontend/justfile lint

lint-backend:
    just --justfile ./backend/justfile lint

lint: lint-frontend lint-backend